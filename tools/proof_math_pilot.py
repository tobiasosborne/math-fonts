#!/usr/bin/env python3
"""Compile and audit both-engine hybrid proofs. All embedded-font artifacts stay private."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET

from fontTools.ttLib import TTFont

REPO = Path(__file__).resolve().parents[1]
STORM = {
    'Baskerville10Pro': ('Baskerville10Pro.otf', '402c85ca431a105b56e34cdbd5a01dae9f44f129e6b4f3c2e062cf5cb21dad3e'),
    'Baskerville10Pro-Italic': ('Baskerville10Pro-Italic.otf', 'b7c1c8e26c169eaa8a05d1354793a3cb9351c7a763c1e0864189f41860c652af'),
    'Baskerville10Pro-Bold': ('Baskerville10Pro-Bold.otf', 'ddc7383e768b3291368a454efef9f2bbddfd36aa55b6b4fc92e61d2bcbcaaa4a'),
    'Baskerville10Pro-BoldItalic': ('Baskerville10Pro-BoldItalic.otf', '4430977b025b08c62f975fbfc06d120fde12be4cab08119fd89ae3752d5bf81f'),
}
UP, IT, BF, BI = STORM
MATH = 'BaskervilleCompanionMath-Pilot'
ROLES = [
    ('bare-variables', r'xfdAHO', IT),
    ('bare-numerals', r'012', UP),
    ('variable-scripts', r'x_{f_d}^{A^{H}}', IT),
    ('numeral-scripts', r'0_{1_2}^{2^{1}}', UP),
    ('mathrm', r'\mathrm{xfdAHO012}', UP),
    ('mathit', r'\mathit{xfdAHO012}', IT),
    ('mathbf', r'\mathbf{xfdAHO012}', BF),
    ('mathbfit', r'\mathbfit{xfdAHO012}', BI),
    ('mathrm-scripts', r'\mathrm{x_{0_1}^{2}}', UP),
    ('mathit-scripts', r'\mathit{x_{0_1}^{2}}', IT),
    ('mathbf-scripts', r'\mathbf{x_{0_1}^{2}}', BF),
    ('mathbfit-scripts', r'\mathbfit{x_{0_1}^{2}}', BI),
    ('unicode-italic', '𝐴𝐻𝑂𝑥𝑓𝑑ℎ', IT),
    ('unicode-bold', '𝐀𝐇𝐎𝐱𝐟𝐝𝟎𝟏𝟐', BF),
    ('unicode-bolditalic', '𝑨𝑯𝑶𝒙𝒇𝒅', BI),
    ('named-operator', r'\operatorname{foo}', UP),
    ('custom-greek', r'\alpha\beta\theta\nu\xi\omega', MATH),
    ('greek-scripts', r'\alpha_{\beta_\theta}^{\nu^\xi}', MATH),
    ('custom-symbols', r'+- = \sum\int\sqrt{\alpha}\hat{\omega}', MATH),
    ('growing-parentheses', r'\left(\frac{\alpha}{\frac{\beta}{\theta}}\right)', MATH),
]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(command, cwd, env=None):
    result = subprocess.run(command, cwd=cwd, env=env, text=True, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, timeout=180)
    return result.returncode, result.stdout


def preamble(font, text_dir):
    for path in (font, text_dir):
        if any(c in str(path) for c in '{}%#\\\n'):
            raise ValueError('TeX paths must not contain braces, percent, hash, backslash or newline')
    return r'''\documentclass[10pt,a4paper]{article}
\usepackage[margin=24mm]{geometry}
\usepackage[mathfont={FONT},textfontdir={TEXT}]{baskervillecompanionmath}
\pagestyle{empty}
\setlength{\parindent}{0pt}
\setlength{\parskip}{6pt}
'''.replace('FONT', str(font)).replace('TEXT', str(text_dir))


PROOF = r'''\begin{document}
{\Large Baskerville companion mathematics: bounded pilot}\par
The original Storm Baskerville supplies the text, ordinary Latin variables and
figures. The companion supplies six custom Greek letters and the small set of
mathematical signs below. These are engineering proofs, with provisional
spacing, weight and finite growth sizes.\par
Original text faces: regular, \textit{italic}, \textbf{bold},
\textbf{\textit{bold italic}}. The reading size is ten points.\par
An inline expression $\alpha+\beta=\theta-\nu$ should share the rhythm of this
paragraph. Bare variables $AHO fxd$ and figures $012$ use Storm. Inline scripts
$x_0^2$ and $\alpha_1^2$ test their relationship at smaller sizes.
\[\int_0^1 f(x)\,\mathrm{d}x = \frac{\alpha+\beta}{\theta-\nu}
\qquad \sum_{x=0}^{2} x^2\]
\[\sqrt{\frac{x^2+1}{2}}\qquad
\sqrt{\frac{\alpha+\sqrt{\beta}}{\theta}}\qquad
\hat{x}\quad \hat{\omega}\]
\[\left(\begin{matrix}\alpha&\beta\\\theta&\nu\end{matrix}\right)
\quad \left(\frac{\alpha}{\beta}\right)
\quad \left(\frac{\alpha}{\frac{\beta}{\theta}}\right)\]
Default: $xfdAHO012$. Upright: $\mathrm{xfdAHO012}$.
Italic: $\mathit{xfdAHO012}$. Bold: $\mathbf{xfdAHO012}$.
Bold italic: $\mathbfit{xfdAHO012}$.\par
Literal Unicode: $𝑥𝑓𝑑𝐴𝐻𝑂$, $𝐱𝐟𝐝𝐀𝐇𝐎𝟎𝟏𝟐$, $𝒙𝒇𝒅𝑨𝑯𝑶$.
Named operator: $\operatorname{foo}(x)$.\par
Script and nested script: $x_{f_d}^{A^{H}}$, $0_{1_2}^{2^{1}}$,
$\alpha_{\beta_\theta}^{\nu^\xi}$.\par
Custom Greek: $\alpha\ \beta\ \theta\ \nu\ \xi\ \omega$.
\newpage
{\Large Enlarged diagnostics}\par
Enlarged ink and layout are shown at twenty-four points. This page does not
establish working-size quality or approval.\par
{\fontsize{24}{34}\selectfont
$\alpha\ \beta\ \theta\ \nu\ \xi\ \omega$\par
$AHO\quad fxd\quad012$\par
$\hat{\alpha}\quad\hat{x}\quad\sqrt{\alpha+\beta}$\par
\[\int_0^1 f(x)\,\mathrm{d}x\qquad\sum_{x=0}^{2}x^2\]
\[\left(\frac{\alpha}{\frac{\beta}{\theta}}\right)\]
}
\end{document}
'''


def canonical_font(name):
    name = re.sub(r'^[A-Z]{6}\+', '', name)
    name = re.sub(r'-Identity-H$', '', name)
    # MuPDF exposes shortened CFF internal names; pdffonts separately verifies
    # the exact PostScript names, all of which must match the five-name allowlist.
    if name.startswith('BaskervilleCompanionMath'):
        return MATH
    if name.startswith('Baskerville10Pro-BoldIta'):
        return BI
    return name


def pdf_fonts(pdf, directory):
    rc, output = run(['pdffonts', str(pdf)], directory)
    if rc:
        raise RuntimeError(output)
    (directory / f'{pdf.stem}.pdffonts.txt').write_text(output)
    names = {re.sub(r'-Identity-H$', '', re.sub(r'^[A-Z]{6}\+', '', row.split()[0]))
             for row in output.splitlines()[2:] if row.strip()}
    if not names or names - {*STORM, MATH}:
        raise RuntimeError(f'Unexpected actual PDF font use: {names}')
    return sorted(names)


def structured(pdf, directory):
    target = directory / f'{pdf.stem}.xml'
    rc, output = run(['mutool', 'draw', '-F', 'stext', '-o', str(target), str(pdf)], directory)
    if rc:
        raise RuntimeError(output)
    return ET.parse(target).getroot().findall('page')


def compile_tex(engine, name, source, directory, env, expect_failure=False):
    tex = directory / f'{name}.tex'
    tex.write_text(source)
    rc, output = run([engine, '-halt-on-error', '-interaction=nonstopmode',
                      '-no-shell-escape', '-recorder', tex.name], directory, env)
    (directory / f'{name}.stdout.txt').write_text(output)
    log = (directory / f'{name}.log').read_text(errors='replace')
    missing = re.findall(r'(?:Missing character:|Missing glyph:)[^\n]*', log)
    if expect_failure:
        if rc == 0 or not missing:
            raise RuntimeError('Out-of-scope symbol did not produce a hard missing-glyph failure')
        return missing
    if rc or missing or 'not an OpenType' in log or 'first font loaded' in log:
        raise RuntimeError(f'{engine}/{name} failed; inspect {directory / (name + ".log")}\n' + output[-3000:])
    return directory / f'{name}.pdf'


def build(font, text_dir, output, dpi=300):
    font, text_dir, output = font.resolve(), text_dir.resolve(), output.resolve()
    if output.exists():
        raise ValueError('Output must be a fresh directory; earlier proofs are immutable')
    inspected = TTFont(font)
    if 'MATH' not in inspected:
        raise ValueError('The companion OTF must contain MATH')
    if not any('math' in [r.ScriptTag for r in inspected[t].table.ScriptList.ScriptRecord]
               for t in ('GSUB', 'GPOS') if t in inspected):
        raise ValueError('The companion must declare the math script; otherwise unicode-math falls back')
    if any(cp in inspected.getBestCmap() for cp in (ord('A'), ord('x'), ord('0'))):
        raise ValueError('The companion must not contain reused ordinary Latin or numeral outlines')
    for _, (filename, expected) in STORM.items():
        if sha(text_dir / filename) != expected:
            raise ValueError(f'External Storm face differs from the pinned original: {filename}')
    for executable in ('lualatex', 'xelatex', 'mutool', 'pdffonts', 'pdftoppm'):
        if not shutil.which(executable):
            raise RuntimeError(f'Required executable unavailable: {executable}')
    output.mkdir(parents=True)
    env = dict(os.environ, TEXINPUTS=str(REPO / 'tex') + os.pathsep + os.environ.get('TEXINPUTS', ''))
    base = preamble(font, text_dir)
    summary = {'schema_version': 1, 'status': 'building', 'font_sha256': sha(font),
               'font': str(font.relative_to(REPO)) if font.is_relative_to(REPO) else font.name,
               'storm_sha256': {filename: digest for filename, digest in STORM.values()},
               'engines': {}, 'scope': '15 custom symbol roles plus externally supplied Storm Latin alphabets and numerals; not full AMS coverage',
               'limitations': ['No script optical drawings: fonts scale to script sizes; ssty is explicitly disabled.',
                               'Finite growing variants, no arbitrary-size assembly.',
                               'Custom Greek weight/spacing remain provisional; technical tests do not establish visual acceptance.',
                               'Only tested math alphabets are supported; no full bold symbol version or AMS repertoire.']}
    try:
        for engine in ('lualatex', 'xelatex'):
            directory = output / 'private' / engine
            directory.mkdir(parents=True)
            proof = compile_tex(engine, 'proof', base + PROOF, directory, env)
            fonts = pdf_fonts(proof, directory)
            if set(fonts) != {*STORM, MATH}:
                raise RuntimeError(f'Proof does not exercise all five intended faces: {fonts}')
            pages = structured(proof, directory)
            role_source = base + '\\begin{document}\n' + '\n\\newpage\n'.join(
                '$' + formula + '$' for _, formula, _ in ROLES) + '\n\\end{document}\n'
            role_pdf = compile_tex(engine, 'roles', role_source, directory, env)
            pdf_fonts(role_pdf, directory)
            role_pages = structured(role_pdf, directory)
            if len(role_pages) != len(ROLES):
                raise RuntimeError('Role audit page count mismatch')
            evidence = []
            for (role, formula, expected), page in zip(ROLES, role_pages):
                used = {canonical_font(f.get('name')) for f in page.findall('.//font') if f.findall('char')}
                if used != {expected}:
                    raise RuntimeError(f'{engine} role {role} used {used}, expected {expected}')
                sizes = sorted({float(f.get('size')) for f in page.findall('.//font')})
                if role.endswith('-scripts') and len(sizes) < 3:
                    raise RuntimeError(f'{engine} role {role} did not exercise three math sizes')
                evidence.append({'role': role, 'formula': formula, 'actual_fonts': sorted(used),
                                 'sizes_pt': sizes, 'glyph_count': len(page.findall('.//char'))})
            negative = compile_tex(engine, 'unsupported', base + r'\begin{document}$\gamma$\end{document}', directory, env, True)
            for index in range(len(pages)):
                rc, rendered = run(['pdftoppm', '-f', str(index + 1), '-l', str(index + 1),
                                    '-r', str(dpi), '-png', '-singlefile', str(proof),
                                    str(directory / f'page-{index+1}-{dpi}dpi')], directory)
                if rc:
                    raise RuntimeError(rendered)
            summary['engines'][engine] = {'status': 'passed', 'actual_pdf_fonts': fonts,
                'proof_pages': len(pages), 'role_checks': evidence,
                'unsupported_gamma_hard_failure': negative,
                'private_proof': f'private/{engine}/proof.pdf',
                'private_rasters': [f'private/{engine}/page-{i+1}-{dpi}dpi.png' for i in range(len(pages))]}
        summary['status'] = 'passed'
    except Exception as exc:
        summary['status'] = 'failed'
        summary['error'] = str(exc)
        raise
    finally:
        (output / 'summary.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False) + '\n')
    (output / 'README.md').write_text(
        '# Hybrid runtime pilot\n\nBoth LuaLaTeX and XeLaTeX compiled the bounded corpus with no missing glyphs. '
        'Every audit page contains one isolated math role; MuPDF inspected the rendered PDF font of its glyphs. '
        'The exact five PostScript names were separately checked with pdffonts. '
        'Default letters, figures, explicit alphabets, literal Unicode styled Latin, named operators and three math sizes passed. '
        'An unsupported gamma produced the required hard error on each engine.\n\n'
        'The original commercial Storm files are external and hash-pinned. All PDFs, embedded-font diagnostics, logs and raster proofs '
        'are below ignored `private/`. See `summary.json` for actual role evidence and limitations. '
        'Passing this technical audit does not approve visual design or establish full AMS coverage.\n')
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--font', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--text-font-dir', type=Path, required=True)
    parser.add_argument('--dpi', type=int, default=300)
    args = parser.parse_args()
    result = build(args.font, args.text_font_dir, args.output, args.dpi)
    print(json.dumps({'status': result['status'], 'output': str(args.output),
                      'engine_roles': {e: len(v['role_checks']) for e, v in result['engines'].items()}}))


if __name__ == '__main__':
    main()
