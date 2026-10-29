# Full-component mathematical ink tracing

`tools/math_trace.py` is a bounded local engineering step, not a new design,
font, or promotion. It consumes a **caller-supplied clean ink ROI** and traces
all pixels with composited grayscale `< 128`. The caller must exclude labels,
guides, neighboring glyphs, and other unintended marks. The tracer cannot infer
which disconnected marks belong to a symbol.

```sh
.venv/bin/python tools/math_trace.py \
  --input /path/to/clean-roi.png \
  --output /path/to/fresh-artifact-directory
```

The output directory must not already exist. No historical scripts, source
images, or runs are modified. The output contains `filled.svg`, `handles.svg`,
`rerender.png`, `curves.json`, and `metrics.json`. The JSON retains the exact
Potrace curves and source byte hash. Handle drawings show the actual control
points used by both the SVG and Cairo rerender.

## Extraction and geometry contract

- Preserve the complete source canvas and source pixel coordinates: x right,
  y down. No automatic crop, EXIF orientation transform, registration,
  translation, independent scaling, component selection, or despeckling.
- Composite alpha on white **before** luminance conversion and thresholding,
  including palette transparency. Invisible black pixels remain white.
- Accept 1-bit, L, LA, RGB, RGBA, and palette inputs. Reject unsupported modes,
  multiple frames, empty ink, and invalid rendering/tracing parameters.
- Reject chromatic RGB by default: channel range greater than two after
  compositing requires explicit `--allow-color` luminance conversion. This is
  a declared conversion choice, not a guide-removal mechanism.
- Use Potrace with `turdsize=0`, `alphamax=1`, curve optimization, default
  minority turn policy, and default optimization tolerance 0.2 source pixels.
  `--tolerance-px` changes that tolerance; `--supersample` controls Cairo
  rendering/downsampling (default 4, allowed 1–16).
- Pack all rows into native unsigned-long words, with leftmost pixels at the
  most significant bits. Final-word padding does not change canvas width.

The Python functions `foreground`, `topology`, `trace_mask`, `trace_image`, and
`export` provide the reusable stages. They follow the repository's existing
`tools` import-path convention. `trace_image` returns `(paths, rerender, report)`.
Reusable C declarations, curve rendering, SVG export, and geometry measurements
are imported from `trace_glyph_trial.py`; its largest-component extraction,
`trace`, `fidelity`, and historical `main` are never called.

## Checks and practical limits

The report measures same-coordinate full-canvas IoU; grayscale RMSE over ink
union and full canvas; bidirectional boundary mean, p95, and maximum distance;
all component areas, boxes, centroids, and all counter areas. No one-pixel
component or counter is filtered out. Ink uses eight-connectivity and background
uses the dual four-connectivity. A white pad identifies exterior background,
even for ink touching the canvas edge.

Topology checks compare source/rerender component and counter counts and
positive/negative traced contours. Spatial overlap checks also require every
source component to overlap exactly one rendered component, and vice versa.
Thus an equal count cannot conceal a vanished dot replaced by an unrelated new
speck. Diagonal contacts and subpixel features still need inspection. These
checks establish measured mask/curve behavior; they do not recognize symbols.

CLI exit 0 means the topology checks pass. Exit 2 means diagnostic artifacts
were written but topology checks failed. Exit 1 reports invalid input or an
operational error. IoU is reported, not used as an automatic design-quality
acceptance threshold. Raster fidelity does not establish family consistency,
optical quality, or MATH/font engineering completeness.

Synthetic test measurements at supersample 8, tolerance 0.2, 197×143 source
pixels:

| Shape | Source/render components | Source/render counters | IoU | Boundary mean px |
| --- | --- | --- | --- | --- |
| equals | 2 / 2 | 0 / 0 | 1.0000 | 0.000 |
| dotted j | 2 / 2 | 0 / 0 | 0.9800 | 0.106 |
| three 16 px dots | 3 / 3 | 0 / 0 | 0.9400 | 0.238 |
| two components with three counters | 2 / 2 | 3 / 3 | 0.9886 | 0.092 |

The 16-pixel dot result exposes smoothing loss at small raster sizes; every dot
survives, but the outline is not pixel-identical. These are synthetic regression
fixtures, not evidence about the accepted family design. Additional tests cover
word-boundary orientation, asymmetric shapes, a single-pixel mark and counter,
canvas-edge and nested ink, transparency, color opt-in, real control handles,
missing/relocated marks, fresh outputs, and the actual CLI.

```sh
.venv/bin/python -m unittest discover -s tests -p test_math_trace.py -v
.venv/bin/python -m unittest discover -s tests -p test_glyph_consistency.py -v
```

## Dependencies and license compatibility

The wrapper requires Pillow, NumPy, SciPy, Cairo, and the installed Potrace C
API. The repository's existing explicit system-package fallback makes these
available to `.venv/bin/python` in this workspace; no package installation is
performed. The inspected runtime is Potrace 1.16. Its installed copyright file
(`/usr/share/doc/libpotrace0/copyright`) declares **GPL-2.0-or-later**, which
includes a GPLv3 option; this repository's `LICENSE` is AGPLv3. Preserve that
upstream license information when packaging the external runtime. This change
reuses C API declarations/export helpers and includes no Potrace tracing
implementation or inherited font outline data. It does not establish licensing
for arbitrary future image/font inputs.
