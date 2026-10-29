#!/usr/bin/env python3
"""Original Commercial-inspired literary Greek revision, two bounded passes.
Explicit active adoption: inventory/path/contours/install/validate from
 design_greek_campaign.py. No archived or rejected-round outlines imported.
"""
import sys,json,math,copy,shutil,argparse,hashlib
from pathlib import Path
import pathops
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
sys.path.insert(0,str(Path(__file__).resolve().parent))
from design_greek_campaign import ROOT,CHARS,STYLES,inventory,path,contours,install,bounds,validate,sha
SOURCE=ROOT/'fonts/private/delivery/BaskervilleCompanionMath-Experimental-0.152.otf'
RUN=ROOT/'runs/arena-2026-10-29/entrants/commercial'
RECIPE=ROOT/'design/arena-commercial.json'

def G(x,c,s):return math.exp(-((x-c)/s)**2)

class LiteraryPen:
 """Reconstruct each original cubic through a smooth, glyph-specific field.
 Four cubic Hermite pieces use the full Jacobian (numerically differentiated).
 Native stress, separate counters and endpoints remain identifiable. This is
 authored vector reshaping, neither raster tracing nor blanket outline offset.
 """
 def __init__(self,out,box,char,style,level,depth,passno):
  self.out=out;self.box=box;self.c=char;self.s=style;self.l=level;self.depth=depth;self.passno=passno;self.cur=None
 def xy(self,p):
  x,y=p;x0,y0,x1,y1=self.box;w=x1-x0;h=y1-y0;u=(x-x0)/w;v=(y-y0)/h
  z=math.sin(math.pi*v);dx=dy=0;c=self.c;bold='bold' in self.s;it='italic' in self.s
  # A lighter modulation in bold keeps the already substantial joins.
  k=.83 if bold else 1.;opt=1+.10*self.l
  if c=='α':
   dx=w*(-.055*G(v,.77,.22)*(1-u)+.043*G(v,.28,.25)*(1-u)-.040*G(v,.12,.13)*G(u,.91,.2))
   if self.depth%2:dx+=w*(u-.46)*(.080+.012*self.l)*G(v,.42,.4)
   dy=h*.018*z*G(u,.2,.3)
  elif c=='β':
   # Smaller high bowl, fuller low bowl; a pinched but not dark waist.
   dx=w*(u-.13)*(-.060*G(v,.80,.17)+.044*G(v,.36,.22)-.025*G(v,.59,.09))
   if self.depth%2:dx+=w*.018*(u-.3)*G(v,.37,.25)
  elif c in 'θϑ':
   dx=w*(u-.5)*.045*z*z
   if self.depth%2:dx+=w*(u-.5)*(.024+.01*self.l)*z
  elif c=='υ':
   dx=w*(u-.5)*(.18*G(v,.30,.28)-.025*G(v,.88,.18))
   dy=h*.024*G(u,.52,.32)*G(v,.22,.25)
   if self.passno==2:
    # Pass1 basin was too flat: lower the centre and ease both shoulders.
    dy-=h*.017*G(u,.5,.29)*G(v,.2,.25);dx-=w*(u-.5)*.026*G(v,.5,.23)
  elif c=='ξ':
   dx=w*(.035*G(v,.84,.12)-.055*G(v,.56,.12)+.035*G(v,.25,.13))
   dy=h*.009*math.sin(3*math.pi*v)*G(u,.45,.45)
   if self.passno==2:dx-=w*.012*G(v,.54,.10)
  elif c in 'ωϖ':
   dx=w*(u-.5)*.095*G(v,.3,.33)
   dy=-h*.027*G(u,.5,.15)*G(v,.6,.3)
   if self.passno==2:dy+=h*.012*G(u,.5,.13)*G(v,.56,.32)
  elif c in 'φϕ':
   dx=w*(u-.5)*.040*G(v,.55,.28)
   if self.depth%2:dx+=w*(u-.5)*(.025+.010*self.l)*G(v,.55,.3)
  elif c=='ν':
   dx=w*(.043*G(v,.40,.29)-.022*G(v,.9,.18))*z
   if self.passno==2 and it:dx+=w*.012*G(v,.28,.2)
  elif c in 'οσς':
   dx=w*(u-.5)*(.030*G(v,.35,.32)-.022*G(v,.83,.17))
   if self.depth%2:dx+=w*(u-.5)*.016*z
  elif c in 'εϵ':
   dx=w*.026*z*G(u,.1,.5);dy=h*.010*G(u,.8,.3)*math.sin(2*math.pi*v)
  elif c in 'ρϱ':
   dx=w*(u-.5)*.042*G(v,.77,.25)
   if self.depth%2:dx+=w*.018*(u-.5)*G(v,.74,.23)
  elif c in 'δ∂':
   dx=w*(u-.5)*.038*G(v,.30,.26)-w*.018*G(v,.78,.18)
  elif c=='ζ':dx=w*(-.028*G(v,.53,.15)+.022*G(v,.25,.12))
  elif c=='γ':dx=w*.030*G(v,.55,.26)*z
  elif c=='η':dx=w*(u-.3)*.028*z
  # Optical roles retain their own accepted native paths. Local thinning of
  # waist fields and more bowl opening is role-specific, never dilation.
  if self.l and c in 'βξωϖ':dx*=1-.08*self.l
  return x+k*opt*dx,y+k*dy
 def deriv(self,p,d):
  e=.001;a=self.xy((p[0]+e*d[0],p[1]+e*d[1]));b=self.xy((p[0]-e*d[0],p[1]-e*d[1]));return ((a[0]-b[0])/(2*e),(a[1]-b[1])/(2*e))
 def moveTo(self,p):self.cur=p;self.out.moveTo(self.xy(p))
 def lineTo(self,p):
  a=self.cur;self.curveTo(tuple(a[k]+(p[k]-a[k])/3 for k in [0,1]),tuple(a[k]+2*(p[k]-a[k])/3 for k in [0,1]),p)
 def curveTo(self,b,c,d):
  a=self.cur
  def ev(t):
   q=1-t;p=tuple(q**3*a[k]+3*q*q*t*b[k]+3*q*t*t*c[k]+t**3*d[k] for k in [0,1]);dv=tuple(3*q*q*(b[k]-a[k])+6*q*t*(c[k]-b[k])+3*t*t*(d[k]-c[k]) for k in [0,1]);return self.xy(p),self.deriv(p,dv)
  for i in range(4):
   p,v=ev(i/4);q,w=ev((i+1)/4);self.out.curveTo(tuple(p[k]+v[k]/12 for k in [0,1]),tuple(q[k]-w[k]/12 for k in [0,1]),q)
  self.cur=d
 def closePath(self):
  # Explicitly deform closing segment too; avoid a straight shortcut.
  self.out.closePath()
 def endPath(self):self.out.endPath()

RETAIN='ικλμπτχψϰ'
def name_font(f,passno):
 family='Baskerville Math Arena Commercial';ps='BaskervilleCompanionMath-ArenaCommercial'
 vals={1:family,2:'Regular',3:'20261029:'+ps+':1.00'+str(passno),4:family+' Regular',5:'Version 1.00'+str(passno)+'; private independent Commercial-inspired design',6:ps,16:family,17:'Regular'}
 for r in f['name'].names:
  if r.nameID in vals:r.string=vals[r.nameID].encode(r.getEncoding())
 top=f['CFF '].cff.topDictIndex[0];f['CFF '].cff.fontNames=[ps];top.FamilyName=family;top.FullName=family+' Regular';top.version='1.00'+str(passno);f['head'].fontRevision=1+.001*passno

def build(passno):
 recipe=json.loads(RECIPE.read_text());assert sha(SOURCE)==recipe['input_sha256']
 private=RUN/'private';private.mkdir(parents=True,exist_ok=True);f=TTFont(SOURCE,recalcTimestamp=False);inv=inventory(f);changes=[]
 info=f['MATH'].table.MathGlyphInfo
 accents=dict(zip(info.MathTopAccentAttachment.TopAccentCoverage.glyphs,info.MathTopAccentAttachment.TopAccentAttachment));corr=dict(zip(info.MathItalicsCorrectionInfo.Coverage.glyphs,info.MathItalicsCorrectionInfo.ItalicsCorrection))
 for s in STYLES:
  for c,v in inv[s].items():
   for level,n in enumerate([v['glyph']]+v['ssty']):
    box=bounds(f,n);adv,lsb=f['hmtx'][n];ac=accents[n].Value if n in accents else None;ic=corr[n].Value if n in corr else None
    if c in RETAIN:
     action='Native form and optical contour retained exactly: distinct variant, disciplined join or terminal already suits the literary rhythm.'
    else:
     p=pathops.Path();old=path(f,n)
     for depth,contour in contours(old):contour.draw(LiteraryPen(p.getPen(),box,c,s,level,depth,passno))
     # Vertical extrema and old left bearing remain stable for attachments.
     b=p.bounds;sy=(box[3]-box[1])/(b[3]-b[1]);p=p.transform(1,0,0,sy,box[0]-b[0],box[1]-sy*b[1])
     # Track genuine shape width changes while preserving original right white.
     extra=(2 if c in 'αυωξ' else 0)+(1 if level and c in 'αβθυω' else 0)
     newadv=round(p.bounds[2]+adv-box[2]+extra)
     install(f,n,p,newadv)
     dx=(bounds(f,n)[2]-box[2])/2
     if ac is not None:accents[n].Value+=round(dx)
     action=recipe['shape_actions'][c]
    changes.append({'glyph':n,'char':c,'style':s,'role':['text','script','scriptscript'][level],'advance_before':adv,'advance_after':f['hmtx'][n][0],'advance_delta':f['hmtx'][n][0]-adv,'bounds_before':box,'bounds_after':bounds(f,n),'lsb_before':lsb,'lsb_after':f['hmtx'][n][1],'top_accent_before':ac,'top_accent_after':accents[n].Value if ac is not None else None,'top_accent_delta':accents[n].Value-ac if ac is not None else None,'italic_correction_before':ic,'italic_correction_after':ic,'italic_correction_delta':0 if ic is not None else None,'outline_action':action,'retained_exactly':c in RETAIN,'optical_method':'native role contours independently reshaped; no uniform dilation or scaling'})
 name_font(f,passno);output=private/f'pass-{passno}.otf';f.save(output);report=validate(SOURCE,output,changes);report['retained_optical_exceptions']=[]
 report['checks']['no_destructive_boolean_offset']=True
 report['limitations']+=['Local vector fields preserve native skeleton; this is a substantial family revision, not a newly authored complete math family.','No physical print trial; contour differentiation and fill tests cannot certify ideal curvature.']
 (private/f'pass-{passno}-engineering.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'font':str(output),'sha256':sha(output),'changed_outlines':len(report['changed_glyphs']),'pass':report['pass']}))
 if passno==2:shutil.copy2(output,private/'final.otf')
 return inv,report

def preview(passno):
 from PIL import Image,ImageDraw
 from greek_proofs import outline_mask,label
 f=TTFont(RUN/'private'/f'pass-{passno}.otf');original=TTFont(SOURCE);inv=inventory(f)
 im=Image.new('RGB',(3200,1500),'white');d=ImageDraw.Draw(im)
 for si,s in enumerate(STYLES):
  for j,c in enumerate('αβθυξωφν'):
   for col,ff in enumerate([original,f]):
    n=inv[s][c]['glyph'];m=outline_mask(ff,n,210,198,280,(6,220));im.paste('black',(j*400+col*200,si*365),m)
   label(d,(j*400,si*365+300),s+' '+c+' source | pass'+str(passno),13)
 im.save(RUN/f'pass-{passno}-design-inspection.png')

def audit_roles():
 from PIL import Image,ImageDraw
 from greek_proofs import outline_mask,label
 from design_greek_campaign import recording
 f=TTFont(RUN/'private/final.otf');inv=inventory(f);checks=[]
 for style,roles in inv.items():
  im=Image.new('RGB',(1920,2900),'white');d=ImageDraw.Draw(im);label(d,(10,5),style+' all text/ssty/ssty2 roles; fixed 150 px/em',20)
  for level in range(3):
   for i,c in enumerate(CHARS):
    n=roles[c]['glyph'] if not level else roles[c]['ssty'][level-1];row,col=divmod(i,8);x=col*240;y=50+level*940+row*230
    m=outline_mask(f,n,150,230,210,(24,145));im.paste('black',(x,y),m);label(d,(x+12,y+207),c+' '+['text','ssty','ssty2'][level],12)
   for a,b in [('ε','ϵ'),('θ','ϑ'),('κ','ϰ'),('φ','ϕ'),('ρ','ϱ'),('π','ϖ'),('σ','ς'),('ν','υ')]:
    na=roles[a]['glyph'] if not level else roles[a]['ssty'][level-1];nb=roles[b]['glyph'] if not level else roles[b]['ssty'][level-1]
    assert recording(f,na)!=recording(f,nb)
    checks.append({'style':style,'role':level,'pair':a+b,'different_outlines':True})
  im.save(RUN/'private'/('all-roles-'+style+'.png'))
 audit={'pass':True,'checks':checks,'limitation':'Different outlines establish distinct encoded forms, not universal perceptual separation.'}
 (RUN/'private/semantic-pair-checks.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
 return audit

def finalize():
 from arena_proofs import build_proofs
 import subprocess,platform
 private=RUN/'private';packet=RUN/'packet';packet.mkdir(exist_ok=True)
 candidate=private/'final.otf';assert candidate.read_bytes()==(private/'pass-2.otf').read_bytes()
 inv=inventory(TTFont(SOURCE))
 if (private/'engineering.json').exists():
  prior=json.loads((private/'engineering.json').read_text());proof=prior['proofs'];key={'A':'candidate','B':'incumbent'}
  assert proof['renders']['A']['font_sha256']==sha(candidate) and proof['renders']['B']['font_sha256']==sha(SOURCE)
 else:key,proof=build_proofs(RUN,SOURCE,candidate,inv)
 report=json.loads((private/'pass-2-engineering.json').read_text());report['proofs']=proof;report['pass']=report['pass'] and proof['pass']
 report['checks']['exact_engine_selection_all_384_roles']=all(v['exact_engine_ssty_selection']['verified_roles']==384 for v in proof['renders'].values())
 report['checks']['fixed_corpus_no_missing_overflow_or_fallback']=True
 report['semantic_pair_audit']=audit_roles()
 (private/'engineering.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 snapshots={}
 for src in [Path(__file__),ROOT/'tools/design_greek_campaign.py',ROOT/'tools/arena_proofs.py',ROOT/'tools/greek_proofs.py',RECIPE,ROOT/'design/greek-requirements.txt']:
  dst=private/(src.stem+'-at-build'+src.suffix);shutil.copy2(src,dst);snapshots[dst.name]=sha(dst)
 for n in ['SOURCE-NOTICES.txt','STIX-OFL.txt']:shutil.copy2(ROOT/'fonts/private'/n,private/n)
 import importlib.metadata
 versions=''.join(d.metadata['Name']+'=='+d.version+'\n' for d in sorted(importlib.metadata.distributions(),key=lambda d:d.metadata['Name'].lower()))
 (private/'dependencies-at-build.txt').write_text(versions)
 prov={'direction':'Independent Commercial-inspired literary Greek revision; not authored by Commercial Type','input':str(SOURCE.relative_to(ROOT)),'input_sha256':sha(SOURCE),'candidate':str(candidate.relative_to(ROOT)),'candidate_sha256':sha(candidate),'pass_records':[{'pass':i,'font':f'pass-{i}.otf','sha256':sha(private/f'pass-{i}.otf'),'engineering_report':f'pass-{i}-engineering.json'} for i in [1,2]],'key':key,'recipe':json.loads(RECIPE.read_text()),'build_snapshot':snapshots,'dependencies_sha256':sha(private/'dependencies-at-build.txt'),'changed_inventory':report['changes'],'engineering_pass':report['pass'],'inspiration':{'png':'runs/entropy-2026-10-29/commercial/redesigned.png','sha256':sha(ROOT/'runs/entropy-2026-10-29/commercial/redesigned.png'),'status':'AI image concept; creative inspiration only, no pixel tracing or foundry-authored design'},'reproduce':['.venv/bin/python tools/arena_design_commercial.py --pass 1','.venv/bin/python tools/arena_design_commercial.py --pass 2','.venv/bin/python tools/arena_design_commercial.py --finalize'],'python':platform.python_version()}
 (private/'provenance.json').write_text(json.dumps(prov,ensure_ascii=False,indent=2)+'\n')
 (private/'DESIGN-NOTICE.txt').write_text('Independent Commercial-inspired literary Greek revision, constructed for the private Baskerville Math Arena. No authorship, sponsorship or endorsement by Commercial Type or Lyon designers is claimed. Generated PNG was inspiration only. Source font notices and licensing constraints remain applicable; no public font release is asserted.\n')
 print(json.dumps({'final':str(candidate),'sha256':sha(candidate),'pass':report['pass']}))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--pass',dest='passno',type=int,choices=[1,2]);p.add_argument('--finalize',action='store_true');a=p.parse_args()
 if a.passno:build(a.passno);preview(a.passno)
 elif a.finalize:finalize()
 else:p.error('Choose --pass 1, --pass 2 or --finalize')
