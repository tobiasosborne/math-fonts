# Working unified-image → hybrid math-font pipeline

This run completes the bounded **end-to-end pilot**. It is not the complete
AMS family or final typographic approval.

## Concrete delivery

- [Authored OpenType math font](delivery/font/BaskervilleCompanionMath-Pilot.otf),
  [build/source manifest](delivery/font/build-manifest.json),
  [compiled vector specimen](delivery/font-specimen.svg).
- [Both-engine outcome](delivery/summary.json) and
  [actual-font-use audit](delivery/runtime/summary.json).
- [Six source/enlargement comparisons](consistency-contact.png),
  [per-glyph metrics](glyph-metrics.json) and [registered sources](font-sources.json).
- Local interactive proof: `delivery/runtime/private/viewer.html`.
  Both-engine reading/enlarged PDFs and 300dpi pages are in the same private
  tree. These embed or render the supplied commercial text face and are not
  published in the public repository.

The custom CFF/MATH OTF has 33 glyphs: six Greek roles, nine mathematical base
roles and provisional derived growth forms, plus space/notdef. Ordinary Latin
letters and numerals come from the **original external Storm Baskerville**
faces. They were not redrawn, copied into this OTF or substituted by another
math font. The old A/H/O image experiments are not used.

## Rebuild locally

```sh
.venv/bin/python tools/run_math_pipeline.py \
  --sources runs/pipeline-2026-10-30/font-sources.json \
  --glyph-run runs/pipeline-2026-10-30 \
  --output /tmp/baskerville-math-rebuild \
  --text-font-dir '/home/tobias/.local/share/fonts/Baskerville 10 Pro' \
  --dpi 300
```

Output must be fresh. This command consumes retained vector/registration
sources, builds the OTF, compiles both engines, audits actual rendered glyph
fonts, and creates the interactive viewer. It performs **no new image calls**.
Requirements: the existing Python environment (fontTools/Pillow), LuaLaTeX,
XeLaTeX, MuPDF, pdffonts/pdftoppm and the four external text faces pinned by
hash. Tracing additionally uses NumPy/SciPy/Cairo and native Potrace 1.16.
The observed environment is recorded in `design/pipeline-environment-2026-10-29.json`.

For the assistant-controlled raster stage, `tools/pipeline_glyph.py prepare`
saves the exact prompt/references and counts dispatch before built-in imagegen;
`record` retains its original PNG; `analyze` uniformly registers, traces,
compares, and emits the measured font-source override. It never makes API calls.
Six fixed Greek targets were enlarged once each, with no retries/corrections.
Each references the SAME unified root, its unaltered crop and substantial
actual Storm samples. Raster-generation replay is not deterministic; retain
the originals. This run used six image calls; the earlier four remain counted
separately and unchanged.

## Technical validation and visual review

- All six enlarged-input traces retain their measured components/counters.
  Master drift is shown explicitly and is not hidden by width fitting.
- Both LuaLaTeX and XeLaTeX pass **20 isolated actual-font role checks each**,
  including ordinary variables/figures, four alphabet faces, styled Unicode,
  named operators, custom Greek, nested scripts and growing constructions.
- Rendered output contains exactly the intended four Storm faces and the
  authored companion. Unsupported gamma fails explicitly rather than silently
  obtaining a glyph from Latin Modern Math or AMS fonts.
- Both reading and enlarged pages were visually inspected. This exposed and
  corrected issues that compile success did not detect: radical roof gaps,
  displaced/overlapping hats and undersized Lua delimiters around a nested
  fraction. The local engineering derivatives and MATH values are recorded.
- Script declarations in both GSUB and GPOS prevent loader-specific fallback.
  The zero GPOS pair and empty GSUB declare math capability without claiming
  optical substitutions or copying another font's layout tables.
- Unit checks cover actual cubic outlines, registration, MATH references,
  component/counter preservation, reproducible font binaries, quota timeout
  cleanup and pace gates. Actual-engine checks are separate from design grades.

## Remaining work

The family remains partial: Greek weight/spacing and the alpha/omega shape
drift need optical review; this small set of mathematical signs is not equivalent
to the AMS repertoire. Large forms are finite derived proof placeholders,
not arbitrary-size assemblies or finished optical masters. Scripts reuse
scaled outlines, and there is no full bold math face. Lua/Xe choose different
delimiter sizes in some cases. Final visual acceptance and complete AMS
coverage remain future work.

Next useful extension is a source/reuse audit for ordinary signs, then full
Greek/variant coverage and proper growing-part assemblies from the SAME root,
with regression proofs retained. No further image generation is implied by
this run's completed six-call contract.
