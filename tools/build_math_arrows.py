#!/usr/bin/env python3
"""Author a finite arrow family from one declared head/shaft grammar, not a trace.

Coordinates are design units (1000/em). Export uses a declared derived y-down
frame compatible with the current build_math_ams.py coordinate transform.
No commercial font, image model, glyph donor or rejected source cell is used.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import unicodedata
import pathops
from fontTools.pens.recordingPen import RecordingPen

ROOT = Path(__file__).resolve().parents[1]
GRAMMAR = ROOT / 'design/arrow-grammar.json'
DEFAULT_OUT = ROOT / 'runs/ams-coverage-2026-10-30/arrows-v1'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def specs():
    result = []
    def add(name, cp, angle=0, ends='right', **kw):
        result.append({'name': name, 'codepoint': cp, 'angle': angle, 'ends': ends, **kw})
    for name, cp, angle, ends in [
        ('left',0x2190,180,'right'),('up',0x2191,90,'right'),
        ('right',0x2192,0,'right'),('down',0x2193,270,'right'),
        ('leftright',0x2194,0,'both'),('updown',0x2195,90,'both'),
        ('northwest',0x2196,135,'right'),('northeast',0x2197,45,'right'),
        ('southeast',0x2198,315,'right'),('southwest',0x2199,225,'right')]:
        add('arrow_'+name,cp,angle,ends)
    for name,cp,angle in [('left',0x21A4,180),('up',0x21A5,90),('right',0x21A6,0),('down',0x21A7,270)]:
        add('arrow_frombar_'+name,cp,angle,bar=True)
    for name,cp,angle,ends in [('left',0x21D0,180,'right'),('up',0x21D1,90,'right'),
        ('right',0x21D2,0,'right'),('down',0x21D3,270,'right'),
        ('leftright',0x21D4,0,'both'),('updown',0x21D5,90,'both')]:
        add('arrow_double_'+name,cp,angle,ends,double=True)
    # Half-head side is canonical BEFORE rotation, not its Unicode direction word.
    for name,cp,angle,side in [('left_up',0x21BC,180,'lower'),('left_down',0x21BD,180,'upper'),
        ('up_right',0x21BE,90,'lower'),('up_left',0x21BF,90,'upper'),
        ('right_up',0x21C0,0,'upper'),('right_down',0x21C1,0,'lower'),
        ('down_right',0x21C2,270,'upper'),('down_left',0x21C3,270,'lower')]:
        add('harpoon_'+name,cp,angle,half_head=side)
    for name,cp,angle,ends,double in [('left',0x27F5,180,'right',False),
        ('right',0x27F6,0,'right',False),('leftright',0x27F7,0,'both',False),
        ('double_left',0x27F8,180,'right',True),('double_right',0x27F9,0,'right',True),
        ('double_leftright',0x27FA,0,'both',True)]:
        add('arrow_long_'+name,cp,angle,ends,long=True,double=double)
    return result


def stroke(path, width, grammar):
    path.stroke(width, pathops.LineCap.BUTT_CAP, pathops.LineJoin.MITER_JOIN, grammar['miter_limit'])
    return path


def shaft(x0, x1, y, grammar):
    p = pathops.Path(); p.moveTo(x0,y); p.lineTo(x1,y)
    return stroke(p,grammar['shaft_thickness'],grammar)


def head(tip, grammar, side=None):
    """Shared centerline cubic chevron or one of its exact halves."""
    length, height = grammar['head_length'], grammar['head_half_height']
    a,b = grammar['head_curve_controls']
    p = pathops.Path()
    p.moveTo(tip-length,height)
    p.cubicTo(tip-length*a[0],height*a[1],tip-length*b[0],height*b[1],tip,0)
    p.cubicTo(tip-length*b[0],-height*b[1],tip-length*a[0],-height*a[1],tip-length,-height)
    if side:
        p = pathops.Path()
        sign = 1 if side == 'upper' else -1
        p.moveTo(tip-length,sign*height)
        p.cubicTo(tip-length*a[0],sign*height*a[1],tip-length*b[0],sign*height*b[1],tip,0)
    return stroke(p,grammar['shaft_thickness'],grammar)


def rotate(path, angle):
    c,s = math.cos(math.radians(angle)),math.sin(math.radians(angle))
    c,s = (0 if abs(v)<1e-10 else v for v in (c,s))
    return path.transform(c,s,-s,c,0,0)


def head_intersection_x(tip, y, grammar):
    """Solve the shared cubic centerline at |y| by monotone bisection."""
    length,height=grammar['head_length'],grammar['head_half_height']
    a,b=grammar['head_curve_controls'];y=abs(y)
    if not 0 <= y <= height:raise ValueError('Shaft falls outside the head')
    lo,hi=0.,1.
    def bez(v,t):return (1-t)**3*v[0]+3*(1-t)**2*t*v[1]+3*(1-t)*t*t*v[2]+t**3*v[3]
    for _ in range(64):
        t=(lo+hi)/2
        if bez([height,height*a[1],height*b[1],0],t)>y:lo=t
        else:hi=t
    t=(lo+hi)/2
    return bez([tip-length,tip-length*a[0],tip-length*b[0],tip],t)


def head_interior(tip, left, grammar):
    """Exact curved half-plane used to trim the WHOLE double-shaft end.

    This avoids a butt-ended rectangle projecting beyond the curve at the
    shaft's upper/lower edge even when its centerline intersects correctly.
    The stroked head overlaps this centerline clip by its half-stroke width.
    """
    length,height=grammar['head_length'],grammar['head_half_height'];a,b=grammar['head_curve_controls']
    p=pathops.Path();p.moveTo(left,height);p.lineTo(tip-length,height)
    p.cubicTo(tip-length*a[0],height*a[1],tip-length*b[0],height*b[1],tip,0)
    p.cubicTo(tip-length*b[0],-height*b[1],tip-length*a[0],-height*a[1],tip-length,-height)
    p.lineTo(left,-height);p.close()
    return p


def arrow(spec, grammar):
    length = grammar['long_centerline_length'] if spec.get('long') else grammar['normal_centerline_length']
    left,right = -length/2,length/2
    half = spec.get('half_head')
    parts = [head(right,grammar,half)]
    if spec['ends'] == 'both':
        parts.append(rotate(head(right,grammar),180))
    if spec.get('double'):
        clip = head_interior(right,left-100,grammar)
        left_clip = rotate(clip,180)
        for y in (-grammar['double_shaft_center_distance']/2,grammar['double_shaft_center_distance']/2):
            # Solve explicitly for audit, then retain the exact curved end
            # across the stripe instead of leaving a protruding flat cap.
            head_intersection_x(right,y,grammar)
            stripe=pathops.op(shaft(left,right,y,grammar),clip,pathops.PathOp.INTERSECTION)
            if spec['ends']=='both':stripe=pathops.op(stripe,left_clip,pathops.PathOp.INTERSECTION)
            parts.append(stripe)
    else:
        parts.append(shaft(left,right-grammar['shaft_thickness']*.25,0,grammar))
    if spec.get('bar'):
        p=pathops.Path(); h=grammar['mapsto_bar_half_height']
        p.moveTo(left,-h);p.lineTo(left,h)
        parts.append(stroke(p,grammar['shaft_thickness'],grammar))
    merged=parts[0]
    for p in parts[1:]:
        merged=pathops.op(merged,p,pathops.PathOp.UNION)
    return rotate(merged,spec['angle']), parts


def cubic_paths(path, grammar):
    """Exact quadratic-to-cubic degree elevation; output builder tag1/2 schema."""
    rec=RecordingPen();path.draw(rec)
    paths=[];segments=[];current=None;start=None
    # Keep font x origin at 0 for a normal horizontal arrow. The builder adds
    # sidebearings itself. Serialized frame baseline is 750; y increases down.
    def point(p):return [round(p[0]+800,6),round(750-(p[1]+grammar['math_axis']),6)]
    for op,pts in rec.value:
        if op=='moveTo':start=current=pts[0];segments=[]
        elif op=='lineTo':
            for end in pts:
                segments.append({'tag':2,'points':[point(current),point(end),point(end)]});current=end
        elif op=='curveTo':
            if len(pts)!=3:raise ValueError('Unexpected cubic arity')
            segments.append({'tag':1,'points':[point(p) for p in pts]});current=pts[-1]
        elif op=='qCurveTo':
            if len(pts)!=2:raise ValueError('Unexpected quadratic arity')
            control,end=pts
            c1=tuple(current[i]+2*(control[i]-current[i])/3 for i in (0,1))
            c2=tuple(end[i]+2*(control[i]-end[i])/3 for i in (0,1))
            segments.append({'tag':1,'points':[point(c1),point(c2),point(end)]});current=end
        elif op=='closePath':
            if current!=start:segments.append({'tag':2,'points':[point(current),point(start),point(start)]})
            paths.append({'segments':segments})
        else:raise ValueError(f'Unsupported path operation: {op}')
    return {'schema_version':1,'frame_kind':'derived_design_units','paths':paths}


def svg_path(path):
    from fontTools.pens.svgPathPen import SVGPathPen
    p=SVGPathPen(None);path.draw(p);return p.getCommands()


def build(output=DEFAULT_OUT, grammar_path=GRAMMAR):
    output=Path(output);grammar=json.loads(Path(grammar_path).read_text())
    if (output/'sources.json').exists():raise FileExistsError('Use a fresh output directory; arrow outputs are immutable')
    root=ROOT/grammar['root_image']
    if sha(root)!=grammar['root_sha256']:raise ValueError('Unified descendant image hash mismatch')
    output.mkdir(parents=True,exist_ok=True)
    sources={};metrics=[];art=[]
    for i,spec in enumerate(specs()):
        path,parts=arrow(spec,grammar);curves=cubic_paths(path,grammar)
        target=output/spec['name'];target.mkdir()
        curvefile=target/'curves.json';curvefile.write_text(json.dumps(curves,indent=2)+'\n')
        import os
        sources[spec['name']]={
            'codepoints':[f"U+{spec['codepoint']:04X}"],'kind':'symbol',
            'curves':str(curvefile.relative_to(output)),'curves_sha256':sha(curvefile),
            'source_crop_box':[0,0,1600,1000],'baseline_root':750,'source_em_pixels':1000,
            'registration_to_root':{'scale':1,'translate_x':0,'translate_y':0},
            'root_sha256':grammar['root_sha256'],'root_image':os.path.relpath(root,output),
            'frame_kind':'derived_design_units',
            'frame_note':'These numerical root/crop/em fields describe a derived design frame, NOT pixel coordinates in root_image. x=canonical_x+800; y=750-(canonical_y+250).',
            'provenance':{'method':'authored shared vector arrow grammar; boolean union of stroked cubic components',
                'grammar':'design/arrow-grammar.json','grammar_sha256':sha(grammar_path),
                'root_reference_crop_pixels':grammar['reference_crop_pixels'],
                'root_reference_role':'valid ordinary right-arrow; visual calibration only; not traced',
                'recipe':spec,'donor_outlines':False,'raster_fit_claimed':False,
                'frame_kind':'derived_design_units','root_frame_registration_claimed':False},
            'status':'provisional authored grammar derivative; optical and engine proof pending'}
        ncontours=len(curves['paths'])
        metrics.append({**spec,'unicode_name':unicodedata.name(chr(spec['codepoint'])),
            'contours':ncontours,'area_design_units2':abs(path.area),
            'canonical_bounds':list(path.bounds),'component_count_before_union':len(parts),
            'double_shaft_centerline_join_x':head_intersection_x((grammar['long_centerline_length'] if spec.get('long') else grammar['normal_centerline_length'])/2,grammar['double_shaft_center_distance']/2,grammar) if spec.get('double') else None,
            'shaft_thickness':grammar['shaft_thickness'],'head_length':grammar['head_length'],
            'head_half_height':grammar['head_half_height'],'curves_sha256':sha(curvefile)})
        col,row=i%4,i//4
        art.append(f'<g transform="translate({col*470+235},{row*260+160})"><path d="{svg_path(path)}" transform="scale(.22,-.22)" fill="black"/><text x="0" y="110" text-anchor="middle" font-size="14">U+{spec["codepoint"]:04X} {spec["name"]}</text></g>')
    (output/'sources.json').write_text(json.dumps({'schema_version':1,'frame_kind':'derived_design_units','sources':sources},indent=2)+'\n')
    report={'status':'authored_provisional_not_optically_accepted','glyph_count':len(metrics),
        'grammar_sha256':sha(grammar_path),'root_sha256':grammar['root_sha256'],
        'raster_fidelity_measured':False,'shared_shaft_thickness':grammar['shaft_thickness'],
        'font_rule_reference':{'source':'tools/build_math_pilot.py','FractionRuleThickness':40,'AxisHeight':250},
        'metrics':metrics,'limitations':grammar['limitations']}
    (output/'metrics.json').write_text(json.dumps(report,indent=2)+'\n')
    svg='<svg xmlns="http://www.w3.org/2000/svg" width="1880" height="2780" viewBox="0 0 1880 2780"><rect width="1880" height="2780" fill="white"/><text x="24" y="28" font-size="20">Shared authored arrow grammar v1 — 34 provisional outlines, no raster-fit claim</text>'
    art.append('<text x="24" y="2420" font-size="20">Working-size rows: 10pt, 7pt, 5pt at 96dpi; no optical size compensation</text>')
    guides=[]
    for size_index,pt in enumerate([10,7,5]):
        for i,spec in enumerate(specs()):
            path,_=arrow(spec,grammar);x=90+(i%17)*108;y=2470+size_index*95+(i//17)*38
            scale=pt*96/72/1000
            art.append(f'<g transform="translate({x},{y})"><path d="{svg_path(path)}" transform="scale({scale},-{scale})" fill="black"/><text x="0" y="21" text-anchor="middle" font-size="9">{pt}pt {spec["codepoint"]:04X}</text></g>')
            guides.append(f'<path d="M{x-40},{y}h80" stroke="#2996bd" stroke-width=".4"/>')
    (output/'grid.svg').write_text(svg+''.join(art)+'</svg>\n')
    (output/'grid-guides.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="1880" height="2780" viewBox="0 0 1880 2780">'+''.join(guides)+'</svg>\n')
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=DEFAULT_OUT)
    args=p.parse_args();print(json.dumps({k:v for k,v in build(args.output).items() if k!='metrics'},indent=2))
if __name__=='__main__':main()
