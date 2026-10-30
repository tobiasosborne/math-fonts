# Reuse Baskerville; author its mathematical companion

User correction, 2026-10-30: use existing Baskerville glyphs rather than
regenerating ordinary letters such as H and O. This updates the production
plan; earlier generated studies and their call ledger remain unchanged.

## Sourcing decision

- Use the supplied Storm Baskerville 10 Pro upright, italic, bold and bold
  italic faces for ordinary serif Latin alphabets, their numerals and suitable
  punctuation. In the 24-role pilot, A/H/O/f/x/d/0/1/2 are external-font roles,
  not image-generation or tracing tasks.
- Keep the accepted newly designed Greek as custom work. It is part of the
  requested visual identity; do not replace it with Storm's native Greek by
  assuming that available coverage always means the desired drawing.
- Retain Storm's native Greek as explicit upright/italic alternates. The user's
  preferred custom Greek stays the default; an alternate does not close a
  missing custom glyph. Unavailable native variants must report an error rather
  than substitute a different epsilon, phi, kappa or other shape.
- Audit existing arithmetic signs, parentheses and accent bases before drawing
  replacements. A cmap entry establishes availability only; test shape,
  math-class spacing, accent positioning, scripts and actual rendering.
- Growing delimiters, radicals, accents, large operators and their assemblies
  need mathematical engineering. Reuse a suitable existing base through an
  explicit runtime mapping where practical; author missing construction pieces
  and shapes from the unified design root. Do not assume that a text font
  supplies MATH data or that arbitrary geometric stretching is acceptable.
- Construct related geometric symbols from shared vector components. For
  arrows, choose shaft weight, head profile, bar spacing and hook curvature
  against the unified root and math rules, then reuse those parameters across
  directions, lengths and semantic variants. Separate raster generations must
  not introduce different heads into the same family. Harpoons, double shafts
  and two successive heads remain distinct constructions. Record any optical
  correction explicitly rather than hiding per-glyph deviations.

One unified design image still governs **new drawing** and provides a visual
comparison with actual Baskerville. Existing-letter cells in the current
foundation are reference/registration anchors, not authority to replace the
original font's geometry. No new image call is needed to remove those roles
from the production drawing queue.

## Integration and release boundary

Prefer explicit runtime selection of user-supplied Storm files and faces,
rather than copying their commercial outlines into the public AGPL font.
The package deliverable is the custom math companion plus a tested loader
configuration using those external alphabets. Do not promise a standalone
font containing every requested scalar. The frozen inventory is package-level
semantic coverage, not a list of outlines all needing new authorship.

`unicode-math` has explicit text math-alphabet interfaces in the installed
implementation (`setmathfontface`, and the fontspec math-alphabet hooks).
Prove the chosen route on both engines before shipping it. In particular,
test bare variables, literal/Unicode numerals, upright and italic selectors,
bold variants, named operators and script sizes. Configuring only `mathrm`
does not prove that default italic variables or Unicode math alphabets use
the intended face. Keep mapping and metric adjustments explicit.

Actual-font-use checks must allow intended Storm alphabet roles and authored
math-symbol roles separately. Intended reuse is not hidden fallback. Continue
rejecting unrelated fonts rendering in-scope math accidentally. No commercial
font binary is copied into or redistributed by this change.

## Effect on the pilot

The pilot still exercises 24 semantic roles, but at least nine need **no new
glyph design**. The remaining nine symbol/construction roles first get a reuse
audit; six custom Greek roles remain. Thus 24 image enlargements are no longer
the production plan. Keep old caps as ceilings, not targets to spend.

A/H/O enlargements and their vectors are retained as tracing experiments only,
excluded from release glyph sourcing. Four image calls were already spent
(one master and these three); the ledger is not reset or discounted. The
overnight timer remains disabled; this change does not extend its work window.

Next implementation milestone: prove reuse of the nine ordinary pilot roles
in an explicit installed-font configuration, audit the nine mathematical
roles, then complete only genuinely missing custom drawings. Repair quota
observation before any renewed image campaign. See
[`design/glyph-sourcing.json`](../design/glyph-sourcing.json).
