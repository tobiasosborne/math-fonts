# Math typography rubric — absolute editorial standard, version 0.3

Status: council grading standard adopted on the user's instruction, 2026-10-29.
Sources resolve in [the research index](../research/typography/README.md).
The scoring scale expresses the project's ambition; the research supplies
its typographic substance. See the [implementation plan](hillclimb-plan.md)
and the [judge prompt](../council/judge-prompt.md).

## The standard: the hypothetical perfect math font

Grade against the ultimate platonic Baskerville companion math typeface:
mathematical clarity, outline craft, optical behaviour, fitting and page colour
resolved with such authority that the result merits a featured new-design
article in a leading typography periodical. Imagine an exacting typography
editor examining the actual proofs and asking why this design deserves those
pages. Mere competence, polish, technical validity or improvement is insufficient.

Describe the hypothetical perfect solution for each criterion, then identify
the visible distance between that ideal and this font. The ideal stays fixed
across rounds. Existing professional fonts and historical specimens inform
judgment; none sets a ceiling. A design can surpass every supplied reference
and still fall short of the ideal.

Scores are absolute. Better than the last build earns no credit by itself.
In paired rounds, score both sides independently against the same ideal before
stating which is better. A winning candidate may still deserve a low score.
Featured quality comes from exactness, character and a fully resolved design,
not novelty, decorative flourishes, fashionable styling or persuasive copy.

Every judgment must answer both: **What is better? What still prevents this
from appearing as a featured new design in a top typography periodical?**
Treat the publication test as our hypothetical editorial bar, never as a claim
that an actual publication or named typographer has endorsed the font.

## What counts as evidence

- **Practice:** published accounts by designers, mathematical compositors,
  foundries, and type-design tool educators. These justify what to inspect.
- **Specification:** Unicode and OpenType describe meaning and mechanisms;
  they do not certify aesthetic excellence or a complete layout algorithm.
- **Empirical:** controlled reading research supports its tested population
  and task. Prose-reading results do not establish mathematical comprehension.
- **Project choice:** proofs, anchors, weights, panel design, thresholds,
  and acceptance rules are ours. Record revisions explicitly.

Primary evidence can support conflicting design traditions. Record that
disagreement and argue which resolution best serves the stated ideal.
Unverified/index-only sources must not carry an acceptance rule. Sources give
reasons to test; actual proof evidence supplies the judgment of this font.

## Engineering preconditions, separately reported

For the declared milestone, establish correct required repertoire and mapping,
parseable required tables, successful output in the target engines, no
unintended fallback, clipping, or collisions in the agreed cases, functional
size variants/assemblies, and correct embedded-font identity and notices.
Use M03/F03 for MATH semantics and M04 for mathematical character distinctions.
Optional repertoire is not required by fiat. Report coverage gaps explicitly.
An engineering failure cannot be offset by a high craft score; a technically
valid OTF can still be poorly designed.

## Rating scale and evidence contract

- **1 — unresolved prototype:** visible fundamental failures, malformed forms,
  broken identity or serious construction incoherence.
- **2 — promising but unfinished:** works, but recurring compromises or an
  unresolved family still demand substantive design. This includes much
  superficially clean prototype work.
- **3 — genuinely polished professional:** an authored, release-quality solution
  for this criterion, with remaining shortcomings confined to minor refinements.
  Explain the positive craft that earns this; mere usability does not qualify.
- **4 — distinguished:** close to feature-worthy, with a specific remaining
  compromise that an exacting editor would insist be resolved.
- **5 — exemplary / feature-worthy:** convincingly realizes the hypothetical
  ideal for this criterion in the supplied proofs. Explain the exceptional
  decisions that earn it and why no visible publication blocker remains.

### No default midpoint

The smoke run's generous 3s are not reference scores and must not be shown to
judges. Grade this campaign afresh. A 3 is an achievement, not the default for
an image without an obvious collision. A diagnosis of recurring incoherence,
frail required forms, unresolved construction or a family needing a redraw is
incompatible with calling that criterion polished professional work: normally
1 or 2 is warranted. Do not average strengths and fundamental defects inside
a criterion into an unexplained 3.

For every score of 3 or above, identify the concrete release-quality achievement
and explain why the observed defects are minor enough for that anchor. For
lower scores, give equally concrete evidence. There is no imposed score quota
or demand to depress scores: evidence, not severity theater, determines them.
The anchor is fixed for all three revision rounds; comparisons with smoke 0.2
scores are not valid measures of progress.

Use `not_assessable` only when the necessary evidence is absent. State the
missing proof, not a guessed score. Do not infer unseen tables or intentions.
Every scored criterion requires:

1. **Ideal:** what a perfect solution would achieve here, in concrete typography.
2. **Observation:** specimen, glyph/formula, region and size supporting the score.
3. **Gap:** exactly where this falls short of the ideal and why that matters.
4. **Editorial justification:** why it earns this score rather than the next
   higher anchor, and what keeps it out of a leading periodical's feature pages.
5. **Next move:** the single design revision most likely to close that gap.
6. **Practice reference:** the source IDs supporting the typographic reasoning.

Be unsparing and specific. “Clean”, “professional”, “balanced”, “more refined”
and “better” are conclusions to substantiate, not evidence. Do not reward
implementation effort or inflate scores because defects have been fixed.
Do not invent faults to sound severe: a 5 is allowed when the evidence earns
it; explain its positive achievement and report no observed gap for that case.
Missing proof coverage limits the verdict's scope; it earns no assumed credit.

### R1 Baskerville compatibility and family coherence

Evidence: M01, M06 §4.3–4.9, P06 (modern revival interpretation),
S04 (historical evidence). The supplied Baskerville face is the immediate
companion; a historical specimen informs vocabulary, not a tracing target.

Proof: Latin and Greek alphabets, digits, operators and symbols alongside
the supplied roman and italic at intended sizes; real inline/display pages.
Inspect apparent size, weight, contrast, stress, proportions, serif/terminal
vocabulary and deliberate semantic differences. Neither identical slopes nor
identical stroke widths across all signs is required.

- **1:** math repeatedly looks imported from an incompatible family; weight,
  proportions or terminals disrupt the surrounding prose.
- **3:** all major demonstrated families share a convincingly authored
  companion voice; remaining mismatches are localized refinements. Recurring
  imported-looking families do not earn this anchor.
- **5:** the mathematical voice feels inevitable beside Baskerville while
  retaining its own authority; every demonstrated alphabet and symbol family
  participates in a distinctive, fully resolved whole worthy of editorial study.

Keep intrinsic craft separate: a beautifully made unlike reference may score
well on R2 and poorly on R1. Do not call it a defective font for that reason.

### R2 Outline craft, stroke logic and detail

Evidence: P03, P04; S01 on enlarged and working-size proofs. Inspect outer
and inner contours, joins, bowls, counters, terminals, stress transitions and
deliberate corners, then verify their effect at reading size.

- **1:** visible accidental kinks, lumps, flat spots, broken hairlines or
  closed counters damage the form or recur across a family.
- **3:** outlines show release-quality stroke logic and resolved joins;
  only minor detail refinement remains. Repeated lumps, unresolved stress or
  substantial contour reconstruction belongs below this anchor.
- **5:** curves, countershapes, stress and terminals have exceptional control
  and character at both diagnostic and reading scales. Their resolution gives
  an editor specific details to feature, beyond merely defect-free outlines.

No generic handle ratio, fixed node count, or demand for G2/G3 at every join
defines excellence. Deliberate corners are not “tangent failures.”

### R3 Fitting, spacing and local rhythm

Evidence: P02, P09, S01, S02. The handbook explicitly treats sidebearings as
design/script dependent; n/o and H/O controls support fitting, not a universal
math spacing formula.

Proof: straight/round/diagonal contexts; digits and punctuation; adjacent
italic symbols; operators and relations; repeated signs. Attribute sidebearing,
italic-correction/math-kern, and engine atom-class spacing separately.

- **1:** persistent holes, clumps, collisions or ambiguous grouping interrupt
  reading and recur in the contextual proofs.
- **3:** fitting is professionally resolved across demonstrated contexts;
  only isolated subtle adjustments remain. Repeated holes, clumps or an
  unresolved spacing system belongs below this anchor.
- **5:** internal and external white space forms an exceptionally assured
  rhythm, from isolated variables to dense formulas; every demonstrated
  correction belongs to a fitting system an exacting editor could hold up.

Equal geometric gaps are not the goal. Ordinary text kerning does not replace
mathematical composition tests.

### R4 Optical behaviour at text, script and script-script sizes

Evidence: P01 pp. 17–19, P05, M02, M07, M08 §7, F01–F02. F04 warns against
generalizing a prose reader's preference into universal performance.

Proof: actual intended sizes, documented physical scale/output conditions,
thin strokes, counters, punctuation, nested scripts and accents. If an optical
axis or alternates exist, verify actual selection and transition behaviour.

- **1:** strokes disappear, counters clog or character distinctions collapse
  at declared use sizes; enlarged views conceal the practical failure.
- **3:** required sizes have deliberate, professionally resolved optical
  behaviour; only minor refinements remain. Recurring frailty, clogged counters
  or missing distinctions at required sizes belongs below this anchor.
- **5:** text, script and script-script feel individually perfected yet
  unmistakably related; small forms preserve clarity and vitality while larger
  forms have the refinement expected of a featured type design.

No axis is mandatory. Successful separate masters, alternates, or a carefully
designed single form may all satisfy the proof task. No arbitrary script
percentage is a quality standard.

### R5 Notation identity and useful distinctions

Evidence: M04 §2.2 and §3; Barbara Beeton's explicit math criteria, M08 §7.
Different mathematical alphabets and weights can carry different meanings.
Text Greek convention, mathematical Greek tradition, and encoded variants are
related but distinct questions.

Proof: isolated symbols and meaningful formulas; relevant Latin/Greek
confusables and variant pairs; regular/bold where declared. Include unfamiliar
forms without rewarding novelty or forcing Latin anatomy onto Greek.

- **1:** repeated plausible misreadings of required symbols or lost semantic
  distinctions make the notation unreliable.
- **3:** the demonstrated required identities are readily distinguishable
  in use, with only subtle refinements remaining. A recurring consequential
  confusable or unresolved variant family belongs below this anchor.
- **5:** symbol identities and semantic distinctions are immediate even in
  difficult contexts, achieved through elegant, script-respecting design rather
  than exaggeration; clarity and character reinforce each other exceptionally.

Require evidence for an alleged confusion. Do not mandate one shape of ν, β,
ϱ or any other letter simply because one model prefers it. Semantic mapping
errors remain engineering failures even when visually inconspicuous.

### R6 Mathematical positioning and composition

Evidence: M03 MathConstants and MathGlyphInfo; M01's real-book development
case. The MATH specification explicitly leaves detailed algorithms to engines.

Proof: simultaneous scripts, italic overhangs, top accents, limits, nested
fractions, aligned relations and matrices; review within real lines/pages.

- **1:** scripts, accents or limits collide, drift from their base, or create
  visibly unstable formula groupings in ordinary declared cases.
- **3:** attachments and clearances are professionally resolved through the
  demonstrated nested structures; only minor tuning remains. Recurring drifting
  accents, awkward scripts or unstable composition belongs below this anchor.
- **5:** even demanding formulas have the optical poise of individually
  composed typography: attachments, clearances and hierarchy feel inevitable.
  The result demonstrates a distinctive mastery of mathematical composition.

Diagnose font, engine, fixture and unknown causes separately. A model's
preferred coordinate is not a universal MATH constant.

### R7 Operators, radicals, delimiters and extensible constructions

Evidence: M03 MathVariants and MathConstants, M06, M08 §7. Inspect the actual
engine-built result, not only the component outlines or a glyph chart.

Proof: large and repeated operators; nested radicals; delimiters around
increasing formula heights; braces, arrows and accents at width/height
transitions. Include enough growth to exercise the declared assembly range.

- **1:** constructions break, show conspicuous seams, lose their character,
  or change weight abruptly as the required extent grows.
- **3:** the demonstrated construction family is professionally resolved
  in shape, joins and transitions; remaining changes are refinements. Working
  but structurally incoherent radicals or delimiters belongs below this anchor.
- **5:** constructions at every demonstrated extent retain the same
  calligraphic authority and optical balance; transitions and joins disappear
  into forms whose refinement merits close editorial attention.

No fixed number of variants or arbitrary-height support is assumed without a
declared requirement. A component chart alone cannot earn a high rating here.

### R8 Reading-page colour, continuity and composure

Evidence: S01 on paragraphs and texture, S02 on balanced white space,
M01 on development in a real book, and M07 on text–math weight matching.
This is a page-level consequence, distinct from R3's local fitting diagnosis.

Proof: sustained Baskerville prose with diverse inline mathematics and display
equations, at actual reading size and on the intended outputs.

- **1:** mathematics creates repeated dark/light interruptions, disruptive
  vertical rhythm or distracting differences between related styles.
- **3:** reading pages show professionally resolved prose–math continuity;
  only localized minor refinements remain. Recurring disruptive families or
  unreliable small-size texture belongs below this anchor.
- **5:** the reading page has exceptional composure and a recognizable voice:
  prose and mathematics sustain one rhythm without flattening their hierarchy.
  Explain why an editor would feature these pages as exemplary mathematical
  typography rather than merely accept them as competent book production.

Darkness ratios may locate problems; equal ink coverage is not the objective.
Council preference cannot establish reading speed, comprehension, accessibility
or fatigue. Those claims need an appropriately designed reader study.

## Council verdict and hillclimb use

Return all eight criterion scores with their ideal, evidence, gap, editorial
justification and next move. Then give:

- **Absolute editorial verdict:** `unresolved`, `functional`, `polished`,
  `distinguished_but_not_feature_ready`, or `feature_ready`.
- **Better versus feature-worthy:** one direct paragraph separating relative
  improvement from remaining distance to the hypothetical perfect font.
- **Three publication blockers, ranked:** the concrete faults or unresolved
  design decisions an exacting editor would send back. If fewer are visible,
  name only those justified; do not manufacture a quota of defects.
- **Positive editorial case:** what, if anything, already deserves attention.
  For `feature_ready`, explain why this deserves a feature and why no observed
  blocker remains. High scores in a few areas cannot conceal a weak family.

Every cycle below feature-readiness must also produce an actionable revision
brief: the observed problem and proof location, proposed change and direction,
reason it could help, proof of success, regression checks, and qualities to
preserve. Rank the next moves and state which to try first. This applies even
when a candidate improves, ties, loses, or the campaign ends at its budget.
Uncertain causes require a concrete diagnostic comparison; missing evidence
requires a specific proof request. “Not good enough” without a path forward
is an incomplete critique. Suggestions remain hypotheses to test.

In paired rounds, report A and B's absolute verdicts and scores as well as
preference. Preserve dissent and engineering failures alongside the aggregate.
A numerical rise selects a useful next iteration; it does not confer editorial
readiness. The research guides rigorous critique; external expert annotation
or a reader study is not a prerequisite for running this council or hillclimb.
