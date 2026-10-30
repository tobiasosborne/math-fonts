# Shared authored arrow grammar

The first family contains 34 finite arrows generated from one shaft, one curved
open chevron and its two exact half-heads. It is provisional authored vector
work, not a raster fit or optical acceptance. The configurable source is
[`design/arrow-grammar.json`](../design/arrow-grammar.json); the implementation is
[`tools/build_math_arrows.py`](../tools/build_math_arrows.py).

The visual calibration is only the ordinary right-arrow cell in the last row
of the active unified descendant image
`runs/ams-coverage-2026-10-30/master-v2/candidate-01/master.png`, SHA-256
`edfb27bedf078bcba86d18112c15d4f03bc25b2bdc6fc0e23083209e85390db7`.
A threshold-128 check of the declared crop finds an inclusive 84 × 38-pixel ink
box and about five long shaft rows. These are coarse proportions, with no
inferred image em or asserted pixel registration. None of the invalid harpoon,
twohead, hook or other arrow cells is traced or adopted.

The 40-unit shaft matches the existing authored pilot's 40-unit fraction rule.
The frame is 1,000 **design units** per em, on a 250-unit math axis. Heads have
190-unit length and 170-unit half-height. The two head centerline cubic controls
are at normalized `(0.90, 0.60)` and `(0.34, 0.10)` from tip-relative length and
height. This creates an open, gently curved wedge rather than a filled triangle.
Every head and shaft uses the same 40-unit stroke; no glyph-specific widths or
head sizes are introduced. Double shafts have centers 120 units apart; mapsto
bars have 145-unit half-height. Normal and long centerlines measure 800 and
1,400 units.

Double shafts need more than a fixed endpoint. The implementation solves the
shared cubic's intersection at each shaft centerline by monotone bisection. It
then clips the entire rectangular stripe against the exact cubic interior,
so its upper and lower corners cannot project outside the head. The stroked
head overlaps that centerline boundary by its half-stroke. Double-ended forms
apply the same operation at both ends. A double-ended double arrow retains
its intended enclosed counter after boolean union.

All cardinal and diagonal orientations are exact rotations. A harpoon uses one
of the same two cubic half-heads, selected before rotation; its Unicode side is
checked after rotation. A bar-ended arrow adds the same perpendicular bar at
the shaft tail. Long arrows extend the shaft and translate the same heads.
Skia PathOps strokes and unions the components; quadratic stroke output is
elevated exactly to cubic degree for export. No glyph outlines are imported
from Storm or any other font.

## Exact finite scope

| Unicode range | Forms | Count |
|---|---|---:|
| U+2190–U+2199 | Single arrows, cardinal, both-ended and diagonal | 10 |
| U+21A4–U+21A7 | Four arrows from a bar | 4 |
| U+21D0–U+21D5 | Double shafts, four cardinal and two both-ended | 6 |
| U+21BC–U+21C3 | Eight directional half-head harpoons | 8 |
| U+27F5–U+27FA | Long left/right/both-ended, single and double shafts | 6 |

“Double arrow” here means the Unicode double-shaft forms. Two successive heads
on a single shaft are a different semantic class and are **deferred**. Hooked,
paired, dashed, negated, curved and extensible arrow constructions are also
unfinished. No wrong placeholder is mapped to those targets. Hooks will need
explicit tangent/curvature continuity rather than an ad hoc terminal graft.

## Export contract

The stable source manifest is
[`runs/ams-coverage-2026-10-30/arrows-v1/sources.json`](../runs/ams-coverage-2026-10-30/arrows-v1/sources.json).
Each entry has explicit Unicode scalar(s), source hashes, root hash, grammar
hash, recipe, cubic contours, and `frame_kind: derived_design_units` in both
entry and provenance. It is directly loadable by `tools/build_math_ams.py`.

The legacy builder field names are retained as compatibility fields:
`source_em_pixels=1000`, `baseline_root=750`, `source_crop_box=[0,0,1600,1000]`,
and identity `registration_to_root`. **These describe the derived design
frame, not pixels in the reference image.** Canonical arrow coordinates are
serialized as `x_frame=x+800`, `y_frame=750-(y+250)`. The existing builder
therefore yields `font_x=x+800` and `font_y=y+250` before its normal sidebearing
translation. `root_image` verifies lineage/reference bytes; it does not assert
a pixel registration. Both `raster_fit_claimed` and
`root_frame_registration_claimed` are explicitly false. No builder change is
needed for the transform; consumers must retain this frame distinction in
reports and avoid applying raster-fit measurements to these sources.

Reproduce in a **fresh** output folder; existing generated folders are immutable:

```sh
.venv/bin/python tools/build_math_arrows.py --output /tmp/math-arrows-reproduction
.venv/bin/python tools/build_math_ams.py \
  --sources runs/ams-coverage-2026-10-30/arrows-v1/sources.json \
  --output /tmp/math-arrows-font
.venv/bin/python -m unittest discover -s tests -p test_math_arrows.py -v
```

## Proofs, checks and remaining optical work

[`grid.svg`](../runs/ams-coverage-2026-10-30/arrows-v1/grid.svg) shows all enlarged
forms and additional rows at 10pt, 7pt and 5pt equivalents at 96dpi. Thin guide
lines are a separate optional
[`grid-guides.svg`](../runs/ams-coverage-2026-10-30/arrows-v1/grid-guides.svg) overlay;
clean ink is never flattened with guides. `grid-preview.png` is a convenience
rendering, not a raster-fit reference. `metrics.json` records topology, area,
bounds, hashes, shared parameters and solved double-shaft joins.

Seven tests check the exact 34-slot set, shared heads and their long-form
translations, exact orientations, correct harpoon sides, bar and double-shaft
semantics, complete curved clipping, connected outlines and the retained double
arrow counter. They also compile the real exported curves into a temporary
CFF/MATH OTF, verify its cmap and cubic contours, and reject output replacement.
This proves the export/font mechanism, not optical quality.

The 10/7/5pt rows use the same geometry. **Optical compensation at script sizes
is unfinished.** At 96dpi the nominal shaft is only about 0.53/0.37/0.27 pixels
at those sizes, so actual engine rendering and weight calibration matter.
Head sharpness, reading-size distinctions, spacing beside Storm, vertical-arrow
placement and bold/size behavior require actual page proofs and design review.
No MATH arrow assemblies or indefinite growth are supplied.

`arrows-v1/preclip-draft/` preserves the initial exploratory output that exposed
projecting double-shaft ends. It is historical only, not an integration source;
its relative paths reflect its original pre-move location. The manifest at the
root of `arrows-v1/` is the corrected, tested source.
