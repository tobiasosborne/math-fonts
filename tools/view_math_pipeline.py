#!/usr/bin/env python3
"""Build a private interactive proof and public compiled-font vector specimen."""
import argparse
import base64
import hashlib
import html
import json
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

NAMES=['alpha','beta','theta','nu','xi','omega']


def build_view(delivery,glyph_run):
    delivery=Path(delivery).resolve();glyph_run=Path(glyph_run).resolve()
    font_path=delivery/'font/BaskervilleCompanionMath-Pilot.otf'
    font=TTFont(font_path);gs=font.getGlyphSet()
    shapes=[]
    for i,name in enumerate(NAMES):
        pen=SVGPathPen(gs);gs[name].draw(pen)
        advance=font['hmtx'][name][0];x=i*1100+(1100-advance)/2
        shapes.append(f'<path d="{pen.getCommands()}" transform="translate({x},1100) scale(1,-1)" fill="black"/>')
        shapes.append(f'<text x="{i*1100+550}" y="1450" text-anchor="middle" font-size="100" fill="black">{name}</text>')
    upm=font['head'].unitsPerEm
    heights={'baseline':0,'x-height':font['OS/2'].sxHeight,
             'cap height':font['OS/2'].sCapHeight,
             'math axis':font['MATH'].table.MathConstants.AxisHeight.Value}
    lines=[]
    for (label,height),color in zip(heights.items(),['#377fbd','#339965','#c08335','#9c68b2']):
        y=1100-height
        lines.append(f'<path d="M0,{y} H6600" fill="none" stroke="{color}" stroke-width="4"/>')
    for i in range(7):
        lines.append(f'<path d="M{i*1100},50 V1320" stroke="#cccccc" stroke-width="3"/>')
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 6600 1520" width="1320" height="304"><rect width="6600" height="1520" fill="white"/>{"".join(shapes)}<g class="guides" style="display:none">{"".join(lines)}</g></svg>'
    (delivery/'font-specimen.svg').write_text(svg+'\n')
    (delivery/'font-specimen-guided.svg').write_text(svg.replace('style="display:none"','')+'\n')
    font.close()
    assets={f'{engine}-{page}':delivery/f'runtime/private/{engine}/page-{page}-300dpi.png'
            for engine in ['lualatex','xelatex'] for page in [1,2]}
    for name in NAMES:
        assets['glyph-'+name]=glyph_run/f'glyphs/{name}/comparison.png'
    template='''<!doctype html><html><meta charset="utf-8"><title>Baskerville math pilot proofs</title><style>
html,body{margin:0;padding:0;background:transparent;color:var(--foreground);font-family:var(--font-sans,system-ui)}*{box-sizing:border-box}p{font-size:13px;line-height:1.5;margin:0 0 10px}.controls{display:flex;flex-wrap:wrap;gap:12px;align-items:center;margin:10px 0}select,button{font:inherit;color:var(--foreground);background:var(--card);border:1px solid var(--border);padding:6px;border-radius:var(--radius)}.paper{overflow:auto;max-height:850px;background:white}.paper img{display:block;width:100%;height:auto}.negative{filter:invert(1)}.note{font-size:12px;opacity:.8}.specimen{background:white;overflow:auto}.specimen svg{width:100%;height:auto;display:block}body.showguides .guides{display:block!important}#stats{min-height:20px}
</style><body>
<p>End-to-end Baskerville mathematics pilot: original Štorm letters and figures, six newly enlarged/traced Greek forms, and a custom MATH companion. Both engines pass 20 isolated actual-font role checks. This is a working pipeline, with partial coverage and provisional optical design.</p>
<div class="controls"><select id="mode" aria-label="Proof view"><option value="page">Reading page</option><option value="large">Enlarged diagnostics</option><option value="font">Compiled font at one common scale</option><option value="glyph">Master agreement</option></select><select id="engine" aria-label="TeX engine"><option value="lualatex">LuaLaTeX</option><option value="xelatex">XeLaTeX</option></select><select id="glyph" aria-label="Greek glyph">__OPTIONS__</select><select id="zoom" aria-label="Zoom"><option value="100">Whole view</option><option value="200">2×</option><option value="400">4×</option></select><label><input id="negative" type="checkbox"> Negative space</label><label><input id="guides" type="checkbox"> Font guides</label></div>
<p id="stats"></p><div id="paper" class="paper"><img id="proof" alt="Actual typeset proof or measured source agreement"></div><div id="font" class="specimen" hidden>__SVG__</div>
<p class="note">The font specimen uses actual compiled CFF curves, shared baseline and units per em. Guides mark its provisional baseline/x-height/cap height/math axis; no per-glyph normalization. Source-agreement views use translation and uniform scale and are not font metrics.</p>
<p class="note">Still a pilot: finite growing variants, uncalibrated weight/spacing, no script optical drawings, full bold math or complete AMS repertoire. Embedded-font proofs stay private; the custom font and source are public.</p>
<div hidden>__ASSETS__</div><script>const $=x=>document.getElementById(x);const METRICS=__METRICS__;
function show(){let mode=$('mode').value;$('paper').hidden=mode==='font';$('font').hidden=mode!=='font';$('engine').hidden=mode==='font'||mode==='glyph';$('glyph').hidden=mode!=='glyph';$('guides').parentElement.hidden=mode!=='font';let key=mode==='glyph'?'glyph-'+$('glyph').value:$('engine').value+'-'+(mode==='large'?2:1);$('proof').src=$('asset-'+key).src;$('proof').style.width=$('zoom').value+'%';$('font').querySelector('svg').style.width=$('zoom').value+'%';$('paper').classList.toggle('negative',$('negative').checked);$('font').classList.toggle('negative',$('negative').checked);document.body.classList.toggle('showguides',$('guides').checked);if(mode==='glyph'){let r=METRICS.find(x=>x.name===$('glyph').value);$('stats').textContent=`${r.name}: master overlap ${(r.master_iou*100).toFixed(1)}%; mean boundary ${r.mean_boundary_master_px.toFixed(2)} source px; native trace overlap ${(r.native_trace_iou*100).toFixed(2)}%. These are different comparisons.`}else $('stats').textContent=mode==='font'?'Actual compiled outlines; no stock Latin or figures were redrawn.':'Original supplied Štorm faces + authored companion; tested font use contains no unrelated math fallback.'}
for(let id of ['mode','engine','glyph','zoom','negative','guides'])$(id).onchange=show;show();</script></body></html>'''
    template=template.replace('__SVG__',svg).replace('__OPTIONS__',''.join(f'<option>{n}</option>' for n in NAMES))
    template=template.replace('__METRICS__',json.dumps(json.loads((glyph_run/'glyph-metrics.json').read_text())['results']))
    private=delivery/'runtime/private'
    for embed in [False,True]:
        tags=[]
        for key,path in assets.items():
            src='data:image/png;base64,'+base64.b64encode(path.read_bytes()).decode() if embed else str(path)
            tags.append(f'<img id="asset-{key}" src="{html.escape(src,quote=True)}">')
        content=template.replace('__ASSETS__',''.join(tags))
        (private/('viewer.html' if embed else 'viewer-preview.html')).write_text(content)
    (delivery/'viewer-manifest.json').write_text(json.dumps({'font_sha256':hashlib.sha256(font_path.read_bytes()).hexdigest(),'units_per_em':upm,'font_specimen':'font-specimen.svg','private_viewer':'runtime/private/viewer.html','guides':heights},indent=2)+'\n')
    return str(private/'viewer.html')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--delivery',type=Path,required=True);p.add_argument('--glyph-run',type=Path,required=True);a=p.parse_args();print(build_view(a.delivery,a.glyph_run))
