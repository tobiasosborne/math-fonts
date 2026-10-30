#!/usr/bin/env python3
"""Build explicitly sourced, calibrated CFF/MATH additions without donor fonts.

--base-sources opts into the frozen 15-role pilot and its measured overrides.
--sources supplies complete new/overridden role records; no glyph is inferred.
See docs/ams-font-builder.md for the declarative source contract.
"""
import argparse
import hashlib
import importlib.util
import json
import math
import re
import unicodedata
from pathlib import Path

from fontTools.fontBuilder import FontBuilder
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.otlLib.builder import buildMathTable
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.ttLib.tables import otTables

# Reuse pure, authored engineering helpers. Never alter the pilot module's globals.
_spec = importlib.util.spec_from_file_location(
    '_ams_pilot_engineering', Path(__file__).with_name('build_math_pilot.py'))
pilot = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pilot)
UPM, CONSTANTS = pilot.UPM, dict(pilot.CONSTANTS)
FONT_NAME = 'BaskervilleCompanionMath-AMS.otf'
PS_NAME = 'BaskervilleCompanionMath-AMS'
REQUIRED = {'codepoints', 'kind', 'curves', 'source_crop_box', 'baseline_root',
            'source_em_pixels', 'registration_to_root', 'root_sha256', 'provenance'}
KINDS = {'greek', 'symbol', 'operator', 'delimiter', 'accent', 'special-alphabet'}
RESERVED = {'.notdef', 'space'}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def finite(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f'{label}: finite numeric value required')
    return value


def _codepoint(value):
    if isinstance(value, str) and re.fullmatch(r'U\+[0-9A-Fa-f]{4,6}', value):
        value = int(value[2:], 16)
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 0x10FFFF:
        raise ValueError('codepoints must be Unicode scalar integers or U+XXXX strings')
    if value < 33 or 0xD800 <= value <= 0xDFFF or unicodedata.category(chr(value)) == 'Cc':
        raise ValueError('Control, space, and surrogate codepoints cannot be source mappings')
    if 48 <= value <= 57 or 65 <= value <= 90 or 97 <= value <= 122:
        raise ValueError('Ordinary Latin letters and numerals must remain external Storm glyphs')
    return value


def _resolve(path, directory):
    p = Path(path)
    return str((directory / p).resolve() if not p.is_absolute() else p.resolve())


def validate_entry(name, entry, directory):
    if not isinstance(name, str) or not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_-]{0,62}', name):
        raise ValueError(f'{name!r}: a safe, unique PostScript role name is required')
    if name in RESERVED or not isinstance(entry, dict):
        raise ValueError(f'{name}: reserved name or invalid source record')
    missing = REQUIRED - entry.keys()
    if missing:
        raise ValueError(f'{name}: missing explicit fields: {", ".join(sorted(missing))}')
    if entry.get('name', name) != name:
        raise ValueError(f'{name}: source name does not match role key')
    result = dict(entry)
    if entry['kind'] not in KINDS:
        raise ValueError(f'{name}: unknown kind (expected one of {sorted(KINDS)})')
    cps = entry['codepoints']
    if not isinstance(cps, list) or not cps:
        raise ValueError(f'{name}: explicit nonempty codepoints list required')
    cps = [_codepoint(cp) for cp in cps]
    if len(cps) != len(set(cps)):
        raise ValueError(f'{name}: duplicate codepoint in role')
    result['codepoints'] = sorted(cps)
    if entry['kind'] == 'greek' and any(
            not (0x370 <= cp <= 0x3FF or 0x1D6A8 <= cp <= 0x1D7CB) for cp in cps):
        raise ValueError(f'{name}: Greek roles require explicit Greek scalar mappings')
    crop = entry['source_crop_box']
    if not isinstance(crop, list) or len(crop) != 4:
        raise ValueError(f'{name}: source_crop_box must contain four root coordinates')
    for v in crop:
        finite(v, f'{name} crop')
    if crop[2] <= crop[0] or crop[3] <= crop[1]:
        raise ValueError(f'{name}: crop must have positive width and height')
    finite(entry['baseline_root'], f'{name} baseline_root')
    if finite(entry['source_em_pixels'], f'{name} source_em_pixels') <= 0:
        raise ValueError(f'{name}: source_em_pixels must be positive')
    reg = entry['registration_to_root']
    if not isinstance(reg, dict) or set(reg) != {'scale', 'translate_x', 'translate_y'}:
        raise ValueError(f'{name}: explicit uniform scale and x/y translations required')
    for k, v in reg.items():
        finite(v, f'{name} registration {k}')
    if reg['scale'] <= 0:
        raise ValueError(f'{name}: registration scale must be positive')
    if not isinstance(entry['root_sha256'], str) or not re.fullmatch(r'[0-9a-f]{64}', entry['root_sha256']):
        raise ValueError(f'{name}: root_sha256 must be a lowercase SHA-256 digest')
    if not isinstance(entry['provenance'], dict) or not entry['provenance']:
        raise ValueError(f'{name}: nonempty explicit provenance object required')
    if not isinstance(entry['curves'], str) or not entry['curves']:
        raise ValueError(f'{name}: curves path required')
    result['curves'] = _resolve(entry['curves'], directory)
    if not Path(result['curves']).is_file():
        raise ValueError(f'{name}: curves file does not exist: {result["curves"]}')
    digest = sha(result['curves'])
    if entry.get('curves_sha256', digest) != digest:
        raise ValueError(f'{name}: curves_sha256 does not match source bytes')
    result['curves_sha256'] = digest
    result['root_image_verified'] = False
    if 'root_image' in entry:
        result['root_image'] = _resolve(entry['root_image'], directory)
        if sha(result['root_image']) != entry['root_sha256']:
            raise ValueError(f'{name}: root_image hash does not match root_sha256')
        result['root_image_verified'] = True
    return result


def load_sources(sources=None, base_sources=None):
    """Complete explicit additions override whole entries; never field-merge them."""
    entries, pilot_engineering = {}, set()
    if base_sources is not None:
        base_path = Path(base_sources).resolve()
        root_image = pilot.ROOT / 'master.png'
        root_hash = sha(root_image)
        for name, old in pilot.load_sources(base_path).items():
            reg = old['registration']
            entry = {**old, 'name': name, 'codepoints': list(pilot.ROLES[name]),
                     'kind': 'greek' if name in pilot.GREEK else 'symbol',
                     'source_em_pixels': 200, 'root_sha256': root_hash,
                     'root_image': str(root_image),
                     'registration_to_root': {'scale': reg['scale'],
                         'translate_x': reg['offset_root'][0], 'translate_y': reg['offset_root'][1]},
                     'provenance': {'source': 'explicit adoption of frozen pilot sources',
                         'base_manifest': str(base_path), 'base_manifest_sha256': sha(base_path),
                         'frozen_root': 'baskerville-unified-master-v1',
                         'registration_note': old.get('registration_note')},
                     'status': 'retained experimental pilot design; optical acceptance pending'}
            entry.pop('registration', None)
            entries[name] = validate_entry(name, entry, base_path.parent)
            pilot_engineering.add(name)
    if sources is not None:
        path = Path(sources).resolve()
        data = json.loads(path.read_text())
        supplied = data.get('sources', data.get('roles'))
        if isinstance(supplied, list):
            names = [entry.get('name') if isinstance(entry, dict) else None for entry in supplied]
            if any(not isinstance(n, str) for n in names) or len(set(names)) != len(names):
                raise ValueError('Role list requires unique explicit names')
            supplied = dict(zip(names, supplied))
        if not isinstance(supplied, dict):
            raise ValueError('Source manifest requires a sources mapping or roles list/mapping')
        for name, entry in supplied.items():
            entries[name] = validate_entry(name, entry, path.parent)
            pilot_engineering.discard(name)
    if not entries:
        raise ValueError('No sources: provide --sources and/or explicitly opt into --base-sources')
    occupied = {}
    for name, entry in sorted(entries.items()):
        for cp in entry['codepoints']:
            if cp in occupied:
                raise ValueError(f'U+{cp:04X}: conflicting roles {occupied[cp]} and {name}')
            occupied[cp] = name
    return dict(sorted(entries.items())), pilot_engineering


def outline(entry):
    """Trace pixels -> uniform root registration -> per-source calibrated UPM."""
    data = json.loads(Path(entry['curves']).read_text())
    paths = data.get('paths') if isinstance(data, dict) else None
    if not isinstance(paths, list) or not paths:
        raise ValueError('Empty traced outline')
    reg, crop = entry['registration_to_root'], entry['source_crop_box']
    factor = UPM / entry['source_em_pixels']

    def point(p):
        if not isinstance(p, (tuple, list)) or len(p) != 2:
            raise ValueError('Curve point must contain x/y coordinates')
        x, y = (finite(v, 'curve coordinate') for v in p)
        return ((x * reg['scale'] + reg['translate_x'] - crop[0]) * factor,
                (entry['baseline_root'] - y * reg['scale'] - reg['translate_y']) * factor)

    pen = RecordingPen()
    for contour in paths:
        segments = contour.get('segments') if isinstance(contour, dict) else None
        if not isinstance(segments, list) or not segments:
            raise ValueError('Every raw contour must contain segments')
        for segment in segments:
            if (not isinstance(segment, dict) or type(segment.get('tag')) is not int
                    or segment['tag'] not in (1, 2) or not isinstance(segment.get('points'), list)
                    or len(segment['points']) != 3):
                raise ValueError('Every segment requires tag 1/2 and three points')
        pen.moveTo(point(segments[-1]['points'][2]))
        for segment in segments:
            a, b, c = map(point, segment['points'])
            if segment['tag'] == 1:
                pen.curveTo(a, b, c)
            else:
                pen.lineTo(b)
                pen.lineTo(c)
        pen.closePath()
    bb = pilot.bounds(pen)
    if bb is None or bb[2] <= bb[0] or bb[3] <= bb[1]:
        raise ValueError('Source must have nonzero width and height')
    return pen, len(paths)


def _metrics(name, entry, raw, legacy):
    if name in legacy:
        return pilot.fit_metrics(name, raw)
    x0, y0, x1, y1 = pilot.bounds(raw)
    bearing = 40 if entry['kind'] == 'greek' else 60
    return pilot.transform(raw, (1, 0, 0, 1, bearing-x0, 0)), round(x1-x0+2*bearing)


def _variants(pens, advances, legacy):
    """Only retain explicitly adopted pilot finite-growth recipes for unchanged roles."""
    vertical, horizontal, recipes = {}, {}, []
    for name in ['left-paren', 'right-paren', 'radical', 'sum', 'integral']:
        if name not in legacy:
            continue
        b = pilot.bounds(pens[name])
        vertical[name] = [(name, round(b[3]-b[1]))]
        factors = [1.5, 2., 3., 4.] if name in ['left-paren', 'right-paren'] else [1.5, 2.]
        for i, factor in enumerate(factors, 1):
            variant = f'{name}.size{i}'
            pens[variant] = (pilot.radical_variant(pens[name], factor) if name == 'radical' else
                pilot.transform(pens[name], (1, 0, 0, factor, 0, CONSTANTS['AxisHeight']*(1-factor))))
            advances[variant] = advances[name]
            bb = pilot.bounds(pens[variant])
            vertical[name].append((variant, round(bb[3]-bb[1])))
            recipes.append({'glyph': variant, 'source': name, 'vertical_scale': factor,
                'around_y': CONSTANTS['AxisHeight'], 'roof_preserving_piecewise_y': name == 'radical',
                'status': 'adopted finite pilot proof placeholder; optical redesign needed'})
    if 'hat-accent' in legacy:
        name = 'hat-accent'
        bb = pilot.bounds(pens[name])
        horizontal[name] = [(name, round(bb[2]-bb[0]))]
        for i, factor in enumerate([1.5, 2.], 1):
            variant = f'{name}.wide{i}'
            pens[variant] = pilot.transform(pens[name], (factor, 0, 0, 1, 0, 0))
            advances[variant] = round(advances[name]*factor)
            bb = pilot.bounds(pens[variant])
            horizontal[name].append((variant, round(bb[2]-bb[0])))
            recipes.append({'glyph': variant, 'source': name, 'horizontal_scale': factor,
                'status': 'adopted finite pilot proof placeholder; optical redesign needed'})
    return vertical, horizontal, recipes


def build(output, sources=None, base_sources=None):
    output = Path(output)
    if any((output / f).exists() for f in [FONT_NAME, 'build-manifest.json', 'sources.json']):
        raise FileExistsError('Use a fresh output directory; existing builds are immutable')
    entries, legacy = load_sources(sources, base_sources)
    pens, advances, records = {}, {}, {}
    missing = RecordingPen()
    for points in [[(60, 0), (60, 700), (540, 700), (540, 0)],
                   [(100, 40), (500, 40), (500, 660), (100, 660)]]:
        missing.moveTo(points[0])
        for p in points[1:]:
            missing.lineTo(p)
        missing.closePath()
    pens.update({'.notdef': missing, 'space': RecordingPen()})
    advances.update({'.notdef': 600, 'space': 250})
    for name, entry in entries.items():
        raw, count = outline(entry)
        pen, advance = _metrics(name, entry, raw, legacy)
        pens[name], advances[name] = pen, advance
        signature = hashlib.sha256(json.dumps(pen.value, separators=(',', ':'), allow_nan=False).encode()).hexdigest()
        records[name] = {**entry, 'contour_count': count, 'bounds_upm': pilot.bounds(pen),
            'advance_upm': advance, 'outline_signature_sha256': signature,
            'retained_pilot_engineering': name in legacy,
            'status': entry.get('status', 'explicit source; design and optical acceptance pending')}
    vertical, horizontal, recipes = _variants(pens, advances, legacy)
    order = list(pens)
    cmap = {32: 'space', **{cp: name for name, entry in entries.items() for cp in entry['codepoints']}}
    fb = FontBuilder(UPM, isTTF=False)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap(cmap)
    boxes = [pilot.bounds(p) for p in pens.values() if pilot.bounds(p)]
    ascender = max(950, math.ceil(max(b[3] for b in boxes)))
    descender = min(-350, math.floor(min(b[1] for b in boxes)))
    fb.setupHorizontalMetrics({name: (advances[name], round(pilot.bounds(pens[name])[0]) if pilot.bounds(pens[name]) else 0) for name in order})
    fb.setupHorizontalHeader(ascent=ascender, descent=descender, lineGap=100)
    family = 'Baskerville Companion Math AMS'
    fb.setupNameTable({'familyName': family, 'styleName': 'Regular',
        'uniqueFontIdentifier': PS_NAME+'-0.1', 'fullName': family, 'psName': PS_NAME,
        'version': 'Version 0.100',
        'licenseDescription': 'Original image-derived outlines and engineering: AGPL-3.0-or-later. No Storm outlines.',
        'licenseInfoURL': 'https://www.gnu.org/licenses/agpl-3.0.html'})
    fb.setupOS2(version=4, sTypoAscender=ascender, sTypoDescender=descender, sTypoLineGap=100,
        usWinAscent=ascender, usWinDescent=-descender, sxHeight=500, sCapHeight=685, fsType=0, fsSelection=0xC0)
    fb.setupPost()
    charstrings = {}
    for name, pen in pens.items():
        t2 = T2CharStringPen(advances[name], None, roundTolerance=0)
        pen.replay(t2)
        charstrings[name] = t2.getCharString()
    fb.setupCFF(PS_NAME, {'FullName': family, 'FamilyName': family, 'Weight': 'Regular'}, charstrings, {})
    if set(CONSTANTS) != {c.name for c in otTables.MathConstants.converters}:
        raise RuntimeError('Every MATH constant must have an intentional value')
    italic = {n: max(20, round((pilot.bounds(pens[n])[2]-pilot.bounds(pens[n])[0])*.08))
              for n, entry in entries.items() if entry['kind'] == 'greek'}
    accents = {n: round((pilot.bounds(p)[0]+pilot.bounds(p)[2])/2) for n, p in pens.items() if pilot.bounds(p)}
    buildMathTable(fb.font, constants=CONSTANTS, italicsCorrections=italic,
        topAccentAttachments=accents, extendedShapes=set(vertical), minConnectorOverlap=40,
        vertGlyphVariants=vertical, horizGlyphVariants=horizontal)
    # A zero pair is real GPOS math/dflt discovery data, not optical substitution.
    first = next(iter(entries))
    addOpenTypeFeaturesFromString(fb.font,
        f'languagesystem math dflt; feature kern {{ pos {first} {first} 0; }} kern;')
    pilot.declare_empty_math_gsub(fb.font)
    fb.font['head'].created = fb.font['head'].modified = 2082844800
    fb.font.recalcTimestamp = False
    output.mkdir(parents=True, exist_ok=True)
    fb.save(output / FONT_NAME)
    manifest = {'schema_version': 1, 'font': FONT_NAME, 'font_sha256': sha(output / FONT_NAME),
        'license': 'AGPL-3.0-or-later', 'units_per_em': UPM, 'glyphs': records,
        'build_inputs': {key: {'path': str(Path(path).resolve()), 'sha256': sha(path)}
            for key, path in [('sources', sources), ('base_sources', base_sources)] if path is not None},
        'sources_snapshot_note': 'Audit snapshot; reproduce using build_inputs and the same base_sources adoption to retain pilot-only recipes.',
        'roots_sha256': sorted({e['root_sha256'] for e in entries.values()}),
        'source_em_policy': 'Per-role source_em_pixels; uniform registration before UPM conversion.',
        'glyph_order': order, 'cmap': {f'U+{cp:04X}': n for cp, n in sorted(cmap.items())},
        'math_constants': CONSTANTS, 'italic_corrections': italic, 'top_accent_attachments': accents,
        'derived_recipes': recipes,
        'math_script_declaration': f'GPOS math/dflt zero {first}-{first} pair; empty GSUB math/dflt; no substitutions',
        'limitations': ['Explicit authored source availability is not design acceptance or complete AMS coverage.',
            'All source contours, components and pinholes retained; no cleanup or donor outline substitution.',
            'Regular is a technical style name; Greek weight and matched-size optical acceptance remain unresolved.',
            'Source em, baselines, sidebearings, MATH constants and attachments require visual calibration.',
            'Only unchanged adopted pilot roles receive finite scaled variants; no assemblies, math kerns, ssty, or optical large sizes.',
            'An overridden growth/accent role needs its own engineering; pilot recipes are not applied automatically.',
            'Ordinary Latin and numerals deliberately absent; external licensed Storm configuration remains required.',
            'Codepoint identity is an explicit author assertion; source fidelity cannot prove semantic or visual correctness.']}
    (output / 'build-manifest.json').write_text(json.dumps(manifest, indent=2, allow_nan=False)+'\n')
    (output / 'sources.json').write_text(json.dumps({'sources': entries}, indent=2, allow_nan=False)+'\n')
    return manifest


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--sources', type=Path)
    p.add_argument('--base-sources', type=Path)
    args = p.parse_args()
    manifest = build(args.output, args.sources, args.base_sources)
    print(json.dumps({'font': str(args.output / FONT_NAME), 'glyph_count': len(manifest['glyph_order']),
        'mapped_scalar_count': len(manifest['cmap']), 'manifest': str(args.output / 'build-manifest.json')}))


if __name__ == '__main__':
    main()
