#!/usr/bin/env python3
"""Make inspectable local reports from completed raster/vector measurements."""
import base64
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / 'runs/glyph-consistency-2026-10-29'
CSS = '''html,body{margin:0;padding:0;background:transparent;color:var(--foreground);font-family:var(--font-sans,system-ui)}*{box-sizing:border-box}p{font-size:14px;line-height:1.5;margin:8px 0 14px}h2{font-size:19px;margin:0 0 10px}.controls{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0}select,button{font:inherit;max-width:100%;color:var(--foreground);background:var(--card);border:1px solid var(--border);padding:8px;border-radius:var(--radius);cursor:pointer}.image{background:white;overflow:auto}.image img{width:100%;height:auto;display:block}.pair{display:grid;grid-template-columns:1fr 1fr;gap:8px}.pair img{width:100%;height:auto;display:block;background:white}.caption{font-size:12px;opacity:.8}a{color:var(--chart-1)}svg text{fill:var(--foreground);font-family:var(--font-sans,system-ui)}.legend{display:flex;gap:12px;flex-wrap:wrap;font-size:12px}.dot{display:inline-block;width:9px;height:9px;margin-right:4px}#chart{height:220px}.muted{font-size:12px;opacity:.8}'''


def read(path):
    return json.loads(path.read_text())


def img(path):
    suffix = 'svg+xml' if path.suffix == '.svg' else 'png'
    return 'data:image/' + suffix + ';base64,' + base64.b64encode(path.read_bytes()).decode()


def write_pair(stem, template, data, paths):
    for embed in [False, True]:
        assets = ''.join(f'<img id="asset-{i}" src="{img(p) if embed else p}">' for i, p in enumerate(paths))
        markup = template.replace('__DATA__', json.dumps(data).replace('<', '\\u003c'))
        markup = markup.replace('__ASSETS__', '<div hidden>' + assets + '</div>')
        (RUN / (stem + ('' if embed else '-preview') + '.html')).write_text(markup)


def main():
    data = read(RUN / 'measurements.json')
    rows = [x for x in data['results'] if x['status'] == 'complete']
    paths = [RUN / 'glyphs' / x['name'] / 'comparison.png' for x in rows]
    template = '''<!doctype html><html><meta charset="utf-8"><title>Greek enlargement consistency</title><style>''' + CSS + '''</style><body>
<h2>Master sheet → individual glyphs</h2><p>32 independent enlargements from one fixed master and unaltered cell crops. Compare the source, registered enlargement and pixel disagreement.</p>
<div id="chart"></div><p class="caption">Silhouette overlap after translation and uniform scale. Width is never stretched independently. This measures shape agreement; it does not establish common font metrics.</p>
<div class="controls"><select id="glyph" aria-label="Glyph"></select></div><p id="stats"></p><div class="image"><img id="comparison" alt="Master, enlargement and disagreement"></div>
<p id="links"></p><p class="muted">Master epsilon/kappa/phi variants are near-duplicates and need separate design review. Counter counting ignores pinholes smaller than four master pixels. The master itself supplies limited detail.</p>
__ASSETS__<script>const DATA=__DATA__;const $=x=>document.getElementById(x);
const bars=DATA.map((r,i)=>`<rect x="${36+i*20}" y="${180-r.silhouette_iou*160}" width="13" height="${r.silhouette_iou*160}" fill="var(--chart-1)"><title>${r.name}: ${(r.silhouette_iou*100).toFixed(1)}%</title></rect><text x="${42+i*20}" y="200" text-anchor="middle" font-size="11">${r.char}</text>`).join('');
$('chart').innerHTML=`<svg viewBox="0 0 700 220" style="width:100%;height:220px" role="img" aria-label="Per glyph silhouette overlap"><text x="0" y="24" font-size="11">100%</text><text x="18" y="180" font-size="11">0</text>${bars}</svg>`;
DATA.forEach((r,i)=>$('glyph').add(new Option(r.char+' · '+r.name,i)));
function show(){let i=+$('glyph').value,r=DATA[i];$('comparison').src=$('asset-'+i).src;$('stats').textContent=`Overlap ${(r.silhouette_iou*100).toFixed(1)}%; mean boundary distance ${r.boundary_mean_master_px.toFixed(2)} master px; 95th percentile ${r.boundary_p95_master_px.toFixed(2)} px; aspect change ${(r.aspect_change_fraction*100).toFixed(1)}%.`;$('links').innerHTML=`<a href="glyphs/${r.name}/enlarged.png">Original enlarged PNG</a> · <a href="glyphs/${r.name}/prompt.txt">Exact prompt</a> · <a href="glyphs/${r.name}/metrics.json">Measurements</a>`}
$('glyph').onchange=show;show();</script></body></html>'''
    write_pair('consistency', template, rows, paths)

    benchmark = read(RUN / 'vector-trial/summary.json')
    records = benchmark['results']
    modes = ['master', 'lanczos8', 'generated']
    cases = []
    paths = []
    for r in records:
        folder = RUN / 'vector-trial'
        stem = r['name'] + '-' + r['mode']
        original = RUN / 'glyphs' / r['name'] / ('master-crop.png' if r['mode'] == 'master' else 'enlarged.png')
        if r['mode'] == 'lanczos8':
            original = folder / (r['name'] + '-lanczos8-input.png')
            from PIL import Image
            im = Image.open(RUN / 'glyphs' / r['name'] / 'master-crop.png')
            im.resize((im.width*8, im.height*8), Image.Resampling.LANCZOS).save(original)
        r['source_asset'] = len(paths); paths.append(original)
        r['fill_asset'] = len(paths); paths.append(folder / (stem + '.svg'))
        r['handle_asset'] = len(paths); paths.append(folder / (stem + '-handles.svg'))
        cases.append(r)
    template = '''<!doctype html><html><meta charset="utf-8"><title>Vectorisation before and after enlargement</title><style>''' + CSS + '''</style><body>
<h2>Actual vectorisation: before and after enlargement</h2><p>Six glyphs, one Potrace 1.16 configuration. Compare the small master, an ordinary 8× Lanczos upscale, and the independent image-model enlargement.</p>
<div class="legend"><span><i class="dot" style="background:var(--chart-1)"></i>Small master</span><span><i class="dot" style="background:var(--chart-2)"></i>Ordinary upscale</span><span><i class="dot" style="background:var(--chart-3)"></i>Generated enlargement</span></div>
<div class="controls"><select id="metric" aria-label="Measurement"><option value="trace">Tracing mismatch % · lower is better</option><option value="master">Difference from original master %</option><option value="nodes">Cubic segment count</option></select></div><div id="chart"></div>
<p id="chart-note" class="caption"></p><div class="controls"><select id="glyph" aria-label="Glyph"></select><select id="source" aria-label="Trace input"><option value="master">Small master</option><option value="lanczos8">Ordinary 8× upscale</option><option value="generated">Generated enlargement</option></select><button id="handles">Show real handles</button></div>
<p id="stats"></p><div class="pair"><div><p class="caption">Raster input</p><img id="raster" alt="Raster used for vectorisation"></div><div><p class="caption" id="vector-label">Actual SVG curves</p><img id="vector" alt="Actual traced cubic Bézier SVG"></div></div>
<p id="links"></p><p class="muted">Overlap measures raster fidelity, not typeface quality. Enlargements can change the master design. All traces use the same corner setting and tolerance proportional to input glyph height; this is one tracing configuration. Smooth tangent joins do not imply continuous curvature. These outlines still need font fitting, optical design and mathematical layout data.</p>
__ASSETS__<script>const DATA=__DATA__,MODES=['master','lanczos8','generated'],NAMES=['alpha','beta','theta','nu','xi','omega'],CHARS=['α','β','θ','ν','ξ','ω'];const $=x=>document.getElementById(x);let handles=false;
function value(r){return $('metric').value==='nodes'?r.cubic_segments:100*(1-($('metric').value==='trace'?r.own_source_iou:r.original_master_iou_after_uniform_registration))}
function chart(){let max=Math.max(...DATA.map(value))*1.12,bars='';DATA.forEach(r=>{let i=NAMES.indexOf(r.name),j=MODES.indexOf(r.mode),v=value(r),h=v/max*150;bars+=`<rect x="${62+i*104+j*23}" y="${175-h}" width="18" height="${h}" fill="var(--chart-${j+1})"><title>${r.name} / ${r.mode}: ${v.toFixed(2)}</title></rect>`});NAMES.forEach((n,i)=>bars+=`<text x="${94+i*104}" y="198" text-anchor="middle" font-size="14">${CHARS[i]}</text>`);$('chart').innerHTML=`<svg viewBox="0 0 710 220" style="width:100%;height:220px" role="img" aria-label="Vectorisation comparison"><text x="10" y="30" font-size="11">${max.toFixed(1)}</text><text x="30" y="177" font-size="11">0</text>${bars}</svg>`;$('chart-note').textContent=$('metric').value==='trace'?'Each vector is compared to its OWN raster input. These are different input images.':$('metric').value==='master'?'All vectors are compared to the SAME original master after translation and uniform scaling. This includes enlargement drift.':'More nodes are not necessarily better. Ordinary upscaling can amplify edge texture into extra curve segments.'}
NAMES.forEach((n,i)=>$('glyph').add(new Option(CHARS[i]+' · '+n,n)));
function show(){const r=DATA.find(r=>r.name===$('glyph').value&&r.mode===$('source').value);$('raster').src=$('asset-'+r.source_asset).src;$('vector').src=$('asset-'+(handles?r.handle_asset:r.fill_asset)).src;$('stats').textContent=`Own-input overlap ${(100*r.own_source_iou).toFixed(2)}%; ${r.cubic_segments} cubics + ${r.explicit_corner_segments} corner segments; original-master overlap ${(100*r.original_master_iou_after_uniform_registration).toFixed(1)}%.`;$('vector-label').textContent=handles?'Actual curve anchors and handles':'Actual SVG curves';$('links').innerHTML=`<a href="vector-trial/${r.name}-${r.mode}.svg">Open vector SVG</a> · <a href="vector-trial/${r.name}-${r.mode}-handles.svg">Real Bézier construction</a> · <a href="vector-trial/${r.name}-${r.mode}.json">Measurements</a>`}
$('glyph').onchange=show;$('source').onchange=show;$('metric').onchange=chart;$('handles').onclick=()=>{handles=!handles;$('handles').textContent=handles?'Show fill':'Show real handles';show()};$('source').value='generated';chart();show();</script></body></html>'''
    write_pair('vectorisation', template, cases, paths)
    print('Built self-contained consistency.html and vectorisation.html plus local preview versions.')


if __name__ == '__main__':
    main()
