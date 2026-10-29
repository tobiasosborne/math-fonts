#!/usr/bin/env python3
"""Trace every dark component in a caller-supplied clean mathematical ink ROI.

No glyph recognition, crop inference, registration, despeckling, or independent
normalization is performed. Labels and guides must already be excluded by the
caller. Potrace is an external GPL-2.0-or-later dependency; no Potrace tracing
implementation or font outline data is included here.
"""
import argparse
import ctypes as C
import hashlib
import json
import math
from pathlib import Path

from PIL import Image

# Reuse the inspected C declarations and curve exporters, never the old
# largest-component extraction, trace(), fidelity(), or any historical main().
# This import also enables the repository's explicit system-package fallback.
from trace_glyph_trial import Bitmap, LIB, geometry, np, ndimage, render, save_svg

THRESHOLD = 128
FG_STRUCTURE = np.ones((3, 3), dtype=bool)
BG_STRUCTURE = ndimage.generate_binary_structure(2, 1)


def foreground(image, *, allow_color=False):
    """Return composited grayscale, ALL gray<128 ink, and extraction metadata.

    RGB is interpreted through Pillow's luminance conversion. Chromatic input
    needs explicit opt-in because a color guide cannot be recognized as a guide.
    Alpha is always composited on white BEFORE luminance/thresholding, including
    palette transparency. Hidden RGB in transparent pixels is never dark ink.
    Unsupported high-bit-depth/color-space modes are rejected, not guessed.
    """
    if image.mode not in {'1', 'L', 'LA', 'RGB', 'RGBA', 'P'}:
        raise ValueError(f'Unsupported source mode {image.mode!r}; supply an 8-bit clean ROI')
    alpha = 'A' in image.getbands() or 'transparency' in image.info
    rgba = image.convert('RGBA')
    rgb_image = Image.alpha_composite(Image.new('RGBA', image.size, 'white'), rgba).convert('RGB')
    rgb = np.asarray(rgb_image, dtype=np.int16)
    chromatic = np.max(rgb, axis=2) - np.min(rgb, axis=2) > 2
    chromatic_pixels = int(chromatic.sum())
    if chromatic_pixels and not allow_color:
        raise ValueError('Chromatic RGB pixels present; remove guides/labels or explicitly allow color luminance')
    gray = np.asarray(rgb_image.convert('L')).copy()
    mask = gray < THRESHOLD
    if not mask.any():
        raise ValueError('No ink below threshold 128 after white alpha compositing')
    return gray, mask, {
        'input_mode': image.mode,
        'alpha_present': alpha,
        'alpha_background': 'white' if alpha else None,
        'luminance_conversion': 'Pillow RGB to L',
        'chromatic_pixels_after_compositing': chromatic_pixels,
        'chromatic_rule': 'max(R,G,B) - min(R,G,B) > 2 after compositing',
        'chromatic_input_allowed': allow_color,
        'threshold_rule': 'gray < 128',
        'removed_ink_pixels': 0,
        'roi_contract': 'Caller supplies clean ink only; no labels/guides are detected or removed.',
    }


def _mask(mask):
    mask = np.asarray(mask)
    if mask.ndim != 2 or mask.dtype != np.bool_ or not mask.size:
        raise ValueError('Expected a nonempty two-dimensional boolean mask')
    if not mask.any():
        raise ValueError('Empty ink mask')
    return mask


def topology(mask):
    """Unfiltered pixel topology: 8-connected ink, dual 4-connected background.

    Every component and one-pixel counter counts. A white pad identifies the
    single exterior background even when ink touches the original canvas edge.
    Bounding boxes are [left, top, right, bottom), in unchanged source pixels.
    """
    mask = np.asarray(mask, dtype=bool)
    if mask.ndim != 2 or not mask.size:
        raise ValueError('Expected a nonempty two-dimensional mask')
    labels, count = ndimage.label(mask, structure=FG_STRUCTURE)
    areas = np.bincount(labels.ravel(), minlength=count + 1)
    components = []
    for index, slices in enumerate(ndimage.find_objects(labels), 1):
        yy, xx = slices
        region = labels[yy, xx] == index
        cy, cx = ndimage.center_of_mass(region)
        components.append({'pixels': int(areas[index]),
                           'bbox': [xx.start, yy.start, xx.stop, yy.stop],
                           'centroid': [float(cx + xx.start), float(cy + yy.start)]})
    background = ~np.pad(mask, 1, constant_values=False)
    bg_labels, bg_count = ndimage.label(background, structure=BG_STRUCTURE)
    exterior = int(bg_labels[0, 0])
    bg_areas = np.bincount(bg_labels.ravel(), minlength=bg_count + 1)
    counters = [int(bg_areas[i]) for i in range(1, bg_count + 1) if i != exterior]
    ys, xs = np.nonzero(mask)
    bbox = [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1] if len(xs) else None
    return {'ink_pixels': int(mask.sum()), 'component_count': int(count),
            'components': components, 'counter_count': len(counters),
            'counter_areas': counters, 'euler_characteristic': int(count) - len(counters),
            'ink_bbox': bbox, 'foreground_connectivity': 8, 'background_connectivity': 4,
            'ink_touches_canvas_edge': bool(mask[0].any() or mask[-1].any() or mask[:, 0].any() or mask[:, -1].any())}


def bitmap_words(mask):
    """Pack leftmost pixels into native unsigned-long MSBs, including row padding."""
    mask = _mask(mask)
    bits = C.sizeof(C.c_ulong) * 8
    if bits not in (32, 64):
        raise RuntimeError(f'Unsupported Potrace word size {bits}')
    w = mask.shape[1]
    padded = np.pad(mask, ((0, 0), (0, (-w) % bits)))
    packed = np.packbits(padded, axis=1, bitorder='big')
    # Convert network-order values to native unsigned longs, rather than merely
    # reinterpreting byte order (which would mirror bits in little-endian words).
    words = packed.view('>u8' if bits == 64 else '>u4').astype(np.uint64 if bits == 64 else np.uint32)
    return np.ascontiguousarray(words)


def trace_mask(mask, *, tolerance_px=.2):
    """Trace the entire mask, retaining its dimensions, position, and every speck."""
    mask = _mask(mask)
    if not math.isfinite(tolerance_px) or tolerance_px < 0:
        raise ValueError('Optimization tolerance must be finite and nonnegative')
    h, w = mask.shape
    words = bitmap_words(mask)
    bitmap = Bitmap(w, h, words.shape[1], words.ctypes.data_as(C.POINTER(C.c_ulong)))
    param = LIB.potrace_param_default()
    if not param:
        raise RuntimeError('Potrace could not allocate parameters')
    state = None
    try:
        param.contents.turdsize = 0  # Never discard even a single isolated pixel.
        param.contents.alphamax = 1.
        param.contents.opticurve = 1
        param.contents.opttolerance = tolerance_px
        state = LIB.potrace_trace(param, C.byref(bitmap))
        if not state or state.contents.status != 0:
            raise RuntimeError('Potrace tracing failed')
        paths = []
        node = state.contents.plist
        while node:
            item = node.contents
            segments = []
            for i in range(item.curve.n):
                tag = int(item.curve.tag[i])
                if tag not in (1, 2):
                    raise RuntimeError(f'Unknown Potrace segment tag {tag}')
                segments.append({'tag': tag,
                                 'points': [[float(p.x), float(p.y)] for p in item.curve.c[i]]})
            if not segments:
                raise RuntimeError('Potrace returned an empty contour')
            paths.append({'sign': chr(item.sign), 'area': int(item.area), 'segments': segments})
            node = item.next
        if not paths:
            raise RuntimeError('Potrace returned no contours for nonempty ink')
        return paths
    finally:
        if state:
            LIB.potrace_state_free(state)
        LIB.potrace_param_free(param)


def component_correspondence(source, rendered):
    """Check spatial overlap for every component without matching glyph semantics."""
    a, na = ndimage.label(source, structure=FG_STRUCTURE)
    b, nb = ndimage.label(rendered, structure=FG_STRUCTURE)
    # Only pixels jointly ink in both masks establish correspondence. Counting
    # alone could overlook a vanished dot replaced by an unrelated new speck.
    jointly_ink = (a > 0) & (b > 0)
    pairs = np.unique(np.column_stack((a[jointly_ink], b[jointly_ink])), axis=0)
    source_targets = [[] for _ in range(na)]
    render_sources = [[] for _ in range(nb)]
    for first, second in pairs:
        source_targets[first - 1].append(int(second))
        render_sources[second - 1].append(int(first))
    return {'source_to_render_components': source_targets,
            'render_to_source_components': render_sources,
            'each_source_overlaps_exactly_one_render_component': all(len(v) == 1 for v in source_targets),
            'each_render_overlaps_exactly_one_source_component': all(len(v) == 1 for v in render_sources)}


def fidelity(gray, vector_render):
    """Measure full-canvas fidelity without cropping, registration or filtering."""
    a = np.asarray(gray, dtype=np.uint8)
    b = np.asarray(vector_render.convert('L'))
    if a.ndim != 2 or a.shape != b.shape:
        raise ValueError('Fidelity requires identical full-canvas dimensions')
    am, bm = a < THRESHOLD, b < THRESHOLD
    union = am | bm
    if not am.any():
        raise ValueError('Fidelity source has empty ink')
    aa, bb = a.astype(float) / 255, b.astype(float) / 255
    da = am & ~ndimage.binary_erosion(am)
    db = bm & ~ndimage.binary_erosion(bm)
    distances = (np.concatenate([ndimage.distance_transform_edt(~da)[db],
                                 ndimage.distance_transform_edt(~db)[da]]) if db.any() else None)
    source, traced = topology(am), topology(bm)
    correspondence = component_correspondence(am, bm)
    checks = {'each_source_component_has_one_spatial_match': correspondence['each_source_overlaps_exactly_one_render_component'],
              'each_render_component_has_one_spatial_match': correspondence['each_render_overlaps_exactly_one_source_component'],
              'component_count_equal': source['component_count'] == traced['component_count'],
              'counter_count_equal': source['counter_count'] == traced['counter_count']}
    return {'full_canvas_iou': float((am & bm).sum() / union.sum()),
            'lost_ink_pixels': int((am & ~bm).sum()), 'added_ink_pixels': int((bm & ~am).sum()),
            'boundary_mean_px': float(distances.mean()) if distances is not None else None,
            'boundary_p95_px': float(np.percentile(distances, 95)) if distances is not None else None,
            'boundary_max_px': float(distances.max()) if distances is not None else None,
            'grayscale_rmse_union': float(np.sqrt(np.mean((aa[union] - bb[union]) ** 2))),
            'grayscale_rmse_full_canvas': float(np.sqrt(np.mean((aa - bb) ** 2))),
            'source_topology': source, 'render_topology': traced,
            'component_correspondence': correspondence,
            'topology_checks': checks, 'raster_topology_preserved': all(checks.values())}


def trace_image(image, *, allow_color=False, tolerance_px=.2, supersample=4):
    """Return reusable curves, a same-size rerender, and auditable measurements."""
    if not isinstance(supersample, int) or isinstance(supersample, bool) or not 1 <= supersample <= 16:
        raise ValueError('Supersampling must be an integer from 1 to 16')
    if image.width * image.height * supersample ** 2 > 100_000_000:
        raise ValueError('Rerender exceeds 100 million pixels; reduce supersampling or supply a smaller clean ROI')
    gray, mask, extraction = foreground(image, allow_color=allow_color)
    paths = trace_mask(mask, tolerance_px=tolerance_px)
    rerender = render(paths, image.size, supersample)
    metrics = fidelity(gray, rerender)
    source = metrics['source_topology']
    positive = sum(p['sign'] == '+' for p in paths)
    negative = sum(p['sign'] == '-' for p in paths)
    contour_checks = {'positive_contours_equal_source_components': positive == source['component_count'],
                      'negative_contours_equal_source_counters': negative == source['counter_count']}
    bbox = source['ink_bbox']
    report = {
        'schema_version': 1, 'potrace_version': LIB.potrace_version().decode(),
        'source_dimensions': list(image.size), 'extraction': extraction,
        'coordinates': 'Source image coordinates, x right/y down; no crop, registration, translation, or scaling.',
        'settings': {'threshold': THRESHOLD, 'despeckling': 0, 'alphamax': 1.,
                     'curve_optimization': True, 'optimization_tolerance_px': tolerance_px,
                     'turnpolicy': 'Potrace default (minority)', 'render_supersample': supersample},
        'geometry': geometry(paths, bbox[3] - bbox[1]),
        'positive_contours': positive, 'negative_contours': negative,
        'contour_topology_checks': contour_checks,
        'fidelity': metrics,
        'topology_preserved': metrics['raster_topology_preserved'] and all(contour_checks.values()),
        'limits': ['Ink semantics, family consistency, and font quality are not established by raster fidelity.',
                   'Thresholding cannot recover missing marks or distinguish labels/guides from intended ink.',
                   'Topology checks count every pixel component/counter; diagonal ambiguities and very small features require inspection.',
                   'Potrace does not guarantee curvature continuity; no font metrics or MATH table are built.'],
    }
    return paths, rerender, report


def export(input_path, output_path, *, allow_color=False, tolerance_px=.2, supersample=4):
    """Write a fresh artifact directory; existing destinations are never reused."""
    input_path, output_path = Path(input_path), Path(output_path)
    if output_path.exists() or output_path.is_symlink():
        raise FileExistsError(f'Output must be a fresh directory: {output_path}')
    # Hash exactly the input bytes decoded here, avoiding an input/hash race.
    import io
    raw = input_path.read_bytes()
    with Image.open(io.BytesIO(raw)) as image:
        if getattr(image, 'n_frames', 1) != 1:
            raise ValueError('Supply one clean single-frame ROI, not an animation or multipage image')
        paths, rerender, report = trace_image(image, allow_color=allow_color,
                                            tolerance_px=tolerance_px, supersample=supersample)
    report['input'] = {'path': str(input_path.resolve()), 'sha256': hashlib.sha256(raw).hexdigest()}
    output_path.mkdir(parents=True, exist_ok=False)
    size = tuple(report['source_dimensions'])
    save_svg(paths, size, output_path / 'filled.svg')
    save_svg(paths, size, output_path / 'handles.svg', handles=True)
    rerender.save(output_path / 'rerender.png')
    (output_path / 'curves.json').write_text(json.dumps({'dimensions': list(size), 'paths': paths}, indent=2) + '\n')
    (output_path / 'metrics.json').write_text(json.dumps(report, indent=2, allow_nan=False) + '\n')
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path, help='Clean single-glyph/symbol ROI; caller must exclude labels and guides')
    parser.add_argument('--output', required=True, type=Path, help='Fresh artifact directory (overwrite refused)')
    parser.add_argument('--allow-color', action='store_true', help='Explicitly convert chromatic ink by luminance after white compositing')
    parser.add_argument('--tolerance-px', type=float, default=.2)
    parser.add_argument('--supersample', type=int, default=4)
    args = parser.parse_args(argv)
    try:
        report = export(args.input, args.output, allow_color=args.allow_color,
                        tolerance_px=args.tolerance_px, supersample=args.supersample)
    except (ValueError, OSError, RuntimeError) as exc:
        parser.exit(1, f'math_trace: {exc}\n')
    print(json.dumps({'output': str(args.output), 'topology_preserved': report['topology_preserved'],
                      'full_canvas_iou': report['fidelity']['full_canvas_iou']}))
    # Retain diagnostic artifacts, but never silently claim topology success.
    return 0 if report['topology_preserved'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
