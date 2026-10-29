# Greek proposal G2 — native nu gesture

Round 1 was rejected. This proposal starts again from retained 0.152 and adopts
none of G1's fitting, counter relief or nu recipe. Its bounded question is whether
a more forward, curved Greek nu gesture can improve family voice and small-size
identity while retaining a pointed base distinct from rounded upsilon and looped
Latin italic v.

Only six outlines change: italic and bold-italic nu, each at text, script and
script-script roles. The other 378 declared Greek roles, Latin v, upsilon,
radicals and every unrelated glyph/metric remain exact. Bold join/counter work
is deliberately left for separate feedback rather than mixed into this proposal.

The accepted native nu contours are explicitly adopted, including their existing
optical forms. A smooth y-preserving horizontal deformation adds 0.21*y plus a
20-unit sinusoidal middle displacement. This shifts the pointed foot relative to
the upper strokes and gives the rising arm forward curvature. Each original
cubic is reconstructed by six cubic Hermite intervals, using the transformed
position and derivative. This is a native-Greek silhouette intervention, not an
assertion that every Greek letter should have a common Latin slope.

Script and script-script receive respectively 3/6 units of additional ink in
regular italic and 2/4 in bold italic. The small-form reinforcement is independent
of base-role weight. Each result is fitted to its exact accepted ink envelope;
advances, sidebearings, heights/depths and italic corrections remain unchanged.
The upper-ink centroid displacement transfers the accepted accent relationship,
with anchor deltas -4 units for the two text forms and -3 for each small form.
No unrelated MATH values change.

P07 informs retention of Greek anatomy; M08 motivates direct confusable and group
proofs; P01/P05 support purposeful optical adjustment; S01 supports testing one
question at reading size and enlarged. The deformation and ink amounts are this
proposal's choices, not numerical prescriptions from those sources.

The proof helper and its specimens/layout are byte-identical to round 1. The
same ten images show the whole alphabet, four styles, natural 8/10/12 pt use,
distance, closed-counter/interletter white, actual optical output, direct variant
and confusable details, and identical controls. Closed-counter masks do not treat
open apertures as holes. Guides retain their measured companion x/p provenance.

Engineering verifies six changed outlines, no changed hmtx entries, preserved
unrelated outlines/tables/MATH, unchanged repertoire/GSUB, preserved topology and
bounded fill-area changes. The compiled glyph-ID trace exercises every one of the
384 roles on both sides. The raw control strings retain positive bbox separation;
this proves no raw-advance collision in those cases, not even optical spacing.
No missing-character or overfull warnings occur in reading/optical/coverage PDFs.

The proposal does not solve the remaining bold joins, all possible attachment
cases, physical-print performance or human recognition. These are explicit
limits, not grounds to infer improvement before the one-shot council review.
