#!/usr/bin/env python3
"""Build the bounded, original-ink CFF/MATH companion pilot; never reads a donor font.

--sources JSON: {"sources": {role: {"curves": "path/to/curves.json",
"source_crop_box": [root_left, root_top, root_right, root_bottom],
"baseline_root": 197, "registration": {"scale": 0.25,
"offset_root": [root_left, root_top]}, "registration_note": "measured..."}}}
Paths resolve relative to the manifest. Registration maps TRACE pixel coordinates
into the unified ROOT: root_xy = trace_xy * scale + offset_root. A single scale
is mandatory: independent width/height fitting is forbidden. Crop and baseline
are in unchanged root coordinates; offsets default to crop origin for 1:1 crops.
Missing roles use the frozen small-source traces. No inference of enlargement
registration is performed: the caller must supply measured registration.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

from fontTools.fontBuilder import FontBuilder
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.otlLib.builder import buildMathTable
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import newTable
from fontTools.ttLib.tables import otTables

REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / 'runs/unified-master-2026-10-29/candidate-01'
FONT_NAME = 'BaskervilleCompanionMath-Pilot.otf'
GREEK = {'alpha': (0x3B1, 0x1D6FC), 'beta': (0x3B2, 0x1D6FD),
         'theta': (0x3B8, 0x1D703), 'nu': (0x3BD, 0x1D708),
         'xi': (0x3BE, 0x1D709), 'omega': (0x3C9, 0x1D714)}
SYMBOLS = {'plus': (0x2B,), 'minus': (0x2212,), 'equals': (0x3D,),
           'sum': (0x2211,), 'integral': (0x222B,), 'radical': (0x221A,),
           'left-paren': (0x28,), 'right-paren': (0x29,), 'hat-accent': (0x302,)}
ROLES = {**GREEK, **SYMBOLS}
UPM = 1000
# Intentional engineering baseline, authored here; no donor MATH table.
CONSTANTS = dict(
    ScriptPercentScaleDown=70, ScriptScriptPercentScaleDown=50,
    DelimitedSubFormulaMinHeight=1300, DisplayOperatorMinHeight=1300,
    MathLeading=150, AxisHeight=250, AccentBaseHeight=500,
    FlattenedAccentBaseHeight=685, SubscriptShiftDown=220,
    SubscriptTopMax=400, SubscriptBaselineDropMin=100,
    SuperscriptShiftUp=400, SuperscriptShiftUpCramped=350,
    SuperscriptBottomMin=120, SuperscriptBaselineDropMax=250,
    SubSuperscriptGapMin=160, SuperscriptBottomMaxWithSubscript=300,
    SpaceAfterScript=50, UpperLimitGapMin=120, UpperLimitBaselineRiseMin=600,
    LowerLimitGapMin=120, LowerLimitBaselineDropMin=600,
    StackTopShiftUp=450, StackTopDisplayStyleShiftUp=650,
    StackBottomShiftDown=350, StackBottomDisplayStyleShiftDown=600,
    StackGapMin=160, StackDisplayStyleGapMin=280,
    StretchStackTopShiftUp=600, StretchStackBottomShiftDown=500,
    StretchStackGapAboveMin=120, StretchStackGapBelowMin=120,
    FractionNumeratorShiftUp=400, FractionNumeratorDisplayStyleShiftUp=650,
    FractionDenominatorShiftDown=350, FractionDenominatorDisplayStyleShiftDown=600,
    FractionNumeratorGapMin=100, FractionNumDisplayStyleGapMin=180,
    FractionRuleThickness=40, FractionDenominatorGapMin=100,
    FractionDenomDisplayStyleGapMin=180, SkewedFractionHorizontalGap=300,
    SkewedFractionVerticalGap=150, OverbarVerticalGap=120,
    OverbarRuleThickness=40, OverbarExtraAscender=40, UnderbarVerticalGap=120,
    UnderbarRuleThickness=40, UnderbarExtraDescender=40,
    RadicalVerticalGap=80, RadicalDisplayStyleVerticalGap=160,
    RadicalRuleThickness=50, RadicalExtraAscender=40,
    RadicalKernBeforeDegree=250, RadicalKernAfterDegree=-100,
    RadicalDegreeBottomRaisePercent=60)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def defaults():
    metrics = json.loads((ROOT / 'provisional-metrics.json').read_text())
    cells = {c['name']: c for c in json.loads((ROOT / 'cells.json').read_text())['cells']}
    return {name: {'curves': str(ROOT / 'small-source-traces' / name / 'curves.json'),
                   'source_crop_box': cells[name]['source_crop_box'],
                   'baseline_root': metrics['row_baselines'][cells[name]['row'] - 1],
                   'registration': {'scale': 1, 'offset_root': cells[name]['source_crop_box'][:2]},
                   'registration_note': 'Unchanged clean crop from unified root; 1:1 source coordinates.'}
            for name in ROLES}


def load_sources(path=None):
    sources = defaults()
    if path:
        path = Path(path).resolve()
        supplied = json.loads(path.read_text())
        supplied = supplied.get('sources', supplied)
        if set(supplied) - set(ROLES):
            raise ValueError('Only the 15 custom pilot roles may be supplied')
        for name, entry in supplied.items():
            entry = dict(entry)
            if 'registration_to_root' in entry:
                reg = entry['registration_to_root']
                entry['registration'] = {'scale': reg['scale'],
                                         'offset_root': [reg['translate_x'], reg['translate_y']]}
            if 'registration' not in entry:
                raise ValueError(f'{name}: explicit uniform registration required')
            sources[name].update(entry)
            p = Path(entry['curves'])
            sources[name]['curves'] = str((path.parent / p).resolve() if not p.is_absolute() else p)
    return sources


def outline(entry):
    """All source contours -> root registration -> common UPM; return cubic pen."""
    data = json.loads(Path(entry['curves']).read_text())
    scale = float(entry['registration']['scale'])
    offset = entry['registration']['offset_root']
    values = [scale, *offset, entry['baseline_root'], *entry['source_crop_box']]
    if not all(math.isfinite(v) for v in values) or scale <= 0:
        raise ValueError('Registration must be finite with positive uniform scale')
    if len(offset) != 2 or len(entry['source_crop_box']) != 4:
        raise ValueError('Registration offset and crop must have 2 and 4 coordinates')
    # All sources share the root source_em=200, independent of crop dimensions.
    factor = UPM / 200
    crop_x = entry['source_crop_box'][0]
    def point(p):
        x, y = p
        if not all(math.isfinite(v) for v in p):
            raise ValueError('Nonfinite curve coordinate')
        return ((x * scale + offset[0] - crop_x) * factor,
                (entry['baseline_root'] - y * scale - offset[1]) * factor)
    pen = RecordingPen()
    if not data['paths']:
        raise ValueError('Empty traced outline')
    for contour in data['paths']:
        segments = contour['segments']
        pen.moveTo(point(segments[-1]['points'][2]))
        for segment in segments:
            a, b, c = map(point, segment['points'])
            if segment['tag'] == 1:
                pen.curveTo(a, b, c)
            elif segment['tag'] == 2:
                pen.lineTo(b)
                pen.lineTo(c)
            else:
                raise ValueError('Unknown Potrace segment tag')
        pen.closePath()
    return pen, len(data['paths'])


def bounds(pen):
    p = BoundsPen(None)
    pen.replay(p)
    return p.bounds


def transform(pen, matrix):
    result = RecordingPen()
    pen.replay(TransformPen(result, matrix))
    return result


def fit_metrics(name, pen):
    """Only translate outlines for sidebearings; never change their design size."""
    x0, y0, x1, y1 = bounds(pen)
    lsb = 40 if name in GREEK else 60
    rsb = 40 if name in GREEK else 60
    # Math accents are positioned relative to AccentBaseHeight by TeX.
    # Register clean source ink above that height instead of its image-row
    # baseline; this is a translation, not a change to the drawn hat.
    dy = CONSTANTS['AccentBaseHeight']+25-y0 if name == 'hat-accent' else 0
    fitted = transform(pen, (1, 0, 0, 1, lsb-x0, dy))
    # TeX draws the vinculum at the radical advance; its ink must overlap.
    if name == 'radical':
        return fitted, math.floor(bounds(fitted)[2])-20
    return fitted, round(x1-x0+lsb+rsb)



def radical_variant(pen, factor):
    """Grow the generated radical while retaining its 50-UPM roof thickness.

    The frozen root roof measures y=745..795 UPM (50 UPM). This is a
    specific measured derivative, not a general radical-recognition algorithm.
    Its roof is the source's original polygonal top strip. Map that strip by
    translation and grow the lower tick monotonically, preserving all contours.
    Unlike whole-y scaling, this keeps the roof compatible with TeX's rule.
    """
    x0, y0, x1, y1 = bounds(pen)
    roof = CONSTANTS['RadicalRuleThickness']
    top = 250 + (y1 - 250) * factor
    bottom = 250 + (y0 - 250) * factor
    lower_scale = ((top-bottom)-roof) / ((y1-y0)-roof)
    def point(p):
        x, y = p
        yy = top + y-y1 if y >= y1-roof else bottom + (y-y0)*lower_scale
        return (x, yy)
    result = RecordingPen()
    for op, pts in pen.value:
        getattr(result, op)(*[point(p) for p in pts])
    return result


def declare_empty_math_gsub(font):
    """XeTeX discovers math through GSUB; this declares no substitutions."""
    gsub = newTable('GSUB')
    gsub.table = otTables.GSUB()
    gsub.table.Version = 0x10000
    script = otTables.Script()
    lang = otTables.LangSys()
    lang.LookupOrder, lang.ReqFeatureIndex = None, 65535
    lang.FeatureIndex, lang.FeatureCount = [], 0
    script.DefaultLangSys = lang
    script.LangSysRecord, script.LangSysCount = [], 0
    record = otTables.ScriptRecord()
    record.ScriptTag, record.Script = 'math', script
    gsub.table.ScriptList = otTables.ScriptList()
    gsub.table.ScriptList.ScriptRecord = [record]
    gsub.table.ScriptList.ScriptCount = 1
    gsub.table.FeatureList = otTables.FeatureList()
    gsub.table.FeatureList.FeatureRecord, gsub.table.FeatureList.FeatureCount = [], 0
    gsub.table.LookupList = otTables.LookupList()
    gsub.table.LookupList.Lookup, gsub.table.LookupList.LookupCount = [], 0
    font['GSUB'] = gsub


def build(output, sources=None):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    if (output / FONT_NAME).exists() or (output / 'build-manifest.json').exists():
        raise FileExistsError('Use a fresh output directory; existing builds are immutable')
    sources = load_sources(sources)
    pens, advances, records = {}, {}, {}
    blank = RecordingPen()
    # Original technical missing-glyph box, not copied from a typeface.
    missing = RecordingPen()
    for points in [[(60, 0), (60, 700), (540, 700), (540, 0)],
                   [(100, 40), (500, 40), (500, 660), (100, 660)]]:
        missing.moveTo(points[0])
        for p in points[1:]: missing.lineTo(p)
        missing.closePath()
    pens.update({'.notdef': missing, 'space': blank})
    advances.update({'.notdef': 600, 'space': 250})
    for name, entry in sources.items():
        raw, count = outline(entry)
        pen, advance = fit_metrics(name, raw)
        pens[name], advances[name] = pen, advance
        records[name] = {**entry, 'curves_sha256': sha(entry['curves']),
                         'contour_count': count, 'bounds_upm': bounds(pen),
                         'advance_upm': advance,
                         'status': 'custom Greek pilot' if name in GREEK else 'experimental custom sign; stock-sign audit pending production decision'}
    vertical, horizontal = {}, {}
    recipes = [{'glyph': 'radical', 'source': 'registered original radical',
                'advance_rule': 'floor(ink xMax)-20 UPM; joins engine vinculum with 20-UPM overlap',
                'roof_thickness_upm': 50, 'source_roof_y_upm': [745, 795]},
               {'glyph': 'hat-accent', 'source': 'registered original hat',
                'placement_rule': 'positive advance and bearings; explicit ink-center MATH attachment; translate ink ymin to AccentBaseHeight+25',
                'target_ink_ymin_upm': CONSTANTS['AccentBaseHeight']+25,
                'source_y_translation_upm': CONSTANTS['AccentBaseHeight']+25-bounds(outline(sources['hat-accent'])[0])[1],
                'reason': 'avoid negative-bearing normalization in math loaders'}]
    # Bounded engineering placeholders, not a claim of designed optical sizes.
    for name in ['left-paren', 'right-paren', 'radical', 'sum', 'integral']:
        b = bounds(pens[name]); variants = [(name, round(b[3]-b[1]))]
        factors = [1.5, 2.0, 3.0, 4.0] if name in ['left-paren', 'right-paren'] else [1.5, 2.0]
        for i, factor in enumerate(factors, 1):
            variant = f'{name}.size{i}'
            pens[variant] = (radical_variant(pens[name], factor) if name == 'radical' else
                             transform(pens[name], (1, 0, 0, factor, 0, 250*(1-factor))))
            advances[variant] = advances[name]
            bb = bounds(pens[variant]); variants.append((variant, round(bb[3]-bb[1])))
            recipes.append({'glyph': variant, 'source': name, 'vertical_scale': factor,
                            'around_y': 250,
                            'roof_preserving_piecewise_y': name == 'radical',
                            'status': 'finite stretched proof placeholder; optical redesign needed'})
        vertical[name] = variants
    horizontal['hat-accent'] = [('hat-accent', round(bounds(pens['hat-accent'])[2]-bounds(pens['hat-accent'])[0]))]
    for i, factor in enumerate([1.5, 2.0], 1):
        variant = f'hat-accent.wide{i}'
        pens[variant] = transform(pens['hat-accent'], (factor, 0, 0, 1, 0, 0))
        advances[variant] = round(advances['hat-accent']*factor)
        bb = bounds(pens[variant]); horizontal['hat-accent'].append((variant, round(bb[2]-bb[0])))
        recipes.append({'glyph': variant, 'source': 'hat-accent', 'horizontal_scale': factor,
                        'status': 'finite stretched proof placeholder'})
    order = list(pens)
    fb = FontBuilder(UPM, isTTF=False)
    fb.setupGlyphOrder(order)
    cmap = {32: 'space', **{cp: name for name, cps in ROLES.items() for cp in cps}}
    fb.setupCharacterMap(cmap)
    all_bounds = [bounds(p) for p in pens.values() if bounds(p)]
    ascender = max(950, math.ceil(max(b[3] for b in all_bounds)))
    descender = min(-350, math.floor(min(b[1] for b in all_bounds)))
    fb.setupHorizontalMetrics({name: (advances[name], round(bounds(pens[name])[0]) if bounds(pens[name]) else 0) for name in order})
    fb.setupHorizontalHeader(ascent=ascender, descent=descender, lineGap=100)
    fb.setupNameTable({'familyName': 'Baskerville Companion Math Pilot', 'styleName': 'Regular',
                      'uniqueFontIdentifier': 'BaskervilleCompanionMath-Pilot-0.1',
                      'fullName': 'Baskerville Companion Math Pilot',
                      'psName': 'BaskervilleCompanionMath-Pilot', 'version': 'Version 0.100',
                      'licenseDescription': 'Original generated-image outline pilot and engineering: AGPL-3.0-or-later. No Storm outlines.',
                      'licenseInfoURL': 'https://www.gnu.org/licenses/agpl-3.0.html'})
    fb.setupOS2(version=4, sTypoAscender=ascender, sTypoDescender=descender, sTypoLineGap=100,
                usWinAscent=ascender, usWinDescent=-descender, sxHeight=500,
                sCapHeight=685, fsType=0, fsSelection=0xC0)
    fb.setupPost()
    charstrings = {}
    for name, pen in pens.items():
        t2 = T2CharStringPen(advances[name], None, roundTolerance=0)
        pen.replay(t2)
        charstrings[name] = t2.getCharString()
    fb.setupCFF('BaskervilleCompanionMath-Pilot',
                {'FullName': 'Baskerville Companion Math Pilot',
                 'FamilyName': 'Baskerville Companion Math Pilot', 'Weight': 'Regular'}, charstrings, {})
    if set(CONSTANTS) != {c.name for c in otTables.MathConstants.converters}:
        raise RuntimeError('Every MATH constant must have an intentional value')
    italic = {n: max(20, round((bounds(pens[n])[2]-bounds(pens[n])[0])*0.08)) for n in GREEK}
    accents = {n: round((bounds(p)[0]+bounds(p)[2])/2) for n, p in pens.items() if bounds(p)}
    buildMathTable(fb.font, constants=CONSTANTS, italicsCorrections=italic,
                   topAccentAttachments=accents, extendedShapes=set(vertical),
                   minConnectorOverlap=40, vertGlyphVariants=vertical,
                   horizGlyphVariants=horizontal)
    # unicode-math/fontspec require a discoverable math script as well as
    # MATH data. Lua ignores empty layout feature sets. A genuine zero-valued
    # pair lookup declares the script without changing any drawing or spacing.
    addOpenTypeFeaturesFromString(fb.font,
        'languagesystem math dflt; feature kern { pos alpha beta 0; } kern;')
    declare_empty_math_gsub(fb.font)
    # Fixed OpenType timestamp: identical inputs produce identical binaries.
    fb.font['head'].created = fb.font['head'].modified = 2082844800
    fb.font.recalcTimestamp = False
    fb.save(output / FONT_NAME)
    manifest = {'schema_version': 1, 'font': FONT_NAME, 'font_sha256': sha(output / FONT_NAME),
                'license': 'AGPL-3.0-or-later', 'units_per_em': UPM,
                'root_sha256': sha(ROOT / 'master.png'), 'source_em_pixels': 200,
                'glyphs': records, 'derived_recipes': recipes, 'glyph_order': order,
                'cmap': {f'U+{cp:04X}': name for cp, name in sorted(cmap.items())},
                'math_constants': CONSTANTS, 'italic_corrections': italic,
                'math_script_declaration': 'GPOS math/dflt zero alpha-beta pair plus empty GSUB math/dflt; no substitutions',
                'top_accent_attachments': accents,
                'limitations': ['15 custom pilot roles only; not full AMS coverage.',
                    'Frozen small-source traces are provisional; source pinholes and all components preserved.',
                    'Greek visual weight unresolved; Regular is a technical style name only.',
                    'Common source-em and row baselines are provisional, not Storm calibration.',
                    'MATH constants, sidebearings, italic corrections and accent attachments require visual calibration.',
                    'Finite scaled variants only (parens up to 4x); no assemblies, optical large sizes, math kerns, or ssty.',
                    'Radical finite variants preserve 50-UPM source roof; tick optical proportions remain provisional.',
                    'No third-party outlines; ordinary Latin and numerals deliberately absent.',
                    'Custom signs are experimental existing design evidence; production sourcing audit remains required.']}
    (output / 'build-manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    (output / 'sources.json').write_text(json.dumps({'sources': sources}, indent=2)+'\n')
    return manifest


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--sources', type=Path)
    args = p.parse_args()
    manifest = build(args.output, args.sources)
    print(json.dumps({'font': str(args.output / FONT_NAME), 'glyph_count': len(manifest['glyph_order']),
                      'manifest': str(args.output / 'build-manifest.json')}))


if __name__ == '__main__':
    main()
