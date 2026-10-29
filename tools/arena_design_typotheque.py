#!/usr/bin/env python3
"""Two-pass Typotheque-inspired arena entrant. Active helpers adopted read-only.
No raster tracing, global outline offsets, archive imports or other entrant inputs.
"""
import argparse, copy, json, math, shutil, sys
from pathlib import Path
import pathops
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
from design_greek_campaign import (ROOT, CHARS, STYLES, inventory, bounds, path,
                                  contours, recording, install, sha, command)
from arena_proofs import build_proofs

RUN=ROOT/'runs/arena-2026-10-29/entrants/typotheque'
RECIPE=ROOT/'design/arena-typotheque.json'

class AnatomyPen:
    """Smooth nonlinear glyph-specific map, reconstructed as cubic Hermite spans.
    Deslant first; modulate bowl breadth/gesture; restore native italic posture.
    Exact chain-rule tangents maintain smooth joins. No contour stroke/offset.
    """
    def __init__(self,out,box,xh,style,c,params,level,settings):
        self.out=out;self.box=box;self.xh=xh;self.style=style;self.c=c
        self.params=params;self.level=level;self.settings=settings;self.cur=None
        self.slant=.19 if style in ['italic','bolditalic'] else 0
        self.mid=(box[0]+box[2])/2-self.slant*(box[1]+box[3])/2
    def map(self,p):
        x,y=p;t=y/self.xh;w,b,gesture,vertical,_,_,_=self.params
        # Existing optical outlines remain separate source drawings. Their
        # broader apertures are enhanced by role-specific bowl proportions.
        op=self.settings['script_opening'][self.level]
        bold='bold' in self.style
        w=1+(w-1)*self.settings['family_width_factor']+(op*.7)
        b*=.86 if bold else 1
        width=w+b*math.sin(math.pi*t)
        if self.c=='β':width+=.042*math.exp(-((t-.28)/.34)**2)-.026*math.exp(-((t-1.12)/.31)**2)
        if self.c=='ξ':width+=.035*math.exp(-((t+.16)/.4)**2)-.025*math.exp(-((t-1.35)/.3)**2)
        yy=y+vertical*math.sin(2*math.pi*t)
        u=x-self.slant*y-self.mid
        xx=self.mid+u*width+gesture*math.sin(math.pi*t)+self.slant*yy
        return xx,yy
    def jac(self,p,d):
        # Stable symmetric derivative of the analytic design map, error well
        # below 1/1024 unit CFF quantisation; keeps cross-axis chain rule.
        h=.001;a=self.map((p[0]-h*d[0],p[1]-h*d[1]));b=self.map((p[0]+h*d[0],p[1]+h*d[1]))
        return ((b[0]-a[0])/(2*h),(b[1]-a[1])/(2*h))
    def moveTo(self,p):self.cur=p;self.out.moveTo(self.map(p))
    def lineTo(self,p):
        a=self.cur;self.curveTo(tuple(a[k]+(p[k]-a[k])/3 for k in (0,1)),tuple(a[k]+2*(p[k]-a[k])/3 for k in (0,1)),p)
    def curveTo(self,b,c,d):
        a=self.cur
        def ev(t):
            u=1-t;p=tuple(u*u*u*a[k]+3*u*u*t*b[k]+3*u*t*t*c[k]+t*t*t*d[k] for k in (0,1))
            v=tuple(3*u*u*(b[k]-a[k])+6*u*t*(c[k]-b[k])+3*t*t*(d[k]-c[k]) for k in (0,1))
            return self.map(p),self.jac(p,v)
        for i in range(8):
            p,v=ev(i/8);q,w=ev((i+1)/8)
            self.out.curveTo(tuple(p[k]+v[k]/24 for k in (0,1)),tuple(q[k]-w[k]/24 for k in (0,1)),q)
        self.cur=d
    def closePath(self):self.out.closePath()
    def endPath(self):self.out.endPath()

def drawn_pair(c,style,level,settings):
    """Authored cubic silhouettes in a shared 500-unit design space.
    Nu: narrow asymmetric trough, curved descending left and rising right.
    Upsilon: open cupped bowl, broad low curve and returning right terminal.
    Weight/optical roles alter interior trajectories, not a silhouette offset.
    """
    p=pathops.Path();q=p.getPen();bold='bold' in style
    ink=(18 if bold else 0)+level*(2.8 if bold else 3.5)
    a=settings['nu_trough_x'];by=settings['upsilon_bowl_y']
    if c=='ν':
        q.moveTo((35,401));q.curveTo((58,447),(91,484),(124,478))
        q.curveTo((165,475),(181,426),(187,366))
        q.curveTo((193,286),(200,143),(a+10+ink,55))
        q.curveTo((310,143),(369,282),(386,399))
        q.curveTo((390,432),(388,461),(402,475))
        q.curveTo((417,490),(451,478),(459,458))
        q.curveTo((474,414),(438,304),(393,215))
        q.curveTo((350,132),(297,51),(259,-10))
        q.curveTo((245,-29),(220,-28),(207,-7))
        q.curveTo((164,76),(145-ink*.32,179),(139-ink*.32,270))
        q.curveTo((132-ink*.32,355),(130-ink*.32,406),(106,418))
        q.curveTo((85,429),(68,406),(53,385));q.lineTo((35,401));q.closePath()
    else:
        q.moveTo((42,400));q.curveTo((60,440),(85,476),(116,478))
        q.curveTo((156,483),(180+ink*.35,448),(182+ink*.35,405))
        q.curveTo((185+ink*.35,331),(163+ink*.45,237),(174+ink*.45,150))
        q.curveTo((181+ink*.45,90),(203,by),(246,by))
        q.curveTo((309,by-4),(356,117),(385,202))
        q.curveTo((408,273),(423,368),(402,419))
        q.curveTo((392,442),(375,447),(374,461))
        q.curveTo((374,482),(419,488),(447,469))
        q.curveTo((491,438),(476,345),(448,259))
        q.curveTo((411,145),(335,12),(243,-14))
        q.curveTo((182,-31),(123-ink*.3,-7),(102-ink*.3,40))
        q.curveTo((76-ink*.3,98),(88-ink*.3,203),(98-ink*.3,292))
        q.curveTo((108-ink*.3,378),(106-ink*.3,419),(87,420))
        q.curveTo((76,423),(61,404),(55,393));q.closePath()
    if style in ['italic','bolditalic']:p=p.transform(1,0,.19,1,0,0)
    return p

def counter_open(p,c,params,level,style,settings):
    # Independent affine counter refinement is safe here because no Boolean
    # operations combine contours. Exterior arms and open apertures survive.
    out=pathops.Path();records=[];bold='bold' in style
    for depth,co in contours(p):
        if depth%2:
            x0,y0,x1,y1=co.bounds;cx=(x0+x1)/2;cy=(y0+y1)/2
            sx=1+(params[4]-1)*settings['counter_factor']+settings['script_opening'][level]*(1.0 if bold else .8)
            sy=1+(params[5]-1)*settings['counter_factor']+settings['script_opening'][level]*.45
            # Theta's two counters keep the mid bar position; counter relief
            # is chiefly horizontal rather than thinning the crossing.
            if c=='θ':sy=1+(sy-1)*.35
            q=co.transform(sx,0,0,sy,cx*(1-sx),cy*(1-sy));out.addPath(q)
            records.append({'depth':depth,'scale_x':sx,'scale_y':sy,'center':[cx,cy]})
        else:out.addPath(co)
    return out,records

def name_font(f,passno):
    family='Baskerville Math Arena Typotheque Inspired'
    ps=f'BaskervilleMathArena-TypothequeP{passno}'
    values={1:family,2:'Regular',3:f'20261029:{ps}:0.20{passno}',4:family+' Regular',5:f'Version 0.20{passno}; Independent private AI-assisted design study',6:ps,16:family,17:'Regular'}
    for r in f['name'].names:
        if r.nameID in values:r.string=values[r.nameID].encode(r.getEncoding())
    top=f['CFF '].cff.topDictIndex[0];f['CFF '].cff.fontNames=[ps]
    top.FamilyName=family;top.FullName=family+' Regular';top.version=f'0.20{passno}';f['head'].fontRevision=.20+passno/1000

def design(source,output,recipe,passno):
    f=TTFont(source,recalcTimestamp=False);inv=inventory(f);info=f['MATH'].table.MathGlyphInfo
    accents=dict(zip(info.MathTopAccentAttachment.TopAccentCoverage.glyphs,info.MathTopAccentAttachment.TopAccentAttachment))
    corrections=dict(zip(info.MathItalicsCorrectionInfo.Coverage.glyphs,info.MathItalicsCorrectionInfo.ItalicsCorrection))
    settings=recipe[f'pass_{passno}'];changes=[]
    for style in STYLES:
        xh=inv[style]['ο']['bounds'][3]
        for c,v in inv[style].items():
            params=recipe['forms'][c]
            for level,n in enumerate([v['glyph']]+v['ssty']):
                ob=bounds(f,n);oa,ol=f['hmtx'][n];old=path(f,n)
                oldac=accents[n].Value if n in accents else None;oldic=corrections[n].Value if n in corrections else None
                if c in 'νυ':
                    p=drawn_pair(c,style,level,settings);b=p.bounds
                    width=(ob[2]-ob[0])*(params[0]+settings['script_opening'][level])
                    sx=width/(b[2]-b[0]);sy=(ob[3]-ob[1])/(b[3]-b[1])
                    p=p.transform(sx,0,0,sy,ob[0]-sx*b[0],ob[1]-sy*b[1]);cr=[]
                    action='authored cubic silhouette: asymmetric Greek nu' if c=='ν' else 'authored cubic silhouette: broad cupped Greek upsilon'
                else:
                    p=pathops.Path();f.getGlyphSet()[n].draw(AnatomyPen(p.getPen(),ob,xh,style,c,params,level,settings))
                    p,cr=counter_open(p,c,params,level,style,settings)
                    b=p.bounds;sy=(ob[3]-ob[1])/(b[3]-b[1]);p=p.transform(1,0,0,sy,0,ob[1]-sy*b[1])
                    # Keep the accepted left-bearing reference so new width
                    # goes to the bowl and exit, not accidental negative LSB.
                    p=p.transform(1,0,0,1,ob[0]-p.bounds[0],0)
                    action='glyph-specific non-affine bowl/gesture remodelling; native Greek skeleton and optical drawing adopted'
                advance=round(p.bounds[2]+(oa-ob[2])+params[6]+level*1.5)
                install(f,n,p,advance);nb=bounds(f,n)
                # Transfer accent location by the same silhouette-envelope
                # expansion, preserving its relative horizontal placement.
                dx=round((nb[2]+nb[0]-ob[2]-ob[0])/2)
                if n in accents:accents[n].Value+=dx
                # Added advance absorbs the widened exit; retain accepted
                # italic-correction value rather than inventing angle equalities.
                changes.append({'glyph':n,'char':c,'style':style,'role':['text','script','scriptscript'][level],
                    'advance_before':oa,'advance_after':advance,'advance_delta':advance-oa,'lsb_before':ol,'lsb_after':f['hmtx'][n][1],
                    'bounds_before':ob,'bounds_after':nb,'top_accent_before':oldac,'top_accent_after':accents[n].Value if n in accents else None,
                    'top_accent_delta':dx if n in accents else None,'italic_correction_before':oldic,'italic_correction_after':oldic,'italic_correction_delta':0 if oldic is not None else None,
                    'outline_action':action,'parameters':params,'counter_transform':cr,'optical_opening':settings['script_opening'][level],
                    'topology_intent':'unchanged','retained_features':'source semantic skeleton/terminals/posture and vertical extents; explicit ssty role source' if c not in 'νυ' else 'source semantic identity, role extents and left-bearing reference; new silhouette'})
    name_font(f,passno);f.save(output);return inv,changes

def validate(source,output,changes):
    a,b=TTFont(source),TTFont(output);names={v['glyph'] for v in changes};inv=inventory(b)
    assert len(names)==384 and len(changes)==384
    assert a.getGlyphOrder()==b.getGlyphOrder() and a.getBestCmap()==b.getBestCmap()
    assert a['GSUB'].compile(a)==b['GSUB'].compile(b)
    changed=[];metrics=[];topology=[];protected=0
    for n in b.getGlyphOrder():
        ra,rb=recording(a,n),recording(b,n)
        if n not in names:
            assert ra==rb and a['hmtx'][n]==b['hmtx'][n],n;protected+=1
        else:
            assert ra!=rb,n;changed.append(n)
            if a['hmtx'][n]!=b['hmtx'][n]:metrics.append(n)
            old,new=path(a,n),path(b,n);ca,cb=contours(old),contours(new)
            oldholes=[co.area for d,co in ca if d%2];newholes=[co.area for d,co in cb if d%2]
            assert len(oldholes)==len(newholes),(n,oldholes,newholes)
            assert len(ca)==len(cb),(n,len(ca),len(cb))
            assert all(x>1 for x in newholes),(n,newholes)
            assert all(math.isfinite(x) for x in new.bounds)
            ratio=new.area/old.area;assert .58<ratio<1.50,(n,ratio)
            simp=pathops.simplify(new);err=abs(simp.area-new.area)
            assert err<max(1,new.area*.0001),(n,new.area,simp.area)
            topology.append({'glyph':n,'contours_before':len(ca),'contours_after':len(cb),'closed_counters':len(newholes),
                             'counter_areas_before':oldholes,'counter_areas_after':newholes,'fill_area_ratio':ratio,'simplification_area_error':err})
    ac,bc=copy.deepcopy(a['MATH']),copy.deepcopy(b['MATH'])
    for tab in [ac,bc]:
        inf=tab.table.MathGlyphInfo
        for cov,values in [(inf.MathTopAccentAttachment.TopAccentCoverage.glyphs,inf.MathTopAccentAttachment.TopAccentAttachment),(inf.MathItalicsCorrectionInfo.Coverage.glyphs,inf.MathItalicsCorrectionInfo.ItalicsCorrection)]:
            for n,v in zip(cov,values):
                if n in names:v.Value=0
    assert ac.compile(a)==bc.compile(b)
    exact=[]
    for tag in a.keys():
        if tag in ['GlyphOrder','CFF ','name','head','hmtx','MATH','hhea']:continue
        assert a[tag].compile(a)==b[tag].compile(b),tag;exact.append(tag)
    for nid in [0,7,8,9,10,11,12,13,14]:
        assert [(r.platformID,r.platEncID,r.langID,r.toUnicode()) for r in a['name'].names if r.nameID==nid]==[(r.platformID,r.platEncID,r.langID,r.toUnicode()) for r in b['name'].names if r.nameID==nid]
    separations=[]
    for s,roles in inv.items():
        for level in range(3):
            for text in ['οθοβεβωοω','νυνυνυ','λογος','φυσικη','αβγδεζηθικλμνξοπρςστυφχψω','εϵθϑκϰφϕρϱπϖ','ψψψ']:
                ns=[roles[c]['glyph'] if level==0 else roles[c]['ssty'][level-1] for c in text]
                gaps=[b['hmtx'][left][0]+bounds(b,right)[0]-bounds(b,left)[2] for left,right in zip(ns,ns[1:])]
                assert min(gaps)>0,(s,level,text,gaps)
                separations.append({'style':s,'role':level,'string':text,'minimum_bbox_separation':min(gaps)})
            for c in CHARS:
                n=roles[c]['glyph'] if level==0 else roles[c]['ssty'][level-1]
                assert bounds(b,n)[0]>=0 and bounds(b,n)[2]<b['hmtx'][n][0],(n,bounds(b,n),b['hmtx'][n])
    pairs=[]
    for s in STYLES:
        for c,d in [('ε','ϵ'),('θ','ϑ'),('κ','ϰ'),('φ','ϕ'),('ρ','ϱ'),('π','ϖ'),('ς','σ'),('ν','υ')]:
            for level in range(3):
                ns=[inv[s][x]['glyph'] if level==0 else inv[s][x]['ssty'][level-1] for x in [c,d]]
                assert ns[0]!=ns[1] and recording(b,ns[0])!=recording(b,ns[1]);pairs.append({'style':s,'role':level,'pair':c+d,'distinct_glyphs':ns})
    return {'pass':True,'roles':384,'base_forms':32,'styles':STYLES,'inventory':inv,'changes':changes,
        'changed_glyphs':changed,'changed_metrics':metrics,'counter_integrity':topology,'raw_advance_collision_checks':separations,'semantic_distinctions':pairs,
        'source_notices_preserved':True,'checks':{'unrelated_outlines_and_hmtx_exact':True,'protected_glyphs':protected,'cmap_and_glyph_order_exact':True,
        'ssty_GSUB_binary_exact':True,'all_128_roles_have_two_explicit_ssty_alternates':True,'radical_variants_assemblies_and_unrelated_MATH_exact':True,
        'closed_counter_and_component_topology_preserved':True,'no_boolean_outline_offsets':True,'finite_bounds_and_boolean_fill_integrity':True,
        'nonnegative_lsb_and_no_horizontal_ink_overflow':True,'unchanged_tables':exact},
        'limitations':['No physical print trial or human reader study.','Area and topology checks are diagnostics, not a universal proof of curve quality or collision freedom.','No blanket offsets; nu/upsilon are original cubic silhouettes, others are deliberate nonlinear revisions of accepted native contours.','Accepted italic corrections preserved; revised top accents transferred by envelope center, requiring further optical scrutiny.']}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--pass',dest='passno',type=int,choices=[1,2],required=True);args=ap.parse_args()
    recipe=json.loads(RECIPE.read_text());source=ROOT/recipe['input'];assert sha(source)==recipe['input_sha256']
    assert sha(ROOT/'tools/arena_proofs.py')==recipe['proof_helper_sha256']
    private=RUN/'private';private.mkdir(parents=True,exist_ok=True)
    output=private/f'pass-{args.passno}.otf';assert not output.exists(),output
    inv,changes=design(source,output,recipe,args.passno);report=validate(source,output,changes)
    if args.passno==1:
        run=private/'pass-1-proofs'
    else:
        shutil.copy2(output,private/'final.otf');run=RUN
    (run/'private').mkdir(parents=True,exist_ok=True);(run/'packet').mkdir(parents=True,exist_ok=True)
    key,proofs=build_proofs(run,source,output,inv);report['proofs']=proofs
    (private/f'engineering-pass-{args.passno}.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    (private/f'pass-{args.passno}-recipe.json').write_text(json.dumps(recipe,ensure_ascii=False,indent=2)+'\n')
    if args.passno==2:
        (private/'engineering.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
        snapshots={}
        for src in [Path(__file__),ROOT/'tools/design_greek_campaign.py',ROOT/'tools/arena_proofs.py',RECIPE,ROOT/'design/greek-requirements.txt']:
            dst=private/(src.stem+'-at-build'+src.suffix);shutil.copy2(src,dst);snapshots[dst.name]=sha(dst)
        deps=command([sys.executable,'-m','pip','freeze']);(private/'dependencies-at-build.txt').write_text(deps)
        for n in ['SOURCE-NOTICES.txt','STIX-OFL.txt']:shutil.copy2(ROOT/'fonts/private'/n,private/n)
        passes=[{'pass':i,'font':str(private/f'pass-{i}.otf'),'sha256':sha(private/f'pass-{i}.otf'),'engineering':str(private/f'engineering-pass-{i}.json'),'recipe':str(private/f'pass-{i}-recipe.json')} for i in [1,2]]
        prov={'entrant':'typotheque','independent_inspired_study':True,'foundry_authorship':False,'input':str(source),'input_sha256':sha(source),
            'font':str(private/'final.otf'),'font_sha256':sha(private/'final.otf'),'design_passes':passes,'recipe':recipe,'build_snapshot':snapshots,
            'adopted_active_helpers':{'design_greek_campaign.py':sha(ROOT/'tools/design_greek_campaign.py'),'arena_proofs.py':sha(ROOT/'tools/arena_proofs.py')},
            'inspiration':{'png':str(ROOT/'runs/entropy-2026-10-29/typotheque/redesigned.png'),'sha256':sha(ROOT/'runs/entropy-2026-10-29/typotheque/redesigned.png'),'role':'creative counter/rhythm ideas only; not traced; incorrect Latin v rejected'},
            'engineering_pass':report['pass'],'identity_key':key,'changed_inventory_file':'engineering.json','notices':['SOURCE-NOTICES.txt','STIX-OFL.txt'],'model_or_image_calls':0}
        (private/'provenance.json').write_text(json.dumps(prov,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'pass':args.passno,'font':str(output),'sha256':sha(output),'engineering_pass':report['pass'],'proofs':str(run/'packet/manifest.json')}))

if __name__=='__main__':main()
