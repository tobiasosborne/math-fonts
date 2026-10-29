# Source audit and supplementary evidence

2026-10-29. Added after reading the three Terra reports; IDs resolve in
[sources.json](sources.json). These notes preserve concise evidence rather
than reproducing copyrighted practitioner essays.

## S01 — Proofs as working experiments

James Edmondson describes a proof as a way to expose and test design problems.
His checklist combines enlarged characters, text at intended sizes and spacing
strings. Context exposes texture and weight faults that an alphabet alone
cannot. He recommends testing alternative settings in both directions, rather
than viewing only the favored design. Project consequence: every revision
needs an explicit question and contextual evidence, not only an attractive
showcase. His optional early-stage .notdef workaround is not appropriate for
our coverage/fallback gate and is not adopted.

## S02 — Whitespace is part of drawing

RoboFont teaches balancing space between glyphs with space inside them and
working on fitting while drawing. Establish sidebearings before kerning;
straight/round controls supply a starting rhythm, with optical adjustment for
other shapes. This is Latin fitting instruction, not a formula for math
atom-class spacing. The current Glyphs handbook P02 independently confirms
that sidebearings depend on design and script, with no fixed size rule.

## S03 — Actual professional shapes, not generated targets

The pinned official STIX Two Math and Text PDF charts are stored locally with
the project license. They permit inspection of repertoire and relative design
choices; they are not working formula proofs or evidence that STIX matches
Baskerville. Review a professional family in its native text setting before
using its craft as a positive control. The M05 README credits Tiro Typeworks
and explains the historical Times model and its revision.

## S04 and S09 — History, with provenance limits

Benton's 1914 historical book is included with its electronic edition terms
and two letter facsimiles. The facsimiles are handwriting, not printed font
samples; do not fit an outline to them or infer printed metrics from them.
The historical narrative is a period account, not neutral experimental proof.
The Columbia catalog independently identifies an original 1757 Virgil title
page. Its image was not acquired. A genuine original body-text scan with
known scale remains necessary before making claims about historical fidelity.
Neither source replaces our supplied digital Baskerville companion.

## S05 — Model judges need calibration

Zheng and colleagues examine position, verbosity and self-enhancement biases
when models judge dialogue. This motivates controls and counterbalancing;
it does not validate visual typography judgment or model-human agreement on
math fonts. Our packet isolation, no-op tests, seeded defects and promotion
rules are proposed methods requiring their own calibration, not typographic
standards extracted from this paper.

## S06 — Contemporary math work crosses the font/engine boundary

Hagen and Sundqvist describe runtime font corrections alongside engine changes
for accents, anchors, primes, radicals and other structures. This is a concrete
warning against attributing every rendered defect to an outline or assuming
all MATH consumers behave alike. Preserve engine versions and any font-loader
tweaks; test the same OTF in declared engines. Their implementation choices
are one advanced system's approach, not universal aesthetic requirements.

## S07 — Current comparison, not one ideal alphabet

Vieth's published 2023 survey supersedes the conference draft as the preferred
citation. It compares mathematical repertoire and alphabet design choices
across families and explicitly leaves detailed metric study outside its scope.
Use this to choose diverse professional controls and coverage cases, not to
invent stroke/spacing thresholds or assume current versions match its samples.

## S08 — A contemporary historical revival

Adobe describes Aldine as a Slimbach design with Latin, Greek and Cyrillic,
variable weight and optical size, and screen use in mind. This establishes a
contemporary professional example of coordinated optical and multilingual
work. The detailed specimen P08 is indexed but returned 404 on direct access;
its precise claims are leads pending retrieval, not active rubric evidence.

## Corrections made during synthesis

- Identified M08 as Barbara Beeton, *The STIX Project — From Unicode to fonts*.
  Its actual math design criteria appear in §7 on printed p. 302. Confirmed
  against the official full-issue PDF; the registry now points at the article.
- Replaced P02's broken indexed PDF link with the directly verified current
  online Spacing chapter. It explicitly rejects fixed sidebearing rules.
- Directly verified P03–P07 and the prose-reading PDF F04. P06's internal page
  labels differ from physical PDF page count; the registry records that.
- Marked P08 as a directly inaccessible lead and removed it from the active
  rubric's evidence list. S08 corroborates only the family-level description.

Unresolved: expert-annotated examples and actual math-reader performance data,
original Baskerville body-text scans at known scale, and stable font/renderer
versions for calibration. These are named implementation prerequisites, not
hidden claims that the council already has ground truth labels.
