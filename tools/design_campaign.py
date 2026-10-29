#!/usr/bin/env python3
"""Reproducible, fresh design recipes and paired proof preparation.

The archived font is a selected input, never executable code or an output path.
"""
import argparse
import copy
import hashlib
import json
import math
import random
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import otTables

from prepare_smoke import TEX

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "archive/2026-10-29-baskerville-companion-math"
CAMPAIGN = ROOT / "runs/campaign-2026-10-29"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def command(args, cwd=None):
    p = subprocess.run(args, cwd=cwd, text=True, capture_output=True)
    if p.returncode:
        raise RuntimeError(p.stdout[-2000:] + p.stderr[-2000:])
    return p.stdout


def bounds(font, name):
    glyphs = font.getGlyphSet()
    p = BoundsPen(glyphs)
    glyphs[name].draw(p)
    return p.bounds


def install(font, name, pen, advance=800):
    top = font["CFF "].cff.topDictIndex[0]
    top.CharStrings[name] = pen.getCharString(private=top.Private,
                                            globalSubrs=font["CFF "].cff.GlobalSubrs)
    box = bounds(font, name)
    font["hmtx"][name] = (advance, round(box[0]))


def rectangle(pen, x0, y0, x1, y1):
    pen.moveTo((x0, y0))
    for point in [(x1, y0), (x1, y1), (x0, y1)]:
        pen.lineTo(point)
    pen.closePath()


def radical_pen(low, high, script=False, bottom=False, smooth=False,tall_weight=48):
    """Original outline: deliberate heavy check, light rise and a curved entry.

    The finite design retains the seed's em, advance, vertical extent and roof
    overlap. Script compensation expands only the inner boundary; no uniform
    geometric enlargement of the em is used.
    """
    shoulder = low + min(480, (high-low)*.55)
    pen = T2CharStringPen(800, None, roundTolerance=0)
    pen.moveTo((18, shoulder+15))
    pen.lineTo((100, shoulder+60))
    pen.curveTo((124, shoulder+76), (151, shoulder+64), (164, shoulder+36))
    pen.lineTo((355, low+18))
    pen.curveTo((361, low+5), (371, low), (384, low))
    pen.lineTo((402, low))
    connector_left=650-tall_weight
    if bottom:
        if smooth:
            pen.curveTo((650, low+1200), (650, low+1350), (650, low+1500))
        else:
            pen.lineTo((650, low+1500))
        pen.lineTo((650, high))
        pen.lineTo((connector_left, high))
        pen.lineTo((connector_left, low+1500))
        if smooth:
            pen.curveTo((connector_left, low+1350), (connector_left, low+1200), (379, low+164))
    else:
        height=high-low
        graded_width=40+(tall_weight-40)*max(0,min(1,(height-1188)/(2892-1188)))
        inner_x=650-graded_width-(5 if script else 0)
        if smooth and height>1600:
            pen.curveTo((650, low+.75*height), (650, high-.1*height), (650, high-48))
        else:
            pen.lineTo((650, high-48))
        pen.lineTo((835, high-48))
        pen.lineTo((835, high))
        pen.lineTo((inner_x if smooth else (605 if script else 610), high))
        if smooth and height>1600:
            pen.curveTo((inner_x, high-.1*height), (inner_x, low+.75*height), (379, low+164))
    if not (smooth and (bottom or high-low>1600)):
        pen.lineTo((374 if script else 379, low+164))
    pen.lineTo((232 if script else 226, shoulder+63))
    pen.curveTo((205, shoulder+109), (170, shoulder+130), (130, shoulder+114))
    pen.lineTo((18, shoulder+42))
    pen.closePath()
    return pen


def radicals_v1(font, smooth=False,tall_weight=48):
    v = font["MATH"].table.MathVariants
    name = font.getBestCmap()[0x221A]
    con = v.VertGlyphConstruction[v.VertGlyphCoverage.glyphs.index(name)]
    changed = []
    for record in con.MathGlyphVariantRecord:
        box = bounds(font, record.VariantGlyph)
        install(font, record.VariantGlyph, radical_pen(box[1], box[3],smooth=smooth,tall_weight=tall_weight))
        changed.append(record.VariantGlyph)
    base_bounds = bounds(font, name)
    for script_name in [name + ".ssty", name + ".ssty2"]:
        install(font, script_name, radical_pen(base_bounds[1], base_bounds[3], script=True,smooth=smooth,tall_weight=tall_weight))
        changed.append(script_name)
        new_con = copy.deepcopy(con)
        new_con.MathGlyphVariantRecord[0].VariantGlyph = script_name
        if script_name in v.VertGlyphCoverage.glyphs:
            v.VertGlyphConstruction[v.VertGlyphCoverage.glyphs.index(script_name)] = new_con
        else:
            v.VertGlyphCoverage.glyphs.append(script_name)
            v.VertGlyphConstruction.append(new_con)
    # OpenType Coverage tables must follow ascending glyph ID.
    ordered = sorted(zip(v.VertGlyphCoverage.glyphs, v.VertGlyphConstruction),
                     key=lambda pair: font.getGlyphID(pair[0]))
    v.VertGlyphCoverage.glyphs = [n for n, c in ordered]
    v.VertGlyphConstruction = [c for n, c in ordered]
    v.VertGlyphCount = len(ordered)
    for part in con.GlyphAssembly.PartRecords:
        pen = T2CharStringPen(800, None, roundTolerance=0)
        if part.glyph.endswith("bottom"):
            pen = radical_pen(0, part.FullAdvance, bottom=True,smooth=smooth,tall_weight=tall_weight)
        elif part.glyph.endswith("ext"):
            rectangle(pen, 650-tall_weight, 0, 650, part.FullAdvance)
        else:
            pen.moveTo((650-tall_weight, 0))
            for point in [(650, 0), (650, part.FullAdvance-48),
                          (835, part.FullAdvance-48), (835, part.FullAdvance),
                          (650-tall_weight, part.FullAdvance)]:
                pen.lineTo(point)
            pen.closePath()
        install(font, part.glyph, pen)
        changed.append(part.glyph)
    return sorted(set(changed))


def experimental_metadata(font, round_number):
    family=f"Baskerville Companion Math Experimental R{round_number}"
    ps=f"BaskervilleCompanionMath-ExperimentalR{round_number}"
    strings={1:family,2:"Regular",3:f"20261029:{ps}:0.{150+round_number}",
             4:family+" Regular",5:f"Version 0.{150+round_number}; PRIVATE EXPERIMENT 2026-10-29 R{round_number}",
             6:ps,16:family,17:"Regular"}
    for record in font["name"].names:
        if record.nameID in strings:
            record.string=strings[record.nameID].encode(record.getEncoding())
    top=font["CFF "].cff.topDictIndex[0]
    font["CFF "].cff.fontNames=[ps]
    top.FamilyName=family
    top.FullName=family+" Regular"
    top.version=f"0.{150+round_number}"
    font["head"].fontRevision=(150+round_number)/1000


def flatten(font, name):
    p = RecordingPen()
    font.getGlyphSet()[name].draw(p)
    points, start, current = [], None, None
    for op, args in p.value:
        if op == "moveTo":
            current = start = args[0]
            points.append(current)
        elif op == "lineTo":
            current = args[0]
            points.append(current)
        elif op == "curveTo":
            a, b, c, d = current, *args
            for i in range(1, 41):
                t, u = i/40, 1-i/40
                points.append(tuple(u**3*a[k]+3*u*u*t*b[k]+3*u*t*t*c[k]+t**3*d[k]
                                    for k in [0, 1]))
            current = d
        elif op == "closePath":
            if points[-1] != start:
                points.append(start)
    return points


def proper_cross(a, b, c, d):
    def cross(p, q, r):
        return (q[0]-p[0])*(r[1]-p[1])-(q[1]-p[1])*(r[0]-p[0])
    return cross(a,b,c)*cross(a,b,d)<-1e-5 and cross(c,d,a)*cross(c,d,b)<-1e-5


def validate_font(source, output, changed):
    before, after = TTFont(source), TTFont(output)
    assert before.getGlyphOrder() == after.getGlyphOrder()
    assert before.getBestCmap() == after.getBestCmap()
    ga, gb = before.getGlyphSet(), after.getGlyphSet()
    for name in after.getGlyphOrder():
        if name in changed:
            continue
        pa, pb = RecordingPen(), RecordingPen()
        ga[name].draw(pa)
        gb[name].draw(pb)
        assert pa.value == pb.value and before["hmtx"][name] == after["hmtx"][name], name
    for name in changed:
        pts = flatten(after, name)
        segs = list(zip(pts, pts[1:]))
        for i, (a,b) in enumerate(segs):
            for j, (c,d) in enumerate(segs):
                if j > i+1 and (i,j) != (0,len(segs)-1):
                    assert not proper_cross(a,b,c,d), (name,i,j)
    v = after["MATH"].table.MathVariants
    root = after.getBestCmap()[0x221A]
    mappings = {}
    for n in [root, root+".ssty", root+".ssty2"]:
        c = v.VertGlyphConstruction[v.VertGlyphCoverage.glyphs.index(n)]
        assert c.MathGlyphVariantRecord[0].VariantGlyph == n
        for rec in c.MathGlyphVariantRecord:
            box = bounds(after, rec.VariantGlyph)
            assert box[3]-box[1] == rec.AdvanceMeasurement
        assert c.GlyphAssembly and len(c.GlyphAssembly.PartRecords) == 3
        mappings[n] = [r.VariantGlyph for r in c.MathGlyphVariantRecord]
    c = v.VertGlyphConstruction[v.VertGlyphCoverage.glyphs.index(root)]
    parts = c.GlyphAssembly.PartRecords
    assert [p.FullAdvance for p in parts] == [1905,651,642]
    # Actual join rectangles coincide at both seams over full 300-unit connectors.
    for name, direction in [(parts[0].glyph,"end"),(parts[1].glyph,"both"),(parts[2].glyph,"start")]:
        box = bounds(after, name)
        if direction in ["both", "start"]:
            assert box[1] == 0
        assert box[3] == next(p.FullAdvance for p in parts if p.glyph==name)
    overlap = v.MinConnectorOverlap
    assert 0 < overlap <= min(p.EndConnectorLength for p in parts[:-1])
    assert all(p.StartConnectorLength == 300 for p in parts[1:])
    # Continuous achievable height intervals at one/two extender transition.
    one = (sum(p.FullAdvance for p in parts)-600, sum(p.FullAdvance for p in parts)-2*overlap)
    two = (sum(p.FullAdvance for p in parts)+651-900,
           sum(p.FullAdvance for p in parts)+651-3*overlap)
    assert two[0] <= one[1]
    connector_box=bounds(after,parts[1].glyph)
    connector_left,connector_right=connector_box[0],connector_box[2]
    return {"pass":True,"changed_glyphs":changed,"unrelated_outlines_and_metrics":"all unchanged",
            "cmap_and_glyph_order":"unchanged","self_crossings":"none in 40-step cubic flattening",
            "finite_and_script_mappings":mappings,"assembly_connector_x":[connector_left,connector_right],
            "min_connector_overlap":overlap,"one_extender_height_interval":one,
            "two_extender_height_interval":two,
            "assembly_seams":f"matching {connector_right-connector_left:g}-unit straight connectors, 300-unit overlap capacity",
            "limits":"Geometry and declared proofs, not a complete collision or arbitrary-engine certification"}


DETAIL = r"""
\newpage
{\LARGE Construction detail specimen}\par
\head{D1 Radicals at 8, 10 and 12 pt}
\newcommand\rootline{$\sqrt{x}\quad\sqrt{\alpha}\quad\sqrt{x^2+y^2}\quad
\sqrt{\frac{x+y}{z}}\quad x_{\sqrt{i}}^{\sqrt{k}}\quad x_{y_{\sqrt{i}}}$\par}
{\fontsize{8}{12}\selectfont\rootline}
{\fontsize{10}{16}\selectfont\rootline}
{\fontsize{12}{19}\selectfont\rootline}
\head{D2 Finite constructions, 22 pt}
{\fontsize{22}{29}\selectfont
$\sqrt{x}\quad\sqrt{\frac{1+x}{1+y}}\quad
\sqrt{\frac{\frac{1+x}{1+y}}{\frac{1+z}{1+t}}}$\par}
\head{D3 Tall construction boundary, 14 pt}
{\fontsize{14}{20}\selectfont
$\sqrt{\rule{0pt}{32pt}x}\quad\sqrt{\rule{0pt}{36pt}x}\quad
\sqrt{\rule{0pt}{40pt}x}\quad\sqrt{\rule{0pt}{44pt}x}\quad
\sqrt{\rule{0pt}{48pt}x}$\par}
\head{D4 Reading line, 10 pt}
For $\alpha>0$, the quantity $\sqrt{\alpha}$ remains positive. Compare
$\sqrt{x}$ and $\sqrt{x^2+y^2}$.\par
The nested expression is $\sqrt{1+\sqrt{1+\sqrt{x}}}$.\par
The small entries $x_{\sqrt{i}}$ and
$x_{y_{\sqrt{i}}}$ retain their mathematical identity in a full sentence.
\head{D5 Degree and nesting checks, 10 pt}
$\sqrt[3]{x}\quad\sqrt[n+1]{\frac{1+x}{1+y}}\quad
\sqrt{1+\sqrt[3]{1+\sqrt{x}}}\quad x_{\sqrt[3]{i}}$\par
"""


def build_proofs(run, source, candidate, seed):
    packet, private = run/"packet", run/"private"
    packet.mkdir()
    identities = ["incumbent", "candidate"]
    random.Random(seed).shuffle(identities)
    images = []
    for side, identity in zip("AB",identities):
        work=private/side
        (work/"fonts").mkdir(parents=True)
        shutil.copy2(source if identity=="incumbent" else candidate, work/"fonts/math.otf")
        for p in (ROOT/"fonts/private/text").glob("*.otf"):
            shutil.copy2(p,work/"fonts"/p.name)
        tex=TEX.replace(r"\end{document}",DETAIL+r"\end{document}")
        (work/"proof.tex").write_text(tex)
        command(["xelatex","-interaction=nonstopmode","-halt-on-error","proof.tex"],work)
        log=(work/"proof.log").read_text()
        assert "Missing character:" not in log and "Overfull" not in log
        embedded=command(["pdffonts",str(work/"proof.pdf")])
        (work/"embedded-fonts.txt").write_text(embedded)
        assert "BaskervilleCompanionMath" in embedded and "STIX" not in embedded
        command(["pdftoppm","-r","180","-png",str(work/"proof.pdf"),str(work/"page")])
        for page in [1,2]:
            dst=packet/f"{side}-{page}.png"
            shutil.copy2(work/f"page-{page}.png",dst)
            images.append({"id":f"{side}-P{page}","path":dst.name,"sha256":sha(dst)})
        # Detail is rerendered at 240 dpi and tightly cropped; never rescale A/B differently.
        command(["pdftoppm","-f","3","-singlefile","-r","240","-png",str(work/"proof.pdf"),str(work/"detail")])
        with Image.open(work/"detail.png") as page:
            cropped=page.crop((150,145,page.width-130,1700))
            dst=packet/f"{side}-detail.png"
            cropped.save(dst)
            images.append({"id":f"{side}-D","path":dst.name,"sha256":sha(dst)})
    paired_id=None
    if run.name!="round-1":
        paired_id="AB-D"
        dst=build_comparison(private,packet)
        images.append({"id":paired_id,"path":dst.name,"sha256":sha(dst)})
    with Image.open(packet/"A-1.png") as page:
        crop=page.crop((120,500,1370,920))
        for side in "XY":
            dst=packet/f"control-{side}.png"
            crop.save(dst)
            images.append({"id":f"control-{side}","path":dst.name,"sha256":sha(dst)})
    manifest={"images":images,"full_page_dpi":180,"detail_dpi":240,
              "detail_crop":"150,145 to page width minus130,1700; equal for A/B",
              "point_convention":"TeX point = 1/72.27 inch",
              "proof_ids":{"P1":"reading/alphabet/fitting/composition","P2":"operators/scripts/constructions","D":"D1 sizes, D2 finite, D3 tall boundary, D4 reading, D5 degrees/nesting"},
              "scope":"declared repertoire and single XeLaTeX engine; not print or complete coverage certification"}
    if paired_id:
        manifest["paired_comparison_image_id"]=paired_id
        manifest["paired_comparison_dpi"]=240
        manifest["paired_comparison_description"]="Direct side-by-side A/B at identical scale: finite22pt, tall14pt, scripts8pt; labels do not indicate chronology or preference."
    (packet/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    return dict(zip("AB",identities))


def build_comparison(private,packet):
    work=private/"comparison"
    (work/"fonts").mkdir(parents=True)
    for side in "AB":
        shutil.copy2(private/side/"fonts/math.otf",work/"fonts"/f"math-{side}.otf")
    for p in (ROOT/"fonts/private/text").glob("*.otf"):
        shutil.copy2(p,work/"fonts"/p.name)
    header=r"""\documentclass[10pt]{article}
\usepackage[paperwidth=190mm,paperheight=150mm,margin=10mm]{geometry}
\usepackage{fontspec,mathtools,unicode-math}
\setmainfont{Baskerville10Pro.otf}[Path=fonts/]
\setmathfont{math-A.otf}[Path=fonts/,math-style=ISO,bold-style=ISO]
\DeclareMathVersion{A}\DeclareMathVersion{B}
\setmathfont{math-A.otf}[Path=fonts/,version=A,math-style=ISO,bold-style=ISO]
\setmathfont{math-B.otf}[Path=fonts/,version=B,math-style=ISO,bold-style=ISO]
\pagestyle{empty}\setlength\parindent{0pt}
\begin{document}
{\large Direct construction comparison}\par\smallskip
Identical TeX point sizes and rendering scale on both sides.\par\medskip
"""
    body=r"""\begin{minipage}[t]{78mm}
\mathversion{SIDE}{\Large SIDE}\par\medskip
Finite construction, 22 pt\par\smallskip
{\fontsize{22}{30}\selectfont $\sqrt{x}\quad\sqrt{\frac{1+x}{1+y}}$\par}
\bigskip Tall construction, 14 pt\par\smallskip
{\fontsize{14}{20}\selectfont $\sqrt{\rule{0pt}{32pt}x}\quad\sqrt{\rule{0pt}{40pt}x}\quad\sqrt{\rule{0pt}{48pt}x}$\par}
\bigskip Script contexts, 8 pt\par\smallskip
{\fontsize{8}{12}\selectfont $\sqrt{x}\quad x_{\sqrt{i}}^{\sqrt{k}}\quad x_{y_{\sqrt{i}}}$\par}
\end{minipage}"""
    tex=header+body.replace("SIDE","A")+r"\hfill"+body.replace("SIDE","B")+r"\end{document}"
    (work/"comparison.tex").write_text(tex)
    command(["xelatex","-interaction=nonstopmode","-halt-on-error","comparison.tex"],work)
    log=(work/"comparison.log").read_text()
    assert "Missing character:" not in log and "Overfull" not in log
    command(["pdftoppm","-singlefile","-r","240","-png",str(work/"comparison.pdf"),str(work/"comparison")])
    with Image.open(work/"comparison.png") as page:
        box=page.convert("L").point(lambda x:255 if x<245 else 0).getbbox()
        box=(max(0,box[0]-24),max(0,box[1]-24),min(page.width,box[2]+24),min(page.height,box[3]+24))
        dst=packet/"AB-detail.png"
        page.crop(box).save(dst)
    return dst


def ensure_seed():
    path=ROOT/"fonts/private"
    (path/"text").mkdir(parents=True,exist_ok=True)
    seed=path/"BaskervilleCompanionMath-v0.150-seed.otf"
    if not seed.exists():
        shutil.copy2(ARCHIVE/"build/BaskervilleCompanionMath-Regular.otf",seed)
    for p in (ARCHIVE/"smoketest/fonts").glob("Baskerville10Pro*.otf"):
        if not (path/"text"/p.name).exists():
            shutil.copy2(p,path/"text"/p.name)
    for name in ["SOURCE-NOTICES.txt","STIX-OFL.txt"]:
        if not (path/name).exists():
            shutil.copy2(ARCHIVE/"build"/name,path/name)
    return seed


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--round",type=int,required=True)
    parser.add_argument("--input",type=Path)
    args=parser.parse_args()
    if args.round not in [1,2,3]:
        raise SystemExit("Later rounds require a new explicit recipe after council feedback")
    source=args.input or ensure_seed()
    run=CAMPAIGN/f"round-{args.round}"
    if run.exists():
        raise SystemExit(f"Refusing to overwrite {run}")
    (run/"private").mkdir(parents=True)
    snapshots={}
    for source_path,name in [(ROOT/"tools/design_campaign.py","design_campaign-at-build.py"),
                             (ROOT/"tools/prepare_smoke.py","prepare_smoke-at-build.py"),
                             (ROOT/f"design/round-{args.round}.json","recipe-at-build.json"),
                             (ROOT/"council/requirements-smoke.txt","requirements-at-build.txt")]:
        destination=run/"private"/name
        shutil.copy2(source_path,destination)
        snapshots[name]=sha(destination)
    candidate=run/"private/candidate.otf"
    font=TTFont(source,recalcTimestamp=False)
    changed=radicals_v1(font,smooth=args.round>=2,tall_weight=60 if args.round==3 else 48)
    if args.round>=2:
        experimental_metadata(font,args.round)
    font.save(candidate)
    report=validate_font(source,candidate,changed)
    (run/"private/engineering.json").write_text(json.dumps(report,indent=2)+"\n")
    key=build_proofs(run,source,candidate,20261029+args.round)
    recipe=json.loads((ROOT/f"design/round-{args.round}.json").read_text())
    (run/"private/provenance.json").write_text(json.dumps({"key":key,"input":str(source),
        "input_sha256":sha(source),"candidate":str(candidate),"candidate_sha256":sha(candidate),
        "recipe":recipe,"changed_glyphs":changed,"engineering_pass":report["pass"],
        "build_snapshot":snapshots},indent=2)+"\n")
    print(run)


if __name__=="__main__":
    main()
