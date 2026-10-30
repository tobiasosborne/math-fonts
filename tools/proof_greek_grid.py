#!/usr/bin/env python3
"""Prove Greek/text alignment at one em scale; licensed outlines stay private.

The grid is an overlay, never a flattened source for tracing. This script does
not modify font outlines, rescale individual glyphs, or claim optical approval.
"""
import argparse
import base64
import html
import json
import os
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

import proof_ams_runtime as ams

REPO = Path(__file__).resolve().parents[1]
NATIVE = 'Baskerville10Pro-Italic'
GREEK = [('alpha', 0x3b1, 0x1d6fc), ('beta', 0x3b2, 0x1d6fd),
         ('theta', 0x3b8, 0x1d703), ('nu', 0x3bd, 0x1d708),
         ('xi', 0x3be, 0x1d709), ('omega', 0x3c9, 0x1d714)]
CONTROLS = 'xnobdpqy'
DEFAULT_GUIDES = {'baseline': 0, 'x_height': 476, 'cap_height': 723,
                  'ascender': 744, 'descender': -271,
                  'lower_overshoot': -18, 'descender_overshoot': -286}
COLORS = {'baseline': '#287cb1', 'x_height': '#298259', 'cap_height': '#bc791e',
          'ascender': '#af485b', 'descender': '#a44b85',
          'lower_overshoot': '#287cb1', 'descender_overshoot': '#a44b85'}


def inspect(font, cp):
    name = font.getBestCmap()[cp]
    glyphset = font.getGlyphSet()
    pen = BoundsPen(glyphset)
    glyphset[name].draw(pen)
    upm = font['head'].unitsPerEm
    return {'character': chr(cp), 'glyph': name,
            'bounds_upm1000': [value * 1000 / upm for value in pen.bounds],
            'advance_upm1000': font['hmtx'][name][0] * 1000 / upm}


def read_grid(path):
    grid = json.loads(path.read_text())
    if grid.get('units_per_em', 1000) != 1000:
        raise ValueError('This proof requires the declared common 1000-unit em')
    guides = grid.get('guides', {})
    values = {}
    for key, fallback in DEFAULT_GUIDES.items():
        value = guides.get(key, fallback)
        if isinstance(value, dict):
            value = value.get('value', value.get('upm', fallback))
        if not isinstance(value, (int, float)):
            raise ValueError(f'Numeric guide required: {key}')
        values[key] = value
    return grid, values


def outline_svg(native, custom, guides, slant_degrees=-12):
    """Draw every glyph at the same point scale, preserving real advances."""
    rows = [('Body and x-height', [('native', c) for c in 'xno'] +
             [('custom', c) for c in 'ανω']),
            ('Ascenders and tall Greek', [('native', c) for c in 'bdhl'] +
             [('custom', c) for c in 'βθξ']),
            ('Descenders and lower space', [('native', c) for c in 'pqyg'] +
             [('custom', c) for c in 'βξ'])]
    width, row_height = 7800, 1550
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {row_height*len(rows)}" width="1560" height="{row_height*len(rows)/5}">',
             f'<rect width="{width}" height="{row_height*len(rows)}" fill="white"/>']
    measurements = []
    for row_index, (label, cells) in enumerate(rows):
        baseline = row_index * row_height + 1000
        parts.append(f'<text x="100" y="{baseline-900}" font-size="100" fill="black">{html.escape(label)} — actual advances, common em</text>')
        parts.append('<g class="guides" style="display:none">')
        for lo, hi, color in [(guides['lower_overshoot'], 0, '#287cb1'),
                              (guides['descender_overshoot'], guides['descender'], '#a44b85')]:
            parts.append(f'<rect x="95" y="{baseline-hi}" width="7600" height="{hi-lo}" fill="{color}" opacity=".13"/>')
        for label_index, (name, value) in enumerate(sorted(guides.items(), key=lambda item: -item[1])):
            y = baseline - value
            color = COLORS[name]
            label_y = baseline - 740 + label_index*105
            parts.append(f'<path d="M95,{y}H6380L6460,{label_y-20}" fill="none" stroke="{color}" stroke-width="3" stroke-dasharray="{8 if "overshoot" in name else 0}"/>')
            parts.append(f'<text x="6490" y="{label_y}" font-size="64" fill="{color}">{name.replace("_", " ")} {value:g}</text>')
        parts.append('</g>')
        x = 120
        for source, character in cells:
            font = native if source == 'native' else custom
            record = inspect(font, ord(character))
            glyphset = font.getGlyphSet()
            pen = SVGPathPen(glyphset)
            glyphset[record['glyph']].draw(pen)
            scale = 1000 / font['head'].unitsPerEm
            import math
            slope = math.tan(math.radians(-slant_degrees))
            for offset in [0, record['advance_upm1000']]:
                lo, hi = guides['descender_overshoot'], guides['ascender']
                parts.append(f'<g class="guides" style="display:none"><path d="M{x+offset+slope*lo},{baseline-lo}L{x+offset+slope*hi},{baseline-hi}" stroke="#627a88" stroke-width="3" opacity=".25"/></g>')
            parts.append(f'<path d="{pen.getCommands()}" transform="translate({x},{baseline}) scale({scale},-{scale})" fill="black"/>')
            parts.append(f'<text x="{x}" y="{baseline+430}" font-size="80" fill="black">{source}: {html.escape(character)}</text>')
            measurements.append({'row': row_index, 'source': source, **record})
            x += record['advance_upm1000'] + 210
    parts.append('</svg>')
    return ''.join(parts), measurements


ROW = r'x\,n\,o\,b\,d\,p\,q\,y\quad\alpha\,\beta\,\theta\,\nu\,\xi\,\omega'


def tex_proof(state, guides, guided):
    rules = []
    if guided:
        for name, value in guides.items():
            color = COLORS[name].lstrip('#')
            rules.append(r'\rlap{\raisebox{' + f'{value/1000:.9f}' +
                         r'em}[0pt][0pt]{\color[HTML]{' + color +
                         r'}\rule{\linewidth}{.08pt}}}')
    gridrow = (r'\newcommand\gridrow[1]{\par\vspace{1.1em}\noindent\leavevmode' +
               ''.join(rules) + r'$#1$\par\vspace{.5em}}')
    return r'''\usepackage{xcolor}
GRIDROW
\begin{document}
{\Large STATE: Greek and original Baskerville italic}\par
All characters below use the same nominal point size and baseline. Roman
Baskerville carries the paragraph; its original italic variables accompany the
new Greek. The rules are calculated from the TeX line origin in em units,
not placed by looking at a screenshot. The clean proof contains no rule ink.
\par
For a smooth function $f(x)=\alpha x+\beta$, let $n\nu+o\omega=x\alpha$.
The comparison of $x\alpha$, $n\nu$ and $o\omega$ tests the lowercase body;
$b\beta$, $d\theta$ and $p\xi$ expose tall forms and descenders.
An expression should retain its texture within \textit{ordinary italic words}.
\gridrow{ROW}
{\fontsize{7}{10}\selectfont Seven-point text and math share this next baseline.
\gridrow{ROW}}
{\fontsize{5}{8}\selectfont Five-point comparison, without a different optical drawing.
\gridrow{ROW}}
Actual nested scripts: $x_{n_o}^{b^d}\quad\alpha_{\beta_\theta}^{\nu^\xi}$.
Accents: $\hat{x}\quad\hat{\alpha}\quad\hat{\omega}$.
\par\vspace{4mm}
{\fontsize{22}{30}\selectfont
\gridrow{x\,n\,o\quad\alpha\,\nu\,\omega}
\gridrow{b\,d\,p\quad\beta\,\theta\,\xi}}
The design remains provisional. Shared baseline origins do not prove that the
visible ink has the right overshoot, height, slant, weight or spacing.
\end{document}
'''.replace('GRIDROW', gridrow).replace('STATE', state.capitalize()).replace('ROW', ROW)


def audit_rows(pdf, directory, math_name, custom):
    pages = ams.pilot.structured(pdf, directory)
    if len(pages) != 4:
        raise RuntimeError(f'Expected three size rows and one nested-script page, got {len(pages)}')
    reports = []
    expected = list(CONTROLS) + [chr(cp) for _, cp, _ in GREEK]
    variants = {chr(alias): chr(base) for _, base, alias in GREEK}
    for index, size in enumerate([10, 7, 5]):
        chars = []
        for font in pages[index].findall('.//font'):
            actual = ams.canonical_font(font.get('name'), math_name)
            font_size = float(font.get('size'))
            for char in font.findall('char'):
                value = char.get('c', '')
                if not value.strip():
                    continue
                identity = variants.get(value, value)
                wanted = NATIVE if identity in CONTROLS else math_name
                if identity not in expected or actual != wanted:
                    raise RuntimeError(f'Unexpected glyph/source in row: {identity!r}, {actual}, expected {wanted}')
                if abs(font_size-size*72/72.27) > .02:
                    raise RuntimeError(f'Point-size mismatch for {identity}: {font_size} vs {size}')
                chars.append({'character': identity, 'actual_character': value, 'font': actual,
                              'size_pdf_pt': font_size, 'baseline_pdf_pt': float(char.get('y'))})
        if [c['character'] for c in chars] != expected:
            raise RuntimeError('The actual PDF row does not contain the exact intended control/Greek sequence')
        baseline_spread = max(c['baseline_pdf_pt'] for c in chars)-min(c['baseline_pdf_pt'] for c in chars)
        if baseline_spread > .002:
            raise RuntimeError(f'Baseline origins differ by {baseline_spread} PDF points')
        reports.append({'nominal_tex_pt': size, 'baseline_spread_pdf_pt': baseline_spread,
                        'per_character_source_checks': chars})
    sizes = {}
    for font in pages[3].findall('.//font'):
        if font.findall('char'):
            actual = ams.canonical_font(font.get('name'), math_name)
            sizes.setdefault(actual, set()).add(float(font.get('size')))
    if set(sizes) != {NATIVE, math_name} or any(len(values) != 3 for values in sizes.values()):
        raise RuntimeError(f'Nested scripts do not exercise three sizes of both intended faces: {sizes}')
    return {'size_rows': reports, 'nested_script_sizes_pdf_pt': {k: sorted(v) for k, v in sizes.items()}}


def build(before_font, after_font, grid_path, text_dir, output, dpi=200):
    output, text_dir = output.resolve(), text_dir.resolve()
    if output.exists():
        raise FileExistsError('Use a fresh proof directory; previous evidence is immutable')
    grid, guides = read_grid(grid_path)
    for _, (filename, expected) in ams.pilot.STORM.items():
        if ams.pilot.sha(text_dir/filename) != expected:
            raise ValueError(f'Original Storm hash differs: {filename}')
    native = TTFont(text_dir/'Baskerville10Pro-Italic.otf')
    output.mkdir(parents=True)
    private = output/'private'
    private.mkdir()
    summary = {'status': 'building', 'grid_sha256': ams.pilot.sha(grid_path),
               'guides_upm1000': guides, 'states': {},
               'scope': 'Six retained custom Greek and exact native italic controls; no automatic outline edits.',
               'distribution': 'Native outlines, embedded fonts, proof pages and viewer stay private.'}
    svg_views, images = {}, {}
    env = dict(os.environ, TEXINPUTS=str(REPO/'tex')+os.pathsep+os.environ.get('TEXINPUTS', ''))
    try:
        for state, font_path in [('before', before_font), ('after', after_font)]:
            font_path = font_path.resolve()
            custom = TTFont(font_path)
            name = custom['name'].getDebugName(6)
            svg, records = outline_svg(native, custom, guides, grid.get('slant_degrees', -12))
            svg_views[state] = svg
            (private/f'{state}-common-em.svg').write_text(svg+'\n')
            record = {'font_sha256': ams.pilot.sha(font_path), 'postscript_name': name,
                      'common_em_measurements': records, 'engines': {}}
            summary['states'][state] = record
            option = '[authored-overlay]' if name != ams.pilot.MATH else ''
            base = ams.pilot.preamble(font_path, text_dir).replace('\\pagestyle',
                '\\usepackage'+option+'{baskervillecompanionams}\n\\pagestyle')
            for engine in ['lualatex', 'xelatex']:
                directory = private/state/engine
                directory.mkdir(parents=True)
                evidence = {'proofs': {}}
                record['engines'][engine] = evidence
                rows = [r'{\fontsize{'+str(size)+r'}{12}\selectfont$'+ROW+'$}' for size in [10, 7, 5]]
                rows.append(r'$x_{n_o}^{b^d}\quad\alpha_{\beta_\theta}^{\nu^\xi}$')
                isolated = ams.pilot.compile_tex(engine, 'isolated-grid-rows',
                    base+r'\begin{document}'+ '\n\\newpage\n'.join(rows)+r'\end{document}', directory, env)
                evidence['actual_font_checks'] = audit_rows(isolated, directory, name, custom)
                ams.pdf_fonts(isolated, directory, name)
                for guided in [False, True]:
                    kind = 'guided' if guided else 'clean'
                    proof = ams.pilot.compile_tex(engine, kind,
                        base+tex_proof(state, guides, guided), directory, env)
                    fonts = ams.pdf_fonts(proof, directory, name)
                    pages = ams.pilot.structured(proof, directory)
                    if len(pages) != 1:
                        raise RuntimeError(f'The one-page grid proof overflowed to {len(pages)} pages')
                    rc, message = ams.pilot.run(['pdftoppm','-r',str(dpi),'-png','-singlefile',str(proof),str(directory/kind)], directory)
                    if rc:
                        raise RuntimeError(message)
                    image = directory/(kind+'.png')
                    key = f'{state}-{engine}-{kind}'
                    images[key] = image
                    evidence['proofs'][kind] = {'actual_fonts': fonts,
                        'pdf': str(proof.relative_to(output)), 'raster': str(image.relative_to(output))}
            custom.close()
        summary['status'] = 'passed'
        write_view(private, svg_views, images)
    except Exception as error:
        summary['status'], summary['error'] = 'failed', str(error)
        raise
    finally:
        native.close()
        (output/'summary.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False)+'\n')
    return summary


def write_view(private, svgs, images):
    template = '''<!doctype html><html><meta charset="utf-8"><style>
html,body{margin:0;padding:0;background:transparent;color:var(--foreground);font-family:var(--font-sans,system-ui)}*{box-sizing:border-box}p{font-size:13px;line-height:1.5;margin:0 0 10px}.controls{display:flex;flex-wrap:wrap;gap:12px;align-items:center;margin:10px 0}select{font:inherit;color:var(--foreground);background:var(--card);border:1px solid var(--border);padding:6px;border-radius:var(--radius)}.paper{overflow:auto;max-height:900px;background:white}.paper svg,.paper img{display:block;width:100%;height:auto}.negative{filter:invert(1)}body.guided .guides{display:block!important}.note{font-size:12px;opacity:.8}
</style><body><p>Greek/text alignment at one common em: original Storm italic controls beside the actual compiled custom Greek. The overlays use measured font coordinates; individual glyphs are never fitted to boxes in this proof.</p><div class="controls"><select id="state" aria-label="Before or after"><option value="after">After calibration</option><option value="before">Before calibration</option></select><select id="mode" aria-label="Proof mode"><option value="grid">Common-em outline grid</option><option value="page">Actual 10/7/5pt math page</option></select><select id="engine" aria-label="TeX engine"><option value="lualatex">LuaLaTeX</option><option value="xelatex">XeLaTeX</option></select><select id="zoom" aria-label="Zoom"><option value="100">Whole view</option><option value="200">2×</option><option value="400">4×</option></select><label><input type="checkbox" id="guides" checked>Measured guides</label><label><input type="checkbox" id="negative">Negative space</label></div><div id="outlines" class="paper"><div id="before" hidden>__BEFORE__</div><div id="after">__AFTER__</div></div><div id="reading" class="paper" hidden><img id="proof" alt="Actual typeset grid proof"></div><p class="note">Baseline, x-height, cap/ascender and descender lines are separate overlays. Bands record observed text overshoot, not a rule that every Greek outline must share identical extreme bounds. Real math pages also place rules from the TeX baseline in em units. The clean versions contain no guide ink. All native outlines and embedded-font pages remain private.</p><div hidden>__ASSETS__</div><script>const $=id=>document.getElementById(id);function show(){let page=$('mode').value==='page',state=$('state').value;$('reading').hidden=!page;$('outlines').hidden=page;$('engine').hidden=!page;for(let s of ['before','after'])$(s).hidden=s!==state;document.body.classList.toggle('guided',$('guides').checked);$('proof').src=$('asset-'+state+'-'+$('engine').value+'-'+($('guides').checked?'guided':'clean')).src;for(let el of [$('proof'),...document.querySelectorAll('#outlines svg')])el.style.width=$('zoom').value+'%';for(let el of [$('reading'),$('outlines')])el.classList.toggle('negative',$('negative').checked)}for(let id of ['state','mode','engine','zoom','guides','negative'])$(id).onchange=show;show();</script></body></html>'''
    template = template.replace('__BEFORE__', svgs['before']).replace('__AFTER__', svgs['after'])
    for embedded in [False, True]:
        tags = []
        for key, path in images.items():
            source = ('data:image/png;base64,'+base64.b64encode(path.read_bytes()).decode()) if embedded else str(path)
            tags.append(f'<img id="asset-{key}" src="{html.escape(source, quote=True)}">')
        (private/('viewer.html' if embedded else 'viewer-preview.html')).write_text(template.replace('__ASSETS__',''.join(tags)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--before-font', type=Path, required=True)
    parser.add_argument('--after-font', type=Path, required=True)
    parser.add_argument('--grid', type=Path, required=True)
    parser.add_argument('--text-font-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--dpi', type=int, default=200)
    args = parser.parse_args()
    result = build(args.before_font, args.after_font, args.grid, args.text_font_dir, args.output, args.dpi)
    print(json.dumps({'status':result['status'], 'private_viewer':str(args.output/'private/viewer.html')},indent=2))


if __name__ == '__main__':
    main()
