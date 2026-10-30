# Greek baseline and height calibration

The user observed that the new Greek did not align with ordinary italic text.
The diagnosis confirmed floating body bottoms and inconsistent body heights.
The corrected experimental font is
[`delivery-01/font/BaskervilleCompanionMath-AMS.otf`](delivery-01/font/BaskervilleCompanionMath-AMS.otf),
SHA-256 `d8243c32fb19fdf3895ef46a9249f96d11bf2eb43db0b6a56c6bd793b55e7566`.
Earlier fonts, roots, enlargements and traces remain unchanged.

## Method and metric authority

[`design/greek-text-grid.json`](../../design/greek-text-grid.json) measures actual
Storm Baskerville 10 Pro Italic at 1,000 units/em: baseline 0, x-height 476,
cap height 723, ascender 744, descender −271, rounded lower overshoot −18 and
descender lower envelope −286. It also records the −12° reference slant and
the original font hash. See the full [grid method](../../docs/greek-text-grid.md).

`calibration-v1/calibration.json` records explicit optical similarities after
the unchanged image registration. Alpha/nu/omega use body extrema; theta uses
tall round extrema; beta/xi use reviewed body landmarks distinct from their
descending strokes. Uniform scaling preserves aspect, slant, curves and
topology. No isolated x/y warping or node cleanup occurs. A future Greek needs
its own reviewed anatomy landmarks rather than an automatic bounding-box fit.

## Verification and visual proofs

- `grid-audit.json`: actual compiled CFF landmarks meet their target lines
  within 0.02 units. This tests numeric placement, not perceptual perfection.
- `delivery-01/runtime/runtime-summary.json`: 296 isolated source/render checks
  on each engine, plus independent original-pilot regressions and hard missing
  symbol probes. The same authored 34 arrows are retained geometrically.
- `proof-02/summary.json`: original italic controls and compiled Greek share
  physical point size and TeX baseline at 10/7/5pt. Each state/engine has 42
  per-character source/size checks; nested scripts exercise three sizes in both
  faces. The baseline-origin spread is zero. Outline alignment is assessed
  independently on the grid; equal PDF origins alone would not prove it.
- Five new tests check actual landmarks, preserved aspect/contours and non-Greek
  geometry, matching font metadata, rejected stale inputs, bounded transforms,
  reproducible output and unchanged historical builds. Nine exporter regression
  tests also pass.

Open `proof-02/private/viewer.html` locally for interactive before/after grids,
actual math pages, removable horizontal/slant guides, zoom and negative space.
All outlines are drawn at one common em in the proof, with actual advances.
Guide-free and guided mathematical pages are separate files. Their rule
positions come from the actual TeX line baseline in em units, not raster guesses.

The proof contains licensed native outlines/embedded fonts, so SVG/PDF/PNG/HTML
proofs remain ignored under `private/`; public reports contain only measurements.
`proof-01` preserves the first successful horizontal-grid proof. `proof-02` adds
reference slant/advance guides; it uses the same corrected font.

## Reproduction and next-glyph gate

Use the commands in [the method](../../docs/greek-text-grid.md) and
[proof documentation](../../docs/greek-grid-proof.md) with fresh output paths.
`tools/run_math_ams.py` requires explicit `--calibration` for new work;
`--allow-uncalibrated` is reserved for reproducing historical output.

Font height/line metadata now matches the measured italic, while Windows
clipping extents still accommodate large math constructions. MATH accent
reference heights follow the text grid; the separate mathematical axis is
unchanged. Width rhythm, weight, slant, spacing and script optical drawings
remain separate design work. Full custom Greek/AMS coverage is still ongoing.
No model/image generation call was used for this correction.
