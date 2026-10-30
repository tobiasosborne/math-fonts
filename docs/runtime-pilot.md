# Hybrid Baskerville math runtime pilot

The runnable package combines the original, externally supplied four Storm
Baskerville 10 Pro files with the authored cubic CFF/MATH companion. The
companion contains six custom Greek letters and nine symbol/construction
roles, with finite growth variants. It contains no ordinary Latin or numeral
outlines. This is an end-to-end pilot, not full AMS coverage or an approved design.

Run from the repository with the existing Python environment and TeX Live:

```sh
.venv/bin/python tools/run_math_pipeline.py \
  --sources runs/pipeline-2026-10-30/font-sources.json \
  --glyph-run runs/pipeline-2026-10-30 \
  --output runs/pipeline-2026-10-30/rebuild-01 \
  --text-font-dir '/home/tobias/.local/share/fonts/Baskerville 10 Pro'
```

`--sources` supplies measured glyph registrations; omitting it deliberately uses
the provisional frozen small-root traces. It does not perform a new image call.
The output directory must be fresh. The run creates a public original font,
source/build manifests and audit summaries. All embedded-font PDFs, raster
proofs, logs, TeX sources, recorder files and detailed PDF text diagnostics stay
below the ignored `runtime/private/` directory. No Storm font is copied.

To audit an already-built OTF, use:

```sh
.venv/bin/python tools/proof_math_pilot.py \
  --font runs/pipeline-2026-10-30/font/BaskervilleCompanionMath-Pilot.otf \
  --output runs/pipeline-2026-10-30/proof-new \
  --text-font-dir '/home/tobias/.local/share/fonts/Baskerville 10 Pro'
```

The runner requires LuaLaTeX, XeLaTeX, MuPDF, pdffonts and pdftoppm. It pins all
four external Storm files by their recorded SHA-256 values; another revival or
synthetic style cannot silently substitute. The authored font must contain
MATH, declare the OpenType `math` script, and omit ordinary pilot Latin/numerals.
`unicode-math` otherwise silently loads Latin Modern when its initial font
fails the math-script check. Both GPOS and GSUB declarations are necessary for
the installed Lua and Xe loaders; the builder records a zero kern pair and an
empty GSUB script declaration, without claiming optical substitutions.

For a document, place `tex/` on TEXINPUTS and use explicit paths:

```tex
\documentclass{article}
\usepackage[
  mathfont={/absolute/path/BaskervilleCompanionMath-Pilot.otf},
  textfontdir={/external/path/Baskerville 10 Pro}
]{baskervillecompanionmath}
\begin{document}
An inline expression $\alpha+x_0^2$.
\[\int_0^1 f(x)\,\mathrm{d}x = \frac{\alpha+\beta}{\theta-\nu}\]
\end{document}
```

The loader owns `amsmath`, `fontspec` and `unicode-math`, selects all four
text faces by filename, and assigns explicit TU symbol families to bare Latin
letters and figures. It maps literal Unicode italic/bold/bold-italic Latin
back to the original Storm character slots. `\mathrm`, `\mathit`, `\mathbf`
and `\mathbfit` select original regular, italic, bold and bold-italic files.
Named operators use Storm regular. Scripts use the same original outlines at
smaller sizes; no optical-size glyphs or `ssty` feature are claimed.

The two-engine audit compiles a working-size page and an enlarged page, then
isolates each font role on its own unlabelled PDF page. MuPDF inspects actual
rendered glyph font names and sizes. A separate `pdffonts` check permits
exactly the intended five PostScript names. Nested scripts must exercise three
sizes. Every successful proof must have no missing-glyph log entry, and an
unsupported gamma must stop each engine with a missing-glyph error. No Latin
Modern Math, Computer Modern, MSAM or MSBM is permitted in rendered output.
The unsupported-symbol test is deliberately kept separate from the final proof.

Only the bounded corpus and named alphabet interfaces are proven. General
Unicode-math symbol-style selectors, full bold mathematics, arbitrary-size
assemblies and the AMS repertoire remain outside this pilot. Growing variants
are provisional scaled constructions; radical roof joins, accent positioning,
spacing and Greek weight still require visual engineering. The delivered
bounded proof fixes roof gaps, hat placement and under-enclosing parentheses;
those fixes are not a general acceptance of arbitrary-size constructions.
A clean technical
audit proves actual font sourcing and runnable layout, not typographic quality.
