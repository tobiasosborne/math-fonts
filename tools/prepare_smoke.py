#!/usr/bin/env python3
"""Build one paired council fixture; never run or modify the archived builder."""
import hashlib
import json
import random
import shutil
import subprocess
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "runs/smoke-2026-10-29"
ARCHIVE = ROOT / "archive/2026-10-29-baskerville-companion-math"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def command(args, cwd=None):
    return subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True).stdout


def widen_operators(source, target):
    font = TTFont(source, recalcTimestamp=False)
    top = font["CFF "].cff.topDictIndex[0]
    cmap = font.getBestCmap()
    axis = font["MATH"].table.MathConstants.AxisHeight.Value
    # A deliberately bounded design hypothesis, not a typographic requirement:
    # 20% wider ink spans; retain 48-unit strokes and 65-unit sidebearings.
    width, advance, middle, half = 540, 670, 335, 24

    def rectangle(pen, x0, y0, x1, y1):
        pen.moveTo((x0, y0))
        for point in [(x1, y0), (x1, y1), (x0, y1)]:
            pen.lineTo(point)
        pen.closePath()

    changes = []
    for char in "+−=":
        name = cmap[ord(char)]
        pen = T2CharStringPen(advance, None)
        if char == "=":
            for center in [axis - 83, axis + 83]:
                rectangle(pen, 65, center - half, 65 + width, center + half)
        elif char == "−":
            rectangle(pen, 65, axis - half, 65 + width, axis + half)
        else:
            pen.moveTo((65, axis - half))
            for point in [(middle-half, axis-half), (middle-half, axis-225),
                          (middle+half, axis-225), (middle+half, axis-half),
                          (65+width, axis-half), (65+width, axis+half),
                          (middle+half, axis+half), (middle+half, axis+225),
                          (middle-half, axis+225), (middle-half, axis+half),
                          (65, axis+half)]:
                pen.lineTo(point)
            pen.closePath()
        top.CharStrings[name] = pen.getCharString(private=top.Private,
                                                globalSubrs=font["CFF "].cff.GlobalSubrs)
        old = font["hmtx"][name]
        font["hmtx"][name] = (advance, 65)
        accents = font["MATH"].table.MathGlyphInfo.MathTopAccentAttachment
        if name in accents.TopAccentCoverage.glyphs:
            accents.TopAccentAttachment[accents.TopAccentCoverage.glyphs.index(name)].Value = middle
        changes.append({"glyph": name, "character": char, "old_metrics": old,
                        "new_metrics": [advance, 65], "old_ink_width": 450,
                        "new_ink_width": width})
    font.save(target)
    # Verify the compiled result, including preservation of every other outline.
    old, new = TTFont(source), TTFont(target)
    assert old.getGlyphOrder() == new.getGlyphOrder()
    modified = {c["glyph"] for c in changes}
    old_glyphs, new_glyphs = old.getGlyphSet(), new.getGlyphSet()
    for name in new.getGlyphOrder():
        if name not in modified:
            from fontTools.pens.recordingPen import RecordingPen
            before, after = RecordingPen(), RecordingPen()
            old_glyphs[name].draw(before)
            new_glyphs[name].draw(after)
            assert before.value == after.value, name
            assert old["hmtx"][name] == new["hmtx"][name], name
    for name in modified:
        pen = BoundsPen(new.getGlyphSet())
        new.getGlyphSet()[name].draw(pen)
        assert pen.bounds[2] - pen.bounds[0] == width, name
    return changes


TEX = r"""\documentclass[10pt]{article}
\usepackage[a4paper,margin=20mm]{geometry}
\usepackage{fontspec,mathtools,unicode-math}
\setmainfont{Baskerville10Pro.otf}[Path=fonts/,ItalicFont=Baskerville10Pro-Italic.otf,BoldFont=Baskerville10Pro-Bold.otf]
\setmathfont{math.otf}[Path=fonts/,math-style=ISO,bold-style=ISO]
\pagestyle{empty}\setlength\parindent{0pt}
\newcommand\head[1]{\par\medskip{\large #1}\par\smallskip}
\begin{document}
{\LARGE Mathematical reading specimen}\par\smallskip
Text 10 pt; TeX points. Inspect at reading size and enlarged.
\head{P1.1 Reading texture}
Let $f\colon\mathbb R\to\mathbb R$ be smooth. The moments
$m_k=\int_0^\infty x^k f(x)\,\mathrm dx$ describe the distribution.
For $y=e^{-x^2}$, the equation $y'+2xy=0$ relates change and area.
If $\alpha>0$, dilation gives
\[\int_{-\infty}^{\infty}e^{-\alpha x^2}\,\mathrm dx=\sqrt{\frac\pi\alpha},
\qquad \widehat f(\xi)=\int_{-\infty}^{\infty}f(x)e^{-2\pi i x\xi}\,\mathrm dx.\]
Here roman prose, italic variables, figures and punctuation should form a
continuous reading rhythm. Compare $a-b=c$, $x+y=z$, $A=B+C$ and
$\alpha-\beta=\gamma$ in the same sentence, then read the paragraph again.
\head{P1.2 Alphabets and confusables, 12 pt}
{\fontsize{12}{16}\selectfont
Roman: Hamburgefontsiv 0123456789. \textit{Italic: Hamburgefontsiv fgjkpxyz.}\par
$\symup{\alpha\beta\gamma\delta\epsilon\zeta\eta\theta\iota\kappa\lambda\mu\nu\xi\pi\rho\sigma\tau\upsilon\phi\chi\psi\omega}$\par
$\symit{\alpha\beta\gamma\delta\epsilon\zeta\eta\theta\iota\kappa\lambda\mu\nu\xi\pi\rho\sigma\tau\upsilon\phi\chi\psi\omega}$\par
$\symbfup{\alpha\beta\theta\kappa\nu\xi\pi\rho\phi\psi\omega}\quad
\symbfit{\alpha\beta\theta\kappa\nu\xi\pi\rho\phi\psi\omega}$\par
$v\nu\quad w\omega\quad \epsilon\varepsilon\quad\theta\vartheta\quad
\kappa\varkappa\quad\phi\varphi\quad\rho\varrho\quad\pi\varpi$\par
$\Gamma\Delta\Theta\Lambda\Xi\Pi\Sigma\Upsilon\Phi\Psi\Omega\quad
\mathcal{ABC}\quad\mathfrak{ABC}\quad\mathbb{RNC}$\par}
\head{P1.3 Fitting and attachment, 10 pt}
$nnonn\quad oohoo\quad HHOHH\quad xv\nu x\quad \xi\xi\quad\zeta\xi\quad
\pi\tau\quad\mu\chi\quad 0123456789$\par
\[x_i^2\quad x_{i_j}^{k^\ell}\quad f_i^j\quad V_a\quad
\hat\alpha\quad\hat\xi\quad\hat\varphi\quad\overline{ABC}\quad\vec x\]
\head{P1.4 Composition}
\[\rho_{\mu\nu}=\sum_{k=0}^n a_{k\mu}a_{k\nu},\qquad
\frac{\partial\psi}{\partial t}=\alpha\nabla^2\psi-\beta\varphi+\epsilon\theta.\]
\[\left(\begin{matrix}a&b\\c&d\end{matrix}\right)
\begin{pmatrix}x\\y\end{pmatrix}=\begin{pmatrix}u\\v\end{pmatrix},\qquad
\frac{1+\frac{x^2}{y}}{1+\frac{z}{1+t}}\]
\newpage
{\LARGE Mathematical construction specimen}\par
\head{P2.1 Operators and relations at 8, 10 and 12 pt}
\newcommand\opline{$a-b=c\quad x+y=z\quad \alpha-\beta=\gamma\quad
1+2=3\quad A=B+C\quad x\pm y\le z\quad a\to b\Rightarrow c$\par}
{\fontsize{8}{11}\selectfont\opline}
{\fontsize{10}{14}\selectfont\opline}
{\fontsize{12}{17}\selectfont\opline}
\head{P2.2 Operator detail, 24 pt}
{\fontsize{24}{32}\selectfont $+\quad-\quad=\quad\pm\quad\to$\par
$x+y=z\quad a-b=c$\par}
\head{P2.3 Scripts at 8, 10 and 12 pt}
\newcommand\scripts{$x_{i_j}^{k^\ell}\quad\alpha_{i_j}^{k^\ell}\quad
\theta_i^2+\phi_j^2\quad\varkappa_{i_j}^{k^\ell}\quad\varpi_{i_j}^{k^\ell}$\par}
{\fontsize{8}{12}\selectfont\scripts}
{\fontsize{10}{15}\selectfont\scripts}
{\fontsize{12}{18}\selectfont\scripts}
\head{P2.4 Operators, limits and extenders}
\[\int_0^1 f(x)\,\mathrm dx\quad\iint_{\mathbb R^2}F\,\mathrm dA\quad
\iiint_\Omega\rho\,\mathrm dV\quad \sum_{i=0}^{n}a_i\quad\prod_{k=1}^n b_k\]
\[\sqrt{x}\quad\sqrt{\frac{1+x^2}{1+y^2}}\quad
\sqrt{\frac{1+\frac{x}{y}}{1+\frac{z}{t}}}\quad
\left\{\frac{1+\frac{x}{y}}{1+\frac{z}{t}}\right\}\]
\[\left(\vphantom{\frac{\dfrac{x}{y}}{\dfrac{z}{t}}}x\right)\quad
\underbrace{a+b+\cdots+z}_{n\text{ terms}}\quad\widehat{abcdef}\]
\head{P2.5 Longer reading line, 10 pt}
The equality $E=mc^2$ sits inside prose, whereas $a-b+c=d$ carries several
short signs. The distinction between $\nu$ and $v$, and between $\varrho$ and
$\rho$, must survive subscripts such as $\nu_i$ and $v_i$ without a dark patch.
\end{document}
"""


def main():
    if RUN.exists():
        raise SystemExit(f"Refusing to overwrite {RUN}")
    packet, private = RUN / "packet", RUN / "private"
    packet.mkdir(parents=True)
    private.mkdir()
    source = ARCHIVE / "build/BaskervilleCompanionMath-Regular.otf"
    base, trial = private / "incumbent.otf", private / "trial.otf"
    shutil.copy2(source, base)
    changes = widen_operators(base, trial)
    identities = ["incumbent", "trial"]
    random.Random(1029).shuffle(identities)
    images = []
    for side, identity in zip("AB", identities):
        work = private / side
        (work / "fonts").mkdir(parents=True)
        shutil.copy2(private / f"{identity}.otf", work / "fonts/math.otf")
        for font in (ARCHIVE / "smoketest/fonts").glob("Baskerville10Pro*.otf"):
            shutil.copy2(font, work / "fonts" / font.name)
        (work / "proof.tex").write_text(TEX)
        result = subprocess.run(["xelatex", "-interaction=nonstopmode", "-halt-on-error",
                                 "proof.tex"], cwd=work, capture_output=True, text=True)
        (work / "build-output.txt").write_text(result.stdout + result.stderr)
        if result.returncode:
            raise SystemExit(f"Proof failed: {work / 'build-output.txt'}")
        log = (work / "proof.log").read_text()
        assert "Missing character:" not in log, side
        assert "Overfull" not in log, side
        embedded = command(["pdffonts", str(work / "proof.pdf")])
        (work / "embedded-fonts.txt").write_text(embedded)
        assert "BaskervilleCompanionMath" in embedded, embedded
        assert "STIX" not in embedded, embedded
        command(["pdftoppm", "-r", "144", "-png", str(work / "proof.pdf"),
                 str(packet / side)])
        for page in (1, 2):
            path = packet / f"{side}-{page}.png"
            assert path.exists(), path
            images.append({"id": f"{side}-P{page}", "path": path.name, "sha256": sha(path)})
    from PIL import Image
    # Identical pair from a shape-rich region, separate from the scored A/B views.
    with Image.open(packet / "A-1.png") as page:
        crop = page.crop((90, 400, 1100, 850))
        for label in ["X", "Y"]:
            path = packet / f"control-{label}.png"
            crop.save(path)
            images.append({"id": f"control-{label}", "path": path.name, "sha256": sha(path)})
    for name, src in [("rubric.md", ROOT / "docs/rubric.md"),
                      ("judge-prompt.md", ROOT / "council/judge-prompt.md"),
                      ("sources.json", ROOT / "research/typography/sources.json")]:
        shutil.copy2(src, packet / name)
    contract = {"mode": "one paired smoke round", "successful_judge_calls_max": 3,
                "judge_attempts_max": 3, "automatic_retries": 0, "debate_rounds": 0,
                "candidate_edits_max": 1, "output_words_target_per_judge": 1800,
                "output_word_limit_is": "prompt instruction, not provider-enforced token cap",
                "token_usage": "record provider-reported usage when available; never infer it",
                "no_progress_stop": "stop after this round regardless of verdict",
                "members": {"opus": {"provider": "claudeAgent", "model": "claude-opus-5-5"},
                            "sol": {"provider": "codex", "model": "gpt-6.1-sol"},
                            "muse": {"provider": "muse", "model": "muse-wonder-full-1.0"}}}
    (RUN / "contract.json").write_text(json.dumps(contract, indent=2) + "\n")
    manifest = {"images": images, "dpi": 144, "tex_point_inches": 1 / 72.27,
                "engine": command(["xelatex", "--version"]).splitlines()[0],
                "renderer": subprocess.run(["pdftoppm", "-v"], capture_output=True,
                                            text=True).stderr.splitlines()[0],
                "pages_per_font": 2, "scope": "bounded fixture; not full repertoire, print or cross-engine certification",
                "image_access": "local paths via each delegate's image tool; must be verified per member",
                "blindness": "neutral labels and no parent history; shared checkout is NOT a sandbox boundary",
                "documents": {p.name: sha(p) for p in packet.glob("*.md")}}
    (packet / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    provenance = {"key": dict(zip("AB", identities)), "source_font": str(source.relative_to(ROOT)),
                  "source_sha256": sha(source), "incumbent_sha256": sha(base),
                  "trial_sha256": sha(trial), "changes": changes,
                  "hypothesis": "Wider +, minus and equals improve operator proportion and rhythm; preserve stroke weight and y positions.",
                  "status": "archived prototype used only as explicitly selected smoke fixture, not new project baseline",
                  "other_outlines_and_advances": "all verified unchanged"}
    (private / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
    print(RUN)


if __name__ == "__main__":
    main()
