# Expanded unified atlas candidate 01: bounded source review

This 1024×1536 candidate has been measured and cropped, not accepted as a font
or full AMS coverage. Root SHA-256: `edfb27bedf078bcba86d18112c15d4f03bc25b2bdc6fc0e23083209e85390db7`.
All 64 crops preserve original pixels and every dark component; labels and
grids are excluded using measured rectangular gutters, without ink cleanup.
`cells.json` records exact geometry, identities, source hashes and dispositions.

The existing regular-companion alpha, beta, theta, nu, xi and omega remain the
actual retained v1 font sources. Their v2 drawings are calibration evidence only.
The atlas's first four rows contain 31 Greek targets plus partial; they do not
include digamma from the older 32-glyph seed. No automatic coverage credit.

## Semantic quarantine

- **r4c2 epsilon-lunate (ϵ, \epsilon):** drawn as lobed ε, not lunate ϵ.
- **r4c4 kappa-variant (ϰ, \varkappa):** too close to ordinary κ; distinct
  anatomy is not established.
- **r3c6 phi-looped (φ, \varphi):** duplicates the straight-stem design rather
  than providing the requested distinct looped variant.
- **r8c5/r8c6 harpoons:** both have full two-sided arrowheads.
- **r8c8 twohead-right:** has two shafts like a double arrow, not two heads
  along one shaft. These bottom-row shapes must never be production references.

The r1c5 lobed ε correctly belongs to **\varepsilon**, not \epsilon.
The r4c5 phi-straight was reviewed independently: its straight central stem,
elliptical bowl and descender are a plausible **ϕ / \phi** prototype. Its
similarity to r3c6 disqualifies r3c6 as a distinct varphi; it does not by itself
disqualify r4c5. Weight, aperture and reading-size performance remain unaccepted.
The distinct theta/rho/pi variants are recognizable source candidates, subject
to individual enlarged and working-size review. Labels are intent, not proof.

Rows 5–7 and the remaining arrows are grammar prototypes only. Their thin,
nearly monoline strokes are visibly unlike the Greek's heavier contrast; stock
sign sourcing, joining/growth construction and optical acceptance remain open.
No sign is installed or claimed as completed by this preparation.

## Shared calibration and its limits

Six retained v1 anchors provide twelve measured width/height ratios. Their
median proposes **0.640430820×** v1 and an atlas em of
**128.086164 pixels**, derived from v1's provisional 200-pixel em.
Widths alone give 0.607157; heights alone give
0.665293. The range is
0.570423–0.729167; RMS dimension
residual is **5.500 atlas pixels**. This
disagreement is real evidence of changed proportions, not a scale to hide.

The common baseline offset is **138.057788 pixels**
below each row's measured upper grid edge. Per-anchor baseline proposals span
130.701–143.083
pixels. Row 3 has no retained anchor; its baseline is an extrapolation. See
`calibration.json` for every observation, residual and explicit uncertainty.
This is a provisional engineering proposal; the v1 metrics themselves were
provisional and no Storm matched-size calibration or silhouette acceptance is
implied. There is one shared atlas em and shared row logic, never independent
glyph normalization.

## Reproduction

Run `.venv/bin/python tools/prepare_ams_atlas.py` from the repository root.
The tool compares existing artifacts byte-for-byte and refuses differences;
it does not overwrite historical evidence. No image generation or font build
is involved. Crop encoding uses Pillow 13.0.0 and fixed PNG settings.
All crops are source evidence, including quarantined shapes. Builder proposals
in `cells.json` intentionally remain incomplete: a real registered trace and
provenance must be supplied, and the provisional calibration must be reviewed.
