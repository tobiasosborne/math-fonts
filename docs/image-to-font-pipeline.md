# Unified-image-to-math-font pipeline

Status: adopted project pipeline and first north star, 2026-10-29.
The accepted design is the current Greek image-derived family. Its expansion
must produce a coherent Baskerville mathematics package. Neither the rejected
arena fonts nor warped inherited outlines are its geometry source.

## Governing invariant: one unified design image

**Everything starts from one approved unified design image.** The current
[Greek master](../runs/glyph-consistency-2026-10-29/master.png) is the accepted
seed. The next design deliverable is a family-wide composition expanding that
same design: Baskerville text, realistic mathematics, alphabets, symbols,
delimiters and their shared construction language in one visual authority.

The package-wide image does not exist yet. Do not claim that the present
32-glyph sheet already covers it. Preserve the seed, expand it deliberately,
and approve a versioned root image before producing the broader repertoire.

1. Pin the actual Baskerville text reference, sizes, styles and file hashes.
2. Integrate the accepted Greek seed into the unified family composition.
   Preserve its character rather than starting another foundry direction.
3. Review the whole composition for weight, contrast, stress, slant, terminals,
   proportions, text/math colour and negative space. Correct the composition
   as a whole before treating its parts as authoritative.
4. Freeze the root PNG, dimensions, hash, source references, prompt and decision.
5. Every category sheet, glyph enlargement, correction, optical-size design
   and assembly design must refer back to this same root version. Production
   sheets are crops or explicitly derived views, never competing design roots.
6. A visual change outside the root's approved design grammar requires a new
   root revision and an impact list. Do not silently drift the design glyph by
   glyph. Keep older roots and all lineage records.

A full mathematical repertoire cannot be legibly inspected as thousands of
tiny marks in one ordinary image-model output. Use a large unified master
atlas with legible derived crops and an accompanying coverage index. Extend
that same composition in controlled stages, carrying approved anchors and the
full root reference into every expansion; review the assembled whole before
freezing a new version. A lower-resolution whole-family view and exact crops
serve different purposes, but identify the same root image. No glyph advances
to production simply because an independently generated category sheet looks
attractive. If it is absent from the approved atlas, it is still undesigned.

## The proven experiment

Evidence: [trial README](../runs/glyph-consistency-2026-10-29/README.md),
[requests/prompts](../runs/glyph-consistency-2026-10-29/requests.json),
[measurements](../runs/glyph-consistency-2026-10-29/measurements.json),
[tracing benchmark](../runs/glyph-consistency-2026-10-29/vector-trial/summary.json).

- One fixed 1254×1254 master; 32 unaltered 144×216 cell crops.
- Each enlargement received the same whole master plus its own exact crop.
  No prior enlargement became the sole reference for the next glyph.
- 32 independent enlargements, each one filled glyph on white, no labels or
  imaginary handles; original generated PNGs retained without upscaling.
- 33 image calls total including the master, no retries or corrections.
- Translation/uniform-scale registration only: no independent width stretch.
- Median enlargement/master silhouette overlap 92.54%; no detected counter
  count changes after ignoring pinholes below four master pixels.
- Six-glyph Potrace benchmark: generated-input median overlap 99.58%, with
  13–32 cubic segments; small-input median 97.63%. These compare different
  native-resolution inputs and do not measure typeface quality.
- Actual cubic traces, actual anchor/handle constructions and 32 SVG exports.
  Smooth tangent joins do not establish curvature continuity or good drawing.

The current epsilon/kappa variants and possibly phi variants are near
duplicates. Preserve them as evidence but resolve intended forms and Unicode
semantics in the unified master before accepting their production mappings.
The prompt requested regular italic, while the accepted output looks heavy.
Its weight remains uncalibrated. Compare at matched apparent size with actual
Storm regular italic and bold italic before assigning a weight or designing
companion styles; do not silently thin the accepted design.

## Production stages and records

### A. Reference and master

Keep text-font identity separate from the newly authored math outlines.
Baskerville text proves compatibility; it is not a license to redistribute
source fonts. Exact text identity and hashes belong in the project manifest.
The master fixes the family, including italic/upright/bold logic and examples
of script-scale treatment, extensible parts and display-size large operators.
Explicitly identify design evidence, approval and unresolved forms.

**Required substantial text reference:** supply the actual rendered Storm
Baskerville 10 Pro sample, not its name alone. The local 2560×4800 reference
contains original prose paragraphs, capitals/lowercase, figures, punctuation
and native Greek in all four actual faces. Keep the whole page for text colour
and unaltered face crops for readable detail. Generate it reproducibly with:

```sh
.venv/bin/python tools/make_baskerville_reference.py \
  --font-dir '/home/tobias/.local/share/fonts/Baskerville 10 Pro' \
  --output /tmp/storm-baskerville-reference
```

The saved local reference is in
`fonts/private/reference-specimens/storm-baskerville-2026-10-29/` with a
manifest of font hashes and crop coordinates. Its public project record is
[Storm reference contract](../design/storm-reference.json). The design prompt
must include this reference alongside the accepted seed or approved root;
production enlargements retain the root as geometry authority and use the
text reference for family calibration. See the
[master prompt template](../design/prompts/unified-master-template.txt).

**Guidelines are removable data:** retain a clean raster and a separate thin,
colour-coded overlay plus an explicit mask and coordinate manifest. The
reference sheet includes baseline/x-height/cap-height guides on sample lines,
calculated from the source font metrics. The math axis, overshoots, slant and
shared cell metrics belong to the future approved math master; do not infer
them from decorative image-model lines. Prompt previews can show guides, but
the expected filled output remains clean. Trace the saved clean glyph, never
erase a flattened guide mask through its silhouette: a guide crossing ink
would destroy real shape information. Keep labels in excluded gutters.

### B. Specimen crops and enlargement

Maintain a semantic glyph inventory, Unicode/command mapping, root hash and
root/cell coordinates. Preserve an unaltered crop for each target. Include the
root and exact crop in every enlargement query. Ask for a faithful filled
silhouette, original high resolution, ample whitespace, common cell geometry,
no labels, annotations, handles, texture or redesign. Preserve raw outputs,
exact prompts, references, per-query ledger and tool metadata. Do not report
quota usage that the tool does not expose.

### C. Image registration and consistency review

Align using one scale and translation, never elastic warping or separate width
fitting. Keep unregistered placement information separately for font fitting.
Measure silhouette intersection-over-union, symmetric boundary mean/p95/max,
gray-edge error, area, aspect, counters and component counts. Review diagnostic
overlays at master scale and enlarged scale, plus negative space and text-size
proofs. Distance-transform thickness is a proxy, not stem-width ground truth.

Treat measurements as a discrepancy map, not a typographic grade. The source
has limited resolution; resampling, gamma and antialiasing influence values.
Set per-category acceptance tolerances after a small calibration batch;
do not blindly use one IoU threshold for an iota, an arrow and a radical.

### D. Faithful local tracing

Current tested recipe: Potrace 1.16, grayscale threshold 128, alphamax 1,
curve optimization on, tolerance 0.0015×ink height, no despeckling. Render the
same exported curves through Cairo at high resolution and downsample. Compare
to both the enlargement and the original master crop. Export filled SVG,
real handles, component/counter topology and geometry metrics.

**Current limitation:** the experimental tracer retains the largest connected
component. That is acceptable only for the inspected connected Greek targets.
Before dotted letters, equality signs, colon, disjoint arrows, ellipses or
other disconnected mathematics, implement foreground extraction that preserves
all intended ink and rejects labels through known crop regions. Test disconnected
forms, holes and isolated dots. The durable exporter fails on discarded dark
components rather than treating the current algorithm as a general tracer.

### E. Optical drawing and font construction

Keep raw tracing separate from edited production outlines. Record every optical
edit with intent, before/after overlays and working-size evidence. Resolve
extrema, unnecessary nodes, overshoots, curvature, hairlines, joins and terminal
behaviour. Recover shared baseline/x-height/cap height, sidebearings, slant and
weight from the family master, not individually normalized black boxes.

Construct explicit styles and script treatments; do not get bold by arbitrary
stroke expansion or condensed script shapes by width scaling. Derive growth
rules and pieces for delimiters, radicals, accents and arrows from the same
root. Build Unicode mapping, font names/metrics and OpenType MATH data. A
collection of faithful SVGs is an intermediate artifact, not a math font.

### F. Rendering and acceptance

Compile a new standalone math OTF and package wrapper; see
[engineering](math-package-engineering.md) and [package plan](baskerville-math-plan.md).
Prove all named commands and encoded slots, then real formulas with Baskerville
text in LuaLaTeX and XeLaTeX. Check display/text/script/scriptscript sizes,
stretching and unusual combinations. Inspect ordinary reading size, distant
page colour, large drawings, inverted negative space and common-scale grids.
Treat missing glyphs, hidden fallback or broken assemblies as rendering failures.
Retain human review of design and mathematical identity alongside numeric tests.

## Reproduce the saved vector result without changing evidence

From the repository root, with the observed dependencies available:

```sh
.venv/bin/python tools/export_glyph_vectors.py \
  --run runs/glyph-consistency-2026-10-29 \
  --output /tmp/baskerville-greek-reproduction
```

The output directory must not exist. The command validates frozen master,
unaltered crops, prompt records and generated-image hashes before tracing. It
creates individual filled and handle SVGs, a registered specimen, a manifest
and ZIP. It does not call an image model. On the observed environment it
reproduced all 32 filled and 32 handle SVGs **byte for byte**; see
[verification](../runs/pipeline-reproduction-2026-10-29/verification.json).
The registered specimen is for visual comparison and is not shared font metrics.

Observed dependencies are recorded in
[environment manifest](../design/pipeline-environment-2026-10-29.json): Python,
Pillow, NumPy, SciPy, Pycairo/native Cairo, fontTools and native potracelib.
The older experimental scripts have fixed paths and write into their original
run directories: do not rerun their `main` entry points over frozen evidence.
Images are retained inputs; replaying a prompt is not deterministic reproduction.

## Bounded campaigns

Every production batch fixes glyph IDs, root version, image-call cap, correction
cap, deadline and stop conditions before starting. Default is one enlargement
per target, no automatic image retry, and local tracing/measurement first.
Reserve an explicitly capped correction pool for demonstrated drift. Corrections
use the original root/crop as authority, the current enlargement as edit target,
specific visible discrepancies and protected good regions. Re-evaluate against
the original and retain the best accepted result, not simply the newest one.

An optional council gives one constructive critique per checkpoint, with a
fixed number of judges and no retry/debate loop. Its scores cannot waive glyph
coverage, identity, technical rendering or the single-root invariant. No new
generation or council campaign is launched by recording this plan.

## Authorities and audit

- [Potrace algorithm](https://potrace.sourceforge.net/potrace.pdf) and
  [library API](https://potrace.sourceforge.net/potracelib.pdf).
- [OpenType MATH](https://learn.microsoft.com/en-us/typography/opentype/spec/math).
- [Primary-source typography evidence](../research/typography/README.md).
- [Read-only pipeline audit](pipeline-audit.md); its missing-exporter finding
  was resolved by the exporter and 64-file reproduction check above. Broader
  component handling and font construction remain future work.
