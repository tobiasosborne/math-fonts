#!/usr/bin/env python3
"""Prove exact external Storm reuse with isolated command pages in both engines.

No font is generated or modified. Embedded commercial outlines remain private.
"""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import re

from fontTools.ttLib import TTFont

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('ams_pilot_proof', REPO / 'tools/proof_math_pilot.py')
pilot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pilot)
LOADER = REPO / 'tex/baskervillecompanionams.sty'
INVENTORY = REPO / 'design/ams-glyph-inventory.json'
PILOT_FONT = REPO / 'runs/pipeline-2026-10-30/delivery/font/BaskervilleCompanionMath-Pilot.otf'
CLASS_NAMES = ['mathord', 'mathop', 'mathbin', 'mathrel', 'mathopen', 'mathclose', 'mathpunct', 'mathalpha']


def arrow_allowlist():
    return [{'command': command, 'codepoint': int(scalar, 16), 'math_class': CLASS_NAMES[int(cls)]}
            for command, cls, scalar in re.findall(
                r'\\BCAMS@arrow\{(\\[A-Za-z]+)\}\{(\d)\}\{([0-9A-F]+)\}', LOADER.read_text())]


def mappings(authored=None):
    """Read actual shipped declarations, rather than a second divergent map."""
    text = LOADER.read_text()
    records = []
    for kind, command, cls, scalar in re.findall(
            r'\\BCAMS@(declare|delimiter)\{(\\(?:[A-Za-z]+|[^A-Za-z]))\}\{(\d)\}\{([0-9A-F]+)\}', text):
        records.append({'command': command, 'codepoint': int(scalar, 16),
                        'math_class': CLASS_NAMES[int(cls)], 'declaration': kind,
                        'source': 'original_external_Storm_regular', 'expected_font': pilot.UP})
    for command, scalar in re.findall(r'\\BCAMS@greek\{(\\[^}]+)\}\{([0-9A-F]+)\}', text):
        records.append({'command': command, 'codepoint': int(scalar, 16),
                        'math_class': 'mathalpha', 'declaration': 'native_Greek_opt_in',
                        'source': 'original_external_Storm_italic_alternate', 'expected_font': pilot.IT})
    if authored is not None:
        cmap = authored.getBestCmap()
        name = authored['name'].getDebugName(6)
        overlay = name != pilot.MATH
        if overlay:
            for record in records:
                if record['declaration'] != 'native_Greek_opt_in' and record['codepoint'] in cmap:
                    record.update(source='authored_AMS_overlay', expected_font=name)
            positions = {r['command']: i for i, r in enumerate(records) if r['declaration'] != 'native_Greek_opt_in'}
            for arrow in arrow_allowlist():
                if arrow['codepoint'] not in cmap:
                    continue
                row = {**arrow, 'declaration': 'authored_arrow', 'source': 'authored_AMS_arrow', 'expected_font': name}
                if arrow['command'] in positions:
                    records[positions[arrow['command']]] = row
                else:
                    positions[arrow['command']] = len(records)
                    records.append(row)
    return records


def literal_mappings(authored):
    """Resolve exactly the same explicit overlay policy as the TeX loader."""
    cmap = authored.getBestCmap()
    name = authored['name'].getDebugName(6)
    overlay = name != pilot.MATH
    rows = {int(scalar, 16): {'codepoint': int(scalar, 16), 'math_class': CLASS_NAMES[int(cls)]}
            for cls, scalar in re.findall(r'\\BCAMS@literal\{(\d)\}\{([0-9A-F]+)\}', LOADER.read_text())}
    if overlay:
        for arrow in arrow_allowlist():
            if arrow['codepoint'] in cmap:
                rows[arrow['codepoint']] = {'codepoint': arrow['codepoint'], 'math_class': arrow['math_class']}
    for cp, row in rows.items():
        row['expected_font'] = name if overlay and cp in cmap else pilot.UP
    # ASCII '-' must address a true minus source, independent of text hyphen.
    rows[0x2d] = {'codepoint': 0x2d, 'source_codepoint': 0x2212, 'math_class': 'mathbin',
                  'expected_font': name if overlay and 0x2212 in cmap else pilot.UP}
    return sorted(rows.values(), key=lambda r: r['codepoint'])


def coverage(records, text_dir):
    inventory = json.loads(INVENTORY.read_text())
    targets = {g['id']: g for g in inventory['glyphs']}
    implemented = {r['command']: r for r in records if r['declaration'] != 'native_Greek_opt_in'}
    custom = {'\\alpha', '\\beta', '\\theta', '\\nu', '\\xi', '\\omega'}
    constructions = {'\\int', '\\intop', '\\sum', '\\sqrtsign'}
    cmap = TTFont(text_dir / pilot.STORM[pilot.UP][0]).getBestCmap()
    unsupported, supported = [], []
    for binding in inventory['command_bindings']:
        name = binding['command']
        if binding['input_kind'] != 'control_sequence':
            continue
        target = targets[binding['target_id']]
        common = {'command': name, 'package': binding['package'], 'target_id': binding['target_id']}
        if name in implemented:
            supported.append({**common, 'source': implemented[name]['source']})
        elif name in custom or name in constructions:
            supported.append({**common, 'source': 'unchanged_authored_pilot'})
        else:
            cps = [int(cp[2:], 16) for cp in target['codepoints']]
            if name == '\\|':
                reason = 'Frozen alias points at single bar; double-bar identity is not supplied and is not substituted.'
            elif cps and (0x370 <= cps[0] <= 0x3ff or 0x1d6a8 <= cps[0] <= 0x1d7cb):
                reason = 'Custom Greek is required; native Greek is opt-in only and cannot close this gap.'
            elif not cps:
                reason = 'Unencoded shape, variant or construction needs explicit engineering.'
            elif len(cps) != 1 or cps[0] not in cmap:
                reason = 'Exact Unicode scalar is absent from the supplied Storm regular cmap.'
            else:
                reason = 'Exact stock scalar exists but this command/construction is not declared in this bounded runtime.'
            unsupported.append({**common, 'reason': reason})
    direct = [b for b in inventory['command_bindings'] if b['package'] == 'amssymb' and b['kind'] == 'Symbol']
    return {'inventory_bindings_supported_by_explicit_command': supported,
            'unsupported_bindings': unsupported, 'direct_amssymb_total': len(direct),
            'direct_amssymb_implemented': sorted(b['command'] for b in direct if b['command'] in implemented),
            'note': 'Command accounting excludes literal Latin/numeral mappings and existing named operator recipes; availability is not optical acceptance.'}


PROOF = r'''\begin{document}
{\Large Baskerville mathematics: source reuse and AMS structures}\par
Ten-point Storm Baskerville text accompanies the authored mathematical font.
Each sign's active source is audited separately. This is a technical and optical working proof;
coverage is deliberately partial. No unrelated mathematical font supplies gaps.
\par
For $x\geq0$ let $f(x)=x^2+\alpha x+\beta$. The estimate
$0\leq f(x)\leq\infty$ tests ordinary inequalities, scripts and spacing.
Configured relations and operations:
$x\approx y$, $x\neq y$, $x\pm y$, $x\times y$, $x\div y$.
\begin{align}
 f(x)&=x^2+\alpha x+\beta,\\
 \int_0^1f(x)\,\mathrm{d}x&=\frac{1}{3}+\frac{\alpha}{2}+\beta,\\
 \lim_{x\to0}\frac{\sin x}{x}&=1.
\end{align}
An arrow can mark a process $x\rightarrow y\rightarrow z$; the active
diagonal arrows are $\nwarrow\ \nearrow\ \swarrow\ \searrow$.
\[
 A=\begin{pmatrix}\alpha&\beta\\\theta&\nu\end{pmatrix},\qquad
 f(x)=\begin{cases}x^2,&x\geq0,\\-x,&x<0.\end{cases}
\]
The cases brace is the supplied rigid glyph. It has no engineered growth yet.
The authored parentheses retain the pilot's finite larger sizes.
\[
 \sum_{x=0}^{2}x^2\qquad \prod_{x=1}^{2}x\qquad
 \sqrt{\frac{x^2+1}{2}}\qquad
 \left(\frac{\alpha}{\frac{\beta}{\theta}}\right)
\]
The product uses one stock size; sums, integrals, radicals, hats and growing
parentheses retain the unchanged authored companion constructions.
\par
Direct AMS symbols with exact stock sources:
$x\centerdot y$, $\eth$, $\lozenge$.
The aliases $\Diamond$, $\yen$, $\circledR$ are also explicit.
The remaining AMS inventory is an open design and engineering requirement.
\par
Text faces: regular, \textit{italic}, \textbf{bold}, \textbf{\textit{bold italic}}.
Math alphabets: $\mathrm{ABC012}$, $\mathit{abc012}$,
$\mathbf{ABC012}$, $\mathbfit{abc012}$.
\newpage
{\Large Custom Greek and optional native alternates}\par
Default authored design:
$\alpha\ \beta\ \theta\ \nu\ \xi\ \omega$.
\par
Explicit native Storm italic alternate:
$\mathstormgreek{\alpha\ \beta\ \theta\ \nu\ \xi\ \omega}$.
\par
Explicit native Storm upright alternate:
$\mathstormgreekup{\alpha\ \beta\ \theta\ \nu\ \xi\ \omega}$.
\par
After either scope the default remains custom:
$\alpha\ \beta\ \theta\ \nu\ \xi\ \omega$.
Native glyphs are retained as optional alternates, not as substitutes for the
unfinished custom Greek alphabet. Absent native shape variants remain errors.
\par
{\fontsize{22}{32}\selectfont
Custom: $\alpha\ \beta\ \theta\ \nu\ \xi\ \omega$\par
Native italic: $\mathstormgreek{\alpha\ \beta\ \theta\ \nu\ \xi\ \omega}$\par
Signs: $+\ -\ =\ \leq\ \geq\ \infty\ \approx\ \partial$\par}
\end{document}
'''


def working_proof(records):
    arrows = {r['codepoint']: r for r in records if r['declaration'] == 'authored_arrow'}
    if not arrows:
        return PROOF
    ordered = [row for _, row in sorted(arrows.items())]
    lines = [r'\newpage{\Large Authored arrow family: working and enlarged proof}\par',
             r'These exact encoded arrows use the authored companion, including arrows also available in Storm. ',
             r'Absent head, hook or pair variants remain missing. Component geometry and optical spacing are provisional.\par']
    commands = {r['command'] for r in records if r['declaration'] == 'authored_arrow'}
    examples = []
    for required, formula in [
            ({r'\rightarrow'}, r'x\rightarrow y\rightarrow z'),
            ({r'\Rightarrow', r'\Leftrightarrow'}, r'x>0\Rightarrow x^2>0\qquad x=0\Leftrightarrow x^2=0'),
            ({r'\mapsto'}, r'f:A\mapsto B\qquad x\mapsto x^2+\alpha'),
            ({r'\rightleftharpoons'}, r'A\rightleftharpoons B'),
            ({r'\nearrow', r'\searrow'}, r'x\nearrow y\qquad y\searrow z'),
            ({r'\longrightarrow', r'\Longrightarrow'}, r'x\longrightarrow y\Longrightarrow z'),
            ({r'\rightarrow', r'\Leftarrow'}, r'x_{\alpha\rightarrow\beta}^{\theta\Leftarrow\nu}')]:
        if required <= commands:
            examples.append(formula)
    lines.extend('\\[' + formula + '\\]' for formula in examples)
    lines.append(r'At working size, the shared stems, heads and bars should retain a consistent rhythm.\par')
    for start in range(0, len(ordered), 6):
        batch = ordered[start:start+6]
        lines.append('$' + r'\quad '.join('x' + r['command'] + '{}y' for r in batch) + r'$\par')
    lines.append(r'\newpage{\Large Enlarged authored arrow diagnostics}\par{\fontsize{22}{32}\selectfont')
    for start in range(0, len(ordered), 6):
        lines.append('$' + r'\quad '.join(r['command'] for r in ordered[start:start+6]) + r'$\par')
    lines.append('}')
    return PROOF.replace(r'\end{document}', '\n'.join(lines) + '\n' + r'\end{document}')


def pdf_fonts(pdf, directory, math_name):
    rc, output = pilot.run(['pdffonts', str(pdf)], directory)
    if rc:
        raise RuntimeError(output)
    (directory / f'{pdf.stem}.pdffonts.txt').write_text(output)
    names = {re.sub(r'-Identity-H$', '', re.sub(r'^[A-Z]{6}\+', '', row.split()[0]))
             for row in output.splitlines()[2:] if row.strip()}
    if not names or names - {*pilot.STORM, math_name}:
        raise RuntimeError(f'Unexpected actual PDF font use: {names}')
    return sorted(names)


def canonical_font(name, math_name):
    original = re.sub(r'^[A-Z]{6}\+', '', name)
    # MuPDF shortens the companion CFF internal name. pdffonts above verifies
    # the complete expected PostScript name independently for each PDF.
    if original.startswith('BaskervilleCompanionMath'):
        return math_name
    return pilot.canonical_font(name)


def check_isolated_pages(engine, pdf, directory, cases, math_name):
    pdf_fonts(pdf, directory, math_name)
    pages = pilot.structured(pdf, directory)
    if len(pages) != len(cases):
        raise RuntimeError(f'{engine}: isolated page count {len(pages)} != {len(cases)}')
    evidence = []
    for case, page in zip(cases, pages):
        used = {canonical_font(f.get('name'), math_name) for f in page.findall('.//font') if f.findall('char')}
        expected = set(case['expected_fonts'])
        if used != expected:
            raise RuntimeError(f'{engine} {case["label"]}: actual fonts {used} != {expected}')
        chars = ''.join(c.get('c', '') for c in page.findall('.//char'))
        if 'expected_character' in case and chars not in case.get('same_source_glyph_characters', [case['expected_character']]):
            raise RuntimeError(f'{engine} {case["label"]}: actual character {chars!r} != {case["expected_character"]!r}')
        if not chars:
            raise RuntimeError(f'{engine} {case["label"]}: no rendered glyphs')
        evidence.append({**case, 'actual_fonts': sorted(used), 'rendered_characters': chars,
                         'glyph_count': len(page.findall('.//char'))})
    return evidence


def build(font, text_dir, output, dpi=160, baseline=True):
    font, text_dir, output = font.resolve(), text_dir.resolve(), output.resolve()
    if output.exists():
        raise ValueError('Use a fresh output directory; proofs are immutable.')
    inspected = TTFont(font)
    math_name = inspected['name'].getDebugName(6)
    if not math_name or not math_name.startswith('BaskervilleCompanionMath') or 'MATH' not in inspected:
        raise ValueError('Use an authored BaskervilleCompanionMath OpenType MATH font.')
    if any(cp in inspected.getBestCmap() for cp in (ord('A'), ord('x'), ord('0'))):
        raise ValueError('Authored companion must not contain reused ordinary Latin/numeral outlines.')
    for filename, expected in pilot.STORM.values():
        if pilot.sha(text_dir / filename) != expected:
            raise ValueError(f'External original Storm hash mismatch: {filename}')
    records = mappings(inspected)
    cmaps = {name: TTFont(text_dir / filename).getBestCmap() for name, (filename, _) in pilot.STORM.items()}
    cmaps[math_name] = inspected.getBestCmap()
    for record in records:
        cp = record['codepoint']
        cmap = cmaps[record['expected_font']]
        if cp not in cmap:
            raise ValueError(f'Exact source cmap lacks {record["command"]}: U+{cp:04X}')
        record['source_codepoint'] = f'U+{cp:04X}'
        record['source_glyph_name'] = cmap[cp]
        # XeTeX's PDF ToUnicode chooses one character when multiple cmap scalars
        # address the very same original glyph (e.g. U+00B7/U+2219). Permit only
        # that pinned-font glyph identity, never visual lookalikes or variants.
        record['same_source_glyph_characters'] = [chr(other) for other, glyph in cmap.items() if glyph == cmap[cp]]
    output.mkdir(parents=True)
    summary = {'schema_version': 1, 'status': 'building', 'font_sha256': pilot.sha(font), 'math_postscript_name': math_name,
               'loader_sha256': pilot.sha(LOADER), 'storm_sha256': {f: h for f, h in pilot.STORM.values()},
               'source_annotations': records, 'coverage': coverage(records, text_dir), 'engines': {},
               'limitations': ['No full AMS coverage or final optical approval.',
                 'Stock rigid signs have text-font metrics; math spacing/axis still needs optical review.',
                 'Braces, brackets, bars and arrows have no arbitrary-size assembly; product has one stock size.',
                 f'{len({r["codepoint"] for r in records if r["declaration"] == "authored_arrow"})} exact authored arrow scalars are installed; omitted head/hook/pair variants remain missing, and any other exact stock arrows remain original Storm.',
                 'Custom Greek scope follows the selected authored font; native Greek is explicit opt-in and closes no custom gap.',
                 'Unchanged companion constructions and script drawings retain pilot limitations.']}
    env = dict(os.environ, TEXINPUTS=str(REPO / 'tex') + os.pathsep + os.environ.get('TEXINPUTS', ''))
    overlay_option = '[authored-overlay]' if math_name != pilot.MATH else ''
    base = pilot.preamble(font, text_dir).replace('\\pagestyle', '\\usepackage' + overlay_option + '{baskervillecompanionams}\n\\pagestyle')
    cases = []
    for record in records:
        command = record['command']
        native = record['declaration'] == 'native_Greek_opt_in'
        formula = '\\mathstormgreek{' + command + '}' if native else command
        cases.append({'label': ('native-italic:' if native else 'custom:' if record['expected_font'] == math_name else 'stock:') + command,
                      'formula': formula, 'expected_fonts': [record['expected_font']],
                      'expected_character': chr(record['codepoint']), 'math_class': record['math_class'],
                      'same_source_glyph_characters': record['same_source_glyph_characters'],
                      'source': record['source'], 'source_glyph_name': record['source_glyph_name']})
        if native:
            upright_cmap = cmaps[pilot.UP]
            upright_glyph = upright_cmap[record['codepoint']]
            cases.append({**cases[-1], 'label': 'native-upright:' + command,
                          'formula': '\\mathstormgreekup{' + command + '}', 'expected_fonts': [pilot.UP],
                          'source': 'original_external_Storm_regular_alternate', 'source_glyph_name': upright_glyph,
                          'same_source_glyph_characters': [chr(cp) for cp, glyph in upright_cmap.items() if glyph == upright_glyph]})
    for literal in literal_mappings(inspected):
        cp = literal['codepoint']
        if cp in (0x7b, 0x7d, 0x5c, 0x24):
            # These characters are TeX syntax; their named aliases are isolated
            # above. Raw Unicode literals cover every installed authored arrow.
            continue
        source_cp = literal.get('source_codepoint', cp)
        cmap = cmaps[literal['expected_font']]
        glyph = cmap[source_cp]
        cases.append({'label': f'literal:U+{cp:04X}', 'formula': chr(cp),
                      'expected_fonts': [literal['expected_font']], 'expected_character': chr(source_cp),
                      'same_source_glyph_characters': [chr(other) for other, g in cmap.items() if g == glyph],
                      'math_class': literal['math_class'], 'source_glyph_name': glyph,
                      'source': 'authored_overlay_literal' if literal['expected_font'] == math_name else 'stock_literal'})
    for cp in (0x3b1, 0x3b2, 0x3b8, 0x3bd, 0x3be, 0x3c9):
        cases.append({'label': f'native-literal:U+{cp:04X}', 'formula': '\\mathstormgreek{' + chr(cp) + '}',
                      'expected_fonts': [pilot.IT], 'expected_character': chr(cp), 'source': 'opt_in_native_literal'})
    # Re-exercise all twenty original roles with the expanded loader; only the
    # deliberate rigid-sign reuse changes the mixed custom-symbols expectation.
    for label, formula, expected in pilot.ROLES:
        expected = math_name if expected == pilot.MATH else expected
        mixed_symbols = {math_name}
        if math_name == pilot.MATH or any(cp not in inspected.getBestCmap() for cp in (0x2b, 0x2212, 0x3d)):
            mixed_symbols.add(pilot.UP)
        cases.append({'label': 'pilot-role:' + label, 'formula': formula,
                      'expected_fonts': sorted(mixed_symbols) if label == 'custom-symbols' else [expected],
                      'source': 'existing_pilot_role_under_expanded_loader'})
    cases.extend([
        {'label': 'native-scope-does-not-leak', 'formula': r'\mathstormgreek{\alpha}\alpha',
         'expected_fonts': [pilot.IT, math_name], 'source': 'native_alternate_scope'},
        {'label': 'native-scripts', 'formula': r'\mathstormgreek{\alpha_{\beta_\theta}^{\nu^\xi}}',
         'expected_fonts': [pilot.IT], 'source': 'native_alternate_three_sizes'},
    ])
    by_command = {record['command']: record for record in records}
    for command in (r'\uparrow', r'\downarrow', r'\updownarrow',
                    r'\Uparrow', r'\Downarrow', r'\Updownarrow'):
        if command in by_command:
            record = by_command[command]
            cases.append({'label': 'vertical-arrow-delimiter:' + command,
                          'formula': r'\left' + command + r'{}x\right' + command,
                          'expected_fonts': sorted({record['expected_font'], pilot.IT}),
                          'source': 'actual_left_right_delimiter_syntax; finite rigid base only'})
    try:
        if baseline:
            old = pilot.build(PILOT_FONT.resolve(), text_dir, output / 'private/pilot-regression', dpi=72)
            summary['unchanged_pilot_regression'] = {e: len(v['role_checks']) for e, v in old['engines'].items()}
        for engine in ('lualatex', 'xelatex'):
            directory = output / 'private' / engine
            directory.mkdir(parents=True)
            source = base + '\\begin{document}\n' + '\n\\newpage\n'.join('$' + c['formula'] + '$' for c in cases) + '\n\\end{document}'
            isolated = pilot.compile_tex(engine, 'isolated-commands', source, directory, env)
            evidence = check_isolated_pages(engine, isolated, directory, cases, math_name)
            proof = pilot.compile_tex(engine, 'working-proof', base + working_proof(records), directory, env)
            fonts = pdf_fonts(proof, directory, math_name)
            pages = pilot.structured(proof, directory)
            negative = {}
            negative_candidates = [('missing-custom-gamma', r'\gamma', 0x3b3, 0x1d6fe),
                                   ('missing-AMS-boxplus', r'\boxplus', 0x229e, 0x229e),
                                   ('missing-core-forall', r'\forall', 0x2200, 0x2200),
                                   ('missing-AMS-boxminus', r'\boxminus', 0x229f, 0x229f),
                                   ('missing-AMS-boxtimes', r'\boxtimes', 0x22a0, 0x22a0),
                                   ('missing-AMS-boxdot', r'\boxdot', 0x22a1, 0x22a1)]
            selected = [(label, formula) for label, formula, raw, styled in negative_candidates
                        if raw not in inspected.getBestCmap() and styled not in inspected.getBestCmap()][:3]
            if not selected:
                raise RuntimeError('Choose a new genuinely uncovered negative target for this enlarged font.')
            for label, formula in selected:
                negative[label] = pilot.compile_tex(engine, label, base + '\\begin{document}$' + formula + '$\\end{document}', directory, env, True)
            for command, cp in [(r'\twoheadleftarrow', 0x219e), (r'\hookrightarrow', 0x21aa), (r'\rightleftarrows', 0x21c4)]:
                if cp not in inspected.getBestCmap():
                    label = 'missing-exact-arrow-' + command[1:]
                    negative[label] = pilot.compile_tex(engine, label, base + '\\begin{document}$' + command + '$\\end{document}', directory, env, True)
            for variant in ('epsilon', 'phi', 'vartheta', 'varkappa', 'varrho', 'varpi'):
                name = 'missing-native-' + variant
                tex = directory / (name + '.tex')
                tex.write_text(base + '\\begin{document}$\\mathstormgreek{\\' + variant + '}$\\end{document}')
                rc, log = pilot.run([engine, '-halt-on-error', '-interaction=nonstopmode', '-no-shell-escape', tex.name], directory, env)
                (directory / (name + '.stdout.txt')).write_text(log)
                if rc == 0 or 'Native Storm Greek variant unavailable' not in log:
                    raise RuntimeError(f'{engine}: missing native {variant} did not fail explicitly')
                negative[name] = ['Explicit package error: Native Storm Greek variant unavailable']
            for index in range(len(pages)):
                rc, log = pilot.run(['pdftoppm', '-f', str(index + 1), '-l', str(index + 1), '-r', str(dpi),
                                     '-png', '-singlefile', str(proof), str(directory / f'working-{index+1}-{dpi}dpi')], directory)
                if rc:
                    raise RuntimeError(log)
            summary['engines'][engine] = {'status': 'passed', 'isolated_command_checks': evidence,
                'actual_pdf_fonts': fonts, 'proof_pages': len(pages), 'hard_missing_failures': negative,
                'private_proof': f'private/{engine}/working-proof.pdf',
                'private_rasters': [f'private/{engine}/working-{i+1}-{dpi}dpi.png' for i in range(len(pages))]}
        summary['status'] = 'passed'
    except Exception as exc:
        summary['status'], summary['error'] = 'failed', str(exc)
        raise
    finally:
        (output / 'runtime-summary.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False) + '\n')
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--font', type=Path, default=REPO / 'runs/pipeline-2026-10-30/delivery/font/BaskervilleCompanionMath-Pilot.otf')
    parser.add_argument('--text-font-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--dpi', type=int, default=160)
    args = parser.parse_args()
    result = build(args.font, args.text_font_dir, args.output, args.dpi)
    print(json.dumps({'status': result['status'], 'engines': {e: len(v['isolated_command_checks']) for e, v in result['engines'].items()},
                      'direct_amssymb_implemented': result['coverage']['direct_amssymb_implemented']}))


if __name__ == '__main__':
    main()
