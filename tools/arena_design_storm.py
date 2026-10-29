#!/usr/bin/env python3
"""Independent Storm-inspired vector entrant; PNG gesture inspiration, no tracing.
Explicitly adopts active inventory/CFF/preservation utilities, never archive code.
"""
import copy,json,math,shutil,sys
from pathlib import Path
import pathops
from fontTools.ttLib import TTFont
from fontTools.pens.t2CharStringPen import T2CharStringPen
from design_greek_campaign import ROOT,CHARS,STYLES,sha,command,inventory,bounds,recording,path,contours,install,WarpPen
from arena_proofs import build_proofs
RUN=ROOT/'runs/arena-2026-10-29/entrants/storm'
SOURCE=ROOT/'fonts/private/delivery/BaskervilleCompanionMath-Experimental-0.152.otf'

def ellipse(x0,y0,x1,y1):
 p=pathops.Path();q=p.getPen();cx=(x0+x1)/2;cy=(y0+y1)/2;rx=(x1-x0)/2;ry=(y1-y0)/2;k=.5522847498
 q.moveTo((cx,y1));q.curveTo((cx+k*rx,y1),(x1,cy+k*ry),(x1,cy));q.curveTo((x1,cy-k*ry),(cx+k*rx,y0),(cx,y0));q.curveTo((cx-k*rx,y0),(x0,cy-k*ry),(x0,cy));q.curveTo((x0,cy+k*ry),(cx-k*rx,y1),(cx,y1));q.closePath();return p

def oval(theta,bold,level,refine):
 w,h=430,(740 if theta else 476);stem=((125 if bold else 83) if refine else (82 if bold else 53))+level*3;hair=((55 if bold else 35) if refine else (48 if bold else 28))+level*1.8
 # Wider lower counter, narrower upper shoulder: deliberate oblique stress.
 outer=ellipse(0,-18,w,h);inner=pathops.Path();p=inner.getPen();p.moveTo((w*.5,h-hair));p.curveTo((w-stem+10,h-hair),(w-stem,420 if theta else 310),(w-stem,215 if theta else 190));p.curveTo((w-stem,-18+hair),(stem-6,-18+hair),(stem-6,185 if theta else 160));p.curveTo((stem-6,390 if theta else 300),(stem-16,h-hair),(w*.5,h-hair));p.closePath()
 out=pathops.op(outer,inner,pathops.PathOp.DIFFERENCE)
 if theta:
  bar=pathops.Path();p=bar.getPen();yy=h*.49;th=((52 if bold else 36) if refine else (43 if bold else 28))+level*1.5
  p.moveTo((20,yy-th/2));p.curveTo((130,yy-th*.65),(310,yy-th*.3),(w-20,yy));p.lineTo((w-20,yy+th/2));p.curveTo((310,yy+th*.3),(130,yy+th*.65),(20,yy+th/2));p.closePath();out=pathops.op(out,bar,pathops.PathOp.UNION)
 return out

def beta(bold,level,refine):
 p=pathops.Path();q=p.getPen();bw=(18 if bold else 0)+level*3
 q.moveTo((58,-260));q.curveTo((73,-100),(80,120),(91,290));q.curveTo((105,535),(135,739),(292,739));q.curveTo((443,739),(466,532),(342,411));q.curveTo((518,367),(513,103),(359,9));q.curveTo((260,-48),(172,-4),(145,70));q.lineTo((123+bw,-260));q.closePath()
 # The upper bowl is compact and rising; lower bowl opens with the descending stem.
 for points in [((176+bw,413),(190+bw,620),(216,686-bw),(291,686-bw),(383-bw,686-bw),(390-bw,497),(290,435),(245,415),(210,408),(176+bw,413)),((162+bw,321),(208,371),(310,382-bw),(366-bw,309),(427-bw,227),(362-bw,58+bw),(270,58+bw),(201+bw,58+bw),(153+bw,128),(162+bw,321))]:
  h=pathops.Path();r=h.getPen();r.moveTo(points[0]);r.curveTo(*points[1:4]);r.curveTo(*points[4:7]);r.curveTo(*points[7:10]);r.closePath();p=pathops.op(p,h,pathops.PathOp.DIFFERENCE)
 return p

def omega(bold,level,refine):
 p=pathops.Path();q=p.getPen();bw=(24 if bold else 0)+level*2
 q.moveTo((150,476));q.curveTo((70,430),(10,260),(10,150));q.curveTo((10,20),(80,-18),(165,-18));q.curveTo((250,-18),(300,35),(335,100));q.curveTo((355,20),(400,-18),(485,-18));q.curveTo((610,-18),(680,140),(680,270));q.curveTo((680,390),(650,476),(580,476));q.curveTo((540,476),(520,440),(550,425));q.curveTo((600-bw,400),(610-bw,350),(605-bw,290));q.curveTo((590-bw,150),(530,55+bw),(470,55+bw));q.curveTo((425+bw,55+bw),(410+bw,140),(445+bw,290));q.curveTo((460+bw,360),(435,405),(400,405));q.curveTo((365-bw,405),(340-bw,355),(355-bw,300));q.curveTo((365-bw,230),(350-bw,115),(285,65+bw));q.curveTo((210,10+bw),(115+bw,75+bw),(115+bw,185));q.curveTo((115+bw,300),(160,370),(195,415));q.curveTo((220,445),(195,476),(150,476));q.closePath();return p

def nu(bold,level,refine):
 p=pathops.Path();q=p.getPen();bw=(18 if bold else 0)+level*2
 q.moveTo((45,365));q.curveTo((70,405),(95,410),(110,355));q.curveTo((150,230),(180,70),(235,-18));q.curveTo((245,-25),(265,-20),(275,0));q.curveTo((340,105),(435,320),(445,430));q.curveTo((450,475),(430,482),(405,477));q.curveTo((365,470),(350,445),(367,428));q.curveTo((395-bw,394),(362-bw,235),(275,72+bw));q.curveTo((230+bw,200),(210+bw,350),(185+bw,425));q.curveTo((168+bw,480),(100,500),(65,450));q.curveTo((40,420),(25,380),(45,365));q.closePath();return p

def phi_closed(bold,level,refine):
 ring=oval(False,bold,level,refine).transform(1,0,0,1,0,0)
 p=pathops.Path();q=p.getPen();cx=215;th=(91 if bold else 57)+level*3
 q.moveTo((cx-th/2,-280));q.curveTo((cx-th*.4,-40),(cx-th*.4,430),(cx-th/2,712));q.lineTo((cx+th/2,712));q.curveTo((cx+th*.3,430),(cx+th*.3,-40),(cx+th/2,-280));q.closePath();return pathops.op(ring,p,pathops.PathOp.UNION)

class NativeGesture(WarpPen):
 def __init__(self,out,xh,char,style,level,refine):self.out=out;self.cur=None;self.xh=xh;self.char=char;self.italic=style in ['italic','bolditalic'];self.level=level;self.refine=refine
 def displacement(self,y):
  t=y/self.xh
  # Articulate compressed curls/turns and open epsilon's exterior aperture.
  amount={'ε':-13,'ϵ':-8,'ξ':14,'ζ':10,'κ':9,'ϰ':9,'υ':-10,'φ':8,'α':5,'ϖ':8}.get(self.char,3)
  return amount*math.sin(math.pi*t)+(4 if self.italic else 0)*math.sin(2*math.pi*t)
 def xy(self,p):return(p[0]+self.displacement(p[1]),p[1])
 def deriv(self,p,d):
  e=.001;dv=(self.displacement(p[1]+e)-self.displacement(p[1]-e))/(2*e);return(d[0]+dv*d[1],d[1])

def name_font(f,passno):
 family='Baskerville Math Arena Storm Inspired';ps=f'BaskervilleMathArenaStorm-P{passno}'
 vals={1:family,2:'Regular',3:f'20261029:{ps}:0.17{passno}',4:family+' Regular',5:f'Version 0.17{passno}; PRIVATE IMAGE-INSPIRED DESIGN; not foundry-authored',6:ps,16:family,17:'Regular'}
 for r in f['name'].names:
  if r.nameID in vals:r.string=vals[r.nameID].encode(r.getEncoding())
 t=f['CFF '].cff.topDictIndex[0];f['CFF '].cff.fontNames=[ps];t.FamilyName=family;t.FullName=family;t.version=f'0.17{passno}';f['head'].fontRevision=(170+passno)/1000

def build(passno):
 f=TTFont(SOURCE,recalcTimestamp=False);inv=inventory(f);changes=[];info=f['MATH'].table.MathGlyphInfo;acc=dict(zip(info.MathTopAccentAttachment.TopAccentCoverage.glyphs,info.MathTopAccentAttachment.TopAccentAttachment));ic=dict(zip(info.MathItalicsCorrectionInfo.Coverage.glyphs,info.MathItalicsCorrectionInfo.ItalicsCorrection));refine=passno==2
 constructors={'β':beta,'θ':lambda b,l,r:oval(True,b,l,r),'ο':lambda b,l,r:oval(False,b,l,r),'ω':omega,'ν':nu,'ϕ':phi_closed}
 for style,roles in inv.items():
  bold='bold' in style;italic=style in ['italic','bolditalic']
  for c,v in roles.items():
   basebox=v['bounds']
   for level,n in enumerate([v['glyph']]+v['ssty']):
    oldbox=bounds(f,n);oldadv,oldlsb=f['hmtx'][n];oldanchor=acc[n].Value;oldic=ic[n].Value
    if c in constructors:
     p=constructors[c](bold,level,refine)
     if italic:p=p.transform(1,0,.14,1,0,0)
     mode='new calligraphic contour construction'
    else:
     p=pathops.Path();f.getGlyphSet()[n].draw(NativeGesture(p.getPen(),basebox[3],c,style,level,refine));mode='native Greek contour with character-specific gesture/white-space adaptation'
     # Inner contours gain lateral white in closed bold counters, with nesting
     # preserved. No blanket offset unions or erosion of open native arms.
     if bold:
      out=pathops.Path()
      for dep,cont in contours(p):
       if dep%2:
        b=cont.bounds;cx=(b[0]+b[2])/2;fac=1.07 if refine else 1.04;cont=cont.transform(fac,0,0,1,cx*(1-fac),0)
       out=pathops.op(out,cont,pathops.PathOp.DIFFERENCE if dep%2 else pathops.PathOp.UNION)
      p=out
    b=p.bounds
    widthfactor=1.065 if c in 'βθοφϕω' else 1.035 if c in 'γζηλχψ∂' else 1.05
    if refine and c=='ω':widthfactor=1.035
    if refine and c=='ν':widthfactor=1.075
    target=(basebox[2]-basebox[0])*widthfactor*(1+.035*level) if c in constructors else (oldbox[2]-oldbox[0])*widthfactor
    sx=target/(b[2]-b[0]);sy=(oldbox[3]-oldbox[1])/(b[3]-b[1]);left=oldbox[0]
    p=p.transform(sx,0,0,sy,left-sx*b[0],oldbox[1]-sy*b[1])
    right=oldadv-oldbox[2]+(7 if c in 'γζηλχψ' else 3);advance=round(p.bounds[2]+right)
    install(f,n,p,advance)
    delta=round((bounds(f,n)[0]+bounds(f,n)[2]-oldbox[0]-oldbox[2])/2);acc[n].Value+=delta;ic[n].Value=max(0,oldic-3)
    changes.append({'glyph':n,'char':c,'style':style,'role':level,'construction':mode,'old_advance':oldadv,'new_advance':advance,'advance_delta':advance-oldadv,'bounds_before':oldbox,'bounds_after':bounds(f,n),'anchor_delta':delta,'italic_correction_delta':ic[n].Value-oldic})
 name_font(f,passno);out=RUN/'private'/f'pass-{passno}.otf';f.save(out);return out,changes

def verify(output,changes):
 a,b=TTFont(SOURCE),TTFont(output);changed={x['glyph'] for x in changes};assert a.getBestCmap()==b.getBestCmap() and a.getGlyphOrder()==b.getGlyphOrder();checks=[]
 for n in b.getGlyphOrder():
  if n not in changed:assert recording(a,n)==recording(b,n) and a['hmtx'][n]==b['hmtx'][n],n
  else:
   old,new=path(a,n),path(b,n);ca,cb=contours(old),contours(new);ha=sum(d%2 for d,c in ca);hb=sum(d%2 for d,c in cb)
   assert ha==hb or (next(x['char'] for x in changes if x['glyph']==n)=='β' and hb==2),(n,ha,hb)
   assert new.area>100 and all(math.isfinite(v) for v in new.bounds),n
   simplified=pathops.simplify(new);assert abs(simplified.area-new.area)<max(1,new.area*.0001),n
   ratio=new.area/old.area
   constructor=next(x['construction'] for x in changes if x['glyph']==n)
   assert (.50<ratio<1.65 if constructor.startswith('new') else .85<ratio<1.25),(n,ratio)
   checks.append({'glyph':n,'closed_counters_before':ha,'closed_counters':hb,'intentional_topology_change':ha!=hb,'area_ratio':new.area/old.area})
 for tag in a.keys():
  if tag not in ['GlyphOrder','CFF ','name','head','hmtx','hhea','MATH']:assert a[tag].compile(a)==b[tag].compile(b),tag
 aa,bb=copy.deepcopy(a['MATH']),copy.deepcopy(b['MATH'])
 for tab in [aa,bb]:
  i=tab.table.MathGlyphInfo
  for cov,vals in [(i.MathTopAccentAttachment.TopAccentCoverage.glyphs,i.MathTopAccentAttachment.TopAccentAttachment),(i.MathItalicsCorrectionInfo.Coverage.glyphs,i.MathItalicsCorrectionInfo.ItalicsCorrection)]:
   for n,v in zip(cov,vals):
    if n in changed:v.Value=0
 assert aa.compile(a)==bb.compile(b)
 boxes={n:bounds(b,n) for n in changed};gaps=[];iv=inventory(b)
 for style,roles in iv.items():
  for level in range(3):
   for text in ['οθοβεβωοω','νυνυνυ','λογος','φυσικη','αβγδεζηθικλμνξοπρςστυφχψω']:
    ns=[roles[c]['glyph'] if not level else roles[c]['ssty'][level-1] for c in text]
    gg=[b['hmtx'][l][0]+boxes[r][0]-boxes[l][2] for l,r in zip(ns,ns[1:])];assert min(gg)>0,(style,level,text,gg);gaps.append({'style':style,'role':level,'string':text,'min_bbox_gap':min(gg)})
 return {'pass':True,'raw_advance_collision_checks':gaps,'changed_glyphs':sorted(changed),'changes':changes,'inventory':inventory(b),'counter_checks':checks,'checks':{'unrelated_outlines_and_metrics_exact':True,'Latin_and_radicals_exact':True,'unrelated_MATH_exact':True,'GSUB_GPOS_cmap_exact':True,'counter_topology_verified_with_declared_beta_two_counter_construction':True,'Boolean_fill_integrity':True},'limitations':['Screen proofs only; no physical print or native-reader study.','New contours need further optical and curve refinement; engineering does not imply editorial perfection.']}

def main():
 passno=int(sys.argv[1]);assert passno in [1,2];(RUN/'private').mkdir(parents=True,exist_ok=True)
 output,changes=build(passno);report=verify(output,changes);work=RUN/'private'/f'pass-{passno}-proof';(work/'private').mkdir(parents=True);(work/'packet').mkdir()
 key,pr=build_proofs(work,SOURCE,output,inventory(TTFont(SOURCE)));report['proofs']=pr
 (RUN/'private'/f'engineering-pass-{passno}.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 if passno==2:
  shutil.copy2(output,RUN/'private/final.otf');shutil.copytree(work/'packet',RUN/'packet');shutil.copy2(work/'private/offline-proof.pdf',RUN/'private/offline-proof.pdf');shutil.copy2(RUN/'private/engineering-pass-2.json',RUN/'private/engineering.json')
  snapshots={}
  for src in [Path(__file__),ROOT/'tools/arena_proofs.py',ROOT/'tools/design_greek_campaign.py',ROOT/'design/arena-storm.json',ROOT/'design/greek-requirements.txt']:
   dst=RUN/'private'/('snapshot-'+src.name);shutil.copy2(src,dst);snapshots[dst.name]=sha(dst)
  for name in ['SOURCE-NOTICES.txt','STIX-OFL.txt']:shutil.copy2(ROOT/'fonts/private'/name,RUN/'private'/name)
  prov={'key':key,'input':str(SOURCE),'input_sha256':sha(SOURCE),'candidate':str(RUN/'private/final.otf'),'candidate_sha256':sha(RUN/'private/final.otf'),'recipe':json.loads((ROOT/'design/arena-storm.json').read_text()),'pass_records':[{ 'pass':i,'path':str(RUN/'private'/f'pass-{i}.otf'),'sha256':sha(RUN/'private'/f'pass-{i}.otf')} for i in [1,2]],'changed_inventory':changes,'pass1_builder_sha256':sha(RUN/'private/pass-1-builder.py'),'pass1_recipe_sha256':sha(RUN/'private/pass-1-recipe.json'),'adopted_helpers':snapshots,'engineering_pass':True}
  (RUN/'private/provenance.json').write_text(json.dumps(prov,ensure_ascii=False,indent=2)+'\n')
 print(output)
if __name__=='__main__':main()
