#!/usr/bin/env python3
"""Prepare, retain and measure one built-in imagegen glyph query.

This tool never invokes a model. Dispatch the saved prompt with the built-in
image tool, then record its original PNG and analyze locally. All new glyphs
derive from the same frozen root. Ordinary Baskerville glyphs are excluded.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil

from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/'runs/pipeline-2026-10-30'
MASTER=ROOT/'runs/unified-master-2026-10-29/candidate-01'
NAMES=['alpha','beta','theta','nu','xi','omega']


def read(p):
    return json.loads(p.read_text())


def write(p,data):
    p.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def prepare(name):
    state=read(RUN/'state.json')
    if state['active_image_request']:
        raise ValueError('A prior query is unresolved; do not dispatch twice')
    if state['image_calls']>=6:
        raise ValueError('Six-call enlargement cap reached')
    folder=RUN/'glyphs'/name
    if folder.exists():
        raise ValueError('Target already has a request; no automatic retries')
    cell=next(x for x in read(MASTER/'cells.json')['cells'] if x['name']==name)
    refs=[MASTER/'master.png',ROOT/cell['crop'],ROOT/'fonts/private/reference-specimens/storm-baskerville-2026-10-29/storm-baskerville-reference.png']
    if sha(refs[0])!=read(MASTER/'cells.json')['root_sha256'] or sha(refs[1])!=cell['crop_sha256']:
        raise ValueError('Frozen root/crop hash differs')
    anatomy={
        'alpha':'asymmetric bowl, counter, slant, joining stroke and energetic right tail',
        'beta':'two bowls, counters, waist, upper stroke and descending lower stroke',
        'theta':'slanted oval, both counters and thin internal crossbar',
        'nu':'pointed descending join, open upper space, slant and rising right stroke; not upsilon',
        'xi':'three turns, joins, terminals, continuous stroke and descending sweep',
        'omega':'paired bowls, open upper space, central join, slant and terminals'}[name]
    prompt=f'''Use case: faithful typography reference enlargement, not a new design.
Image 1 is the ONE approved unified Baskerville math foundation master. Image 2 is its exact unaltered crop for italic Greek {name}, “{cell['character']}”, row {cell['row']} column {cell['column']}, target {cell['target_codepoint']}. Image 3 is a substantial page of actual Storm Baskerville 10 Pro in regular/italic/bold/bolditalic. This last image supplies family context ONLY: the master and crop are authoritative for anatomy and weight; do not substitute Storm's Greek or the older heavier Greek seed.

Produce ONE large sharp black FILLED enlargement of exactly this cropped glyph on pure white, at highest practical original resolution, preferably a near-square canvas. Uniformly enlarge the entire source crop and pad with white if necessary. Preserve its natural aspect, relative proportions and visible framing; do not independently stretch width/height or maximize its black bounding box to fill the page. All glyphs must ultimately fit back to the original unified root's common scale, not individually normalized sizes.

Preserve the {anatomy}, and the exact source thick/thin contrast, stress, curvature, apertures and serif/terminal treatment. The current root is an explicit regular-companion experiment. Keep this root's actual weight. Do not beautify, redesign, make it more conventional, thin/embolden it or invent extra details. Resolve pixel edges into smooth clean contours with the same visible shape; this is faithful enlargement, not an independent foundry design.

Exactly one completely unclipped filled glyph with ample white margins. NO labels, duplicate reference glyphs, titles, guides, grid, measuring lines, outlines, handles, nodes, arrows, textures, shadows, border or watermark. Only the enlarged black silhouette on white. Real vector handles and removable measured guides are generated locally afterward.
'''
    folder.mkdir(parents=True)
    (folder/'prompt.txt').write_text(prompt)
    write(folder/'request.json',{'status':'dispatched','name':name,'cell':cell,
          'references':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in refs],
          'prompt_sha256':sha(folder/'prompt.txt'),'image_calls':1,
          'dispatched_at':datetime.now(timezone.utc).isoformat()})
    state['image_calls']+=1
    state['active_image_request']=str((folder/'request.json').relative_to(ROOT))
    state['stage']='glyph_dispatched'
    write(RUN/'state.json',state)
    print(json.dumps({'prompt':str(folder/'prompt.txt'),'references':[str(p) for p in refs]},indent=2))


def record(name,source):
    folder=RUN/'glyphs'/name
    request=read(folder/'request.json')
    dest=folder/'enlarged.png'
    if dest.exists():
        raise ValueError('Refusing to replace retained model output')
    with Image.open(source) as im:
        if im.format!='PNG':
            raise ValueError('Retain the original PNG, not a converted file')
        dims=list(im.size)
    shutil.copyfile(source,dest)
    write(folder/'result.json',{'status':'complete','image':'enlarged.png','sha256':sha(dest),
          'dimensions':dims,'tool':'built-in imagegen','image_calls':1,'token_usage_exposed':False})
    print(dest)


def analyze(name):
    # These six selected Greek sources are connected; disconnected targets
    # must use a separate full-component registration, never the legacy fit.
    from glyph_consistency_report import registered,compare_png,np,component
    from math_trace import foreground,topology,export
    folder=RUN/'glyphs'/name
    req=read(folder/'request.json');cell=req['cell']
    result=read(folder/'result.json')
    if sha(folder/'enlarged.png')!=result['sha256']:
        raise ValueError('Retained generated image changed')
    source=Image.open(ROOT/cell['crop']);image=Image.open(folder/'enlarged.png')
    _,sm,_=foreground(source,allow_color=True);_,tm,_=foreground(image,allow_color=True)
    if topology(sm)['component_count']!=1 or topology(tm)['component_count']!=1:
        raise ValueError('Connected-only registration is not valid for this input')
    a,b,metrics=registered(source,image)
    compare_png(a,b,folder/'comparison.png')
    Image.fromarray(np.uint8(np.clip(1-b,0,1)*255)).save(folder/'registered.png')
    _,_,box,_=component(image);s=metrics['registration']['uniform_scale']
    reg={'scale':s,
         'translate_x':cell['source_crop_box'][0]+metrics['registration']['translate_x']-s*max(0,box[0]-8),
         'translate_y':cell['source_crop_box'][1]+metrics['registration']['translate_y']-s*max(0,box[1]-8)}
    write(folder/'consistency.json',{'method':'Connected Greek: one uniform scale and translation only. Full-component trace; explicit RGB luminance conversion.',
          'metrics':metrics,'registration_to_root':reg,
          'root_sha256':req['references'][0]['sha256']})
    report=export(folder/'enlarged.png',folder/'trace',allow_color=True,
                  tolerance_px=.0015*(box[3]-box[1]),supersample=2)
    state=read(RUN/'state.json')
    state['active_image_request']=None
    state['stage']='glyph_traced_pending_visual_review'
    if name not in state['completed_custom_targets']:
        state['completed_custom_targets'].append(name)
    write(RUN/'state.json',state)
    sources={}
    for target in NAMES:
        path=RUN/'glyphs'/target/'consistency.json'
        if path.exists() and (path.parent/'trace/curves.json').exists():
            sources[target]={'curves':f'glyphs/{target}/trace/curves.json',
                             'registration_to_root':read(path)['registration_to_root'],
                             'registration_note':'Measured uniform registration of retained enlargement to frozen root; no width fitting.'}
    write(RUN/'font-sources.json',{'sources':sources})
    print(json.dumps({'name':name,'master_iou':metrics['silhouette_iou'],
          'master_boundary_px':metrics['boundary_mean_master_px'],
          'aspect_change':metrics['aspect_change_fraction'],
          'trace_iou':report['fidelity']['full_canvas_iou'],
          'topology_preserved':report['topology_preserved'],
          'cubics':report['geometry']['cubic_segments']},indent=2))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['prepare','record','analyze'])
    parser.add_argument('name',choices=NAMES)
    parser.add_argument('--source',type=Path)
    args=parser.parse_args()
    if args.action=='prepare':prepare(args.name)
    elif args.action=='record':
        if not args.source:parser.error('record requires --source')
        record(args.name,args.source)
    else:analyze(args.name)


if __name__=='__main__':
    main()
