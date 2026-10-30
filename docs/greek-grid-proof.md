# Actual Greek/text grid proof

`tools/proof_greek_grid.py` compares the old and revised compiled Greek beside
the **original supplied Storm italic**. It does not derive targets from the
new glyphs, fit glyphs into equal boxes, or modify any outline. Reference fonts
are hash-pinned to `design/storm-reference.json`/the established runtime pins.

```sh
.venv/bin/python tools/proof_greek_grid.py \
  --before-font runs/ams-coverage-2026-10-30/delivery-arrows-03/font/BaskervilleCompanionMath-AMS.otf \
  --after-font /path/to/calibrated/BaskervilleCompanionMath-AMS.otf \
  --grid design/greek-text-grid.json \
  --text-font-dir '/external/Baskerville 10 Pro' \
  --output /tmp/greek-grid-proof --dpi 200
```

The output directory must be fresh. `summary.json` contains measured numeric
bounds, advances, font hashes and actual-font checks. Commercial outlines,
embedded-font PDFs/rasters, source TeX and the interactive viewer stay below
`private/`, which must remain ignored. No reference outline belongs in a public
font or public SVG.

## Common-em outline view

The proof converts each font's units per em to one common 1,000-unit frame.
Every glyph then uses its actual advance plus a constant comparison gap. There
is no per-glyph bounding-box normalization or visual size fitting. Three rows
compare Latin body letters, ascenders and descenders with the six custom Greek.

Guide coordinates come from the supplied `guides` mapping: `baseline`,
`x_height`, `cap_height`, `ascender`, `descender`, `lower_overshoot` and
`descender_overshoot`. Defaults are the measured Storm italic values
0, 476, 723, 744, −271, −18 and −286 respectively, in the same 1,000-unit frame.
The body-baseline and descender bands record observed outline zones. They are
not instructions to force every glyph's extremum onto one line. Each guide is
a removable overlay; clean glyph ink is retained separately.

## Actual text and script rendering

Both LuaLaTeX and XeLaTeX render before/after proofs with external Storm text,
native italic variables and the authored companion. The page includes inline
expressions, exact 10pt/7pt/5pt comparison rows, nested scripts, accents and an
enlarged comparison. Clean and guided versions are separate PDFs and rasters.

On guided pages, TeX places thin rules from the **same line baseline** using
`guide / 1000 em` offsets. The rules are not painted onto screenshots or
positioned by eye. The clean proof has no rule ink. The viewer switches state,
engine, guides, zoom and negative-space view.

An independent four-page role proof checks the exact sequence of eight native
italic controls and six custom Greek at all three sizes. MuPDF inspects every
actual PDF character's font, scalar identity, physical point size and baseline
origin. A separate nested-script page must exercise three sizes of both intended
faces. `pdffonts` independently rejects any unrelated font. Equal PDF baseline
origins prove execution, **not visible outline alignment**: the outline-grid
measurements and optical inspection still determine whether height, overshoot,
slant, weight and spacing are appropriate.
