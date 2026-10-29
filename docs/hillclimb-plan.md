# Plan: an exacting typography council and hillclimb

Updated 2026-10-29 to the user's absolute editorial standard. The council grades
against a hypothetical perfect Baskerville companion math font and must explain
the gap between “better” and “featured new design in a top typography
periodical”. The [rubric](rubric.md) defines that bar; the
[judge prompt](../council/judge-prompt.md) makes the reasoning mandatory.
The bounded [three-round campaign](../runs/campaign-2026-10-29/summary.md) is
now implemented and complete; round 2 is retained after nine evaluator tasks.
A complete newly authored math family remains future work. The earlier one-round
[smoke harness](../council/README.md) has now exercised the proof packet,
T3 Code delegates, ballot validation and aggregation. See its
[outcome and instrument findings](../runs/smoke-2026-10-29/coordinator-review.md).
Its raw scores did not justify promotion; its archived-font fixture remains
separate from the fresh design. No further rounds have been launched.

## The governing decision

The council is an aggressive design critic. It can start grading once it has
real proofs and the rubric. Expert-annotated examples, reader studies and a
separate calibration research phase are not prerequisites. The research library
provides substantive typographic standards; the hypothetical ideal provides
the ambition. Reference fonts, the incumbent and generated targets never set
the ceiling. A/B victory and editorial readiness are separate outcomes.

## 1. Assemble actual font proofs

Record the supplied Baskerville face/version, candidate OTF, declared repertoire,
engines, point sizes and output conditions. Preserve font hashes, source revision,
engine/renderer versions and proof-source hashes with every round.

Build a compact proof packet that exposes the eight rubric criteria:

- Latin, Greek, digits, punctuation, variants and confusables, both isolated
  and in mathematical context.
- Straight/round/diagonal fitting contexts, adjacent italic letters, operators,
  relations and repeated signs.
- Inline and display math in real Baskerville prose, with actual text,
  script and script-script views at documented sizes.
- Difficult scripts, accents, limits, fractions, radicals, matrices, wide
  accents and delimiter/assembly transitions.
- Enlarged shape details alongside reading-size pages: the council must judge
  the resulting typography, not just attractive large outlines.

Use the actual target math engine; add another supported engine to expose
interoperability defects. Verify required mappings, successful shaping,
font identity, fallback, clipping and construction behaviour. Mechanical
correctness is a precondition and earns no aesthetic credit.

Keep `archive/` unchanged. Explicitly copy any chosen source fonts or lessons
into the fresh workflow with hashes and notices. Old scripts and thresholds
remain inactive. Published references can illustrate craft, but their quality
is also open to criticism against the same ideal.

## 2. Prepare independent council packets

Borrow Sublimite's `prepare → run → aggregate` shape, structured responses,
blinded A/B identities, saved raw outputs and identical-pair checks. The
[inspection](../research/sublimite/README.md) and pinned reference files remain
available for implementation. Its UI rubric and member selection do not carry over.

Each member gets the same source-grounded rubric, judge prompt and proof packet.
Every member grades all eight criteria. Different review emphases can encourage
careful looking, but no member is allowed to omit the whole-font editorial
judgment. Select available models explicitly during implementation and record
model versions/settings. Do not represent them as named human typographers.

Use neutral candidate labels and keep the identity key, designer rationale,
previous scores and other members' verdicts outside judge access. Record image
hashes and actual image delivery. Include an identical pair and occasional
visible-defect checks to catch broken observation. These are lightweight round
checks, not a research program that delays design work. A clear control failure,
missing image or malformed ballot makes that member's result invalid; report
the round as incomplete rather than silently changing the planned panel.

## 3. Require absolute scores and editorial arguments

Use [rubric version 0.3](rubric.md): 1 unresolved prototype, 2 promising but
unfinished, 3 genuinely polished release-quality work with only minor
refinements left, 4 distinguished but compromised, 5 exemplary and feature-worthy.
Recurring structural or family defects do not earn a default 3. Judges must
justify the positive release-quality achievement behind every score of 3 or more.
All eight scores need these fields:

```text
criterion_id
score                 1..5, or null when not assessable
ideal                 concrete hypothetical perfect solution
observation           proof ID, glyph/formula, region and size
gap_to_ideal         exact visible shortfall, or no observed gap for an earned 5
editorial_justification why this score; why not the next higher score
next_move             single most valuable design revision, if needed
verification          proof and visible success condition; regression checks
preserve              successful qualities the revision must retain
source_ids            practitioner/specification references for the reasoning
```

For a non-assessable criterion, record the missing evidence explicitly instead
of inventing a score. For A/B, return this assessment independently for each
side, followed by the preference. Improvement alone does not raise an absolute
score. Functional passing tests, engineering effort and production polish
alone do not establish a feature-worthy design.

The overall response must include an absolute editorial verdict for each font,
a paragraph titled “Better versus feature-worthy”, ranked publication blockers,
a positive editorial case if one is earned, and the next change to try.
A 5 requires affirmative evidence of exceptional design, not just failure to
notice defects. A lower score requires visible reasons, not theatrical severity.

Every cycle must end with constructive feedback in the existing ballots and
the coordinator's report. For each publication blocker, require an observed
problem, an actionable proposed change and direction, a reason it could help,
and a named proof/success condition with regression checks and qualities to
preserve. The coordinator synthesizes these into a prioritized revision brief,
retaining substantive dissent and selecting one coherent next experiment.
If the cause is uncertain, prescribe a bounded diagnostic comparison rather
than pretend certainty. A vague rejection is incomplete feedback.

This applies to improvements that remain below the ideal, rejected proposals,
ties, and the last cycle of a campaign. Constructive feedback uses the same
response budget; it does not trigger extra judge calls or model debates.
Reserve output space for the revision brief before optional commentary.

## 4. Aggregate without hiding the actual criticism

Show every member's scores and verdict, per-criterion means, overall mean,
paired preferences, dissent, engineering failures and publication blockers.
Use equal criterion weights initially as a transparent project choice.
An overall mean summarizes the council's judgment; it is not the definition
of the hypothetical perfect font.

For the first hillclimb, use Sublimite's conservative iteration rule: prefer a
candidate when its overall mean rises and no member reports a criterion
regression, provided engineering checks pass and the round is complete.
An apparent regression must be resolved in the proofs; a higher average cannot
bury it. Ties keep the incumbent. Document any later change to this policy.

The subsequent user-authorized three-round campaign supersedes that initial
mean-gain proposal with its [frozen contract](../runs/campaign-2026-10-29/contract.json):
at least two candidate preferences, no incumbent preference, no criterion-score
regression, engineering pass and parent evidence audit. A score gain is not
required because small supported improvements can occur inside an integer
anchor. That change was made before round 1, not in reaction to its outcome.

Track two separate outcomes:

1. **Iteration winner:** which version is the more promising next incumbent.
2. **Editorial readiness:** whether each judge would feature it against the
   stated ideal, with its reasons and remaining blockers.

Never relabel the winner as feature-ready automatically. Only report council
consensus on feature-readiness when every member independently gives that
verdict, with complete proof coverage and no unresolved publication blocker.
Otherwise preserve the split verdict. This is the council's hypothetical
editorial judgment, not a claim of actual publication acceptance.

## 5. Close the loop

1. Grade the initial candidate absolutely; rank the gaps to the ideal.
2. Pick the most consequential publication blocker and state one design
   hypothesis. Change a coherent family of shapes, fitting or optical behaviour.
3. Build the OTF and all affected proofs, including contexts that could regress.
4. Run an independent blind A/B council round. Both sides face the same
   absolute rubric and editorial test.
5. Apply the iteration rule, retain all raw critiques, and save the chosen
   version with a before/after proof sheet, remaining publication gaps, and
   an actionable revision brief explaining the next experiment and its checks.
6. Repeat while meaningful gains remain, within a declared call/token budget.
   Stop and report when the budget ends or repeated changes do not improve
   the result. Maintain rollback and a ledger of rejected as well as accepted work.

Before a campaign starts, declare finite assessment, total token/call, per-ballot
output and failure-retry limits, plus a no-progress stopping condition. The
previously suggested numerical limits remain proposals until selected. Reaching
a limit ends execution, not the obligation to explain what could improve.
The final report preserves the best version and its constructive next-step
brief. Further work requires a new campaign instruction; an unfinished critique
or unresolved publication blocker does not automatically extend the budget.

Freeze the rubric during a round. If it changes, regrade both sides under the
same version. Periodically include unseen formulas to expose narrow optimization.
Real typographer/user feedback can enrich critique whenever available; the
council and hillclimb proceed without waiting for it.

## Implementation sequence

1. Proof sources and deterministic renderer, with manifest and engineering checks.
2. Packet preparation, member configuration and structured response schema.
3. Judge calls using the committed prompt; full response validation and raw logs.
4. Aggregation showing absolute scores, publication gaps, relative gains and dissent.
5. Experiment ledger and candidate iteration/promotion command.

Verify the machinery with missing images/members, duplicate criteria, invalid
scores, absent editorial reasons or actionable revision briefs, A/B identity
leakage, identical pairs and
regressions hidden by an average. No model call is needed to test these rules.
The first live council run then produces the actual design diagnosis, and the
hillclimb works directly on its most important publication blockers.
