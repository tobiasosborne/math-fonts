#!/usr/bin/env python3
"""Hoefler-inspired editorial Greek, independently authored arena entrant.
Active helpers explicitly adopted for inventory, CFF installation and preservation.
No raster tracing, archived code, rejected Greek experiments, or foundry outlines.
"""
import argparse,copy,json,math,shutil,hashlib,subprocess
from pathlib import Path
import pathops
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
from design_greek_campaign import ROOT,CHARS,STYLES,sha,bounds,path,inventory,install,contours,recording,upper_ink_centroid
SOURCE=ROOT/'fonts/private/delivery/BaskervilleCompanionMath-Experimental-0.152.otf'
RUN=ROOT/'runs/arena-2026-10-29/entrants/hoefler'
EXPECTED='c00cb777cadca12c268e291d727b722568715fda3f58635f40066d918c04327c'
# Explicitly retained anatomy; these glyphs receive no contour or metric edit.
RETAIN='γηιμνοπρςστχψϑϰϕϱϖ∂'
# Nu is authored below, so remove it from retain.
RETAIN=RETAIN.replace('ν','')

def make(ops):
 p=pathops.Path();q=p.getPen()
 for op,args in ops:getattr(q,op)(*args)
 return p

def oval(x0,y0,x1,y1):
 k=.5522847498;cx=(x0+x1)/2;cy=(y0+y1)/2;rx=(x1-x0)/2;ry=(y1-y0)/2
 return make([('moveTo',[(cx,y1)]),('curveTo',[(cx+k*rx,y1),(x1,cy+k*ry),(x1,cy)]),('curveTo',[(x1,cy-k*ry),(cx+k*rx,y0),(cx,y0)]),('curveTo',[(cx-k*rx,y0),(x0,cy-k*ry),(x0,cy)]),('curveTo',[(x0,cy+k*ry),(cx-k*rx,y1),(cx,y1)]),('closePath',[])])

def authored(c,bold,level,passno):
 # Optical changes alter individual white/black boundaries, not outline offsets.
 b=1 if bold else 0;small=level
 if c=='θ':
  outer=oval(0,-18,440,712)
  # Bold deliberately gets a longer vertical white, with resilient top and foot.
  side=(87 if not b else 122)-small*2.2
  inner=oval(side,15+7*b,440-side,680-7*b)
  p=pathops.op(outer,inner,pathops.PathOp.DIFFERENCE)
  thick=(35 if not b else 61)+(2 if not b else 1)*small
  yy=352+(3 if passno==2 else 0)
  bar=make([('moveTo',[(50,yy-thick/2)]),('lineTo',[(390,yy+12-thick/2)]),('lineTo',[(390,yy+12+thick/2)]),('lineTo',[(50,yy+thick/2)]),('closePath',[])])
  return pathops.op(p,bar,pathops.PathOp.UNION)
 if c=='β':
  p=make([('moveTo',[(82,-260)]),('curveTo',[(86,-100),(77,290),(83,490)]),('curveTo',[(87,649),(169,739),(291,739)]),('curveTo',[(404,739),(468,666),(468,569)]),('curveTo',[(468,461),(410,392),(316,367)]),('curveTo',[(433,349),(501,275),(501,166)]),('curveTo',[(501,42),(407,-18),(285,-18)]),('curveTo',[(218,-18),(172,7),(155,43)]),('lineTo',[(163,-250)]),('curveTo',[(143,-263),(106,-267),(82,-260)]),('closePath',[])])
  edge=31*b-2*small;waist=396+(4 if passno==2 else 0)
  up=make([('moveTo',[(158+edge,waist)]),('curveTo',[(245,395),(379-edge,421),(382-edge,558)]),('curveTo',[(386-edge,646),(349,704),(287,704)]),('curveTo',[(200+edge,704),(160+edge,619),(158+edge,waist)]),('closePath',[])])
  lo=make([('moveTo',[(159+edge,87)]),('curveTo',[(197,43),(255,24),(306,28)]),('curveTo',[(391-edge,34),(419-edge,95),(418-edge,174)]),('curveTo',[(418-edge,281),(331,345),(160+edge,333)]),('curveTo',[(157+edge,240),(157+edge,164),(159+edge,87)]),('closePath',[])])
  if passno==2:
   # Final cubic white passage replaces the mechanical rectangle at the waist.
   white=make([('moveTo',[(159+edge,87)]),('curveTo',[(197,43),(255,24),(306,28)]),('curveTo',[(391-edge,34),(419-edge,95),(418-edge,174)]),('curveTo',[(418-edge,281),(331,345),(220+edge,333)]),('curveTo',[(193+edge,330),(184+edge,382),(211+edge,398)]),('curveTo',[(238+edge,414),(379-edge,448),(382-edge,558)]),('curveTo',[(386-edge,646),(349,704),(287,704)]),('curveTo',[(200+edge,704),(160+edge,619),(158+edge,400)]),('curveTo',[(157+edge,300),(157+edge,164),(159+edge,87)]),('closePath',[])])
   return pathops.op(p,white,pathops.PathOp.DIFFERENCE)
  # Native Greek beta has a continuous white passage at its left waist.
  corridor=make([('moveTo',[(158+edge,300)]),('lineTo',[(203+edge,300)]),('lineTo',[(203+edge,450)]),('lineTo',[(158+edge,450)]),('closePath',[])])
  white=pathops.op(pathops.op(up,lo,pathops.PathOp.UNION),corridor,pathops.PathOp.UNION)
  return pathops.op(p,white,pathops.PathOp.DIFFERENCE)
 if c=='ν':
  # Greek forward rising right arm, restrained wedge at foot, penlike entry.
  t=27*b;tip=9+small*1.6;return_x=(80-t*.6) if passno==2 else (111-t*.3);return_control=(70-t*.4) if passno==2 else (96-t*.4)
  return make([('moveTo',[(0,399)]),('curveTo',[(25,456),(54,479),(84,477)]),('curveTo',[(133,475),(152+t,405),(169+t,329)]),('lineTo',[(219+t,80+tip)]),('curveTo',[(292,181),(357,313),(366,424)]),('curveTo',[(363,447),(351,461),(351,468)]),('curveTo',[(379,480),(416,481),(436,469)]),('curveTo',[(437,353),(332,163),(220,13)]),('curveTo',[(211,0),(193,-15),(180,-18)]),('lineTo',[(return_x,295)]),('curveTo',[(return_control,358),(81,408),(51,416)]),('curveTo',[(35,420),(21,411),(10,393)]),('closePath',[])])
 return None

class LocalPen:
 """Smooth local landmark edits with analytic cubic tangent reconstruction."""
 def __init__(self,out,fn):self.out=out;self.fn=fn;self.cur=None
 def moveTo(self,p):self.cur=p;self.out.moveTo(self.fn(p))
 def lineTo(self,p):
  a=self.cur;self.curveTo(tuple(a[k]+(p[k]-a[k])/3 for k in [0,1]),tuple(a[k]+2*(p[k]-a[k])/3 for k in [0,1]),p)
 def curveTo(self,b,c,d):
  a=self.cur
  def ev(t):
   u=1-t;p=tuple(u**3*a[k]+3*u*u*t*b[k]+3*u*t*t*c[k]+t**3*d[k] for k in [0,1]);v=tuple(3*u*u*(b[k]-a[k])+6*u*t*(c[k]-b[k])+3*t*t*(d[k]-c[k]) for k in [0,1]);eps=.0001
   q=self.fn(p);v1=self.fn((p[0]+eps*v[0],p[1]+eps*v[1]));return q,tuple((v1[k]-q[k])/eps for k in [0,1])
  for i in range(8):
   p,v=ev(i/8);q,w=ev((i+1)/8);self.out.curveTo(tuple(p[k]+v[k]/24 for k in [0,1]),tuple(q[k]-w[k]/24 for k in [0,1]),q)
  self.cur=d
 def closePath(self):self.out.closePath()
 def endPath(self):self.out.endPath()

# x/y landmarks normalized to native bounding box. Each changes a particular
# crossing, bowl, shoulder, turn or terminal; no family-wide width/offset recipe.
LANDMARKS={
 'α':[(.60,.48,-.018,.024,.22),(.88,.11,.022,0,.17)],
 'δ':[(.62,.83,-.032,.012,.22),(.30,.29,-.020,0,.25)],
 'ε':[(.55,.52,.035,.018,.25),(.84,.85,.018,.020,.20)],
 'ζ':[(.38,.69,-.038,.015,.18),(.62,.22,.035,-.012,.22)],
 'κ':[(.55,.49,-.025,.017,.18),(.82,.12,.025,0,.17)],
 'λ':[(.39,.67,.025,0,.22),(.78,.13,.025,.018,.18)],
 'ξ':[(.38,.72,-.052,.024,.18),(.58,.52,.040,.018,.16),(.37,.33,-.042,-.010,.16),(.73,.12,.028,-.006,.18)],
 'υ':[(.40,.14,-.020,.008,.22),(.77,.54,.020,0,.25)],
 'φ':[(.24,.49,-.022,0,.25),(.76,.49,.022,0,.25)],
 'ω':[(.24,.26,-.026,0,.22),(.75,.26,.026,0,.22),(.49,.45,0,.040,.20)],
 'ϵ':[(.40,.50,-.028,.015,.22),(.79,.87,.025,0,.18)]}

def local_shape(f,n,c,level,passno,bold):
 box=bounds(f,n);x0,y0,x1,y1=box;w=x1-x0;h=y1-y0
 params=LANDMARKS[c]
 def fn(p):
  x=(p[0]-x0)/w;y=(p[1]-y0)/h;dx=dy=0
  for xx,yy,ax,ay,r in params:
   g=math.exp(-((x-xx)**2+(y-yy)**2)/(2*r*r));dx+=ax*g;dy+=ay*g
  # Small scripts open critical arms locally; the modulation is purpose-specific.
  fac=1+.12*level
  if c=='ξ' and passno==2:fac*=.83 # first pass turns were too fussy at working size
  if c=='ω' and bold and passno==2:fac*=1.12
  return p[0]+w*dx*fac,p[1]+h*dy*fac
 p=pathops.Path();f.getGlyphSet()[n].draw(LocalPen(p.getPen(),fn));return p

def fit(p,box,style):
 if style in ['italic','bolditalic']:p=p.transform(1,0,.20,1,0,0)
 b=p.bounds;sx=(box[2]-box[0])/(b[2]-b[0]);sy=(box[3]-box[1])/(b[3]-b[1]);return p.transform(sx,0,0,sy,box[0]-sx*b[0],box[1]-sy*b[1])

def metadata(f,passno):
 family='Baskerville Math Arena Hoefler Inspired';ps='BaskervilleMathArena-HoeflerInspired'
 vals={1:family,2:'Regular',3:f'20261029:{ps}:1.00{passno}',4:family+' Regular',5:f'Version 1.00{passno}; PRIVATE independent AI exploration; not foundry authored',6:ps,16:family,17:'Regular'}
 for r in f['name'].names:
  if r.nameID in vals:r.string=vals[r.nameID].encode(r.getEncoding())
 top=f['CFF '].cff.topDictIndex[0];f['CFF '].cff.fontNames=[ps];top.FamilyName=family;top.FullName=family+' Regular';top.version=f'1.00{passno}';f['head'].fontRevision=1+passno/1000

def build(passno):
 assert sha(SOURCE)==EXPECTED
 f=TTFont(SOURCE,recalcTimestamp=False);inv=inventory(f);changes=[];info=f['MATH'].table.MathGlyphInfo
 accents=dict(zip(info.MathTopAccentAttachment.TopAccentCoverage.glyphs,info.MathTopAccentAttachment.TopAccentAttachment));ics=dict(zip(info.MathItalicsCorrectionInfo.Coverage.glyphs,info.MathItalicsCorrectionInfo.ItalicsCorrection))
 for style in STYLES:
  for c,v in inv[style].items():
   for level,n in enumerate([v['glyph']]+v['ssty']):
    oldbox=bounds(f,n);aw,lsb=f['hmtx'][n];oldac=accents[n].Value if n in accents else None;oldic=ics[n].Value if n in ics else None;old=path(f,n);action='native anatomy and metrics retained';p=None
    if c in 'βθν':p=fit(authored(c,'bold' in style,level,passno),oldbox,style);action='authored cubic outline with role-specific white/black boundaries'
    elif c in LANDMARKS:p=local_shape(f,n,c,level,passno,'bold' in style);action='localized landmark curve editing: '+{'α':'crossing and exit','δ':'upper turn and bowl','ε':'waist and upper terminal','ζ':'upper turn and lower swing','κ':'junction and lower arm','λ':'rise and foot','ξ':'three articulated turns and terminal','υ':'rounded foot and right shoulder','φ':'opposed counterwalls','ω':'balanced lobes and raised centre','ϵ':'lunate opening and terminal'}[c]
    delta=0
    if p is not None:
     # Small optical spacing is differentiated by vulnerable anatomy.
     delta=(3+level*2) if c in 'βθξφω' else (2+level) if c in 'νυλ' else 0
     install(f,n,p,aw+delta)
     if n in accents:accents[n].Value+=round(upper_ink_centroid(p,oldbox[3])-upper_ink_centroid(old,oldbox[3]))
     if n in ics:ics[n].Value=max(0,oldic-delta)
    changes.append({'glyph':n,'char':c,'style':style,'role':['text','script','scriptscript'][level],'outline_action':action,'advance_before':aw,'advance_after':f['hmtx'][n][0],'advance_delta':delta,'lsb_before':lsb,'lsb_after':f['hmtx'][n][1],'bounds_before':oldbox,'bounds_after':bounds(f,n),'top_accent_before':oldac,'top_accent_after':accents[n].Value if n in accents else None,'italic_correction_before':oldic,'italic_correction_after':ics[n].Value if n in ics else None})
 metadata(f,passno);out=RUN/'private'/f'pass-{passno}.otf';out.parent.mkdir(parents=True,exist_ok=True);f.save(out);(RUN/'private'/f'pass-{passno}-changes.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2)+'\n');return out,changes

def validate(out,changes):
 a,b=TTFont(SOURCE),TTFont(out);names={r['glyph'] for r in changes if r['outline_action']!='native anatomy and metrics retained'};checks=[];actual=[]
 assert a.getGlyphOrder()==b.getGlyphOrder() and a.getBestCmap()==b.getBestCmap()
 assert a['GSUB'].compile(a)==b['GSUB'].compile(b)
 for n in b.getGlyphOrder():
  ra,rb=recording(a,n),recording(b,n)
  if n not in names:assert ra==rb and a['hmtx'][n]==b['hmtx'][n],n
  else:
   assert ra!=rb,n;actual.append(n);pa,pb=path(a,n),path(b,n);ca,cb=contours(pa),contours(pb);ha=[c.area for d,c in ca if d%2];hb=[c.area for d,c in cb if d%2]
   assert len(ha)==len(hb),(n,ha,hb)
   assert all(v>1 for v in hb)
   ratio=pb.area/pa.area;assert .58<ratio<1.55,(n,ratio)
   simple=pathops.simplify(pb);assert abs(simple.area-pb.area)<max(1,pb.area*.0001),(n,pb.area,simple.area)
   checks.append({'glyph':n,'closed_counters':len(hb),'min_counter_area':min(hb) if hb else None,'fill_area_ratio':ratio,'finite_bounds':all(math.isfinite(x) for x in pb.bounds),'boolean_fill_equal':True})
 ac,bc=copy.deepcopy(a['MATH']),copy.deepcopy(b['MATH'])
 for tab in [ac,bc]:
  inf=tab.table.MathGlyphInfo
  for cov,vals in [(inf.MathTopAccentAttachment.TopAccentCoverage.glyphs,inf.MathTopAccentAttachment.TopAccentAttachment),(inf.MathItalicsCorrectionInfo.Coverage.glyphs,inf.MathItalicsCorrectionInfo.ItalicsCorrection)]:
   for n,v in zip(cov,vals):
    if n in names:v.Value=0
 assert ac.compile(a)==bc.compile(b)
 for tag in a.keys():
  if tag in ['GlyphOrder','CFF ','name','head','hmtx','MATH','hhea']:continue
  assert a[tag].compile(a)==b[tag].compile(b),tag
 for nid in [0,7,8,9,10,11,12,13,14]:assert [(r.platformID,r.platEncID,r.langID,r.toUnicode()) for r in a['name'].names if r.nameID==nid]==[(r.platformID,r.platEncID,r.langID,r.toUnicode()) for r in b['name'].names if r.nameID==nid]
 gaps=[];inv=inventory(b)
 for s,roles in inv.items():
  for level in range(3):
   for text in ['οθοβεβωοω','νυνυνυ','λογος','φυσικη',CHARS]:
    ns=[roles[c]['glyph'] if level==0 else roles[c]['ssty'][level-1] for c in text];gg=[b['hmtx'][l][0]+bounds(b,r)[0]-bounds(b,l)[2] for l,r in zip(ns,ns[1:])];assert min(gg)>0,(s,level,text,min(gg));gaps.append({'style':s,'role':level,'string':text,'minimum_bbox_separation':min(gg)})
 return {'pass':True,'roles':384,'base_forms':32,'styles':STYLES,'inventory':inv,'changes':changes,'changed_glyphs':actual,'changed_metrics':[r['glyph'] for r in changes if r['advance_delta'] or r['lsb_before']!=r['lsb_after']],'retained_forms':[c for c in CHARS if c not in LANDMARKS and c not in 'βθν'],'counter_integrity':checks,'raw_advance_collision_checks':gaps,'checks':{'unrelated_outlines_and_hmtx_exact':True,'cmap_and_glyph_order_exact':True,'ssty_GSUB_binary_exact':True,'all_128_roles_have_two_explicit_ssty_alternates':True,'radical_variants_assemblies_and_unrelated_MATH_exact':True,'closed_counter_topology_preserved':True,'finite_bounds_and_boolean_fill_integrity':True,'source_notices_preserved':True},'limitations':['No physical print or human reader study.','Authored glyph fill guard is broad; actual images and topology inspection remain necessary.','Raw-advance corpus and engine proofs are bounded, not an exhaustive math collision guarantee.','Native supporting forms and variants are retained deliberately; this is a Greek family revision, not a newly authored entire math family.']}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--pass',dest='passno',type=int,choices=[1,2]);ap.add_argument('--package',action='store_true');args=ap.parse_args()
 if args.passno:
  out,changes=build(args.passno);report=validate(out,changes);(RUN/'private'/f'pass-{args.passno}-engineering.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(out)
 if args.package:package()

def deformation_audit():
 rows=[]
 for c,params in LANDMARKS.items():
  fac=1.24*(.83 if c=='ξ' else 1.12 if c=='ω' else 1)
  determinants=[]
  for ix in range(31):
   for iy in range(31):
    x=ix/30;y=iy/30;jxx=jyy=1.;jxy=jyx=0.
    for xx,yy,ax,ay,r in params:
     g=math.exp(-((x-xx)**2+(y-yy)**2)/(2*r*r));gx=-(x-xx)*g/(r*r);gy=-(y-yy)*g/(r*r)
     jxx+=fac*ax*gx;jxy+=fac*ax*gy;jyx+=fac*ay*gx;jyy+=fac*ay*gy
    determinants.append(jxx*jyy-jxy*jyx)
  assert min(determinants)>.5,(c,min(determinants))
  rows.append({'character':c,'sampled_normalized_domain':'31 × 31 grid over native ink bounding box','maximum_optical_modulation_factor':fac,'minimum_jacobian_determinant':min(determinants),'meaning':'Smooth local deformation has no sampled fold; not a universal curve-quality certificate.'})
 return rows

def package():
 from arena_proofs import build_proofs
 private=RUN/'private';final=private/'final.otf';shutil.copy2(private/'pass-2.otf',final);report=json.loads((private/'pass-2-engineering.json').read_text());inv=inventory(TTFont(final));(RUN/'packet').mkdir(exist_ok=True)
 key,pr=build_proofs(RUN,SOURCE,final,inv);report['local_curve_deformation_audit']=deformation_audit();report['proofs']=pr;report['pass']=report['pass'] and pr['pass'];(private/'engineering.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 snaps={}
 for src in [Path(__file__),ROOT/'tools/arena_proofs.py',ROOT/'tools/greek_proofs.py',ROOT/'tools/design_greek_campaign.py',ROOT/'design/arena-hoefler.json',ROOT/'design/greek-requirements.txt']:
  dst=private/(src.stem+'-at-build'+src.suffix);shutil.copy2(src,dst);snaps[dst.name]=sha(dst)
 for n in ['SOURCE-NOTICES.txt','STIX-OFL.txt']:shutil.copy2(ROOT/'fonts/private'/n,private/n)
 prov={'key':key,'input':str(SOURCE),'input_sha256':sha(SOURCE),'candidate':str(final),'candidate_sha256':sha(final),'pass_1_sha256':sha(private/'pass-1.otf'),'pass_2_sha256':sha(private/'pass-2.otf'),'recipe':json.loads((ROOT/'design/arena-hoefler.json').read_text()),'changed_inventory':report['changes'],'build_snapshot':snaps,'engineering_pass':report['pass'],'concept_image_sha256':sha(ROOT/'runs/entropy-2026-10-29/hoefler/redesigned.png'),'authorship':'Independent AI Greek revision inspired by a generated editorial concept; not authored or endorsed by Hoefler & Co.; no foundry outlines used.'}
 (private/'provenance.json').write_text(json.dumps(prov,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'font':str(final),'sha256':sha(final),'pass':report['pass']}))
if __name__=='__main__':main()
