# Expanded unified atlas preparation

`tools/prepare_ams_atlas.py` prepares the single frozen candidate at
`runs/ams-coverage-2026-10-30/master-v2/candidate-01/master.png`.
Its SHA-256 is
`edfb27bedf078bcba86d18112c15d4f03bc25b2bdc6fc0e23083209e85390db7`.
This bounded local pass generates no images or fonts. It does not replace the
six retained regular-companion v1 glyphs or claim new coverage acceptance.

```sh
.venv/bin/python tools/prepare_ams_atlas.py
.venv/bin/python -m unittest discover -s tests -p test_ams_atlas.py -v
```

The tool writes only `cells.json`, `calibration.json`, `review.md`, and
`crops/*.png` beneath that candidate directory. Before writing, it computes every
output and checks all existing artifacts byte-for-byte. Any difference raises
an error before missing outputs are written; it never overwrites evidence.
The input root digest and 1024×1536 dimensions are pinned. `--directory` permits
a copied candidate for verification; a different image is rejected.

## Exact source extraction

The grid has nine horizontal and nine vertical boundary bands. A projection of
grayscale pixels below 245 identifies boundary lines crossing more than 85% of
the corresponding dimension. Within each row's interior, pixels below 128 form
two separated y bands: actual glyphs, then labels. The cut falls halfway through
the measured whitespace between them; at least four blank rows are required.
The tool refuses images without exactly this measured structure rather than
guessing new extraction rules.

Each crop is an unchanged rectangle of original pixels. Crop windows keep two
clear pixels beyond grid bands and exclude label gutters. No whitening,
resizing, thresholding, filtering, despeckling, counter filling, width fitting,
or glyph normalization is applied to saved images. Thresholding is measurement
only. Pixel-level comparison tests confirm every crop equals the corresponding
source rectangle. Components use 8-connectivity; every component and tiny speck
is counted and preserved. Grayscale fringes and generated background remain
source evidence. All rectangles, row windows, grid bands, crop hashes, ink
bounds and component areas are recorded in `cells.json`.

The crop rectangles and excluded grid/label windows are the removable geometric
mask. They are not generated guides or geometry to trace. Production tracing
must consume clean ink crops, never labels, grid overlays, or handle diagrams.

## Identity and quarantine

All 64 intended cells have explicit Unicode and TeX identities. First-four-row
entries map native characters and mathematical italic aliases separately.
The 32 targets here are **31 Greek forms plus partial**; digamma from the older
Greek seed is absent. The native labels are identity requests, not a finding
that every drawing matches them.

Six crops are quarantined: epsilon-lunate r4c2, kappa-variant r4c4, phi-looped
r3c6, left-harpoon r8c5, right-harpoon r8c6, and twohead-right r8c8.
Their crops remain evidence; they cannot be production references. The first
three fail the requested Greek variant distinction; the bottom three have
wrong arrowheads/shaft counts. Exact findings are in the candidate's review.

The epsilon-lobed cell maps **ε / U+03B5 / U+1D700 / `\varepsilon`**.
The quarantined epsilon-lunate request maps
**ϵ / U+03F5 / U+1D716 / `\epsilon`**. The quarantined phi-looped request maps
**φ / U+03C6 / U+1D711 / `\varphi`**. Phi-straight maps
**ϕ / U+03D5 / U+1D719 / `\phi`** and was independently judged a plausible
straight-stem source candidate. That is not optical acceptance.

Alpha, beta, theta, nu, xi and omega v2 redraws are calibration evidence only;
the actual v1 pipeline sources stay retained. Other unquarantined Greek forms
are provisional design references. The remaining sign cells are family-grammar
prototypes pending stock-sign audit and individual engineering. Every entry
has `coverage_credit: false` and `font_source_ready: false`.

## Shared scale and baselines

Six frozen v1 anchors, their original cell coordinates, actual threshold ink
boxes, and provisional row baselines supply twelve width/height ratios.
The robust shared scale is their median: **0.6404308202154101**.
Multiplying the old provisional 200-pixel em gives **128.08616404308202 pixels**
for the entire v2 atlas. No per-glyph scale is applied.

For each anchor, both top and bottom ink edges predict a baseline using that
same scale and the known v1 baseline. Their midpoint supplies one baseline
offset relative to its v2 row's top grid edge. The median of the six proposals
is the shared offset, **138.05778790389394 pixels**. Adding it to each Greek
row's measured top edge supplies the proposed row baseline. Row 3 has no
anchor and is explicitly marked extrapolated. Rows 5–8 have no assigned font
baseline because mathematical symbol alignment requires separate calibration.

The width-ratio median is **0.607157**, versus **0.665293** for heights.
The twelve ratios span **0.570423–0.729167**, and dimension residual RMS is
**5.500 atlas pixels**. These are changed proportions and placement, not a
faithful enlargement of the six anchors. The independent least-squares scale,
ratio MAD, every dimension residual, baseline proposal range/MAD, and per-anchor
observations appear in `calibration.json`.

This calibration is **provisional and uncertain**. The v1 em/baselines were
already provisional; bounding boxes cannot establish silhouette fidelity,
stroke weight, slant, or matched-size Storm compatibility. Do not treat the
reported decimal precision as design accuracy or confidence bounds. Enlarge
and prove each missing design against the root and real retained glyphs before
adopting production metrics.

## Builder handoff

Greek cells include a deliberately incomplete `builder_calibration_proposal`
compatible with `tools/build_math_ams.py` conventions: codepoints, kind, original
crop rectangle, shared em, row baseline and root digest. An unresized crop uses
uniform registration `scale=1` and translation equal to its root crop origin.
An independent enlargement requires its actual measured uniform registration;
never copy the unresized-crop transform to a differently scaled image.

These proposals have no curves path or complete provenance, so they cannot be
silently used as production font sources. The caller must honor quarantine and
anchor retention, supply the real trace and lineage, and explicitly review the
provisional calibration. The preparation tool performs no font builds.
