# Upright A — first pilot enlargement

One built-in imagegen call, no retry or correction. References: the approved
single unified root, its exact unaltered A crop, and substantial actual Storm
samples as context. The new outline is not copied from a reference font.

The enlarged A preserves the source's two stems, triangular counter and serif
logic. Full-component Potrace tracing preserves its one component and one
counter; native-input overlap is 99.83% with 27 cubic segments. The filled SVG,
real handles, curves and rerender are under `trace/`.

Registered master overlap is 88.17%, mean boundary distance 0.82 source pixels,
p95 2 pixels, aspect change +2.67% and ink area +5.33%. Visual inspection of
`comparison.png` confirms a lower crossbar, slightly broader proportions and
serif/edge drift. These metrics compare the enlargement to the root; they are
different from tracing accuracy and are not typeface grades. Registration used
one uniform scale and translation; no independent width stretch.

Keep as a **pilot candidate**, not a release-accepted glyph. Test the deviations
in a root-aligned font proof before deciding whether a bounded image correction
or local optical edit is warranted. Do not declare it perfected or silently
replace the root with its new proportions. No correction call is spent now.

The source is connected, so the existing connected-only registration routine
is valid here. It is NOT valid for future equals/disconnected targets; those
need full-component registration while tracing already preserves all components.
Both original RGB images remain unchanged; tracing explicitly uses luminance
conversion and records it in metrics. No guides are flattened into the ink.
