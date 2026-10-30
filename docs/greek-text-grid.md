# A measured text grid for the Greek companion

The metric authority is the supplied **Storm Baskerville 10 Pro Italic**, at its
actual 1,000 units per em. `design/greek-text-grid.json` records the exact font
hash, measured control outlines, guides and line metrics. It contains numerical
measurements, not commercial outline data. Never infer a baseline from image
canvas padding or independently rescale proof glyphs until they look aligned.

## Separate the coordinate systems

1. **Image fidelity:** enlargement → measured registration → frozen root. Keep
   this record immutable. A good bitmap overlap does not prove correct placement
   in a text font.
2. **Optical/font placement:** source font units → explicit reviewed similarity
   against text anatomy landmarks. Record uniform scale and vertical translation
   separately; preserve aspect, stroke topology and source curve hashes.
3. **Proof:** draw original text and the actual compiled Greek at one common em
   and real point size. Removable guides reveal errors; they never resize ink.

For a future specimen canvas with a declared image em `E` and baseline `b`,
guide height `h` is placed at **`pixel_y = b − h × E / 1000`**. The em and
baseline must be stored with the root. For an enlargement, transform the guide
coordinates through its measured registration. Save clean ink, overlay and
guide coordinates separately; do not trace the annotation layer or erase guide
ink from a flattened picture. Exact crops cannot establish their own new em.

## Actual reference lines and zones

| Guide | Units | Evidence |
|---|---:|---|
| Baseline | 0 | The source font origin |
| Lowercase body top | 476 | Actual `x n o a c e` outline tops and `sxHeight` |
| Cap height | 723 | Source `sCapHeight`; actual H in the control report |
| Ascender | 744 | Median of actual `b d h k l` tops |
| Text descender | −271 | Actual `p q` bottoms and source typographic descent |
| Rounded body bottom | −18 | Median actual `o a c e` bottoms |
| Descender lower envelope | −286 | Actual `f g p q y` range |
| Italic guide angle | −12° | Source `post.italicAngle`; a comparison guide |

The actual italic has a measured rounded lower overshoot but no distinct upper
overshoot among those six body controls. Do not import a generic +10/+15-unit
overshoot rule or reinterpret an unrelated hinting zone as a measured outline.
The slant guides do not shear the Greek; widths, weight and slant remain optical
review subjects. The mathematical axis stays separately declared at 250 units.

These are **design lines**, not every glyph's bounding box. Tall theta does not
belong in an x-height box. A descending beta's bowl has a body-baseline landmark
distinct from its stem end; xi's body-to-tail join is distinct from its tail
extremum. Tails may stop above the deepest text descender. Every new anatomy
needs a reviewed class and landmark definition before the pipeline accepts it.

## First six-glyph correction

`tools/calibrate_greek_grid.py` measures the hash-pinned external italic and
records the first profile in
`runs/greek-grid-2026-10-30/calibration-v1/calibration.json`.

- Alpha, nu and omega use the actual body top/bottom extrema, targeting 476/−18.
- Theta uses the tall round top/bottom, targeting 744/−18.
- Beta uses the explicitly reviewed outer lower-bowl cubic minimum and top,
  targeting −18/744; the descending stem is not the baseline measurement.
- Xi uses the explicitly reviewed lower-body-to-tail join and top, targeting
  −18/744; the tail retains its own descending depth.

Beta/xi landmark operation indices, coordinates and source curve hashes are
recorded. Changed sources or registrations fail closed and require re-review.
This is a deliberate per-glyph optical size correction, **not** a change to
bitmap registration or a hidden fit in the proof. X and y always use the same
scale. Corrections above 10% scale or 200 units translation require redesign
rather than automatic acceptance. No nodes are moved and no widths are squeezed.

The new builder profile also sets `sxHeight=476`, `sCapHeight=723`, typographic
and `hhea` line metrics to 744/−271/48, and MATH accent reference heights to
476/723. Windows clipping extents still enclose the actual large math variants;
those extents are not substituted for ordinary text line spacing. The 34 arrows
and every other non-Greek outline remain byte-for-byte unchanged geometrically.

`tools/run_math_ams.py` now requires explicit `--calibration` for new builds.
`--allow-uncalibrated` exists only for historical reproduction. Adding a new
Greek without an explicit reviewed profile role fails instead of inheriting
arbitrary image-row metrics.

## Rebuild and verify

```sh
.venv/bin/python tools/run_math_ams.py \
  --output /tmp/baskerville-grid-build \
  --base-sources runs/pipeline-2026-10-30/font-sources.json \
  --sources runs/ams-coverage-2026-10-30/arrows-v1/sources.json \
  --calibration runs/greek-grid-2026-10-30/calibration-v1/calibration.json \
  --text-font-dir '/external/Baskerville 10 Pro' --dpi 200
.venv/bin/python tools/calibrate_greek_grid.py \
  --after-font /tmp/baskerville-grid-build/font/BaskervilleCompanionMath-AMS.otf \
  --profile runs/greek-grid-2026-10-30/calibration-v1/calibration.json \
  --output /tmp/baskerville-grid-audit.json
.venv/bin/python -m unittest discover -s tests -p test_greek_grid.py -v
```

The post-build audit recomputes landmarks from **actual compiled CFF outlines**,
checks a 0.02-unit engineering tolerance, and checks line/height metadata. That
tolerance tests coordinate/export correctness, not perceptual quality.
The [proof tool](greek-grid-proof.md) independently checks actual fonts, glyph
identities, point sizes and TeX baselines at 10/7/5pt on both engines, including
nested scripts and accents. Inspect clean, negative-space and enlarged views.
Grid matching alone does not settle weight, width rhythm, spacing, hinting or
the final optical compensation for script sizes.

## Practice behind the method

OpenType distinguishes lowercase/capital height from line-spacing and clipping
metrics; they cannot repair an outline by themselves.
See the [OpenType OS/2 specification](https://learn.microsoft.com/en-us/typography/opentype/spec/os2).
Glyphs describes separating baseline, height and overshoot zones, keeping family
line metrics synchronized, and judging optical overshoot rather than enforcing
identical bounds. See [vertical metrics](https://glyphsapp.com/learn/vertical-metrics/),
[drawing and overshoot](https://glyphsapp.com/learn/sketching), and
[alignment zones](https://glyphsapp.com/learn/hinting-postscript-autohinting).
The chosen numerical values come from our actual licensed reference, not from
those tutorials' example fonts.
