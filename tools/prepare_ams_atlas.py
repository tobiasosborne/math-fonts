#!/usr/bin/env python3
"""Measure the bounded v2 8x8 atlas; save untouched ink-region crops and audits.

No tracing, font build, image generation, cleanup, normalization, or promotion.
Existing outputs must match byte-for-byte; conflicting evidence is never replaced.
"""
import argparse
import hashlib
import io
import json
import math
import statistics
from pathlib import Path

import PIL
from PIL import Image

REPO = Path(__file__).resolve().parents[1]
DEFAULT = REPO / 'runs/ams-coverage-2026-10-30/master-v2/candidate-01'
V1 = REPO / 'runs/unified-master-2026-10-29/candidate-01'
EXPECTED_SHA = 'edfb27bedf078bcba86d18112c15d4f03bc25b2bdc6fc0e23083209e85390db7'
ROOT_ID = 'baskerville-unified-master-v2-candidate-01'
ROWS = [
    [('alpha', 'α', 0x1D6FC, 'alpha'), ('beta', 'β', 0x1D6FD, 'beta'),
     ('gamma', 'γ', 0x1D6FE, 'gamma'), ('delta', 'δ', 0x1D6FF, 'delta'),
     ('epsilon-lobed', 'ε', 0x1D700, 'varepsilon'), ('zeta', 'ζ', 0x1D701, 'zeta'),
     ('eta', 'η', 0x1D702, 'eta'), ('theta', 'θ', 0x1D703, 'theta')],
    [('iota', 'ι', 0x1D704, 'iota'), ('kappa', 'κ', 0x1D705, 'kappa'),
     ('lambda', 'λ', 0x1D706, 'lambda'), ('mu', 'μ', 0x1D707, 'mu'),
     ('nu', 'ν', 0x1D708, 'nu'), ('xi', 'ξ', 0x1D709, 'xi'),
     ('omicron', 'ο', 0x1D70A, 'omicron'), ('pi', 'π', 0x1D70B, 'pi')],
    [('rho', 'ρ', 0x1D70C, 'rho'), ('final-sigma', 'ς', 0x1D70D, 'varsigma'),
     ('sigma', 'σ', 0x1D70E, 'sigma'), ('tau', 'τ', 0x1D70F, 'tau'),
     ('upsilon', 'υ', 0x1D710, 'upsilon'), ('phi-looped', 'φ', 0x1D711, 'varphi'),
     ('chi', 'χ', 0x1D712, 'chi'), ('psi', 'ψ', 0x1D713, 'psi')],
    [('omega', 'ω', 0x1D714, 'omega'), ('epsilon-lunate', 'ϵ', 0x1D716, 'epsilon'),
     ('theta-variant', 'ϑ', 0x1D717, 'vartheta'), ('kappa-variant', 'ϰ', 0x1D718, 'varkappa'),
     ('phi-straight', 'ϕ', 0x1D719, 'phi'), ('rho-variant', 'ϱ', 0x1D71A, 'varrho'),
     ('pi-variant', 'ϖ', 0x1D71B, 'varpi'), ('partial', '∂', 0x1D715, 'partial')],
    [('left-bracket', '[', None, 'lbrack'), ('right-bracket', ']', None, 'rbrack'),
     ('left-brace', '{', None, 'lbrace'), ('right-brace', '}', None, 'rbrace'),
     ('left-floor', '⌊', None, 'lfloor'), ('right-floor', '⌋', None, 'rfloor'),
     ('left-ceil', '⌈', None, 'lceil'), ('right-ceil', '⌉', None, 'rceil')],
    [('element', '∈', None, 'in'), ('not-element', '∉', None, 'notin'),
     ('subset', '⊂', None, 'subset'), ('subset-equal', '⊆', None, 'subseteq'),
     ('precedes', '≺', None, 'prec'), ('precedes-equal', '≼', None, 'preccurlyeq'),
     ('succeeds', '≻', None, 'succ'), ('succeeds-equal', '≽', None, 'succcurlyeq')],
    [('forall', '∀', None, 'forall'), ('exists', '∃', None, 'exists'),
     ('emptyset', '∅', None, 'varnothing'), ('nabla', '∇', None, 'nabla'),
     ('vdash', '⊢', None, 'vdash'), ('dashv', '⊣', None, 'dashv'),
     ('models', '⊨', None, 'models'), ('perpendicular', '⊥', None, 'perp')],
    [('right-arrow', '→', None, 'rightarrow'), ('double-iff', '⇔', None, 'Leftrightarrow'),
     ('maps-to', '↦', None, 'mapsto'), ('left-right-arrow', '↔', None, 'leftrightarrow'),
     ('left-harpoon', '↼', None, 'leftharpoonup'), ('right-harpoon', '⇀', None, 'rightharpoonup'),
     ('hook-left', '↩', None, 'hookleftarrow'), ('twohead-right', '↠', None, 'twoheadrightarrow')],
]
ANCHORS = {'alpha', 'beta', 'theta', 'nu', 'xi', 'omega'}
QUARANTINE = {
    'epsilon-lunate': 'Wrong variant: visibly two-lobed epsilon, not the requested lunate epsilon with middle bar.',
    'kappa-variant': 'Near duplicate of regular kappa; distinct varkappa anatomy is not established.',
    'phi-looped': 'Straight oblique central stem and near-duplicate phi-straight silhouette; requested distinct looped varphi anatomy absent.',
    'left-harpoon': 'Full two-sided arrowhead, not the requested single-sided harpoon.',
    'right-harpoon': 'Full two-sided arrowhead, not the requested single-sided harpoon.',
    'twohead-right': 'Double horizontal shaft/implication-like arrow, not two arrowheads on one shaft.',
}


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(data):
    return (json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False)+'\n').encode()


def runs(indices):
    result = []
    for i in indices:
        if result and i == result[-1][1]+1:
            result[-1][1] = i
        else:
            result.append([i, i])
    return result


def grid_and_windows(image):
    """Measure full grid bands and glyph/label whitespace; never erase pixels."""
    gray = image.convert('L')
    w, h = gray.size
    pixels = gray.tobytes()
    horizontal = runs(y for y in range(h)
        if sum(v < 245 for v in pixels[y*w:(y+1)*w]) > .85*w)
    vertical = runs(x for x in range(w)
        if sum(pixels[y*w+x] < 245 for y in range(h)) > .85*h)
    if len(horizontal) != 9 or len(vertical) != 9:
        raise ValueError('Expected exactly nine measured horizontal and vertical grid bands')
    windows = []
    for row in range(8):
        top, bottom = horizontal[row][1]+3, horizontal[row+1][0]-2
        left, right = vertical[0][1]+3, vertical[-1][0]-2
        ink_runs = runs(y for y in range(top, bottom)
            if any(v < 128 for v in pixels[y*w+left:y*w+right]))
        if len(ink_runs) != 2:
            raise ValueError(f'Row {row+1}: glyph and label bands are not separated unambiguously')
        glyph, label = ink_runs
        gap = [glyph[1]+1, label[0]]
        if gap[1]-gap[0] < 4:
            raise ValueError(f'Row {row+1}: insufficient whitespace before labels')
        windows.append({'row': row+1, 'glyph_dark_y_inclusive': glyph,
            'label_dark_y_inclusive': label, 'separating_whitespace_y': gap,
            'crop_y': [top, (gap[0]+gap[1])//2],
            'label_exclusion_y': [(gap[0]+gap[1])//2, bottom]})
    return horizontal, vertical, windows


def ink_bbox(image):
    return image.convert('L').point(lambda v: 255 if v < 128 else 0).getbbox()


def components(image):
    """Count every threshold component, including specks; report without removal."""
    gray = image.convert('L')
    w, h = gray.size
    todo = {i for i, value in enumerate(gray.tobytes()) if value < 128}
    areas = []
    while todo:
        stack = [todo.pop()]
        area = 0
        while stack:
            i = stack.pop()
            area += 1
            x, y = i % w, i // w
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    xx, yy = x+dx, y+dy
                    if 0 <= xx < w and 0 <= yy < h:
                        neighbor = yy*w+xx
                        if neighbor in todo:
                            todo.remove(neighbor)
                            stack.append(neighbor)
        areas.append(area)
    return sorted(areas, reverse=True)


def calibration(cells, v1=V1):
    old = json.loads((v1 / 'cells.json').read_text())
    metrics = json.loads((v1 / 'provisional-metrics.json').read_text())
    if sha_bytes((v1 / 'master.png').read_bytes()) != old['root_sha256']:
        raise ValueError('V1 reference root hash does not match frozen cell evidence')
    old_cells = {c['name']: c for c in old['cells']}
    observations, ratios, dimension_pairs = [], [], []
    for cell in cells:
        name = cell['name']
        if name not in ANCHORS:
            continue
        prior = old_cells[name]
        prior_image = Image.open(v1 / 'master.png')
        original_crop = prior_image.crop(prior['source_crop_box'])
        bb = ink_bbox(original_crop)
        v1_bbox = [bb[0]+prior['source_crop_box'][0], bb[1]+prior['source_crop_box'][1],
                   bb[2]+prior['source_crop_box'][0], bb[3]+prior['source_crop_box'][1]]
        if list(bb) != prior['ink_bbox_in_crop']:
            raise ValueError(f'{name}: frozen v1 metadata does not match actual anchor pixels')
        v2_bbox = cell['ink_bbox_root']
        sizes1 = [v1_bbox[2]-v1_bbox[0], v1_bbox[3]-v1_bbox[1]]
        sizes2 = [v2_bbox[2]-v2_bbox[0], v2_bbox[3]-v2_bbox[1]]
        local = [b/a for a, b in zip(sizes1, sizes2)]
        ratios.extend(local)
        dimension_pairs.extend(zip(sizes1, sizes2))
        observations.append({'name': name, 'row_v2': cell['row'],
            'v1_bbox_root': v1_bbox, 'v2_bbox_root': v2_bbox,
            'v1_baseline_root': metrics['row_baselines'][prior['row']-1],
            'v2_row_grid_top': cell['grid_cell_box'][1],
            'width_ratio_v2_over_v1': local[0], 'height_ratio_v2_over_v1': local[1]})
    scale = statistics.median(ratios)
    offsets = []
    for obs in observations:
        a, b = obs['v1_bbox_root'], obs['v2_bbox_root']
        top_baseline = b[1] + scale*(obs['v1_baseline_root']-a[1])
        bottom_baseline = b[3] + scale*(obs['v1_baseline_root']-a[3])
        proposal = (top_baseline+bottom_baseline)/2-obs['v2_row_grid_top']
        offsets.append(proposal)
        obs.update({'baseline_offset_from_top_edge_pixels': top_baseline-obs['v2_row_grid_top'],
            'baseline_offset_from_bottom_edge_pixels': bottom_baseline-obs['v2_row_grid_top'],
            'baseline_offset_midpoint_pixels': proposal,
            'width_residual_pixels': (b[2]-b[0])-scale*(a[2]-a[0]),
            'height_residual_pixels': (b[3]-b[1])-scale*(a[3]-a[1])})
    baseline_offset = statistics.median(offsets)
    for obs in observations:
        obs['baseline_offset_residual_pixels'] = obs['baseline_offset_midpoint_pixels']-baseline_offset
    row_tops = {cell['row']: cell['grid_cell_box'][1] for cell in cells if cell['row'] <= 4}
    return {'schema_version': 1, 'status': 'provisional_uncertain; not an accepted optical/font calibration',
        'method': 'Median of six anchor width and height ratios (12 observations); common baseline offset is median of six top/bottom-derived midpoint offsets. No per-glyph scaling.',
        'root_sha256': cells[0]['root_sha256'], 'v1_root_sha256': old['root_sha256'],
        'v1_cells_sha256': sha_bytes((v1 / 'cells.json').read_bytes()),
        'v1_metrics_sha256': sha_bytes((v1 / 'provisional-metrics.json').read_bytes()),
        'v1_source_em_pixels': metrics['source_em_pixels'], 'scale_v2_over_v1': scale,
        'source_em_pixels': scale*metrics['source_em_pixels'],
        'comparison_scale_least_squares': sum(a*b for a,b in dimension_pairs)/sum(a*a for a,b in dimension_pairs),
        'comparison_width_ratio_median': statistics.median(o['width_ratio_v2_over_v1'] for o in observations),
        'comparison_height_ratio_median': statistics.median(o['height_ratio_v2_over_v1'] for o in observations),
        'scale_ratio_range': [min(ratios), max(ratios)],
        'scale_ratio_median_absolute_deviation': statistics.median(abs(v-scale) for v in ratios),
        'row_baseline_offset_pixels': baseline_offset,
        'baseline_offset_proposal_range_pixels': [min(offsets), max(offsets)],
        'baseline_offset_median_absolute_deviation_pixels': statistics.median(abs(v-baseline_offset) for v in offsets),
        'rms_dimension_residual_pixels': math.sqrt(statistics.mean(
            o[key]**2 for o in observations for key in ['width_residual_pixels', 'height_residual_pixels'])),
        'row_baselines': {str(row): top+baseline_offset for row, top in sorted(row_tops.items())},
        'observed_anchor_rows': sorted({o['row_v2'] for o in observations}),
        'unanchored_greek_rows': [3], 'anchors': observations,
        'uncertainties': ['V1 em and row baselines were themselves provisional; this is not Storm metric calibration.',
            'Anchor width/height ratios disagree: v2 is a redraw, not a registered pixel-identical expansion.',
            'Bounding-box calibration does not measure silhouette fidelity, stroke weight, slant or local anatomy.',
            'Row 3 has no retained v1 anchor; its baseline is extrapolated from the shared grid-offset model.',
            'Rows 5-8 have no calibrated font baseline and are reference prototypes only.',
            'Only one shared scale and one baseline offset are proposed; no per-glyph fitting is authorized.',
            'Retain the actual six pilot glyphs from v1; do not replace them with atlas redraws.']}


def _review(cells, cal):
    return f'''# Expanded unified atlas candidate 01: bounded source review

This 1024×1536 candidate has been measured and cropped, not accepted as a font
or full AMS coverage. Root SHA-256: `{cells[0]['root_sha256']}`.
All 64 crops preserve original pixels and every dark component; labels and
grids are excluded using measured rectangular gutters, without ink cleanup.
`cells.json` records exact geometry, identities, source hashes and dispositions.

The existing regular-companion alpha, beta, theta, nu, xi and omega remain the
actual retained v1 font sources. Their v2 drawings are calibration evidence only.
The atlas's first four rows contain 31 Greek targets plus partial; they do not
include digamma from the older 32-glyph seed. No automatic coverage credit.

## Semantic quarantine

- **r4c2 epsilon-lunate (ϵ, \\epsilon):** drawn as lobed ε, not lunate ϵ.
- **r4c4 kappa-variant (ϰ, \\varkappa):** too close to ordinary κ; distinct
  anatomy is not established.
- **r3c6 phi-looped (φ, \\varphi):** duplicates the straight-stem design rather
  than providing the requested distinct looped variant.
- **r8c5/r8c6 harpoons:** both have full two-sided arrowheads.
- **r8c8 twohead-right:** has two shafts like a double arrow, not two heads
  along one shaft. These bottom-row shapes must never be production references.

The r1c5 lobed ε correctly belongs to **\\varepsilon**, not \\epsilon.
The r4c5 phi-straight was reviewed independently: its straight central stem,
elliptical bowl and descender are a plausible **ϕ / \\phi** prototype. Its
similarity to r3c6 disqualifies r3c6 as a distinct varphi; it does not by itself
disqualify r4c5. Weight, aperture and reading-size performance remain unaccepted.
The distinct theta/rho/pi variants are recognizable source candidates, subject
to individual enlarged and working-size review. Labels are intent, not proof.

Rows 5–7 and the remaining arrows are grammar prototypes only. Their thin,
nearly monoline strokes are visibly unlike the Greek's heavier contrast; stock
sign sourcing, joining/growth construction and optical acceptance remain open.
No sign is installed or claimed as completed by this preparation.

## Shared calibration and its limits

Six retained v1 anchors provide twelve measured width/height ratios. Their
median proposes **{cal['scale_v2_over_v1']:.9f}×** v1 and an atlas em of
**{cal['source_em_pixels']:.6f} pixels**, derived from v1's provisional 200-pixel em.
Widths alone give {cal['comparison_width_ratio_median']:.6f}; heights alone give
{cal['comparison_height_ratio_median']:.6f}. The range is
{cal['scale_ratio_range'][0]:.6f}–{cal['scale_ratio_range'][1]:.6f}; RMS dimension
residual is **{cal['rms_dimension_residual_pixels']:.3f} atlas pixels**. This
disagreement is real evidence of changed proportions, not a scale to hide.

The common baseline offset is **{cal['row_baseline_offset_pixels']:.6f} pixels**
below each row's measured upper grid edge. Per-anchor baseline proposals span
{cal['baseline_offset_proposal_range_pixels'][0]:.3f}–{cal['baseline_offset_proposal_range_pixels'][1]:.3f}
pixels. Row 3 has no retained anchor; its baseline is an extrapolation. See
`calibration.json` for every observation, residual and explicit uncertainty.
This is a provisional engineering proposal; the v1 metrics themselves were
provisional and no Storm matched-size calibration or silhouette acceptance is
implied. There is one shared atlas em and shared row logic, never independent
glyph normalization.

## Reproduction

Run `.venv/bin/python tools/prepare_ams_atlas.py` from the repository root.
The tool compares existing artifacts byte-for-byte and refuses differences;
it does not overwrite historical evidence. No image generation or font build
is involved. Crop encoding uses Pillow {PIL.__version__} and fixed PNG settings.
All crops are source evidence, including quarantined shapes. Builder proposals
in `cells.json` intentionally remain incomplete: a real registered trace and
provenance must be supplied, and the provisional calibration must be reviewed.
'''


def prepare(directory=DEFAULT, v1=V1):
    directory, v1 = Path(directory), Path(v1)
    raw = (directory / 'master.png').read_bytes()
    digest = sha_bytes(raw)
    if digest != EXPECTED_SHA:
        raise ValueError('Wrong candidate image hash; this measured review applies only to candidate 01')
    with Image.open(io.BytesIO(raw)) as original:
        image = original.copy()
    if image.size != (1024, 1536):
        raise ValueError('Expected the reviewed 1024x1536 candidate')
    horizontal, vertical, windows = grid_and_windows(image)
    artifacts, cells = {}, []
    for r, row in enumerate(ROWS):
        for c, (name, character, alias, tex) in enumerate(row):
            box = [vertical[c][1]+3, windows[r]['crop_y'][0],
                   vertical[c+1][0]-2, windows[r]['crop_y'][1]]
            crop = image.crop(box)
            bb = ink_bbox(crop)
            if bb is None or min(bb[0], bb[1], crop.width-bb[2], crop.height-bb[3]) < 2:
                raise ValueError(f'{name}: crop lacks a safe dark-ink margin')
            stream = io.BytesIO()
            crop.save(stream, format='PNG', optimize=False, compress_level=9)
            encoded = stream.getvalue()
            artifacts[Path('crops') / f'{name}.png'] = encoded
            quarantine = name in QUARANTINE
            status = ('quarantined_semantic_failure' if quarantine else
                'retained_v1_anchor_redraw_evidence_only' if name in ANCHORS else
                'provisional_greek_design_reference' if r < 4 else 'family_grammar_prototype_only')
            cps = [ord(character)] + ([alias] if alias else [])
            if name == 'phi-straight':
                note = 'Independently reviewed: plausible straight-stem phi (ϕ); duplicate r3c6 does not establish distinct varphi. Optical acceptance pending.'
            else:
                note = QUARANTINE.get(name, 'Identity is visually plausible; not optical acceptance or font coverage.')
            areas = components(crop)
            cells.append({'name': name, 'character': character, 'row': r+1, 'column': c+1,
                'codepoints': cps, 'unicode_labels': [f'U+{cp:04X}' for cp in cps],
                'tex_command': '\\'+tex, 'root_id': ROOT_ID, 'root_sha256': digest,
                'grid_cell_box': [vertical[c][0], horizontal[r][0], vertical[c+1][1]+1, horizontal[r+1][1]+1],
                'source_crop_box': box, 'crop': f'crops/{name}.png', 'crop_sha256': sha_bytes(encoded),
                'ink_bbox_in_crop': list(bb), 'ink_bbox_root': [bb[0]+box[0], bb[1]+box[1], bb[2]+box[0], bb[3]+box[1]],
                'components_8_connected': len(areas), 'component_areas': areas,
                'removed_ink_pixels_inside_crop': 0,
                'status': status, 'review_note': note, 'quarantined': quarantine,
                'usable_as_design_reference': r < 4 and not quarantine and name not in ANCHORS,
                'font_source_ready': False, 'coverage_credit': False})
    cal = calibration(cells, v1)
    for cell in cells:
        if cell['row'] <= 4:
            cell['builder_calibration_proposal'] = {
                'kind': 'symbol' if cell['name'] == 'partial' else 'greek',
                'codepoints': cell['codepoints'], 'source_crop_box': cell['source_crop_box'],
                'baseline_root': cal['row_baselines'][str(cell['row'])],
                'source_em_pixels': cal['source_em_pixels'], 'root_sha256': digest,
                'registration_to_root_for_unresized_crop': {'scale': 1,
                    'translate_x': cell['source_crop_box'][0], 'translate_y': cell['source_crop_box'][1]},
                'status': 'incomplete proposal; no curves/provenance; calibration and semantic eligibility must be reviewed'}
    manifest = {'schema_version': 1, 'root_id': ROOT_ID, 'root_sha256': digest,
        'image_size': list(image.size), 'grid_bands_inclusive': {'horizontal': horizontal, 'vertical': vertical},
        'row_ink_label_windows': windows, 'crop_policy': 'Original rectangular pixel crops only; grid gutters and label windows excluded, no ink processing.',
        'measurement_thresholds': {'grid_gray_below': 245, 'ink_gray_below': 128,
            'grid_projection_fraction': .85, 'grid_clearance_pixels': 2},
        'png_encoding': {'pillow_version': PIL.__version__, 'compress_level': 9, 'optimize': False},
        'cells': cells, 'scope': '31 Greek targets plus partial and 32 sign prototypes; no digamma; no coverage credit.'}
    artifacts[Path('cells.json')] = json_bytes(manifest)
    artifacts[Path('calibration.json')] = json_bytes(cal)
    artifacts[Path('review.md')] = _review(cells, cal).encode()
    # Compare every pre-existing output BEFORE writing any missing outputs.
    for relative, data in artifacts.items():
        dest = directory / relative
        if dest.exists() and dest.read_bytes() != data:
            raise FileExistsError(f'Immutable evidence differs: {dest}')
    for relative, data in artifacts.items():
        dest = directory / relative
        if not dest.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            with dest.open('xb') as handle:
                handle.write(data)
    return manifest, cal


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, default=DEFAULT)
    parser.add_argument('--v1', type=Path, default=V1)
    args = parser.parse_args()
    manifest, cal = prepare(args.directory, args.v1)
    print(json.dumps({'cells': len(manifest['cells']), 'quarantined': sum(c['quarantined'] for c in manifest['cells']),
        'source_em_pixels': cal['source_em_pixels'], 'status': cal['status']}))


if __name__ == '__main__':
    main()
