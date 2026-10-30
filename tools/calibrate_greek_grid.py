#!/usr/bin/env python3
"""Measure an external italic text grid and record explicit Greek optical fits.

This does not redraw outlines, infer a baseline from canvas whitespace, or
change image registration. All fits are uniform similarities in font units.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import statistics

from fontTools.misc.bezierTools import calcCubicBounds
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
NAMES = ['alpha', 'beta', 'theta', 'nu', 'xi', 'omega']
BEFORE = ROOT / 'runs/ams-coverage-2026-10-30/delivery-arrows-03/font/BaskervilleCompanionMath-AMS.otf'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_new(path, value):
    path = Path(path)
    data = json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n'
    if path.exists() and path.read_text() != data:
        raise FileExistsError(f'Immutable grid evidence differs: {path}')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data)


def glyph_bounds(font, name):
    gs = font.getGlyphSet()
    pen = BoundsPen(gs)
    gs[name].draw(pen)
    return list(pen.bounds)


def measure_text(path):
    reference = json.loads((ROOT / 'design/storm-reference.json').read_text())
    expected = next(face['sha256'] for face in reference['faces'] if face['style'] == 'Italic')
    if sha(path) != expected:
        raise ValueError('External Storm italic hash differs from pinned reference')
    font = TTFont(path)
    if font['head'].unitsPerEm != 1000:
        raise ValueError('Explicit normalization required for another em')
    cmap = font.getBestCmap()
    controls = {char: {'bounds_upm': glyph_bounds(font, cmap[ord(char)]),
                       'advance_upm': font['hmtx'][cmap[ord(char)]][0]}
                for char in 'xnoacebdhklfgpqyH'}
    xheight = statistics.median(controls[c]['bounds_upm'][3] for c in 'xnoace')
    ascender = statistics.median(controls[c]['bounds_upm'][3] for c in 'bdhkl')
    lower = statistics.median(controls[c]['bounds_upm'][1] for c in 'oace')
    descender = statistics.median(controls[c]['bounds_upm'][1] for c in 'pq')
    descender_overshoot = min(controls[c]['bounds_upm'][1] for c in 'fgpqy')
    return {'schema_version': 1, 'units_per_em': 1000,
            'reference': {'filename': Path(path).name, 'sha256': expected,
                          'font_identity': font['name'].getDebugName(6)},
            'guides': {'baseline': 0, 'x_height': xheight,
                       'cap_height': font['OS/2'].sCapHeight,
                       'ascender': ascender, 'descender': descender,
                       'lower_overshoot': lower, 'descender_overshoot': descender_overshoot},
            'slant_degrees': font['post'].italicAngle,
            'controls': controls,
            'font_metrics': {'ascender': font['OS/2'].sTypoAscender,
                'descender': font['OS/2'].sTypoDescender,
                'line_gap': font['OS/2'].sTypoLineGap,
                'x_height': font['OS/2'].sxHeight, 'cap_height': font['OS/2'].sCapHeight},
            'zones': {'body_bottom': [lower, 0], 'body_top_observed': [xheight, xheight],
                      'descender_bottom': [descender_overshoot, descender]},
            'sources': ['https://learn.microsoft.com/en-us/typography/opentype/spec/os2',
                        'https://glyphsapp.com/learn/vertical-metrics/',
                        'https://glyphsapp.com/learn/sketching'],
            'policy': 'Measured outline landmarks, not generic overshoot assumptions. Line metrics and visible outline heights are distinct. Guides are removable; source ink stays unchanged.'}


def anatomy(font, name):
    bounds = glyph_bounds(font, name)
    if name in ['alpha', 'nu', 'omega', 'theta']:
        return {'body_bottom': bounds[1], 'top': bounds[3],
                'selector': 'Actual lower/upper curve extrema; non-descending anatomy.'}
    pen = RecordingPen()
    font.getGlyphSet()[name].draw(pen)
    if name == 'beta':
        # Reviewed outer lower bowl, not the descending stem or inner counter.
        op, controls = pen.value[10]
        if op != 'curveTo':
            raise ValueError('Beta anatomical landmark changed; review required')
        start = pen.value[9][1][-1]
        bottom = calcCubicBounds(start, *controls)[1]
        selector = {'operation': 10, 'kind': 'outer_lower_bowl_y_min',
                    'start': start, 'controls': controls}
    elif name == 'xi':
        op, controls = pen.value[5]
        if op != 'curveTo':
            raise ValueError('Xi anatomical landmark changed; review required')
        bottom = controls[-1][1]
        selector = {'operation': 5, 'kind': 'lower_body_to_descending_tail_join',
                    'point': controls[-1],
                    'review': 'Chosen visible lower-body join; tail remains a descender, not a bounding-box baseline.'}
    else:
        raise ValueError('A new Greek needs a reviewed anatomy class and landmarks')
    return {'body_bottom': bottom, 'top': bounds[3], 'selector': selector}


def prepare(text_font, output, grid_path=ROOT / 'design/greek-text-grid.json'):
    output = Path(output)
    if output.exists():
        raise FileExistsError('Use a fresh calibration run')
    grid = measure_text(text_font)
    font = TTFont(BEFORE)
    sources = json.loads((BEFORE.parent / 'build-manifest.json').read_text())['glyphs']
    roles = {}
    for name in NAMES:
        marks = anatomy(font, name)
        target_top = grid['guides']['x_height' if name in ['alpha','nu','omega'] else 'ascender']
        target_bottom = grid['guides']['lower_overshoot']
        scale = (target_top-target_bottom)/(marks['top']-marks['body_bottom'])
        shift = target_bottom-scale*marks['body_bottom']
        if not .9 <= scale <= 1.1 or abs(shift) > 200:
            raise ValueError(f'{name}: bounded similarity is insufficient; redesign required')
        roles[name] = {'class': 'x_height_body' if name in ['alpha','nu','omega'] else 'tall_round' if name=='theta' else 'tall_descending',
            'source_curves_sha256': sources[name]['curves_sha256'],
            'before_bounds_upm': glyph_bounds(font, name),
            'landmarks_before': marks,
            'targets': {'body_bottom': target_bottom, 'top': target_top},
            'uniform_scale': scale, 'translate_y': shift,
            'method': 'Explicit optical similarity against text landmarks; preserves aspect, slant, curves and topology. Source registration is not changed.',
            'descender_policy': 'Descending anatomy may stop above the text descender line; do not force every tail to the same depth.'}
    profile = {'schema_version': 1, 'units_per_em': 1000,
               'before_font_sha256': sha(BEFORE), 'grid': str(Path(grid_path).relative_to(ROOT)),
               'font_metrics': grid['font_metrics'],
               'math_constants': {'AccentBaseHeight': int(grid['guides']['x_height']),
                                  'FlattenedAccentBaseHeight': int(grid['guides']['cap_height'])},
               'roles': roles,
               'limits': 'No anisotropic deformation, node edits, automatic baseline inference, slant shear or weight compensation. Widths keep the authored aspect; spacing remains a separate optical task.'}
    write_new(grid_path, grid)
    write_new(output / 'calibration.json', profile)
    return profile


def audit(after, profile_path, output):
    profile = json.loads(Path(profile_path).read_text())
    font = TTFont(after)
    records = {}
    for name, correction in profile['roles'].items():
        actual = anatomy(font, name)
        residuals = {key: actual[key]-correction['targets'][key] for key in ['body_bottom','top']}
        if max(abs(v) for v in residuals.values()) > .02:
            raise ValueError(f'{name}: post-build grid residual exceeds .02 UPM: {residuals}')
        box = glyph_bounds(font, name)
        if box[1] < -286.02:
            raise ValueError(f'{name}: descender exceeds reference envelope')
        records[name] = {'before_bounds_upm': correction['before_bounds_upm'],
                         'after_bounds_upm': box, 'landmark_residuals_upm': residuals,
                         'uniform_scale': correction['uniform_scale'],
                         'translate_y': correction['translate_y']}
    fm = profile['font_metrics']
    if (font['OS/2'].sxHeight,font['OS/2'].sCapHeight) != (fm['x_height'],fm['cap_height']):
        raise ValueError('Compiled x-height/cap metadata differs from grid')
    if (font['hhea'].ascent,font['hhea'].descent,font['hhea'].lineGap) != (fm['ascender'],fm['descender'],fm['line_gap']):
        raise ValueError('Compiled line metrics differ from text')
    result = {'status':'passed_grid_landmarks_not_final_optical_acceptance',
              'font_sha256':sha(after), 'profile_sha256':sha(profile_path),
              'glyphs':records, 'tolerance_upm':.02,
              'caveats':['Six reviewed Greek only; new anatomy requires explicit landmark review.',
                         'Slant, stroke weight, italic corrections and spacing still require optical work.']}
    write_new(output, result)
    return result


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--text-font',type=Path)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--after-font',type=Path)
    p.add_argument('--profile',type=Path)
    a=p.parse_args()
    if a.after_font:
        print(json.dumps(audit(a.after_font,a.profile,a.output),indent=2))
    else:
        if not a.text_font:p.error('--text-font required to measure reference')
        profile=prepare(a.text_font,a.output)
        print(json.dumps({name:{'scale':e['uniform_scale'],'dy':e['translate_y']} for name,e in profile['roles'].items()},indent=2))
