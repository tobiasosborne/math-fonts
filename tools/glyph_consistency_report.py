#!/usr/bin/env python3
"""Measure fixed-master / independent enlargement fidelity, not font quality.

Registration permits translation and ONE uniform scale. It never stretches the
width independently, so aspect and anatomical drift remain measurable.
"""
import base64
import hashlib
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

try:
    import numpy as np
    from scipy import ndimage, optimize
except ImportError:
    # Explicit local fallback; these system packages were inspected and tested.
    sys.path.append('/usr/lib/python3/dist-packages')
    import numpy as np
    from scipy import ndimage, optimize

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / 'runs/glyph-consistency-2026-10-29'
LABEL = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'


def read(path):
    return json.loads(path.read_text())


def component(image):
    gray = np.asarray(image.convert('L'), dtype=np.float32)
    darkness = 1 - gray / 255
    labels, count = ndimage.label(darkness > .5)
    areas = np.bincount(labels.ravel())
    areas[0] = 0
    if not count or not areas.max():
        raise ValueError('No substantial dark silhouette')
    chosen = int(areas.argmax())
    mask = labels == chosen
    yy, xx = np.nonzero(mask)
    box = (int(xx.min()), int(yy.min()), int(xx.max()) + 1, int(yy.max()) + 1)
    # Retain gray edge pixels adjoining the chosen component, reject labels.
    nearby = ndimage.binary_dilation(mask, iterations=4)
    darkness *= nearby
    return darkness, mask, box, int(areas.sum() - areas[chosen])


def holes(mask):
    labels, _ = ndimage.label(ndimage.binary_fill_holes(mask) & ~mask)
    # Subpixel/one-pixel pinholes after resampling are not meaningful counters.
    return int(np.count_nonzero(np.bincount(labels.ravel())[1:] >= 4))


def thickness(mask):
    dt = ndimage.distance_transform_edt(mask)
    ridge = (dt == ndimage.maximum_filter(dt, size=3)) & (dt > 1)
    values = 2 * dt[ridge]
    return float(np.median(values)) if len(values) else 0.


def registered(master, target):
    a, am, ab, ax = component(master)
    b, bm, bb, bx = component(target)
    bx0, by0, bx1, by1 = bb
    b = b[max(0, by0 - 8):by1 + 8, max(0, bx0 - 8):bx1 + 8]
    bm = b > .5
    sy = (ab[3] - ab[1]) / (bb[3] - bb[1])
    ac = ndimage.center_of_mass(am)
    bc = ndimage.center_of_mass(bm)
    initial = np.array([np.log(sy), ac[1] - sy * bc[1], ac[0] - sy * bc[0]])
    # Controlled antialiasing before native-resolution image-space optimization.
    filtered = ndimage.gaussian_filter(b, max(.1, .45 / sy))

    def warp(p, supersample=1, raw=False):
        scale = np.exp(p[0])
        return ndimage.affine_transform(
            b if raw else filtered, np.eye(2) / (scale * supersample),
            offset=(np.array([-p[2], -p[1]]) + .5 / supersample - .5) / scale,
            output_shape=tuple(v * supersample for v in a.shape), order=1,
            mode='constant', cval=0, prefilter=False)

    def objective(p):
        return float(np.mean((warp(p) - a) ** 2))

    bounds = [(initial[0] - .18, initial[0] + .18),
              (initial[1] - 12, initial[1] + 12),
              (initial[2] - 12, initial[2] + 12)]
    fit = optimize.minimize(objective, initial, method='Powell', bounds=bounds,
                            options={'maxiter': 25, 'maxfev': 250, 'xtol': .005, 'ftol': 1e-8})
    p = fit.x if objective(fit.x) <= objective(initial) else initial
    # Final evaluation renders at 8x and downsamples with the same recorded filter.
    hi = Image.fromarray(np.uint8(np.clip(warp(p, 8, True), 0, 1) * 255), 'L')
    aligned = np.asarray(hi.resize((a.shape[1], a.shape[0]), Image.Resampling.LANCZOS), dtype=np.float32) / 255
    cm = aligned > .5
    union = am | cm
    intersection = am & cm
    ba = am & ~ndimage.binary_erosion(am)
    bb_mask = cm & ~ndimage.binary_erosion(cm)
    da = ndimage.distance_transform_edt(~ba)
    db = ndimage.distance_transform_edt(~bb_mask)
    distances = np.concatenate([da[bb_mask], db[ba]])
    aspect_a = (ab[2] - ab[0]) / (ab[3] - ab[1])
    aspect_b = (bb[2] - bb[0]) / (bb[3] - bb[1])
    h = ab[3] - ab[1]
    metrics = {
        'silhouette_iou': float(intersection.sum() / max(1, union.sum())),
        'boundary_mean_master_px': float(distances.mean()),
        'boundary_p95_master_px': float(np.percentile(distances, 95)),
        'boundary_max_master_px': float(distances.max()),
        'boundary_mean_fraction_height': float(distances.mean() / h),
        'darkness_rmse_union': float(np.sqrt(np.mean((aligned[union] - a[union]) ** 2))),
        'ink_area_change_fraction': float(cm.sum() / am.sum() - 1),
        'aspect_change_fraction': float(aspect_b / aspect_a - 1),
        'master_counters': holes(am), 'enlarged_counters': holes(cm),
        'master_thickness_proxy_px': thickness(am), 'enlarged_thickness_proxy_px': thickness(cm),
        'master_glyph_height_px': h, 'extra_dark_pixels_outside_main_component': bx,
        'master_extra_dark_pixels': ax,
        'registration': {'uniform_scale': float(np.exp(p[0])), 'translate_x': float(p[1]),
                         'translate_y': float(p[2]), 'function_evaluations': int(fit.nfev),
                         'independent_width_stretch': False},
    }
    return a, aligned, metrics


def compare_png(a, b, destination):
    scale = 2
    w, h = a.shape[1] * scale, a.shape[0] * scale
    result = Image.new('RGB', (w * 3, h + 58), 'white')
    d = ImageDraw.Draw(result)
    font = ImageFont.truetype(LABEL, 15)
    for index, (arr, title) in enumerate([(a, 'Master crop'), (b, 'Enlargement aligned')]):
        im = Image.fromarray(np.uint8(np.clip(1 - arr, 0, 1) * 255)).convert('RGB')
        result.paste(im.resize((w, h), Image.Resampling.LANCZOS), (index * w, 42))
        d.text((index * w + 8, 12), title, fill='black', font=font)
    aa, bb = a > .5, b > .5
    overlay = np.full((*a.shape, 3), 255, dtype=np.uint8)
    overlay[aa & bb] = [0, 0, 0]
    overlay[aa & ~bb] = [208, 60, 95]
    overlay[bb & ~aa] = [40, 119, 205]
    result.paste(Image.fromarray(overlay).resize((w, h), Image.Resampling.NEAREST), (w * 2, 42))
    d.text((w * 2 + 8, 12), 'Red: master / blue: enlarged', fill='black', font=font)
    result.save(destination)


def main():
    results = []
    for entry in read(RUN / 'requests.json'):
        folder = Path(entry['folder'])
        if not (folder / 'result.json').exists():
            continue
        generation = read(folder / 'result.json')
        if generation['status'] != 'complete':
            results.append({'name': entry['name'], 'char': entry['char'], 'status': 'failed'})
            continue
        a, b, metrics = registered(Image.open(entry['crop']), Image.open(folder / 'enlarged.png'))
        compare_png(a, b, folder / 'comparison.png')
        Image.fromarray(np.uint8(np.clip(1 - b, 0, 1) * 255)).save(folder / 'registered.png')
        record = {'name': entry['name'], 'char': entry['char'], 'status': 'complete', **metrics}
        (folder / 'metrics.json').write_text(json.dumps(record, indent=2) + '\n')
        results.append(record)
    good = [r for r in results if r['status'] == 'complete']
    report = {'completed': len(good), 'requested': 32, 'results': results,
              'median_iou': float(np.median([r['silhouette_iou'] for r in good])) if good else None,
              'counter_count_changes': [r['name'] for r in good if r['master_counters'] != r['enlarged_counters']],
              'method': 'Threshold128; largest connected dark component; translate + uniform scale only; bounded250-evaluation registration;8x render then Lanczos downsample; symmetric binary-boundary distances.',
              'limits': ['Metrics quantify raster consistency, not typeface quality or correct mathematical identity.',
                         'Per-glyph registration removes framing/size differences; it does not establish common font metrics, fitting or baseline consistency.',
                         'The small master is uncertain at about a pixel scale; enlarged detail is inferred rather than recovered.',
                         'Near-duplicate epsilon/kappa/phi variants in the master remain separate source-design concerns.',
                         'Raw grayscale darkness is compared; the image model renderer/gamma/PSF are not exposed.',
                         'Distance-transform ridge thickness is a proxy, not a measured font stem width.']}
    (RUN / 'measurements.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'results'}, indent=2))


if __name__ == '__main__':
    main()
