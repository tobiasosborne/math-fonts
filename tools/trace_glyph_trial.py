#!/usr/bin/env python3
"""Compare actual Potrace cubic outlines before/after glyph enlargement.

Calls the locally installed libpotrace via its documented C API. No image-model
calls or inherited font outlines. Cairo draws the SAME curves used in SVG.
"""
import ctypes as C
import ctypes.util
import json
import math
import sys
from pathlib import Path

from PIL import Image
from glyph_consistency_report import RUN, component, holes, np, ndimage, registered

sys.path.append('/usr/lib/python3/dist-packages')
import cairo


class Point(C.Structure):
    _fields_ = [('x', C.c_double), ('y', C.c_double)]


class Curve(C.Structure):
    _fields_ = [('n', C.c_int), ('tag', C.POINTER(C.c_int)), ('c', C.POINTER(Point * 3))]


class PathNode(C.Structure):
    pass


PathNode._fields_ = [('area', C.c_int), ('sign', C.c_int), ('curve', Curve),
                    ('next', C.POINTER(PathNode)), ('childlist', C.POINTER(PathNode)),
                    ('sibling', C.POINTER(PathNode)), ('priv', C.c_void_p)]


class State(C.Structure):
    _fields_ = [('status', C.c_int), ('plist', C.POINTER(PathNode)), ('priv', C.c_void_p)]


class Bitmap(C.Structure):
    _fields_ = [('w', C.c_int), ('h', C.c_int), ('dy', C.c_int), ('map', C.POINTER(C.c_ulong))]


class ParamPrefix(C.Structure):
    # Full allocation is owned by Potrace; access only its documented prefix.
    _fields_ = [('turdsize', C.c_int), ('turnpolicy', C.c_int), ('alphamax', C.c_double),
                ('opticurve', C.c_int), ('opttolerance', C.c_double)]


LIB = C.CDLL(ctypes.util.find_library('potrace'))
LIB.potrace_param_default.restype = C.POINTER(ParamPrefix)
LIB.potrace_param_free.argtypes = [C.POINTER(ParamPrefix)]
LIB.potrace_trace.argtypes = [C.POINTER(ParamPrefix), C.POINTER(Bitmap)]
LIB.potrace_trace.restype = C.POINTER(State)
LIB.potrace_state_free.argtypes = [C.POINTER(State)]
LIB.potrace_version.restype = C.c_char_p


def trace(image):
    darkness, mask, box, extra = component(image)
    h, w = mask.shape
    bits = C.sizeof(C.c_ulong) * 8
    padded = np.pad(mask, ((0, 0), (0, (-w) % bits)))
    packed = np.packbits(padded, axis=1, bitorder='big')
    dtype = '>u8' if bits == 64 else '>u4'
    words = np.ascontiguousarray(packed.view(dtype).astype(np.uint64 if bits == 64 else np.uint32))
    bitmap = Bitmap(w, h, words.shape[1], words.ctypes.data_as(C.POINTER(C.c_ulong)))
    param = LIB.potrace_param_default()
    assert param
    param.contents.turdsize = 0
    param.contents.alphamax = 1.
    param.contents.opticurve = 1
    param.contents.opttolerance = .0015 * (box[3] - box[1])
    state = LIB.potrace_trace(param, C.byref(bitmap))
    assert state and state.contents.status == 0
    paths = []
    try:
        node = state.contents.plist
        while node:
            item = node.contents
            segments = []
            for i in range(item.curve.n):
                segments.append({'tag': int(item.curve.tag[i]),
                                 'points': [[float(p.x), float(p.y)] for p in item.curve.c[i]]})
            paths.append({'sign': chr(item.sign), 'segments': segments})
            node = item.next
    finally:
        LIB.potrace_state_free(state)
        LIB.potrace_param_free(param)
    return paths, (w, h), box


def draw(ctx, paths):
    for path in paths:
        ctx.move_to(*path['segments'][-1]['points'][2])
        for seg in path['segments']:
            a, b, c = seg['points']
            if seg['tag'] == 1:
                ctx.curve_to(*a, *b, *c)
            elif seg['tag'] == 2:
                ctx.line_to(*b)
                ctx.line_to(*c)
            else:
                raise ValueError('Unknown Potrace segment tag')
        ctx.close_path()


def render(paths, size, supersample):
    w, h = size
    surface = cairo.ImageSurface(cairo.FORMAT_RGB24, w * supersample, h * supersample)
    ctx = cairo.Context(surface)
    ctx.set_source_rgb(1, 1, 1)
    ctx.paint()
    ctx.scale(supersample, supersample)
    ctx.set_source_rgb(0, 0, 0)
    draw(ctx, paths)
    ctx.set_fill_rule(cairo.FILL_RULE_WINDING)
    ctx.fill()
    surface.flush()
    pixels = np.frombuffer(surface.get_data(), np.uint8).reshape(h * supersample, surface.get_stride())
    gray = pixels[:, :w * supersample * 4:4].copy()
    return Image.fromarray(gray, 'L').resize(size, Image.Resampling.LANCZOS)


def svg_path(paths):
    commands = []
    fmt = lambda p: f'{p[0]:.6f},{p[1]:.6f}'
    for path in paths:
        commands.append('M' + fmt(path['segments'][-1]['points'][2]))
        for seg in path['segments']:
            a, b, c = seg['points']
            commands.append(('C' + ' '.join(map(fmt, [a, b, c]))) if seg['tag'] == 1
                            else 'L' + fmt(b) + ' ' + fmt(c))
        commands.append('Z')
    return ' '.join(commands)


def save_svg(paths, size, destination, handles=False):
    w, h = size
    path = svg_path(paths)
    # SVG + Cairo use the same image-oriented coordinate convention.
    content = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
               f'<rect width="{w}" height="{h}" fill="white"/>']
    if not handles:
        content.append(f'<path d="{path}" fill="black" fill-rule="nonzero"/>')
    else:
        unit = max(w, h) / 1000
        content.append(f'<path d="{path}" fill="none" stroke="black" stroke-width="{unit}"/>')
        for curve in paths:
            previous = curve['segments'][-1]['points'][2]
            for seg in curve['segments']:
                a, b, c = seg['points']
                if seg['tag'] == 1:
                    for anchor, control in [(previous, a), (c, b)]:
                        content.append(f'<path d="M{anchor[0]},{anchor[1]} L{control[0]},{control[1]}" stroke="#2277dd" stroke-width="{unit}"/>')
                        content.append(f'<rect x="{control[0]-2*unit}" y="{control[1]-2*unit}" width="{4*unit}" height="{4*unit}" fill="white" stroke="#2277dd" stroke-width="{unit}"/>')
                content.append(f'<circle cx="{c[0]}" cy="{c[1]}" r="{2.5*unit}" fill="#2277dd"/>')
                previous = c
    content.append('</svg>')
    destination.write_text('\n'.join(content))


def geometry(paths, glyph_height):
    angles, jumps = [], []
    cubic_count = corners = 0
    for path in paths:
        ss = path['segments']
        for i, s in enumerate(ss):
            if s['tag'] == 1:
                cubic_count += 1
            else:
                corners += 1
            nxt = ss[(i+1) % len(ss)]
            if s['tag'] != 1 or nxt['tag'] != 1:
                continue
            p0 = np.array(ss[i-1]['points'][2])
            p1, p2, p3 = map(np.array, s['points'])
            q1, q2, q3 = map(np.array, nxt['points'])
            v, u = 3*(p3-p2), 3*(q1-p3)
            av, au = 6*(p3-2*p2+p1), 6*(q2-2*q1+p3)
            if min(np.linalg.norm(v), np.linalg.norm(u)) < 1e-8:
                continue
            cosine = np.dot(v, u) / (np.linalg.norm(v)*np.linalg.norm(u))
            angles.append(math.degrees(math.acos(np.clip(cosine, -1, 1))))
            cross = lambda x, y: float(x[0]*y[1]-x[1]*y[0])
            jumps.append(abs(cross(v, av)/np.linalg.norm(v)**3 - cross(u, au)/np.linalg.norm(u)**3)*glyph_height)
    return {'cubic_segments': cubic_count, 'explicit_corner_segments': corners,
            'closed_contours': len(paths),
            'max_smooth_join_angle_degrees': max(angles, default=0),
            'median_normalized_curvature_jump': float(np.median(jumps)) if jumps else 0,
            'curvature_continuity_guaranteed': False}


def fidelity(image, vector_render):
    a, am, box, _ = component(image)
    b, bm, _, _ = component(vector_render)
    union = am | bm
    da = am & ~ndimage.binary_erosion(am)
    db = bm & ~ndimage.binary_erosion(bm)
    distances = np.concatenate([ndimage.distance_transform_edt(~da)[db],
                                ndimage.distance_transform_edt(~db)[da]])
    h = box[3] - box[1]
    return {'own_source_iou': float((am & bm).sum()/union.sum()),
            'own_source_boundary_mean_px': float(distances.mean()),
            'own_source_boundary_p95_px': float(np.percentile(distances, 95)),
            'own_source_boundary_mean_per_1000_height': float(distances.mean()/h*1000),
            'own_source_darkness_rmse_union': float(np.sqrt(np.mean((a[union]-b[union])**2))),
            'source_counters': holes(am), 'vector_counters': holes(bm)}


def main():
    out = RUN / 'vector-trial'
    out.mkdir(exist_ok=True)
    names = ['alpha', 'beta', 'theta', 'nu', 'xi', 'omega']
    results = []
    for name in names:
        folder = RUN / 'glyphs' / name
        source = Image.open(folder / 'master-crop.png').convert('L')
        enlarged = Image.open(folder / 'enlarged.png').convert('L')
        cases = [('master', source), ('lanczos8', source.resize((source.width*8, source.height*8), Image.Resampling.LANCZOS)),
                 ('generated', enlarged)]
        for mode, image in cases:
            paths, size, box = trace(image)
            stem = out / f'{name}-{mode}'
            save_svg(paths, size, stem.with_suffix('.svg'))
            save_svg(paths, size, out / f'{name}-{mode}-handles.svg', handles=True)
            ss = 8 if image.height < 300 else 2
            rendered = render(paths, size, ss)
            rendered.save(stem.with_suffix('.png'))
            record = {'name': name, 'mode': mode, 'input_dimensions': size,
                      'glyph_height': box[3]-box[1], 'render_supersample': ss,
                      'optimization_tolerance_px': .0015*(box[3]-box[1]),
                      **geometry(paths, box[3]-box[1]), **fidelity(image, rendered)}
            # Same original master is the independent reference for all three.
            _, _, cross = registered(source, rendered)
            record['original_master_iou_after_uniform_registration'] = cross['silhouette_iou']
            record['original_master_boundary_mean_px'] = cross['boundary_mean_master_px']
            results.append(record)
            (out / f'{name}-{mode}.json').write_text(json.dumps(record, indent=2)+'\n')
            print(name, mode, 'ownIoU', round(record['own_source_iou'],4),
                  'masterIoU',round(record['original_master_iou_after_uniform_registration'],4),
                  'cubics',record['cubic_segments'], flush=True)
    report = {'tool': LIB.potrace_version().decode(), 'source':'https://potrace.sourceforge.net/potracelib.pdf',
              'glyphs': names, 'results': results,
              'settings': {'threshold':128,'alphamax':1,'curve_optimization':True,
                           'tolerance_fraction_glyph_height':.0015,'despeckling':0},
              'limits':['One fixed tracing configuration, not an exhaustive comparison of vectorizers.',
                        'High overlap with generated input does not prove fidelity to the master or font quality.',
                        'Potrace smooths tangent transitions but does not guarantee curvature continuity.',
                        'Counter/semantic distinctions missing from the master cannot be established by tracing.',
                        'These SVG outlines are not a finished font: fitting, optical masters and MATH integration remain.']}
    (out / 'summary.json').write_text(json.dumps(report, indent=2)+'\n')


if __name__ == '__main__':
    main()
