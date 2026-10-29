# Greek proposal G1 — design record

This is one proposal across the 32 lower-Greek/variant/partial forms, four serif
styles and three existing size roles (384 roles, not 384 independently drawn
letters). The seed is retained radical campaign 0.152; the historical archive,
smoke and radical campaign outputs are untouched.

The native Greek alphabet is substantially retained. Fitting redistributes some
left entry space for beta, rho, iota, theta, kappa, mu, psi and variant rho, while
adding modest shape-dependent exit white. Diagonal/descending exits receive more
space than round silhouettes. Slant and different edge shapes justify remaining
asymmetry; equality of numerical bearings was not the objective. Raw-advance
strings isolate fitting from TeX atom spacing. The proposal must earn its rhythm
in those strings and in the natural formulas, not through reduced bearing
variance.

Italic and bold-italic nu are rebuilt from the supplied native Greek nu, with a
smooth baseline-concentrated displacement of 105 units (scaled by source
x-height), versus the inherited more strongly displaced posture. Cubic Hermite
reconstruction samples each original cubic in six intervals. Native entry,
stroke contrast and Greek gesture remain; isolated and contextual Latin v / nu /
upsilon proofs test whether its distinction remains convincing. This is a
Greek-specific intervention, not an alteration of Latin v.

Enclosed bold counters receive three units of relief. Existing script forms
receive a small additional ink gain and independent counter opening, with less
ink gain in bold. Nesting is preserved, including black islands. Vertical bounds
are restored after optical adjustment, protecting height and depth relationships.
The bold psi script-script outline is explicitly retained: its offset Boolean
proved unreliable and lost the arms, caught before freeze by a fill-area audit.
Only its fitting advance changes. Base regular contours other than nu are retained apart from selected translation;
the active tool performs no blanket Latin-serif or slope conversion.

All advances, translations, bounds, accent anchors and italic-correction changes
are itemized in private engineering.json. Top accent anchors follow translation;
nu's anchor follows its changed horizontal centre. Existing italic correction is
reduced by the additional trailing clearance to avoid counting that space twice.
Unrelated MATH data, including the retained radicals, are exact.

The sources support the working method, not these particular numbers: P02/S02
on design-specific fitting and inner/outer white; P01/P05 on coordinated optical
adjustment; P07 on Greek integrity; M08 on confusable recognition and group
review; S01 on proofs as experiments. No universal equal-width, equal-bearing,
equal-counter or equal-slope standard is claimed.

## Proof contract

The ten neutral PNGs provide A/B natural 8/10/12 pt pages; paired complete regular
and bold style grids; unblurred distance pages; closed-counter and interletter
white masks beside unmasked forms; actual script contexts with enlarged existing
optical alternates; direct variant/confusable details; and identical X/Y controls.
The private PDF contains every diagnostic mode plus the original vector reading
pages. Each manifest entry records its mode, scale and locator.

Grid x-height/descender guides come from measured supplied companion x/p outlines,
not composite donor OS/2 metrics. Greek omicron top is separately labelled and
may coincide with a companion guide. Cyan masks show closed white components
only; open apertures remain exterior. Orange masks show rowwise white between
adjacent silhouettes in a declared body band, not every white pixel or a claim
that equal gaps are desirable. Both sides use fixed scale/origins/rendering,
without equalizing width, ink density or counters.

## Verification and limits

The compiled font preserves unrelated outlines/metrics, cmap, glyph order, GSUB
and unrelated MATH structures. Counter counts, finite bounds, gross fill-area retention and Boolean fill
integrity pass. Area retention guards accidental shape loss; it does not certify craft. A technical XeLaTeX page and MuPDF glyph-ID trace confirm all 384
expected base/script/script-script roles actually occur. Declared raw-advance
control strings have positive horizontal bounding-box separation in all styles
and size roles. Reading, optical and coverage pages have no missing-character or
overfull warnings; reading PDFs embed only the intended companion/math fonts.

These checks do not prove publication quality, exhaustive attachment/collision
coverage, physical-print performance or reader recognition. Accent centring and
the optical result remain visual questions. No claim of perfection or improvement
is made before the parent audit and one-shot council comparison.
