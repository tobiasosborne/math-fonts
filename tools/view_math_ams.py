#!/usr/bin/env python3
"""Retain compiled-arrow specimens and a private actual-math proof viewer."""
import argparse
import base64
import html
import json
import unicodedata
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont


def build_view(delivery):
    delivery = Path(delivery).resolve()
    font = TTFont(delivery / 'font/BaskervilleCompanionMath-AMS.otf')
    glyphset = font.getGlyphSet()
    cmap = font.getBestCmap()
    arrows = [(cp, name) for cp, name in sorted(cmap.items())
              if any(word in unicodedata.name(chr(cp), '') for word in ['ARROW', 'HARPOON'])]
    columns, cell_w, cell_h = 4, 1750, 1200
    width = columns * cell_w
    height = ((len(arrows) + columns - 1) // columns) * cell_h
    paths, guides = [], []
    axis = font['MATH'].table.MathConstants.AxisHeight.Value
    for index, (cp, name) in enumerate(arrows):
        pen = SVGPathPen(glyphset)
        glyphset[name].draw(pen)
        col, row = index % columns, index // columns
        advance = font['hmtx'][name][0]
        x, baseline = col * cell_w + (cell_w - advance) / 2, row * cell_h + 800
        paths.append(f'<path d="{pen.getCommands()}" transform="translate({x},{baseline}) scale(1,-1)"/>')
        paths.append(f'<text x="{col*cell_w+cell_w/2}" y="{row*cell_h+1100}" text-anchor="middle" font-size="80">U+{cp:04X} {html.escape(name)}</text>')
        for y, color in [(baseline, '#377fbd'), (baseline-axis, '#9c68b2')]:
            guides.append(f'<path d="M{col*cell_w},{y}h{cell_w}" stroke="{color}" stroke-width="5"/>')
        guides.append(f'<path d="M{col*cell_w}, {row*cell_h}v{cell_h}" stroke="#bbb" stroke-width="4"/>')
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="1400" height="{height/5}"><rect width="{width}" height="{height}" fill="white"/><g fill="black">{"".join(paths)}</g><g class="guides" style="display:none">{"".join(guides)}</g></svg>'
    (delivery / 'compiled-arrows.svg').write_text(svg + '\n')
    (delivery / 'compiled-arrows-guided.svg').write_text(svg.replace('style="display:none"', '') + '\n')
    font.close()
    runtime = json.loads((delivery / 'runtime/runtime-summary.json').read_text())
    assets, preview_assets, options = [], [], []
    for engine, record in runtime['engines'].items():
        for index, relative in enumerate(record['private_rasters']):
            key = f'{engine}-{index}'
            path = delivery / 'runtime' / relative
            data = base64.b64encode(path.read_bytes()).decode()
            assets.append(f'<img id="asset-{key}" src="data:image/png;base64,{data}">')
            preview_assets.append(f'<img id="asset-{key}" src="{html.escape(str(path), quote=True)}">')
            selected = ' selected' if engine == 'lualatex' and index == 2 else ''
            options.append(f'<option value="{key}"{selected}>{engine}, page {index+1}</option>')
    content = '''<!doctype html><html><meta charset="utf-8"><style>
    html,body{margin:0;padding:0;color:var(--foreground);background:transparent;font-family:var(--font-sans,system-ui)}*{box-sizing:border-box}p{font-size:13px;line-height:1.5;margin:0 0 10px}.controls{display:flex;gap:12px;flex-wrap:wrap;align-items:center;margin:10px 0}select{font:inherit;color:var(--foreground);background:var(--card);border:1px solid var(--border);padding:6px;border-radius:var(--radius)}.paper{overflow:auto;max-height:850px;background:white}.paper img{display:block;width:100%;height:auto}.paper svg{display:block;width:100%;height:auto}.negative{filter:invert(1)}body.guided .guides{display:block!important}.note{opacity:.8;font-size:12px}
    </style><body><p>Shared arrow components in the actual compiled math font, with original Storm Baskerville text and preferred custom Greek. Working-size pages and enlarged outlines remain provisional optical proofs.</p>
    <div class="controls"><select id="mode" aria-label="Proof view"><option value="page">Actual math pages</option><option value="font">Compiled arrow grid</option></select><select id="page" aria-label="Engine and page">__OPTIONS__</select><select id="zoom" aria-label="Zoom"><option value="100">Whole view</option><option value="200">2×</option><option value="400">4×</option></select><label><input type="checkbox" id="negative">Negative space</label><label><input type="checkbox" id="guides">Baseline / math axis</label></div>
    <div id="reading" class="paper"><img id="proof" alt="Actual Baskerville math proof"></div><div id="font" class="paper" hidden>__SVG__</div>
    <p class="note">Every arrow uses the shared head and shaft parameters; direction and semantics are explicit constructions. Grid outlines come from the delivered CFF, at a common scale. Finite lengths, script-size optical compensation and complete AMS coverage remain unfinished. Native Storm Greek is an explicit alternate.</p><div hidden>__ASSETS__</div>
    <script>const $=id=>document.getElementById(id);function show(){let grid=$('mode').value==='font';$('reading').hidden=grid;$('font').hidden=!grid;$('page').hidden=grid;$('proof').src=$('asset-'+$('page').value).src;for(let el of [$('proof'),$('font').querySelector('svg')])el.style.width=$('zoom').value+'%';for(let el of [$('reading'),$('font')])el.classList.toggle('negative',$('negative').checked);document.body.classList.toggle('guided',$('guides').checked)}for(let id of ['mode','page','zoom','negative','guides'])$(id).onchange=show;show();</script></body></html>'''
    content = content.replace('__OPTIONS__', ''.join(options)).replace('__SVG__', svg)
    (delivery / 'runtime/private/viewer-preview.html').write_text(content.replace('__ASSETS__', ''.join(preview_assets)))
    path = delivery / 'runtime/private/viewer.html'
    path.write_text(content.replace('__ASSETS__', ''.join(assets)))
    return path


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--delivery', type=Path, required=True)
    print(build_view(parser.parse_args().delivery))
