"""Arena proofs: explicitly adopted Greek diagnostics plus a continuous article.
The raster concepts are never input to rendering; every glyph is from compiled OTF.
"""
import json, math, shutil, xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageChops
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
from design_greek_campaign import ROOT,CHARS,STYLES,TEXT_NAMES,sha,command,bounds,contours,path
LABEL='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def label(d,xy,text,size=21,fill='#303030'):d.text(xy,text,font=ImageFont.truetype(LABEL,size),fill=fill)
def header(im,title,subtitle):
 d=ImageDraw.Draw(im);label(d,(25,17),title,28);label(d,(25,56),subtitle,18)
def cpfont(fontpath,px):return ImageFont.truetype(str(fontpath),px)
def glyph(im,fontpath,cp,x,y,em,fill='black'):
 ImageDraw.Draw(im).text((x,y),chr(cp),font=cpfont(fontpath,em),fill=fill,anchor='ls')
def flattened(c):
 r=RecordingPen();c.draw(r);pts=[];cur=None
 for op,args in r.value:
  if op in ['moveTo','lineTo']:cur=args[0];pts.append(cur)
  elif op=='curveTo':
   a=cur;b,c,d=args
   for i in range(1,33):
    t=i/32;u=1-t;pts.append(tuple(u**3*a[k]+3*u*u*t*b[k]+3*u*t*t*c[k]+t**3*d[k] for k in [0,1]))
   cur=d
  elif op=='qCurveTo':
   a=cur;b,c=args
   for i in range(1,25):
    t=i/24;pts.append(tuple((1-t)**2*a[k]+2*(1-t)*t*b[k]+t*t*c[k] for k in [0,1]))
   cur=c
 return pts

def outline_mask(font,n,em,width,height,origin):
 # Same em for every glyph; contour nesting determines white counters.
 ss=3;im=Image.new('L',(width*ss,height*ss),0);d=ImageDraw.Draw(im)
 for depth,c in contours(path(font,n)):
  points=[((origin[0]+x*em/1000)*ss,(origin[1]-y*em/1000)*ss) for x,y in flattened(c)]
  d.polygon(points,fill=0 if depth%2 else 255)
 return im.resize((width,height),Image.Resampling.LANCZOS)

def closed_counter(mask):
 # Flood exterior white from border. Remaining white components are closed
 # counters; open apertures remain connected to exterior and are excluded.
 binary=mask.point(lambda v:255 if v>128 else 0)
 bg=binary.copy();ImageDraw.floodfill(bg,(0,0),128,thresh=0)
 return bg.point(lambda v:255 if v==0 else 0)

def pasted_mask(im,mask,xy,colour):
 layer=Image.new('RGB',mask.size,colour);im.paste(layer,xy,mask)

def measured_guides():
 out={}
 for s,filename in zip(STYLES,TEXT_NAMES):
  f=TTFont(ROOT/'fonts/private/text'/filename);cm=f.getBestCmap()
  out[s]={'baseline':0,'companion_x_top':bounds(f,cm[ord('x')])[3],'companion_p_bottom':bounds(f,cm[ord('p')])[1],'source':filename,'source_sha256':sha(ROOT/'fonts/private/text'/filename)}
 return out

def grid(fonts,inv,styles,guides,title):
 im=Image.new('RGB',(1960,1470),'white');header(im,title,'130 px/em; fixed cells and origins; blue = baseline, grey = measured companion x/p, red = Greek omicron top')
 d=ImageDraw.Draw(im)
 for side in 'AB':
  xo=30 if side=='A' else 1010;label(d,(xo,95),side,30)
  f=TTFont(fonts[side])
  for si,s in enumerate(styles):
   yy=145+si*650;g=guides[s];otop=bounds(f,inv[s]['ο']['glyph'])[3]
   label(d,(xo,yy),f'{s}; x={g["companion_x_top"]:g}, p={g["companion_p_bottom"]:g}, ο top={otop:g}',18)
   for i,c in enumerate(CHARS):
    row,col=divmod(i,8);x=xo+col*116;y=yy+125+row*148
    for val,color in [(0,'#7296bd'),(g['companion_x_top'],'#c6c6c6'),(g['companion_p_bottom'],'#c6c6c6'),(otop,'#dfb6b6')]:
     dy=y-val*.13;d.line((x,dy,x+108,dy),fill=color,width=1)
    glyph(im,fonts[side],inv[s][c]['cp'],x+6,y,130)
    advance=f['hmtx'][inv[s][c]['glyph']][0]*.13;d.line((x+6+advance,y+3,x+6+advance,y+10),fill='#8e8e8e')
    label(d,(x+5,y+42),c,16)
 return im

def space_study(fonts,inv):
 im=Image.new('RGB',(1960,2010),'white');header(im,'Counters and interletter white','Fixed em and advances. Cyan = enclosed counters only. Orange = between adjacent silhouettes in the labelled body band.')
 d=ImageDraw.Draw(im)
 for side in 'AB':
  xo=25 if side=='A' else 1005;label(d,(xo,98),side,30);f=TTFont(fonts[side])
  for si,s in enumerate(['italic','bolditalic']):
   yy=150+si*870;label(d,(xo,yy),s+' — unmasked forms, then closed-counter mask',20)
   for j,c in enumerate('οθφβεω'):
    n=inv[s][c]['glyph'];mask=outline_mask(f,n,170,150,215,(12,145))
    x=xo+j*156;im.paste('black',(x,yy+35),mask);im.paste('black',(x,yy+245),mask)
    cc=closed_counter(mask);pasted_mask(im,cc,(x,yy+245),'#23b7cf')
    label(d,(x+10,yy+450),c,18)
   # A second natural string and a duplicate whose interletter white is marked.
   label(d,(xo,yy+490),'Raw glyph advances: οθοβεβωοω (no math atom glue)',18)
   text='οθοβεβωοω';em=160;canvas=(930,190);origin=(6,130)
   masks=[];x=origin[0]
   for c in text:
    m=outline_mask(f,inv[s][c]['glyph'],em,*canvas,(x,origin[1]));masks.append(m);x+=f['hmtx'][inv[s][c]['glyph']][0]*em/1000
   allink=Image.new('L',canvas,0)
   for m in masks:allink=ImageChops.lighter(allink,m)
   im.paste('black',(xo,yy+510),allink);im.paste('black',(xo,yy+635),allink)
   white=Image.new('L',canvas,0);wd=ImageDraw.Draw(white)
   xh=bounds(f,inv[s]['ο']['glyph'])[3]*em/1000
   for y in range(round(origin[1]-.9*xh),round(origin[1]-.08*xh)):
    for left,right in zip(masks,masks[1:]):
     aa=[i for i,v in enumerate(left.crop((0,y,canvas[0],y+1)).getdata()) if v>128];bb=[i for i,v in enumerate(right.crop((0,y,canvas[0],y+1)).getdata()) if v>128]
     if aa and bb and max(aa)+1<min(bb):wd.line((max(aa)+1,y,min(bb)-1,y),fill=180)
   pasted_mask(im,white,(xo,yy+635),'#e9a553')
 return im

def details(fonts,inv):
 im=Image.new('RGB',(1960,1510),'white');header(im,'Direct form and variant comparison','190 px/em confusables; 150 px/em variants; 112 px/em context. Fixed A/B origins and scales.')
 d=ImageDraw.Draw(im)
 groups=[('italic','Latin v / ν / υ; context νυνυνυ',None),('bolditalic','Latin v / ν / υ; context νυνυνυ',None),('italic','εϵ θϑ κϰ φϕ ρϱ πϖ','εϵθϑκϰφϕρϱπϖ'),('bolditalic','εϵ θϑ κϰ φϕ ρϱ πϖ','εϵθϑκϰφϕρϱπϖ')]
 for side in 'AB':
  xo=25 if side=='A' else 1005;label(d,(xo,95),side,30);f=TTFont(fonts[side])
  for j,(s,lab,chars) in enumerate(groups):
   y=180+j*240 if j<2 else 720+(j-2)*370;label(d,(xo,y-20),s+' — '+lab,19)
   if chars:
    for k,c in enumerate(chars):glyph(im,fonts[side],inv[s][c]['cp'],xo+5+(k%6)*151,y+120+(k//6)*150,150)
   else:
    cps=[0x1D463 if s=='italic' else 0x1D497,inv[s]['ν']['cp'],inv[s]['υ']['cp']]
    for k,cp in enumerate(cps):glyph(im,fonts[side],cp,xo+20+k*180,y+130,190)
    text='νυνυνυ';x=xo+560
    for c in text:
     glyph(im,fonts[side],inv[s][c]['cp'],x,y+130,112);x+=f['hmtx'][inv[s][c]['glyph']][0]*.112
 return im

def optical_sheet(fonts,inv,optical_actual):
 im=Image.new('RGB',(1960,1480),'white');header(im,'Optical script comparison','Upper: XeLaTeX actual 8/10/12 pt contexts at 180 dpi. Lower: existing text/script/script-script outlines at identical 180 px/em.')
 d=ImageDraw.Draw(im)
 for side in 'AB':
  xo=25 if side=='A' else 1005;label(d,(xo,95),side,30)
  # Dedicated matched physical-size specimen; no crops through baselines.
  page=optical_actual[side];im.paste(page,(xo,140))
  f=TTFont(fonts[side]);s='italic'
  for level in range(3):
   y=650+level*245;label(d,(xo,y-35),['text outlines','ssty alternate 1','ssty alternate 2'][level],21)
   for k,c in enumerate('ανυθοω'):
    n=inv[s][c]['glyph'] if not level else inv[s][c]['ssty'][level-1]
    mask=outline_mask(f,n,180,155,215,(12,145));im.paste('black',(xo+k*154,y),mask)
 return im

TEX_HEADER=r'''\documentclass[10pt]{article}
\usepackage[a4paper,margin=14mm]{geometry}
\usepackage{fontspec,mathtools,unicode-math}
\setmainfont{Baskerville10Pro.otf}[Path=fonts/]
\setmathfont{math.otf}[Path=fonts/,math-style=ISO,bold-style=ISO]
\pagestyle{empty}\setlength\parindent{0pt}\setlength\parskip{3pt}
\begin{document}
'''

def natural_tex(side):
 """One continuous article page, identical prose/math and measure on both sides."""
 out=TEX_HEADER.replace('a4paper,margin=14mm','a4paper,margin=19mm')
 out+=r'''{\fontsize{15}{18}\selectfont Diffusion, uncertainty and a vibrating domain}\par
{\fontsize{9}{12}\selectfont SIDE — Baskerville mathematics, a continuous reading page}\par\medskip
\fontsize{10.5}{14}\selectfont
A localized disturbance spreads through a medium according to its diffusivity
$\kappa>0$. If $\phi(\xi)$ gives the initial temperature, then a point far from the
origin responds later and more weakly. For a homogeneous line the temperature
$u(x,t)$ solves $\partial_tu=\kappa\partial_x^2u$; the heat kernel makes that
relationship explicit:
\[
u(x,t)=\frac{1}{\sqrt{4\pi\kappa t}}
 \int_{-\infty}^{\infty}\exp\!\left[-\frac{(x-\xi)^2}{4\kappa t}\right]
 \phi(\xi)\,d\xi .
\]
The factor $\pi$ fixes normalization while $\xi$ is an integration variable, not
an additional material constant. In an anisotropic body the coefficients
$\symbfup{\kappa}$ form a tensor; a perturbation $\eta$ changes the local flux
$\psi$ and can couple the modes $\alpha_\nu$ and $\beta_\nu$. We distinguish a
mode index $\nu$, a displacement $\upsilon$, and a velocity $v$: their roles
remain different even inside a small expression such as $v_{\nu_{\upsilon}}$.

Measurement adds another kind of spreading. A Gaussian density has location
$\mu$ and standard deviation $\sigma$, so the same observed value $x$ can be
consistent with several nearby states. Its density and total mass are
\[
 \rho(x\mid\mu,\sigma)=\frac{1}{\sigma\sqrt{2\pi}}
 \exp\!\left[-\frac{(x-\mu)^2}{2\sigma^2}\right],
 \qquad\int_{-\infty}^{\infty}\rho(x\mid\mu,\sigma)\,dx=1.
\]
A small error $\epsilon$ in location and a tolerance $\varepsilon$ in the model
need not denote the same quantity. Likewise $\theta$ and $\vartheta$, $\phi$ and
$\varphi$, $\rho$ and $\varrho$, $\kappa$ and $\varkappa$, and $\pi$ and $\varpi$
retain conventional separate forms. The parameter vectors
$\symbfit{\alpha}$ and $\symbfit{\beta}$ collect fitted values; the upright
$\symup{\mu}$ labels a fixed reference while italic $\mu$ is estimated.

For a vibrating membrane the domain $\Omega$ supplies the boundary condition.
The lowest eigenvalue is characterized by the Rayleigh quotient, which balances
strain energy against displacement. With $\phi=0$ on $\partial\Omega$,
\[
 \lambda_1=\inf_{\phi\ne0}
 \frac{\displaystyle\int_\Omega |\nabla\phi|^2\,d\Omega}
 {\displaystyle\int_\Omega \phi^2\,d\Omega},
 \qquad -\Delta\phi=\lambda\phi .
\]
The modes $\gamma$, $\delta$, $\zeta$ and $\chi$ may be indexed by $\iota$ or
$\tau$; a coupling $\omega$ then modifies the response. Local coordinates
$\nu_{\upsilon_{\iota}}$ and the trial field $\hat\phi_\phi^\phi$ demand clear
small forms as well as stable accents. Averaging gives $\bar\omega$ and
$\hat\nu$, while the flux direction is written $\vec\rho$. The ordinary
symbols $\omicron$, $\varsigma$ and $\sigma$ remain separately available.

In a two-mode approximation one solves
$\left(\begin{smallmatrix}\alpha&\beta\\\nu&\upsilon\end{smallmatrix}\right)$
for the amplitudes and compares
$\sqrt{\alpha^2+\beta_\nu^2}$ with
$\sqrt[\nu]{\phi_\rho/\omega_\theta}$.
The equations serve the argument within a paragraph: their weight, rhythm and
white space should allow the prose to continue without a change of voice.

\medskip{\fontsize{8}{10}\selectfont
Small notation (8 pt): $\alpha_{\beta_{\gamma}}+\nu_{\upsilon_{\iota}}
+\omega_{\theta_{\phi}}$, $\nu\ne\upsilon$, $v\ne\nu$, and
$\partial_\theta\phi=\epsilon+\varepsilon$. This is a reading-size check;
enlarged alphabet and counter studies accompany the page.\par}
\end{document}'''.replace('SIDE',side)
 return out

def build_proofs(run,source,candidate,inv):
 private=run/'private';packet=run/'packet';fonts={'A':Path(candidate),'B':Path(source)};key={'A':'candidate','B':'incumbent'};actual={};proof_checks={}
 for side in 'AB':
  work=private/side;(work/'fonts').mkdir(parents=True)
  shutil.copy2(fonts[side],work/'fonts/math.otf')
  for n in TEXT_NAMES:shutil.copy2(ROOT/'fonts/private/text'/n,work/'fonts'/n)
  (work/'proof.tex').write_text(natural_tex(side));command(['xelatex','-interaction=nonstopmode','-halt-on-error','proof.tex'],work)
  log=(work/'proof.log').read_text();assert 'Missing character:' not in log and 'Overfull' not in log
  embedded=command(['pdffonts',str(work/'proof.pdf')]);(work/'embedded-fonts.txt').write_text(embedded)
  expected_ps=TTFont(fonts[side])['name'].getDebugName(6);assert expected_ps in embedded and 'STIX' not in embedded
  # Assert one fixed reading page; all raster captures share the physical scale.
  pdfinfo=command(['pdfinfo',str(work/'proof.pdf')]);assert 'Pages:           1' in pdfinfo,pdfinfo
  command(['pdftoppm','-singlefile','-r','180','-png',str(work/'proof.pdf'),str(work/'page')])
  actual[side]=Image.open(work/'page.png').convert('RGB');actual[side].save(packet/f'{side}-natural.png')
  proof_checks[side]={'missing_characters':False,'overfull_boxes':False,'unexpected_fallback':False,'embedded_font_report':str(work/'embedded-fonts.txt'),'pdf_sha256':sha(work/'proof.pdf'),'font_sha256':sha(work/'fonts/math.otf')}
 optical_actual={}
 for side in 'AB':
  work=private/side
  optical=TEX_HEADER.replace('a4paper,margin=14mm','paperwidth=120mm,paperheight=59mm,margin=4mm')
  optical+=r'Actual script contexts, 8 / 10 / 12 TeX pt.\par'+'\n'
  for size in [8,10,12]:
   optical+=r'{\fontsize{'+str(size)+'}{'+str(size*1.6)+r'}\selectfont '+str(size)+r' pt: $\alpha_{\beta_{\gamma}}+\nu_{\upsilon_{\iota}}+\omega_{\theta_{\phi}}+v_{\nu_{\upsilon}}$\par}'+ '\n'
  optical+=r'{\fontsize{10}{16}\selectfont $\symup{α}_{\symup{ν}_{\symup{θ}}} + \symit{α}_{\symit{ν}_{\symit{θ}}}+ \symbfup{α}_{\symbfup{ν}_{\symbfup{θ}}}+ \symbfit{α}_{\symbfit{ν}_{\symbfit{θ}}}$\par}\end{document}'
  (work/'optical.tex').write_text(optical);command(['xelatex','-interaction=nonstopmode','-halt-on-error','optical.tex'],work)
  log=(work/'optical.log').read_text();assert 'Missing character:' not in log and 'Overfull' not in log
  command(['pdftoppm','-singlefile','-r','180','-png',str(work/'optical.pdf'),str(work/'optical')]);optical_actual[side]=Image.open(work/'optical.png').convert('RGB')
 # A separate technical page exercises every declared style and optical role.
 # MuPDF's trace reports original CID glyph IDs, compared against compiled GSUB
 # mappings. This validates actual engine selection, not just feature presence.
 for side in 'AB':
  work=private/side;f=TTFont(fonts[side]);coverage=TEX_HEADER+r'\fontsize{10}{15}\selectfont Optical selection audit\par'+'\n'
  for cmd,s in [('symup','upright'),('symit','italic'),('symbfup','bold'),('symbfit','bolditalic')]:
   coverage+=s+': $'+chr(92)+cmd+'{'+CHARS+'}$'+r'\par'+'\n'
   coverage+='$x_{'+chr(92)+cmd+'{'+CHARS+'}}$'+r'\par'+'\n'
   coverage+='$x_{y_{'+chr(92)+cmd+'{'+CHARS+'}}}$'+r'\par\medskip'+'\n'
  coverage+=r'\end{document}';(work/'coverage.tex').write_text(coverage);command(['xelatex','-interaction=nonstopmode','-halt-on-error','coverage.tex'],work)
  log=(work/'coverage.log').read_text();assert 'Missing character:' not in log and 'Overfull' not in log
  command(['mutool','draw','-F','trace','-o',str(work/'coverage-trace.xml'),str(work/'coverage.pdf')])
  xml=ET.parse(work/'coverage-trace.xml');used=set()
  for span in xml.findall('.//span'):
   if 'BaskervilleCompanionMath' in span.attrib.get('font','') or 'Arena' in span.attrib.get('font',''):
    used.update(int(g.attrib['glyph']) for g in span.findall('g'))
  expected={f.getGlyphID(n):n for st in inv.values() for v in st.values() for n in [v['glyph']]+v['ssty']}
  missing=[n for gid,n in expected.items() if gid not in used];assert not missing,missing
  assert 0 not in used
  proof_checks[side]['exact_engine_ssty_selection']={'expected_roles':len(expected),'verified_roles':len(expected),'missing':missing,'glyph_id_trace':str(work/'coverage-trace.xml'),'audit_tex':str(work/'coverage.tex'),'audit_pdf':str(work/'coverage.pdf')}
 guides=measured_guides();grid(fonts,inv,['upright','italic'],guides,'Complete lowercase Greek — upright and italic').save(packet/'AB-grid-regular.png')
 grid(fonts,inv,['bold','bolditalic'],guides,'Complete lowercase Greek — bold and bold italic').save(packet/'AB-grid-bold.png')
 space_study(fonts,inv).save(packet/'AB-negative.png');details(fonts,inv).save(packet/'AB-forms.png');optical_sheet(fonts,inv,optical_actual).save(packet/'AB-optical.png')
 distance=Image.new('RGB',(1700,1240),'white');header(distance,'Distance and line colour','Unblurred fixed A4 pages reduced to 60 dpi equivalent (1/3 of the 180 dpi captures). No ink/width normalization.')
 d=ImageDraw.Draw(distance)
 for side,x in [('A',80),('B',920)]:
  label(d,(x,100),side,30);im=actual[side];im=im.resize((round(im.width/3),round(im.height/3)),Image.Resampling.LANCZOS);distance.paste(im,(x,145))
 distance.save(packet/'AB-distance.png')
 # True control is exactly identical pixels from a companion text region.
 control=actual['A'].crop((90,80,1320,230))
 for side in 'XY':control.save(packet/f'control-{side}.png')
 specs=[('A-natural','A-natural.png','Working-size reading proof','Continuous Baskerville article: 10.5/14 TeX pt body, 8 pt small-note; A4 at 180 dpi, same measure and content. Optical sheet also provides8/10/12pt scripts.'),('B-natural','B-natural.png','Working-size reading proof','Continuous Baskerville article: 10.5/14 TeX pt body, 8 pt small-note; A4 at 180 dpi, same measure and content. Optical sheet also provides8/10/12pt scripts.'),('AB-grid-regular','AB-grid-regular.png','Complete alphabet grid','Upright and italic; 130 px/em, fixed cells/origins. Measured companion x/p guides plus Greek ο top. Advance tick at actual hmtx advance.'),('AB-grid-bold','AB-grid-bold.png','Complete alphabet grid','Bold and bold italic; same 130 px/em fixed geometry.'),('AB-distance','AB-distance.png','Distance / text colour','Unblurred 1/3 Lanczos page reduction to 60 dpi equivalent. Simulated distance, not a physical reading study.'),('AB-negative','AB-negative.png','Counter and interletter white','170 px/em isolated forms, 160 px/em raw-advance strings. Cyan shows threshold128 enclosed white components (border flood excludes open apertures). Orange shows rowwise white between adjacent silhouettes over 0.08–0.90 of Greek ο height. Black natural forms remain visible; no width or density normalization.'),('AB-optical','AB-optical.png','Optical forms','Upper dedicated script-context pages at original 180 dpi; lower text/ssty/ssty2 outlines all at 180 px/em, no independent size normalization.'),('AB-forms','AB-forms.png','Direct confusable / variant comparison','190 px/em isolated confusables; 150 px/em variants; 112 px/em context strings. Both columns use identical scales, origins and content.'),('control-X','control-X.png','Identical control','Same pixels as control-Y; no font inference justified.'),('control-Y','control-Y.png','Identical control','Same pixels as control-X; no font inference justified.')]
 manifest={'images':[{'id':i,'path':p,'sha256':sha(packet/p),'mode':m,'description':desc} for i,p,m,desc in specs],'paired_comparison_image_id':'AB-forms','paired_comparison_image_ids':['AB-grid-regular','AB-grid-bold','AB-negative','AB-optical','AB-forms'],'control_image_ids':['control-X','control-Y'],'guide_definitions':guides,'point_convention':'TeX point = 1/72.27 inch','scope':'32 forms, four serif styles, existing ssty roles. Single XeLaTeX/FreeType render environment; no physical print or human reading validation.','specimen_source_sha256':sha(private/'A/proof.tex'),'optical_specimen_source_sha256':sha(private/'A/optical.tex'),'fixed_view_contract':'All entrants and matches reuse this article and diagnostic layout; A/B content differs only in neutral label and selected compiled font.'}
 (packet/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
 # Offline book includes original vector reading pages and every diagnostic PNG.
 book=private/'proof-book';book.mkdir()
 tex=r'\documentclass{article}\usepackage[a4paper,margin=0mm]{geometry}\usepackage{pdfpages,graphicx}\pagestyle{empty}\begin{document}'+'\n'
 for side in 'AB':tex+=r'\includepdf[pages=-]{'+str(private/side/'proof.pdf')+'}\n'
 for i,p,m,desc in specs[2:]:tex+=r'\clearpage\null\vfill\noindent\includegraphics[width=\paperwidth,height=.96\paperheight,keepaspectratio]{'+str(packet/p)+r'}\vfill\null'+'\n'
 tex+=r'\end{document}';(book/'proof-book.tex').write_text(tex);command(['xelatex','-interaction=nonstopmode','-halt-on-error','proof-book.tex'],book);shutil.copy2(book/'proof-book.pdf',private/'offline-proof.pdf')
 return key,{'pass':True,'renders':proof_checks,'offline_pdf':str(private/'offline-proof.pdf'),'guide_definitions':guides,'renderer_versions':{'xelatex':command(['xelatex','--version']).splitlines()[0],'pdftoppm':__import__('subprocess').run(['pdftoppm','-v'],capture_output=True,text=True).stderr.splitlines()[0]}}
