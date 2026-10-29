# What to borrow from Sublimite

Inspected 2026-10-29. The exact ten-file reference snapshot and hashes are in
[provenance.json](provenance.json); the source checkout was clean at
`c95b6ebc3dc365c7c428dff35d8d739ba52bab8d`. Its LICENSE is included in
`snapshot/`. This is research material, not an activated council runner.

## The existing loop

`tools/council_run.py` separates `prepare`, `run`, and `aggregate`. It packages
screenshots and its rubric into a prompt, collects structured responses from
three model members, then reports scores, disagreement, per-criterion changes,
and identical-pair noise. Absolute grading diagnoses weaknesses; seeded blind
A/B compares an incumbent with a proposal. The identity key stays outside the
prompt. Calls batch scenes per member and preserve raw outputs. The associated
tests cover selected schema, aggregation, blindness, and call-shape behavior.

`docs/design/council.md` treats scores as advisory and requires both improvement
without member-level regressions and Tobias's before/after approval. That is
Sublimite's policy, not an inherited authorization rule for this repository.
The actual typeface shoot-out report admits optical design intent cannot be
established from screenshots; some model responses assume sizes or discuss
unseen details. A future math council must support abstention and distinguish
visible evidence from a suggestion needing another proof.

## Reuse the structure; replace the evidence and judgment

- Retain the prepare/judge/aggregate split, deterministic packet identities,
  saved raw results, seeded A/B identities, and no-op controls.
- Replace editor scenes and C1–C10 with real mathematical proofs at documented
  sizes and typographer-backed criteria. Never inherit UI-specific rules such
  as integer-pixel line pitch, a single accent, or the rubric's dislike of
  anonymous faces. Those are not typeface-quality standards.
- Retain its existing research as a lead list: `state-of-design-2026.md`
  §2 points to Monaspace, Iosevka, optical sizes, FreeType, and rendering;
  `research.json` documents the council's origins. Independently verify the
  relevant primary sources. UI trend reports and generated persona/target
  pictures are not ground truth for math typography.

## Changes required before using the pattern here

These are observations from the inspected implementation, not claims about all
council systems:

1. `aggregate_cmd` skips invalid output and continues with the remaining
   members. Here a missing or invalid required ballot should make a round
   incomplete, not quietly change the panel.
2. `aggregate_ab` reports control noise but does not invalidate noisy judges.
   It also does not require every expected scene's preference exactly once.
   Here control failure must affect eligibility, with missing controls invalid.
3. `validate` checks only part of the declared schema. Use full schema
   validation plus semantic checks (unique IDs, complete proof coverage,
   source IDs, image hashes, and no unsupported visible-evidence claims).
4. The round identifies filenames but does not pin artifact hashes, renderer
   configuration, rubric version, or source corpus. Pin these before scoring.
5. One seeded identity map does not establish order robustness. Include
   counterbalanced repeat packets, no-op pairs, and known visible defects;
   register their acceptance rule before the candidate is revealed.
6. An arithmetic mean of ordinal scores and a veto for every single negative
   ballot can reward noise or stall indefinitely. Report distributions and
   repeated paired preferences, keep functional regressions separate, and
   preregister a conservative promotion rule after measuring judge stability.
7. Models need actual image access. The council notes already record a void
   run where a member received filenames without seeing pixels. Use an
   image-read receipt tied to packet hashes; textual assurances alone do not
   establish perception. Positive and negative control performance is needed.
8. No programmer should see the sealed holdout or hidden control identities.
   A key beside the prompt on an unrestricted filesystem is only nominal
   blinding. The judge process needs a packet-only directory or equivalent
   tool access boundary, with no source checkout or identity key available.

## Lessons explicitly selected from our deprecated prototype

These remain hypotheses and historical observations, not reactivated rules.
The archived verifier smoke test and specificity study show that pooled ratios
can flag professionally drawn fonts, so corpus percentiles cannot define
universal correctness. Its integral rounds were confounded by transplanting
otherwise good signs into incompatible prose. Its 2026-10-21 Greek verdict was
void because a damaged control was not separated. The fresh setup must grade
craft separately from Baskerville compatibility, select controls for the
question actually being asked, and freeze calibration before looking at the
candidate. Do not weaken a failed control rule retroactively.

Original records remain under `archive/2026-10-29-baskerville-companion-math/`
(`research/verifier/SMOKE-TEST.md`, `specificity.md`, and
`verdicts/2026-10-21-greek.md`). No archived code or threshold is adopted.
