# First north star: unified Baskerville mathematics

Adopted direction, 2026-10-29. Continue the accepted image-derived design;
develop a complete, consistent mathematics family and LaTeX package for the
pinned Storm Baskerville 10 Pro text. This is an implementation plan, not a
claim that a font or new master is finished. No image campaign is started here.

## Design authority

**Everything starts from one unified design image.** Integrate the accepted
Greek seed and a substantial four-face Storm text sample into one family-wide
master composition. Every later specimen view, enlargement, correction,
weight, optical treatment and construction derives from its approved version.
Category production sheets never become independent stylistic roots.

The current Greek was prompted regular italic but appears heavy. Preserve its
accepted character and keep weight unclassified until the unified-master proof
compares it with actual Storm italic and bold italic at matched apparent size.
Decide whether the current treatment occupies the regular or bold role before
designing its companion. Do not silently thin it or count it as both weights.

The reference packet now contains a 2560×4800 PNG of actual Storm regular,
italic, bold and bold italic, each with substantial prose, alphabets, figures,
punctuation and Greek. Relevant face crops supplement the whole page in the
prompt. The source identities/hashes are in
[the Storm reference contract](../design/storm-reference.json). Thin measured
baseline/x-height/cap-height lines live in a removable overlay with a mask;
the clean image remains intact. Math-axis and construction guides are added
only after the math geometry is calibrated. Guides are never traced as ink.

The approved Greek sheet is the seed, not the finished whole-family image.
The first master establishes the complete design language. Broader repertoire
is added to that same indexed atlas in controlled root revisions, with whole
family review and preserved approved regions. An individual target is not
production-ready until its actual form or explicit construction rule is
present in the approved root. Use exact atlas crops for legibility alongside
the whole-family image; a dense thumbnail cannot specify fine contours.

## Coverage and deliverables

Target core LaTeX mathematics + `amsmath` layout + AMS font/symbol command
coverage, with a finite modern alphabet set. `amsmath` alone is not a glyph
catalogue. [AMS math facilities](https://ctan.org/pkg/amsmath),
[AMS font/symbol facilities](https://ctan.org/pkg/amsfonts).

The [full inventory](ams-glyph-inventory.md) and
[machine-readable manifest](../design/ams-glyph-inventory.json) currently record:

- **1,196 distinct Unicode scalar targets**, including the required alphabets,
  figures, symbols, arrows, accents and base delimiters.
- **12 sequence targets** for specific standardized/negated variants.
- **717 unencoded/recipe/engineering requests**, including bold counterparts,
  size variants, construction pieces and display forms.
- **585 package/input bindings**, representing 577 distinct spellings;
  aliases can share an outline, while semantically distinct variants cannot
  be merged casually. All 204 direct `amssymb` names are included.

These are overlapping semantic and work counts, **not 1,925 independent
drawings, not a final font glyph count and not 1,925 image calls**. Shape
sharing, mapped aliases and engineered parts will reduce some work; bold and
script construction requirements can add physical glyphs. Resolve the actual
outline list before budgeting the full generation campaign.

The alphabet set includes serif upright/italic/bold/bolditalic Latin and
Greek; script, fraktur/bold-fraktur and double-struck Latin; sans upright and
monospace Latin; five encoded numeral sets. Lowercase script/double-struck and
full four-style Greek are deliberate modern extensions, not claims about the
minimal historic AMS set. Optional extra styles stay outside the frozen list.

Release deliverables are original editable sources, regular and designed bold
math OpenType fonts, OpenType MATH data, a LaTeX loader with audited command
compatibility, reproducible builds and both-engine proof bundles. The regular
math face is an intermediate milestone; full designed bold-symbol support
completes the broader north star. A regular OTF plus bold alphabet codepoints
does not provide a complete bold mathematical expression.

Use **LuaLaTeX first, XeLaTeX as a required second engine**, with `unicode-math`
and `amsmath`. Traditional pdfLaTeX integration is a separate future encoding/
metrics project. Reference text fonts remain user-supplied dependencies.

## Implementation stages

| Stage | Concrete work | Exit evidence |
| --- | --- | --- |
| 0. Preserve and reproduce | Freeze current PNGs, prompts, crops, SVGs, hashes, parameters and environment; store primary-source coverage inputs. | Done: 32 filled SVGs + 32 real-handle views reproduced byte for byte in a new directory. |
| 1. Unified master | Use substantial Storm samples and accepted Greek seed; resolve apparent weight and variant identities; establish shared alphabets, symbols, metrics and construction grammar together. | Approved single image/version/hash, indexed regions, clean and guided views, explicit style/weight decisions. |
| 2. A real math-font pilot | Produce a diagnostic 24-target subset, preserve connected and disconnected ink, fit shared metrics, build cubic outlines and initial MATH data. | New OTF renders fixed formulas in both engines without hidden fallback; working-size Baskerville pages approved. |
| 3. Fixed repertoire batches | Extend that same approved atlas, then crop → enlarge → measure → trace → optical edit in bounded groups. Latin/Greek/figures first; then ordinary symbols/relations, arrows, accents and large operators. | Every target has accepted root lineage, correct identity, curve proof and shared-scale context. |
| 4. Complete math engineering | Finish spacing, italics, accent anchors, script behaviour, MATH constants/kerns, growing delimiters/radicals/accents/arrows, display operators and command shims. | Exhaustive inventory and growth-transition proofs, actual font-use audit, no missing glyphs or undefined commands. |
| 5. Bold and release | Complete the designed bold companion from the same root; exercise bold composites; rebuild and package source/fonts/loader/examples/proofs. | Both engines pass the full fixed corpus, regular and bold; final visual approval at reading size and in large drawings. |

The 24-target pilot is deliberately explicit: Greek **α β θ ν ξ ω**; Latin
**A H O f x d**; digits **0 1 2**; and **+ − = ∑ ∫ √ ( )** plus a **hat accent**.
Fraction bars are calibrated rules, not another independent drawing. Reuse
existing Greek only through explicit adoption when its approved master form,
weight and scale survive the root revision; otherwise new sources are needed.

Pilot formulas include a nested fraction/root with alpha, beta and x;
an integral of f(x) with limits 0 and 1; simultaneous scripts; a hat; and tall
parentheses. The pilot does not use another font to conceal out-of-scope math.
Its limited coverage is marked, and it is not a public complete-font release.

Before broadening tracing, fix the experimental largest-component extractor:
it would discard dots and disconnected components of i/j, equality, colon,
ellipses and many mathematical symbols. Add meaningful topology/orientation
tests and fail on unexplained discarded ink. Keep labels and guides outside
the clean extraction region. The current reproduction tool intentionally fails
on disconnected dark ink rather than quietly mis-tracing it.

## Bounded work and constructive review

Proposed **first production campaign**, subject to a separately fixed run
contract: at most three master-design calls (one proposed root, two revisions),
at most 24 pilot enlargements, and a shared pool of at most six corrective
image edits. That is **33 image calls maximum**, potentially fewer if unchanged
accepted sources can be adopted. No automatic retries, judge debates or
additional styles. Stop on the cap or approved pilot, whichever comes first.
If the root is not good enough after its cap, report the gaps before drawing
24 inconsistent derivatives.

Later repertoire batches fix 24–48 named target IDs, a root revision budget,
one enlargement per new target and a capped correction pool before dispatch.
Calculate cost after command aliases, shared outlines and constructions are
resolved. Prefer local tracing/measurement/curve corrections where appropriate;
do not spend another image call merely because an opaque grade is low.

Every checkpoint returns **what works, the exact remaining gap, an actionable
change and the next proof that would test it**. Check semantic identity and
engineering failures separately from visual refinements. A council, if used,
has a fixed judge count, one critique each and no retry/debate cycle; it cannot
waive the unified root or technical rendering tests. Never claim perfection
from an overlap metric or high council score.

## What “renders correctly” must prove

- Every inventoried command and style resolves to its intended semantic glyph
  or approved construction, with correct operator/relation spacing.
- No `.notdef`, missing-character messages, undefined commands or synthetic
  style substitution; actual math glyphs come from the authored font.
- Fractions, roots, scripts, accents, limits, matrices and aligned equations
  work in display/text/script/scriptscript and cramped contexts.
- Delimiters and horizontal constructions survive every size transition and
  long repeated assemblies without gaps, clipping or wrong proportions.
- Baselines, axis, sidebearings, contrast and page colour read naturally beside
  Storm Baskerville at 8–12 pt; large, distance, negative-space and grid proofs
  agree on design quality. Compare regular and bold roles separately.
- Package loading is tested in ordinary and AMS document classes. Successful
  compilation does not prove absence of fallback: local control probes found
  legacy MSBM10 use when `amssymb` preceded `unicode-math`. The loader must own
  audited compatibility aliases and actual font-use checks, not simply load
  legacy symbol fonts to make commands compile.

The [engineering contract](math-package-engineering.md) details the MATH data,
loader order, font-use inspection and proof matrix. OpenType MATH supplies
layout data and constructions, not a complete typesetting algorithm;
[the specification](https://learn.microsoft.com/en-us/typography/opentype/spec/math)
is the technical source. Maintain separate approved rendering baselines for
LuaLaTeX and XeLaTeX rather than expecting identical pixels.

## Durable project records

- [Pipeline](image-to-font-pipeline.md) and
  [single-master state](../design/unified-master.json).
- [Substantial text reference contract](../design/storm-reference.json) and
  [master prompt template](../design/prompts/unified-master-template.txt).
- [Coverage inventory](ams-glyph-inventory.md),
  [JSON](../design/ams-glyph-inventory.json) and
  [frozen source bytes](../research/coverage/README.md).
- [Engineering contract](math-package-engineering.md),
  [read-only visual/reproducibility audit](pipeline-audit.md).
- [Observed environment](../design/pipeline-environment-2026-10-29.json) and
  [64-file reproduction verification](../runs/pipeline-reproduction-2026-10-29/verification.json).

The new audit agents have completed their scoped work. The rejected arena
remains stopped. Next production work starts with the unified master, not an
independent alphabet campaign or an automatic continuation of old rounds.
