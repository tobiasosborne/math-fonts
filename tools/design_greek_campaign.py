#!/usr/bin/env python3
"""Active Greek design pipeline: native-anatomy fitting and optical refinement.
No archived code is imported. Each build records its exact sources privately.
"""
import argparse, copy, hashlib, json, math, shutil, subprocess, unicodedata
from pathlib import Path
import pathops
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.qu2cuPen import Qu2CuPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.roundingPen import RoundingPen
ROOT=Path(__file__).resolve().parents[1]
CHARS='αβγδεζηθικλμνξοπρςστυφχψωϵϑϰϕϱϖ∂'
STYLES=['upright','italic','bold','bolditalic']
TEXT_NAMES=['Baskerville10Pro.otf','Baskerville10Pro-Italic.otf','Baskerville10Pro-Bold.otf','Baskerville10Pro-BoldItalic.otf']
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def command(args,cwd=None):
 p=subprocess.run(args,cwd=cwd,text=True,capture_output=True)
 if p.returncode: raise RuntimeError(p.stdout[-4000:]+p.stderr[-2000:])
 return p.stdout

def bounds(font,n):
 p=BoundsPen(font.getGlyphSet());font.getGlyphSet()[n].draw(p);return p.bounds

def recording(font,n):
 p=RecordingPen();font.getGlyphSet()[n].draw(p);return p.value

def path(font,n):
 p=pathops.Path();font.getGlyphSet()[n].draw(p.getPen());return p

def inventory(font):
 cmap=font.getBestCmap();out={s:{} for s in STYLES}
 for c in CHARS: out['upright'][c]={'cp':ord(c),'glyph':cmap[ord(c)]}
 for cp,n in cmap.items():
  d=unicodedata.decomposition(chr(cp)).split()
  if len(d)!=2 or d[0]!='<font>' or chr(int(d[1],16)) not in CHARS: continue
  desc=unicodedata.name(chr(cp),'')
  s=next((s for prefix,s in [('MATHEMATICAL BOLD ITALIC','bolditalic'),('MATHEMATICAL ITALIC','italic'),('MATHEMATICAL BOLD','bold')] if desc.startswith(prefix)),None)
  if s: out[s][chr(int(d[1],16))]={'cp':cp,'glyph':n}
 alternates={}
 for f in font['GSUB'].table.FeatureList.FeatureRecord:
  if f.FeatureTag=='ssty':
   for li in f.Feature.LookupListIndex:
    for sub in font['GSUB'].table.LookupList.Lookup[li].SubTable:
     alternates.update(getattr(sub,'alternates',{}))
 for s in STYLES:
  assert len(out[s])==32,(s,len(out[s]))
  for c,v in out[s].items():
   v.update(advance=font['hmtx'][v['glyph']][0],bounds=bounds(font,v['glyph']),ssty=alternates[v['glyph']])
   assert len(v['ssty'])==2
 return out

def interior(c):
 # Find an interior point just inside a contour edge. This avoids bbox centres
 # outside crescents and does not assume a universal contour orientation.
 pen=RecordingPen();c.draw(pen);pts=[];cur=None
 for op,args in pen.value:
  if op in ['moveTo','lineTo']:cur=args[0];pts.append(cur)
  elif op=='curveTo':
   a=cur;b,d,e=args
   for i in range(1,17):
    t=i/16;u=1-t;pts.append((u**3*a[0]+3*u*u*t*b[0]+3*u*t*t*d[0]+t**3*e[0],u**3*a[1]+3*u*u*t*b[1]+3*u*t*t*d[1]+t**3*e[1]))
   cur=e
  elif op=='qCurveTo':
   pts.extend(args);cur=args[-1]
 for a,b in zip(pts,pts[1:]+pts[:1]):
  dx,dy=b[0]-a[0],b[1]-a[1];le=math.hypot(dx,dy)
  if le<.01:continue
  for sign in [-1,1]:
   pt=((a[0]+b[0])/2-sign*dy/le*.03,(a[1]+b[1])/2+sign*dx/le*.03)
   if c.contains(pt):return pt
 raise ValueError('Cannot locate contour interior')

def contours(p):
 cc=list(p.contours);out=[]
 for c in cc:
  if c.area<.01: continue
  pt=interior(c)
  depth=sum(1 for other in cc if other is not c and other.area>c.area and other.contains(pt))
  out.append((depth,c))
 return sorted(out,key=lambda dc:(dc[0],-dc[1].area))

def grow(p,r):
 if not r:return p
 stroke=pathops.Path();stroke.addPath(p);stroke.stroke(r*2,pathops.LineCap.ROUND_CAP,pathops.LineJoin.ROUND_JOIN,4);stroke.convertConicsToQuads(.01)
 return pathops.op(p,stroke,pathops.PathOp.UNION)

def optical(p,ink,counter):
 # Preserve nesting, including black islands inside counters. White contours
 # are enlarged independently, not mistaken for open exterior apertures.
 out=pathops.Path()
 for depth,c in contours(p):
  q=grow(c,counter if depth%2 else ink)
  out=pathops.op(out,q,pathops.PathOp.DIFFERENCE if depth%2 else pathops.PathOp.UNION)
 return out

class WarpPen:
 """Cubic Hermite reconstruction of a smooth Greek-specific x displacement."""
 def __init__(self,out,amount,xh):self.out=out;self.amount=amount;self.xh=xh;self.cur=None
 def xy(self,p):return (p[0]+self.amount*max(0,1-p[1]/self.xh)**2,p[1])
 def deriv(self,p,d):return (d[0]-(2*self.amount/self.xh)*max(0,1-p[1]/self.xh)*d[1],d[1])
 def moveTo(self,p):self.cur=p;self.out.moveTo(self.xy(p))
 def lineTo(self,p):
  a=self.cur;self.curveTo(tuple(a[k]+(p[k]-a[k])/3 for k in [0,1]),tuple(a[k]+2*(p[k]-a[k])/3 for k in [0,1]),p)
 def curveTo(self,b,c,d):
  a=self.cur
  def ev(t):
   u=1-t;p=tuple(u**3*a[k]+3*u*u*t*b[k]+3*u*t*t*c[k]+t**3*d[k] for k in [0,1]);dv=tuple(3*u*u*(b[k]-a[k])+6*u*t*(c[k]-b[k])+3*t*t*(d[k]-c[k]) for k in [0,1]);return self.xy(p),self.deriv(p,dv)
  for i in range(6):
   p,v=ev(i/6);q,w=ev((i+1)/6)
   self.out.curveTo(tuple(p[k]+v[k]/18 for k in [0,1]),tuple(q[k]-w[k]/18 for k in [0,1]),q)
  self.cur=d
 def closePath(self):self.out.closePath()
 def endPath(self):self.out.endPath()

def new_nu(style,level):
 text=TTFont(ROOT/'fonts/private/text'/TEXT_NAMES[STYLES.index(style)])
 name=text.getBestCmap()[ord('ν')];xh=bounds(text,text.getBestCmap()[ord('x')])[3]
 p=pathops.Path();text.getGlyphSet()[name].draw(WarpPen(p.getPen(),105*xh/476,xh))
 if level:
  cx=(p.bounds[0]+p.bounds[2])/2;factor=1+.035*level;p=p.transform(factor,0,0,1,cx*(1-factor),0)
  p=optical(p,3.6*level,2.4*level)
 return p

def install(font,n,p,advance):
 p.convertConicsToQuads(.02)
 pen=T2CharStringPen(advance,None,roundTolerance=0)
 p.draw(Qu2CuPen(RoundingPen(pen,roundFunc=lambda x:round(x*1024)/1024),max_err=.02,all_cubic=True))
 top=font['CFF '].cff.topDictIndex[0];top.CharStrings[n]=pen.getCharString(private=top.Private,globalSubrs=font['CFF '].cff.GlobalSubrs)
 font['hmtx'][n]=(advance,round(bounds(font,n)[0]))

def metadata(font,version):
 family=f'Baskerville Companion Math Experimental G{version-159}';ps=f'BaskervilleCompanionMath-ExperimentalG{version-159}'
 values={1:family,2:'Regular',3:f'20261029:{ps}:0.{version}',4:family+' Regular',5:f'Version 0.{version}; PRIVATE GREEK EXPERIMENT 2026-10-29',6:ps,16:family,17:'Regular'}
 for r in font['name'].names:
  if r.nameID in values:r.string=values[r.nameID].encode(r.getEncoding())
 top=font['CFF '].cff.topDictIndex[0];font['CFF '].cff.fontNames=[ps];top.FamilyName=family;top.FullName=family+' Regular';top.version=f'0.{version}';font['head'].fontRevision=version/1000

class GreekGesturePen(WarpPen):
 """A forward Greek nu gesture; invertible y-preserving deformation."""
 def __init__(self,out,xh,shear,bulge):self.out=out;self.xh=xh;self.shear=shear;self.bulge=bulge;self.cur=None
 def xy(self,p):return (p[0]+self.shear*p[1]+self.bulge*math.sin(math.pi*p[1]/self.xh),p[1])
 def deriv(self,p,d):return (d[0]+(self.shear+self.bulge*math.pi/self.xh*math.cos(math.pi*p[1]/self.xh))*d[1],d[1])

def upper_ink_centroid(p,xh):
 # Sample the upper 40% of actual ink, not the bbox centre. The delta transfers
 # the existing anchor's relationship rather than inventing an absolute rule.
 x0,y0,x1,y1=p.bounds;xs=[]
 for y in range(round(.6*xh),round(xh),2):
  for x in range(math.floor(x0),math.ceil(x1),2):
   if p.contains((x+1,y+1)):xs.append(x+1)
 assert xs
 return sum(xs)/len(xs)

def design_nu_g2(source,output,recipe):
 f=TTFont(source,recalcTimestamp=False);inv=inventory(f);changes=[];info=f['MATH'].table.MathGlyphInfo
 accents=dict(zip(info.MathTopAccentAttachment.TopAccentCoverage.glyphs,info.MathTopAccentAttachment.TopAccentAttachment))
 corrections=dict(zip(info.MathItalicsCorrectionInfo.Coverage.glyphs,info.MathItalicsCorrectionInfo.ItalicsCorrection))
 for style in ['italic','bolditalic']:
  v=inv[style]['ν']
  for level,n in enumerate([v['glyph']]+v['ssty']):
   oldbox=bounds(f,n);oldadvance,oldlsb=f['hmtx'][n];old=path(f,n);oldaccent=accents[n].Value;oldic=corrections[n].Value
   p=pathops.Path();f.getGlyphSet()[n].draw(GreekGesturePen(p.getPen(),oldbox[3],recipe['shear'],recipe['middle_bulge']))
   gain=level*(2 if style=='bolditalic' else 3)
   if gain:p=optical(p,gain,0)
   box=p.bounds;sx=(oldbox[2]-oldbox[0])/(box[2]-box[0]);sy=(oldbox[3]-oldbox[1])/(box[3]-box[1]);tx=oldbox[0]-sx*box[0];ty=oldbox[1]-sy*box[1]
   p=p.transform(sx,0,0,sy,tx,ty)
   anchor_delta=round(upper_ink_centroid(p,oldbox[3])-upper_ink_centroid(old,oldbox[3]));accents[n].Value+=anchor_delta
   install(f,n,p,oldadvance)
   # Advance, sidebearing and italic correction remain the accepted metrics.
   f['hmtx'][n]=(oldadvance,oldlsb)
   assert all(abs(a-b)<.01 for a,b in zip(oldbox,bounds(f,n)))
   changes.append({'glyph':n,'char':'ν','style':style,'role':['text','script','scriptscript'][level],'advance_before':oldadvance,'advance_after':oldadvance,'advance_delta':0,'bounds_before':oldbox,'bounds_after':bounds(f,n),'lsb_before':oldlsb,'lsb_after':oldlsb,'top_accent_before':oldaccent,'top_accent_after':accents[n].Value,'top_accent_delta':anchor_delta,'italic_correction_before':oldic,'italic_correction_after':oldic,'italic_correction_delta':0,'outline_action':'Accepted native Greek contour given forward curved rising gesture; same ink envelope and metrics','shear':recipe['shear'],'middle_bulge':recipe['middle_bulge'],'ink_gain':gain,'closed_counter_relief':0,'envelope_transform':[sx,0,0,sy,tx,ty],'source_adoption':'Retained0.152 nu and its existing optical contours; no G1 components promoted.'})
 metadata(f,recipe['version']);f.save(output)
 return inv,changes

def design(source,output,recipe):
 if recipe.get('proposal')=='nu-gesture-g2':return design_nu_g2(source,output,recipe)
 f=TTFont(source,recalcTimestamp=False);inv=inventory(f);changes=[];info=f['MATH'].table.MathGlyphInfo
 accents=dict(zip(info.MathTopAccentAttachment.TopAccentCoverage.glyphs,info.MathTopAccentAttachment.TopAccentAttachment))
 corrections=dict(zip(info.MathItalicsCorrectionInfo.Coverage.glyphs,info.MathItalicsCorrectionInfo.ItalicsCorrection))
 # Edge classes express different silhouette needs. The open entry of beta,
 # rho and iota can accept some left-space redistribution; diagonal exits
 # need more trailing white. Their bearings intentionally remain unequal.
 entry_shift={'β':-14,'ρ':-10,'ι':-12,'θ':-4,'κ':-3,'μ':-3,'ψ':-3,'ϱ':-8}
 exit_space={c:6 for c in CHARS}
 for c in 'γζηλχψ∂':exit_space[c]=12
 for c in 'εκπςτυϰϖ':exit_space[c]=9
 for style in STYLES:
  for c,v in inv[style].items():
   for level,n in enumerate([v['glyph']]+v['ssty']):
    oldbox=bounds(f,n);oldadvance,oldlsb=f['hmtx'][n];oldic=corrections[n].Value if n in corrections else None;oldaccent=accents[n].Value if n in accents else None;p=path(f,n)
    changed_nu=c=='ν' and style in ['italic','bolditalic']
    if changed_nu:
     p=new_nu(style,level)
     # Source Greek retains its native height/depth; fit to accepted extents.
     b=p.bounds;sy=(oldbox[3]-oldbox[1])/(b[3]-b[1]);p=p.transform(1,0,0,sy,0,oldbox[1]-sy*b[1])
    isbold='bold' in style
    gain=(1.5 if level==1 else 2.3) if level else 0
    if isbold:gain*=.6
    relief=(3.0 if isbold else 0)+(1.0*level if isbold else .6*level)
    if n=='u1D6D9.greek.ssty2':gain=relief=0 # Preserve native psi: offset Boolean is unreliable here.
    if gain or relief:p=optical(p,gain,relief)
    # Preserve vertical extremes after ink adjustment; prevent optical growth
    # from silently changing line relationships or accent clearances.
    b=p.bounds;sy=(oldbox[3]-oldbox[1])/(b[3]-b[1]);p=p.transform(1,0,0,sy,0,oldbox[1]-sy*b[1])
    tx=entry_shift.get(c,0)
    if style in ['italic','bolditalic']:tx=round(tx*.65)
    # Native nu has a different width after posture reconstruction. Set its
    # left space from the incumbent, retain the face's actual relative width.
    if changed_nu:tx=oldbox[0]+tx-p.bounds[0]
    p=p.transform(1,0,0,1,tx,0)
    right=oldadvance-oldbox[2]+exit_space[c]
    advance=round(p.bounds[2]+right)
    install(f,n,p,advance)
    anchor_dx=tx
    if changed_nu:anchor_dx=(bounds(f,n)[0]+bounds(f,n)[2]-oldbox[0]-oldbox[2])/2
    if n in accents:accents[n].Value+=round(anchor_dx)
    if n in corrections:corrections[n].Value=max(0,corrections[n].Value-exit_space[c])
    changes.append({'glyph':n,'char':c,'style':style,'role':['text','script','scriptscript'][level], 'advance_before':oldadvance,'advance_after':advance,'advance_delta':advance-oldadvance,'bounds_before':oldbox,'bounds_after':bounds(f,n),'lsb_before':oldlsb,'lsb_after':f['hmtx'][n][1],'top_accent_before':oldaccent,'top_accent_after':accents[n].Value if n in accents else None,'translation_x':tx,'top_accent_delta':round(anchor_dx) if n in accents else None,'italic_correction_before':oldic,'italic_correction_delta':corrections[n].Value-oldic if n in corrections else None,'italic_correction_after':corrections[n].Value if n in corrections else None,'outline_action':'native Greek nu posture' if changed_nu else 'counter relief/optical ink' if gain or relief else 'translation only' if tx else 'native contour retained','ink_gain':gain,'closed_counter_relief':relief})
 metadata(f,recipe['version']);f.save(output)
 return inv,changes

def validate(source,output,changes):
 a,b=TTFont(source),TTFont(output);names={v['glyph'] for v in changes};inv=inventory(b)
 assert a.getGlyphOrder()==b.getGlyphOrder() and a.getBestCmap()==b.getBestCmap()
 assert a['GSUB'].compile(a)==b['GSUB'].compile(b)
 changed_outlines=[];changed_advances=[];counter_tests=[]
 for n in b.getGlyphOrder():
  ra,rb=recording(a,n),recording(b,n)
  if n not in names:assert ra==rb and a['hmtx'][n]==b['hmtx'][n],n
  else:
   if ra!=rb:changed_outlines.append(n)
   if a['hmtx'][n]!=b['hmtx'][n]:changed_advances.append(n)
   old,new=path(a,n),path(b,n)
   ca,cb=contours(old),contours(new)
   oldholes=[c.area for d,c in ca if d%2];newholes=[c.area for d,c in cb if d%2]
   assert len(oldholes)==len(newholes),(n,oldholes,newholes)
   assert all(x>1 for x in newholes),(n,newholes)
   assert all(math.isfinite(x) for x in new.bounds)
   area_ratio=new.area/old.area
   assert .85<area_ratio<1.20,(n,area_ratio) # Gross fill-loss guard, not a quality metric.
   # Boolean simplification must not erase substantial contour area: a useful
   # crossing/fill diagnostic, not a claim of proof-perfect Bezier craft.
   simp=pathops.simplify(new);assert abs(simp.area-new.area)<max(1,new.area*.0001),(n,new.area,simp.area)
   counter_tests.append({'glyph':n,'closed_counters':len(newholes),'min_counter_area':min(newholes) if newholes else None,'fill_area_ratio':area_ratio})
 # All MATH structures except permitted Greek anchors/corrections stay exact.
 ac,bc=copy.deepcopy(a['MATH']),copy.deepcopy(b['MATH'])
 for tab in [ac,bc]:
  inf=tab.table.MathGlyphInfo
  for cov,values in [(inf.MathTopAccentAttachment.TopAccentCoverage.glyphs,inf.MathTopAccentAttachment.TopAccentAttachment),(inf.MathItalicsCorrectionInfo.Coverage.glyphs,inf.MathItalicsCorrectionInfo.ItalicsCorrection)]:
   for n,v in zip(cov,values):
    if n in names:v.Value=0
 assert ac.compile(a)==bc.compile(b)
 # Every unaffected SFNT table apart from rewritten CFF/name/head/hmtx is exact.
 for tag in a.keys():
  if tag in ['GlyphOrder','CFF ','name','head','hmtx','MATH','hhea']:continue
  assert a[tag].compile(a)==b[tag].compile(b),tag
 # Positive horizontal bbox separation proves the tested raw-advance pairs
 # cannot collide; it says nothing about optical equality or TeX attachments.
 separations=[]
 for s,roles in inv.items():
  for level in range(3):
   for text in ['οθοβεβωοω','νυνυνυ','λογος','φυσικη','αβγδεζηθικλμνξοπρςστυφχψω']:
    ns=[roles[c]['glyph'] if level==0 else roles[c]['ssty'][level-1] for c in text]
    gaps=[b['hmtx'][left][0]+bounds(b,right)[0]-bounds(b,left)[2] for left,right in zip(ns,ns[1:])]
    assert min(gaps)>0,(s,level,text,gaps)
    separations.append({'style':s,'role':level,'string':text,'minimum_bbox_separation':min(gaps)})
 for nid in [0,7,8,9,10,11,12,13,14]:
  assert [(r.platformID,r.platEncID,r.langID,r.toUnicode()) for r in a['name'].names if r.nameID==nid]==[(r.platformID,r.platEncID,r.langID,r.toUnicode()) for r in b['name'].names if r.nameID==nid]
 return {'pass':True,'raw_advance_collision_checks':separations,'source_notices_preserved':True,'retained_optical_exceptions':[{'glyph':'u1D6D9.greek.ssty2','reason':'Offset Boolean loses arms; accepted native optical outline retained, only fitting advance changes.'}] if 'u1D6D9.greek.ssty2' in names else [],'roles':384,'base_forms':32,'styles':STYLES,'inventory':inv,'changes':changes,'changed_glyphs':changed_outlines,'changed_metrics':changed_advances,'counter_integrity':counter_tests,'checks':{'unrelated_outlines_and_hmtx_exact':True,'cmap_and_glyph_order_exact':True,'ssty_GSUB_binary_exact':True,'all_128_roles_have_two_explicit_ssty_alternates':True,'radical_variants_assemblies_and_unrelated_MATH_exact':True,'closed_counter_topology_preserved':True,'finite_bounds_and_boolean_fill_integrity':True},'limitations':['No physical print trial or human reader study.','Counter topology and Boolean fill checks do not establish all curve-quality or collision cases.','Grid bearings are diagnostics, not equality targets.']}

def main():
 p=argparse.ArgumentParser();p.add_argument('--round',type=int,required=True);p.add_argument('--input',type=Path);args=p.parse_args()
 recipepath=ROOT/f'design/greek-round-{args.round}.json';recipe=json.loads(recipepath.read_text());source=args.input or ROOT/recipe['input']
 assert sha(source)==recipe['input_sha256']
 run=ROOT/f'runs/greek-campaign-2026-10-29/round-{args.round}';private=run/'private';packet=run/'packet'
 if run.exists():raise SystemExit('Refusing to overwrite round')
 private.mkdir(parents=True);packet.mkdir();candidate=private/'candidate.otf';inv,changes=design(source,candidate,recipe);report=validate(source,candidate,changes)
 from greek_proofs import build_proofs
 key,proof_report=build_proofs(run,source,candidate,inv)
 report['proofs']=proof_report;report['pass']=report['pass'] and proof_report['pass']
 (private/'engineering.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 snapshots={}
 for src in [Path(__file__),ROOT/'tools/greek_proofs.py',recipepath,ROOT/'design/greek-requirements.txt']:
  dst=private/(src.stem+'-at-build'+src.suffix);shutil.copy2(src,dst);snapshots[dst.name]=sha(dst)
 for n in ['SOURCE-NOTICES.txt','STIX-OFL.txt']:shutil.copy2(ROOT/'fonts/private'/n,private/n)
 prov={'key':key,'input':str(source),'input_sha256':sha(source),'candidate':str(candidate),'candidate_sha256':sha(candidate),'recipe':recipe,'build_snapshot':snapshots,'engineering_pass':report['pass']}
 (private/'provenance.json').write_text(json.dumps(prov,ensure_ascii=False,indent=2)+'\n');print(run)
if __name__=='__main__':main()
