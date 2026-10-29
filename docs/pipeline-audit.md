# Image-derived design pipeline: evidence and reproducibility audit

Audit of the existing trial, 2026-10-29. This is a read-only assessment of its
artifacts and scripts, not a new design, image generation, font build, or quality
certification. The accepted visual direction is the starting point for a unified
Baskerville mathematics package; the present studies are not a completed font.

## What the evidence actually shows

The [Greek master](../runs/glyph-consistency-2026-10-29/master.png) has a
coherent italic, high-contrast family character. Its SHA-256 is
`7538ac467dc73705b289ea99937d6d659c01cff5052d20b212fffc77ed4af98e`,
matching the existing contract. Visually inspected the master and the separate
alpha, theta, zeta and omega enlargements: the shapes retain the characteristic
slanted forms and contrasting strokes, with alpha's open tail, theta's crossbar,
zeta's long sweep and omega's paired bowls. Inspected the actual rendered
alpha, theta and omega benchmark curves and a rendering of the delivered zeta
SVG: they closely resemble their respective enlarged inputs at display scale.
This visual inspection does not establish that all characters are correct or
that these shapes will work at text sizes.

The [trial README](../runs/glyph-consistency-2026-10-29/README.md) records 33
image calls, no retries, 32 independent enlargements, and the local tracing
benchmark. Its 92.54% median master overlap measures registered raster
consistency; the six-glyph own-input trace overlap is a different measurement.
Neither measures design quality, semantic correctness, common metrics, spacing,
or rendered mathematical layout. Uniform registration deliberately discards
per-image position and scale. The small master and image reconstruction limit
the accuracy with which original details can be inferred. Potrace cubic joins
are nearly tangent under the recorded metric, but curvature continuity is not
guaranteed. The filled outputs and handle views are real vector studies, not
evidence of a compiled or promoted font.

## One family root

The next visual design stage must have **one approved unified master composition**
as the family-wide root. The current Greek master and outlines are immutable,
accepted design evidence to integrate into that composition, not a separate
competing family root. Freeze the new root file, exact prompt, references,
dimensions, approval state and SHA-256 in a versioned manifest. Every subsequent
visual generation must include that same root as a reference. Category sheets
and glyph enlargements are derived production aids, with their crop coordinates,
source hashes, prompt and output hash recorded; they do not become independent
design roots. Avoid chaining a prior enlargement as the sole design reference.
Record any deliberately revised root as a new version with a reason and review,
never by silently replacing the approved file. The first unified root remains to
be made; the Greek master alone does not cover the entire proposed package.

Measurement can identify a discrepancy, but must not silently redesign a glyph.
Maintain separately the immutable source, raw trace and each explicitly described
optical or semantic edit, with before/after overlays, geometry and working-size
proofs. Preserve a decision record describing intent and the deviation from the
source. A more conventional symbol cannot simply be substituted under a fidelity
label. Epsilon and variant epsilon, kappa and variant kappa, and possibly phi and
variant phi are near duplicates in the Greek master. Determine their intended
mathematical identities and mappings explicitly before font integration; high
trace fidelity can faithfully preserve a mistaken or ambiguous distinction.

## Reproduction boundaries

- [Measurement code](../tools/glyph_consistency_report.py) uses a fixed run
  directory and reads absolute `crop` and `folder` paths in `requests.json`;
  copying the project elsewhere requires path remapping. Its main routine writes
  comparisons, registered images, metrics and the aggregate report into the
  original run. Do not run it against the immutable evidence. It retains only
  the largest connected dark component, which is unsuitable without review for
  disconnected marks and many mathematical symbols.
- [Trace code](../tools/trace_glyph_trial.py) exposes reusable trace and SVG
  functions, but its command-line main is hard-coded to six benchmark glyphs
  and writes into the original `vector-trial` directory. The tools searched do
  not contain a dedicated all-32 export entry point or the combined specimen
  assembly command. The 32-output [manifest](../runs/glyph-consistency-2026-10-29/vector-outlines/manifest.json)
  records input/output hashes and geometry, but alone is not an executable
  recipe for reproducing the export. Verify reconstructed outputs against it in
  a new directory rather than overwriting the historical run.
- The scripts rely on Pillow, NumPy, SciPy, Cairo Python bindings, a discoverable
  native Potrace library and a system DejaVu font for labels; the code appends
  `/usr/lib/python3/dist-packages` and assumes the given font path. The recorded
  tracing library is potracelib 1.16. Capture exact package, Python, native
  library and platform versions, configuration and command line in a portable
  environment manifest; do not assume hashes will match across versions.
- The three existing tests cover identical registration, detection of width
  distortion, and an asymmetric counter and orientation through Potrace/Cairo.
  They do not validate all 32 exports, complex multi-component glyphs, font
  semantics or final typesetting. Replaying image generation is not guaranteed
  to regenerate the same images; retain the image outputs themselves as inputs.

## Bounded next work

1. Prepare and approve the single family root using the accepted Greek evidence;
   freeze identity and lineage before category production.
2. In a separate working directory, make an explicit all-glyph exporter with
   input/output paths, dependencies and parameters captured, then compare
   source and SVG hashes and geometry with the existing manifest. Report any
   mismatch; do not rewrite the archived evidence.
3. Extend component handling and tests for disconnected forms, holes and
   mathematical marks before applying the trace procedure to broader coverage.
4. Make a small proof set with shared scale, baseline, spacing and real
   Baskerville text/math at working and enlarged sizes, including semantic
   variant comparisons. Document optical changes and evaluate them in context
   before treating them as font-ready. Broader AMS coverage and OpenType MATH
   engineering require their own explicit inventory and implementation work.
