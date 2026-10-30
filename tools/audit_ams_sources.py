#!/usr/bin/env python3
"""Audit frozen AMS requests against actual external Storm and authored pilot files.

Reads cmap/metrics/tables, never reads or copies outlines. Availability, loader
mapping, macro definition, rendered evidence and optical acceptance are separate.
Use --probe-macros for a private, non-typesetting LuaLaTeX ifdefined probe.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / 'design/ams-glyph-inventory.json'
PILOT = ROOT / 'runs/pipeline-2026-10-30/delivery/font/BaskervilleCompanionMath-Pilot.otf'
OUT = ROOT / 'runs/ams-coverage-2026-10-30'
STYLES = {'upright': 'Regular', 'italic': 'Italic', 'bold_upright': 'Bold', 'bold_italic': 'Bold italic'}
GREEK_ROLES = {'alpha', 'beta', 'theta', 'nu', 'xi', 'omega'}
GEOMETRIC = {'arrow', 'relation', 'binary_operator', 'accent', 'horizontal_extensible'}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_ucd(path):
    result = {}
    for line in path.read_text().splitlines():
        p = line.split(';')
        result[int(p[0], 16)] = {'name': p[1], 'decomposition': p[5]}
    return result


def decomposition(cp, ucd):
    """One-step mathematical compatibility decomposition; never guess shape aliases."""
    raw = ucd.get(cp, {}).get('decomposition', '').split()
    return int(raw[-1], 16) if len(raw) == 2 and raw[0] == '<font>' else cp


def font_info(path, expected=None):
    digest = sha(path)
    if expected and digest != expected:
        raise ValueError(f'Source hash mismatch: {path}')
    with TTFont(path, lazy=True) as font:
        cmap = font.getBestCmap()
        constructions = {}
        if 'MATH' in font:
            mv = font['MATH'].table.MathVariants
            for axis, cov, cons in [('vertical', mv.VertGlyphCoverage, mv.VertGlyphConstruction),
                                    ('horizontal', mv.HorizGlyphCoverage, mv.HorizGlyphConstruction)]:
                if cov:
                    for name, c in zip(cov.glyphs, cons):
                        constructions[name] = {'axis': axis, 'variants': [
                            {'glyph_name': v.VariantGlyph, 'advance': v.AdvanceMeasurement}
                            for v in c.MathGlyphVariantRecord], 'has_assembly': c.GlyphAssembly is not None}
        return {'math_constructions': constructions, 'path': str(path), 'sha256': digest, 'cmap_count': len(cmap),
                'has_math_table': 'MATH' in font, 'glyph_count': len(font.getGlyphOrder()),
                'cmap': cmap, 'glyph_order': font.getGlyphOrder()}


def stock_candidates(cp, faces):
    return [{'style': style, 'source_codepoint': f'U+{cp:04X}',
             'glyph_name': info['cmap'][cp], 'sha256': info['sha256']}
            for style, info in faces.items() if cp in info['cmap']]


def classify(g, ucd, faces, pilot):
    cps = [int(c[2:], 16) for c in g['codepoints']]
    cp = cps[0] if len(cps) == 1 else None
    style = g.get('alphabet_style')
    # Compatibility decomposition is permitted for styled alphabet requests,
    # never to collapse independent symbols such as hslash into a text letter.
    source_cp = (decomposition(cp, ucd) if style in STYLES or cp in (0x1D6A4, 0x1D6A5)
                 else cp)
    if cp in (0x1D6A4, 0x1D6A5):
        style = 'italic'
    name = ' '.join(g['unicode_names'])
    # Greek codepoints and mathematical Greek decompositions, including partial/nabla.
    greek = source_cp is not None and (0x370 <= source_cp <= 0x3FF or
                source_cp in (0x2202, 0x2207) and g['category'] == 'alphabet')
    candidates = stock_candidates(source_cp, faces) if source_cp is not None else []
    cmap_glyph = pilot['cmap'].get(cp)
    row = {'target_id': g['id'], 'codepoints': g['codepoints'], 'characters': g['characters'],
           'unicode_names': g['unicode_names'], 'category': g['category'],
           'unicode_math_class': g.get('unicode_math_class'),
           'encoding_kind': g['encoding_kind'], 'alphabet_style': style,
           'stock_candidates': candidates, 'pilot_cmap_glyph': cmap_glyph,
           'accepted_design': False, 'rendered_proof': 'not_established_by_this_audit',
           'source_outline_read_or_copied': False,
           'native_greek_alternate_only': bool(greek and candidates)}
    if not cps:
        cls = {'composite_recipe': 'package_recipe_required',
               'legacy_shape_variant': 'missing_legacy_shape_or_recipe',
               'bold_symbol_variant': 'bold_engineering_required',
               'bold_dotless_variant': 'bold_dotless_mapping_required',
               'size_variant': 'size_engineering_required',
               'display_variant': 'display_engineering_required',
               'assembly_part': 'assembly_engineering_required',
               'legacy_construction_piece': 'construction_piece_required'}[g['category']]
        row.update(availability_class=cls, base_id=g.get('base_id'),
                   reason='An encoded base does not establish this unencoded engineering request.')
    elif len(cps) > 1:
        row.update(availability_class='sequence_binding_required',
                   reason='Component availability does not prove the requested variation or composed shape.')
    elif cmap_glyph and cmap_glyph in GREEK_ROLES:
        row.update(availability_class='custom_pilot_greek',
                   design_evidence='retained six-role regular-companion pilot; final optical acceptance pending',
                   reason='Custom drawing retained. Plain Greek alias does not prove the separate upright design.',
                   style_caveat=style == 'upright')
    elif greek and style in ('italic', 'bold_italic'):
        row.update(availability_class='missing_custom_greek',
                   reason='Custom italic Greek is mandatory even where Storm has native Greek; old 32 studies are not adopted.')
    elif cmap_glyph:
        row.update(availability_class='custom_pilot_symbol',
                   reason='Actual authored pilot cmap entry; growth and optical quality remain provisional.')
    elif style in STYLES and source_cp is not None and (65 <= source_cp <= 90 or 97 <= source_cp <= 122 or 48 <= source_cp <= 57):
        chosen = [c for c in candidates if c['style'] == STYLES[style]]
        row.update(availability_class='external_storm_alphabet' if chosen else 'missing_expressive_outline',
                   selected_source=chosen[0] if chosen else None,
                   reason='Exact UCD font decomposition to original ASCII slot and requested Storm face; loader proof separate.')
    elif greek:
        row.update(availability_class='missing_custom_greek',
                   reason='Custom Greek remains the default design requirement. Native Storm Greek is an explicit opt-in alternate only.')
    elif g['category'] in ('alphabet', 'numeral'):
        # Do not pretend Storm serif is script/fraktur/sans/double-struck/monospace.
        if style and style not in STYLES:
            row.update(availability_class='missing_expressive_alphabet',
                       reason='Stock serif ASCII decomposition is not this requested alphabet design.')
        elif candidates:
            row.update(availability_class='external_storm_alphabet',
                       selected_source=next((c for c in candidates if c['style'] == STYLES.get(style)), candidates[0]),
                       reason='Exact native source slot available; explicit style mapping and proof required.')
        else:
            row.update(availability_class='missing_expressive_outline', reason='No exact stock or current pilot slot.')
    elif candidates:
        row.update(availability_class='external_rigid_symbol_candidate',
                   reason='Exact source cmap slot only; suitability, math spacing and runtime selection not established.')
    elif g['category'] in GEOMETRIC or any(s in name for s in ('TRIANGLE', 'SQUARE', 'CIRCLE', 'DIAMOND', 'LOZENGE', 'BRACKET', 'CEILING', 'FLOOR')):
        row.update(availability_class='geometric_construction_candidate',
                   reason='New unified-root geometry/recipe candidate; not an existing or accepted outline.')
    else:
        row.update(availability_class='missing_expressive_outline', reason='No exact stock or current pilot slot.')
    return row


def macro_probe(bindings, output, font, textdir):
    """Check definitions without expanding/typesetting commands; all 204 included."""
    output.mkdir(parents=True, exist_ok=True)
    direct = [b for b in bindings if b['package'] == 'amssymb' and b['kind'] == 'Symbol']
    if len(direct) != 204:
        raise ValueError('Frozen direct AMS set changed')
    names = sorted({b['command'][1:] for b in direct})
    lines = [r'\documentclass{article}',
             r'\usepackage[mathfont={' + str(font) + '},textfontdir={' + str(textdir) + r'}]{baskervillecompanionmath}',
             r'\begin{document}']
    for name in names:
        lines.append(r'\ifcsname '+name+r'\endcsname\expandafter\ifx\csname '+name+r'\endcsname\relax\typeout{AMS-AUDIT:'+name+r':undefined}\else\typeout{AMS-AUDIT:'+name+r':defined}\fi\else\typeout{AMS-AUDIT:'+name+r':undefined}\fi')
    lines.append(r'\end{document}')
    tex = output / 'macro-probe.tex'
    tex.write_text('\n'.join(lines) + '\n')
    env = os.environ.copy()
    env['TEXINPUTS'] = str(ROOT / 'tex') + os.pathsep + env.get('TEXINPUTS', '')
    loader = ROOT / 'tex/baskervillecompanionmath.sty'
    loader_hash = sha(loader)
    proc = subprocess.run(['lualatex', '-interaction=nonstopmode', '-halt-on-error',
                           '-output-directory=' + str(output), str(tex)], cwd=ROOT,
                          env=env, capture_output=True, text=True, timeout=120)
    (output / 'console.txt').write_text(proc.stdout + proc.stderr)
    if proc.returncode:
        raise RuntimeError(f'Private macro probe failed; see {output}/console.txt')
    if sha(loader) != loader_hash:
        raise RuntimeError('Loader changed during macro probe; report cannot identify tested state')
    log = (output / 'macro-probe.log').read_text()
    found = dict(re.findall(r'AMS-AUDIT:([^:\s]+):(defined|undefined)', log))
    if set(found) != set(names):
        raise RuntimeError('Macro probe did not return exact direct-command set')
    return {'status': 'measured', 'engine': 'lualatex',
            'meaning': 'ifcsname/non-relax only; zero commands expanded or typeset; not glyph/rendered coverage',
            'private_probe': str(tex.relative_to(ROOT)),
            'loader_sha256': loader_hash,
            'unicode_math_package': next((line for line in log.splitlines() if 'Package: unicode-math ' in line), None),
            'results': [{'command': '\\' + n, 'defined': found[n] == 'defined'} for n in names],
            'counts': dict(Counter(found.values()))}


def build(output=OUT, probe=False, inventory=INVENTORY, pilot_path=PILOT):
    inv = json.loads(inventory.read_text())
    ref = json.loads((ROOT / 'design/storm-reference.json').read_text())
    ucd_path = ROOT / 'research/coverage/2026-10-29/UnicodeData.txt'
    ucd = read_ucd(ucd_path)
    for source in inv['sources']:
        path = ROOT / 'research/coverage/2026-10-29' / source['id']
        if sha(path) != source['sha256']:
            raise ValueError(f'Frozen source changed: {source["id"]}')
    faces = {f['style']: font_info(Path(f['source']), f['sha256']) for f in ref['faces']}
    pilot = font_info(pilot_path)
    rows = [classify(g, ucd, faces, pilot) for g in inv['glyphs']]
    by_id = {r['target_id']: r for r in rows}
    for g, row in zip(inv['glyphs'], rows):
        base = by_id.get(g.get('base_id', ''))
        base_glyph = base['pilot_cmap_glyph'] if base else row['pilot_cmap_glyph']
        row['pilot_growth_construction'] = pilot['math_constructions'].get(base_glyph)
        row['engineering_coverage_credit'] = False
    bindings = [{**b, 'availability_class': by_id[b['target_id']]['availability_class'],
                 'pilot_cmap_glyph': by_id[b['target_id']]['pilot_cmap_glyph'],
                 'rendered_proof': 'not_established_by_this_audit'} for b in inv['command_bindings']]
    if probe:
        macros = macro_probe(bindings, output / 'private/source-audit', pilot_path, Path(ref['faces'][0]['source']).parent)
    else:
        macros = {'status': 'not_run', 'results': []}
    macro_by = {m['command']: m['defined'] for m in macros['results']}
    for b in bindings:
        b['macro_defined'] = macro_by.get(b['command'])
    missing = defaultdict(list)
    for r in rows:
        if r['availability_class'].startswith(('missing_', 'geometric_')):
            missing[r['availability_class']].append(r['target_id'])
    next_greek = [r['target_id'] for r in rows if r['availability_class'] == 'missing_custom_greek'
                  and r['alphabet_style'] == 'italic' and any('SMALL' in n for n in r['unicode_names'])]
    geometric = [r['target_id'] for r in rows if r['availability_class'] == 'geometric_construction_candidate']
    direct = [b for b in bindings if b['package'] == 'amssymb' and b['kind'] == 'Symbol']
    engine_summary = ROOT / 'runs/pipeline-2026-10-30/delivery/runtime/summary.json'
    baseline = json.loads(engine_summary.read_text())
    result = {
        'schema_version': 1, 'status': 'source_availability_audit_not_design_acceptance',
        'inventory': str(inventory.relative_to(ROOT)), 'inventory_sha256': sha(inventory),
        'policy': 'External Storm reuse; custom Greek default; native Greek opt-in alternates only; exact scalar identity; no unrelated donor/fallback.',
        'native_greek_alternates': [{'style': style, 'source_sha256': info['sha256'],
             'default': False, 'coverage_credit_for_missing_custom': False,
             'slots': [{'codepoint': f'U+{cp:04X}', 'glyph_name': n}
                       for cp,n in sorted(info['cmap'].items()) if 0x391 <= cp <= 0x3FF]}
            for style, info in faces.items()],
        'frozen_primary_sources': inv['sources'],
        'external_fonts': [{k: v for k, v in f.items() if k not in ('cmap', 'glyph_order')} | {'style': s}
                           for s, f in faces.items()],
        'authored_font': {k: v for k, v in pilot.items() if k != 'cmap'} |
                        {'cmap': [{'codepoint': f'U+{cp:04X}', 'glyph': n} for cp,n in sorted(pilot['cmap'].items())]},
        'counts': {'targets': len(rows), 'encoded_scalar_targets': sum(r['encoding_kind'] == 'scalar' for r in rows),
                   'sequence_targets': sum(r['encoding_kind'] == 'sequence' for r in rows),
                   'unencoded_targets': sum(r['encoding_kind'] == 'unencoded' for r in rows),
                   'by_availability_class': dict(sorted(Counter(r['availability_class'] for r in rows).items())),
                   'bindings_by_availability_class': dict(sorted(Counter(b['availability_class'] for b in bindings).items())),
                   'ordinary_serif_ascii_style_targets': sum(r['availability_class'] == 'external_storm_alphabet' and r['alphabet_style'] in STYLES and 32 <= int(r['selected_source']['source_codepoint'][2:],16) < 127 for r in rows),
                   'binding_rows': len(bindings), 'distinct_command_spellings': len({b['command'] for b in bindings}),
                   'direct_amssymb_commands': len(direct),
                   'direct_amssymb_by_availability': dict(sorted(Counter(b['availability_class'] for b in direct).items())),
                   'inventory_targets_in_pilot_cmap': sum(r['pilot_cmap_glyph'] is not None for r in rows),
                   'accepted_design_targets_claimed': 0, 'new_rendered_targets_claimed': 0},
        'targets': rows, 'bindings': bindings, 'direct_amssymb': direct,
        'alphabet_selector_requests': inv['alphabet_sets'], 'operator_recipes': inv['operator_recipes'],
        'engineering_constructions': inv['engineering_constructions'],
        'missing_base_classes': dict(missing),
        'unencoded_requirements_by_class': {c: [r['target_id'] for r in rows if r['availability_class'] == c]
             for c in sorted({r['availability_class'] for r in rows if r['encoding_kind'] == 'unencoded'})},
        'bounded_next_batches': [
            {'purpose': 'Continue custom lowercase italic Greek from frozen root', 'target_ids': next_greek,
             'first_batch_limit': 6, 'authorization': 'proposal only, no image call made by audit'},
            {'purpose': 'Exact stock rigid-symbol reuse before any replacement drawings',
             'target_ids': [r['target_id'] for r in rows if r['availability_class'] == 'external_rigid_symbol_candidate'],
             'authorization': 'runtime mapping and measured proofs required'},
            {'purpose': 'Geometric construction design queue', 'target_ids': geometric,
             'first_batch_limit': 12, 'authorization': 'proposal only; candidates are not outlines'}],
        'macro_availability': macros,
        'existing_rendering_baseline': {'source': str(engine_summary.relative_to(ROOT)),
            'sha256': sha(engine_summary), 'status': baseline['status'],
            'engine_role_checks': {e: len(v['role_checks']) for e,v in baseline['engines'].items()},
            'note': '20 narrow role checks per engine are not 585 commands or 1196 scalar proofs. Existing baseline is unchanged.'},
        'limitations': ['cmap availability does not establish optical quality or runtime mapping.',
            'Native Greek recorded without adopting stock italic Greek.',
            'Old 32 enlarged studies remain evidence only; no new regular glyph is silently sourced from them.',
            'Size/display/bold/assembly and sequence requests require their own shape/layout proofs.',
            'Macro definition is not successful expansion, glyph coverage or rendered coverage.',
            'No source outlines or licensed binaries are included in this report.']}
    output.mkdir(parents=True, exist_ok=True)
    (output / 'source-audit.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, default=OUT)
    p.add_argument('--probe-macros', action='store_true')
    args = p.parse_args()
    result = build(args.output.resolve(), args.probe_macros)
    print(json.dumps({'counts': result['counts'], 'macro_counts': result['macro_availability'].get('counts')}, indent=2))

if __name__ == '__main__':
    main()
