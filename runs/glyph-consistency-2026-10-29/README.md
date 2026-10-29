# Greek enlargement and vectorisation trial

Completed 2026-10-29. Built-in imagegen produced one fixed master and 32
independent glyph enlargements: **33 image calls, no retries or correction
calls**. Vector tracing and measurements were entirely local. All subagents
remain stopped. No font was promoted or compiled by this experiment.

## Inspect the results

- [Master PNG](master.png), [exact master prompt](master-prompt.txt).
- [All 32 enlargement comparisons](consistency.html), with source / registered
  enlargement / difference views and individual prompt links.
- [Measured before/after vectorisation](vectorisation.html), including actual
  filled SVGs and actual curve handles for six representative glyphs.
- [All 32 vector outlines, ZIP](vector-outlines.zip).
- [Registered vector specimen](vector-outlines/registered-specimen.svg).
- [Per-glyph requests and exact prompts](requests.json), [bounded contract](contract.json).

## Findings

All 32 requested enlargements completed. Median silhouette intersection over
union against the original master is **92.54%**, after translation and uniform
scaling only. Independent horizontal stretching is forbidden. No change in
counter count was detected when ignoring pinholes smaller than four master
pixels. Zeta, tau, theta, mu and kappa have the lowest overlap and are useful
first candidates for visual correction review.

The local Potrace benchmark tested alpha, beta, theta, nu, xi and omega:

| Input | Median overlap with its own input | Cubic segments per glyph |
| --- | ---: | ---: |
| Small master crop | 97.63% | 16–31 |
| Ordinary 8× Lanczos upscale | 99.62% | 96–294 |
| Image-model enlargement | 99.58% | 13–32 |

The enlarged clean targets are straightforward to trace faithfully with compact
curves. Ordinary upscaling preserved raster edge texture and produced many
extra segments under this configuration. This is one tracer and configuration,
not a survey or parameter optimization. Own-input overlap compares different
rasters at different resolutions; it is not a direct score of design quality.
The separate original-master metric in the interactive report measures drift
introduced by enlargement as well as tracing.

## Reproducible method and limits

Every image query received the same master plus its unaltered 144×216 cell
crop. No enlarged result was used as another glyph's reference. Master and
enlargement outputs are stored at their original generated resolutions.

`tools/glyph_consistency_report.py` measures silhouette overlap, symmetric
boundary distances, darkness error, area and aspect changes, counter count,
and a distance-transform thickness proxy. Registration uses bounded numerical
optimization followed by 8× rendering and Lanczos downsampling. It removes
individual framing and overall size differences; it cannot establish common
font metrics, baselines or spacing. Low-resolution master edges, raster gamma
and filtering impose measurement uncertainty. The thickness proxy is not a
typographer's stem-width measurement.

`tools/trace_glyph_trial.py` uses locally installed **potracelib 1.16** through
its [documented C API](https://potrace.sourceforge.net/potracelib.pdf): threshold
128, alphamax 1, curve optimization enabled, tolerance 0.0015 times input glyph
height, no despeckling, largest connected component selected. Cairo renders
the same cubic curves exported to SVG. Cubic joins have nearly identical
tangent directions, but continuous curvature is not guaranteed. Construction
views show calculated anchors and handles, not image-model annotations.

These are faithful raster-derived outline studies, not a finished font. Font
construction still requires shared metrics, spacing, optical correction,
working-size Baskerville text/math proofs and mathematical layout data. The
master's ordinary/variant epsilon and kappa, and possibly phi, are near
duplicates; raster fidelity does not verify their mathematical identities.

Three meaningful tests passed in `tests/test_glyph_consistency.py`: identical
raster registration, detection of independent width distortion, and Potrace
bit orientation/counter preservation on an asymmetric synthetic shape.
Runtime used project Pillow plus existing system NumPy, SciPy and Cairo;
no external tracing service or image-generation API was used for vector work.

`correction-prompt-template.txt` describes a possible third-generation edit
against the original source. It has **not** been executed. Further image calls
need a separately bounded scope.
