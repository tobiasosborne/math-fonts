# Baskerville math package: engineering contract and bounded implementation plan

Planning baseline: 2026-10-29. This document specifies future implementation;
it does not report a completed font, authorize image calls, reopen the arena,
or promote an earlier experimental font.

## Design invariant and present evidence

**Everything starts from one approved unified design image.** The accepted
current image-derived Greek design is the seed for that composition. All
alphabet, numeral, symbol, weight and size sheets must be crops or documented
derivations of that root. Independent glyph enlargements receive the root and
their original crop, never another enlargement as their sole source. Every
font glyph must identify its root-image region or an explicit construction
rule derived from the root's family grammar. This includes arrowheads, rules,
radical parts, delimiter assemblies and optical variants. No unrelated font
outlines may silently become the geometry for an uncovered class.

The existing [Greek trial](../runs/glyph-consistency-2026-10-29/README.md)
contains 32 independent enlargements and locally traced cubic outlines.
Preserve it unchanged. Its reported registration removes individual size and
framing differences; it does not establish a baseline, advance width, spacing,
optical size, mathematical identity or MATH data. In particular, epsilon,
kappa and phi variant identity needs a semantic review. The full-family root
composition is a future approved artifact; the Greek sheet alone does not
establish the entire AMS family.

The accepted Greek prompt calls for regular italic, but its visual weight is
unresolved and appears closer to bold italic. Keep this as an accepted italic
design with uncalibrated weight. Before assigning a weight or deriving companion
styles, compare the unified master at matched x-height and optical size with
the pinned Baskerville regular italic and bold italic. Do not silently thin
the accepted forms or relabel their weight to resolve the discrepancy.

## Concrete v1 target

**Sourcing update:** [reuse policy](glyph-reuse-policy.md) supersedes the
standalone-all-outlines assumption below. Existing ordinary Baskerville
alphabets/numerals are external-font roles supplied through explicit tested
configuration. The custom OTF supplies new mathematical work. Validate intended
multi-font sourcing, rather than requiring all package coverage in one binary.

Ship a cubic-outline OpenType math font, tentatively
`BaskervilleCompanionMath-Regular.otf`, plus a small LaTeX loader. The font
contains the complete frozen v1 repertoire, its mathematical alphabet styles,
script optical variants and construction pieces. “Regular” describes its
default math version; bold alphabet glyphs are separately encoded inside it.
Ordinary and bold mathematical symbols are different requirements. A complete
bold math version needs a separately engineered MATH font. The adopted full
inventory includes that bold companion as a completion milestone, after the
first regular-math implementation; a regular-only build is an intermediate
deliverable, not the completed north star. See the [coordinator plan](baskerville-math-plan.md).

The primary engine is **LuaLaTeX**, with **XeLaTeX** a required second engine.
Use `unicode-math` and `amsmath`. `unicode-math` requires OpenType mathematics
and aims for substantial legacy compatibility, while documenting differences
from traditional definitions. [Package scope](https://ctan.org/pkg/unicode-math)
and [AMS layout facilities](https://ctan.org/pkg/amsmath).

Deliverables proposed for the v1 release:

| Artifact | Purpose |
| --- | --- |
| Original editable source, cubic contours, feature source, metrics and construction recipes | Rebuild the new family without inherited patched geometry |
| `.otf` containing `MATH`, `cmap`, CFF outlines and required font metadata | Portable math-font binary; no dependency on a patched system font |
| `baskervillecompanionmath.sty` | Engine guard, deterministic font selection, explicit options and tested AMS command aliases |
| Example text-font configuration | User-supplied Baskerville file paths and all four prose faces, independent of the math loader |
| Frozen command/codepoint/glyph inventory and provenance manifest | Define what “standard AMS coverage” means and what each glyph uses |
| PDFs, raster proofs, engine logs, actual font-use reports and regression summaries | Verify layout, appearance and absence of fallback |
| License/attribution files, build lock and installation example | Establish redistributable contents and reproducibility |

Reject pdfLaTeX in this loader with an actionable engine message. A legacy
pdfLaTeX release would need its own encodings, TFM/VF metrics, font maps,
compatible outline format and extensible recipes. An OpenType `MATH` table
does not provide that integration. Keep this separate from v1; do not promise
that an OTF plus `.sty` automatically supports pdfLaTeX.

## Pin the Baskerville text reference

Read-only inspection found these distinct local choices:

| Local family | Evidence and implication |
| --- | --- |
| Baskerville 10 Pro / Baskerville 120 Pro | Storm/František Štorm metadata; installed 2006 files. Earlier active proof tools explicitly select the **10 Pro** files. This is the recommended provisional proof reference. |
| Berthold Baskerville / Berthold Baskerville Book | Separate installed TTF families; regular carries Adobe 1992 copyright and Berthold trademark metadata. Do not substitute based on the word Baskerville. |
| GFS Baskerville | Installed regular OTF, 389 glyphs, no `MATH`; an additional Greek/text reference, not the selected four-face text family or a complete math engine font. |
| Berenis ADF Pro / Berenis ADF Pro Math | Installed; the inspected “Math” OTF has 1,280 glyphs **without** a `MATH` table. Its name does not make it a `unicode-math` replacement. |

The four provisional text files live in
`/home/tobias/.local/share/fonts/Baskerville 10 Pro/`. Freeze these identities
before the first mixed-page proof:

| Filename | SHA-256 |
| --- | --- |
| `Baskerville10Pro.otf` | `402c85ca431a105b56e34cdbd5a01dae9f44f129e6b4f3c2e062cf5cb21dad3e` |
| `Baskerville10Pro-Italic.otf` | `b7c1c8e26c169eaa8a05d1354793a3cb9351c7a763c1e0864189f41860c652af` |
| `Baskerville10Pro-Bold.otf` | `ddc7383e768b3291368a454efef9f2bbddfd36aa55b6b4fc92e61d2bcbcaaa4a` |
| `Baskerville10Pro-BoldItalic.otf` | `4430977b025b08c62f975fbfc06d120fde12be4cab08119fd89ae3752d5bf81f` |

Regular and italic identify version `001.000`; bold and bold italic identify
`1.000 2006 initial release`. All use 1,000 units per em. This pins the existing
files, not purchase entitlement or approval of a new reference. The foundry's
current [Baskerville Original page](https://www.stormtype.com/families/baskerville-original)
is a separate current product reference; do not assume it is binary-identical
to these local versions. Final reference selection must be recorded in the
design contract with files, hashes, apparent-size comparison and rights status.

Load text by explicit filename/path with explicit italic/bold/bold-italic
partners. Do not use a family-name search that can select another revival or
synthetic style. Keep text fonts outside the distributable math-font payload.

## AMS integration is a mapping and layout contract

Canonical package order is `amsmath`, any required compatibility support,
then `unicode-math`; the loader supplies the new `.otf` explicitly. The
upstream [implementation requires amsmath](https://raw.githubusercontent.com/latex3/unicode-math/master/um-code-opening.dtx).
Its [user documentation](https://raw.githubusercontent.com/latex3/unicode-math/master/um-doc-main.tex)
explains the OpenType font selection, legacy alphabet distinctions, math
styles and script-font options. The default configuration should preserve
familiar TeX conventions using explicit `math-style=TeX,bold-style=TeX`;
offer ISO conventions as a named option and prove both mappings.

The loader must fail clearly if its specified file is absent or lacks MATH;
it must never continue with an implicit Latin Modern Math default. A proposed
user-facing setup is:

```tex
\usepackage{amsmath}
\usepackage{baskervillecompanionmath} % future loader; selects authored OTF
```

The loader itself owns any needed `graphicx` dependency and the supported
`unicode-math` configuration. Its text-font example should remain separate,
using the four pinned prose files from a user-specified path.

`amsmath` owns structures such as `align`, matrices, cases, `\text`, fractions,
operator declarations and limits. A font supplies the glyphs and layout data;
it does not implement these environments. Conversely, `amssymb` supplies
legacy symbol declarations using AMS font families; see the
[AMS fonts package](https://ctan.org/pkg/amsfonts). **Command compatibility
does not require using those legacy font binaries.** The v1 loader should
provide missing aliases through audited Unicode glyphs or approved family
constructions and should not require `amssymb` as its canonical dependency.

For every supported command record: argument grammar, math class, Unicode
scalar or sequence, chosen style, actual glyph(s), growing/non-growing status,
and whether it is an alias, dedicated glyph or macro construction. Preserve
relation/binary/operator spacing, delimiter semantics and variant identities.
Do not equate a variant with a superficially similar character just to make a
compile pass. Inventory `\Bbbk`, `\varnothing`, `\smallsetminus`, negated
relations and variant subset/superset signs explicitly. Non-Unicode variants
need documented feature/sequence or loader access, not invented Unicode values.

Keep `\mathrm`, `\mathit`, `\mathbf`, `\mathsf`, `\mathtt` behavior explicit:
these may select text alphabets under `unicode-math`, whereas `\symup`,
`\symit`, `\symbfup` and `\symbfit` request mathematical alphabets. Test both
paths and their font allowlists. `\text{...}` intentionally uses prose fonts.
Do not assume `\boldsymbol` or `\bm` is a complete bold-symbol solution;
specify supported use and compare alphabet commands with composite expressions.
Support of a bold whole formula requires actual bold operators and construction
pieces, not merely bold A–Z and Greek.

Local compatibility probes used an installed **TeX Gyre Pagella Math control**,
not a proposed substitute for the authored family. On both engines,
`unicode-math` followed by `amssymb` fails with `Command \eth already defined`.
Without legacy `amssymb`, `\nleqslant` was undefined in installed version 0.8r.
The existing `\smallsetminus` construction called `\rotatebox` and required
`graphicx` in the probe. These findings require explicit loader decisions and
an exhaustive command audit; successful common formulas are insufficient.
With `graphicx` and without the unsupported alias, the canonical probe compiled
on both engines. With `amssymb` loaded first and both `\nleqslant` and
`\varsubsetneq` included, it also compiled, but `pdffonts` showed **MSBM10**
embedded on both engines. That is direct evidence of legacy font use surviving
a successful Unicode-math document. The control test used Latin Modern prose
intentionally; that text use must not be mistaken for mathematical fallback.
Classes such as `amsart` that preload AMS font support need separate tests.
Never blanket-disable their package declarations and assume equivalence.

## Engineering the font from the master grammar

Adopt a shared coordinate system before fitting: UPM, baseline, x-height,
cap height, math axis, overshoots, ascender/descender and stroke/rule targets.
Measure the approved root and the pinned prose font at matched apparent size;
record intentional mathematical adjustments. Resolve actual sidebearings and
advances in strings, not by per-cell registration. Retain raster-fit evidence
through optical editing: before/after masks, boundary distances, counter
counts, darkness and area, plus control-point/tangent views. These measurements
are diagnostics; none substitutes for working-size reading.

The OpenType interface has three components: `MathConstants`, `MathGlyphInfo`
and `MathVariants`. Per-glyph information covers italic corrections, top-accent
attachments, extended-shape coverage and height-dependent math kerns.
Variants can use discrete sizes and assemblies; assembly parts specify
connector lengths, advances and extender status, with a minimum overlap.
The table supplies data rather than one universal layout algorithm.
[OpenType MATH specification](https://learn.microsoft.com/en-us/typography/opentype/spec/math).

The following are proposed engineering tasks and proof obligations, not
numerical values to inherit from another font:

| Area | Required implementation and evidence |
| --- | --- |
| Constants | Maintain a complete reviewed constants source. Calibrate axis/leading, script percentages, display-operator threshold, accent heights, script shifts and gaps, limit placement, stacks, fraction shifts/gaps/rules, skewed fractions, bars, radicals and radical-degree placement. Associate each family with a small proof and a recorded rationale. Zero is allowed only with an explicit reason. |
| Italic correction | Set by glyph and style after advances are fixed; test f, V, Greek overhangs and integral limits against upright neighbors and simultaneous scripts. Do not use one global slant correction. |
| Top accents | Set optical attachment for bases and accents, including skewed Greek, narrow letters, dotless i/j and stretched accents. Check single and nested accents independently of ordinary GPOS mark attachment. |
| Math kerns | Review four corners with multiple script shapes and heights. Require ordered break heights and finite values; test right scripts plus supported prescripts. Validate actual engine behavior. |
| Extended shapes | Mark tall constructions deliberately so attached scripts track the complete expression; prove nested parentheses with external scripts. |
| Vertical growth | Derive parentheses, brackets, braces, floors, ceilings, bars and radicals from the root's curvature/stroke grammar. Give appropriate discrete variants and repeated-part assemblies; verify braced middle symmetry and radical-to-rule joins. |
| Horizontal growth | Derive arrows, over/underbraces and wide accents from the same root. Prove narrow, medium, wide and multi-extender spans; preserve arrowhead contrast, brace cusp and accent centering. AMS extensible-arrow macros may use leaders or composite machinery, so test the macro output as well as the font's MATH entry. |
| Operators | Design text/display sums, products, integrals and supported multiple/contour forms with their limits and family color. Different growing classes need different recipes; do not mechanically stretch every symbol. |

Populate ordinary metrics and semantic `cmap` before indexing MATH data;
rebuild every coverage table against the final glyph order. Preserve cubic
curves in CFF, correct winding/counters, valid bounding boxes and no unintended
intersections or degenerate segments. Validate all glyph references including
unencoded assembly pieces. Use a full Unicode cmap supporting supplementary
math alphabets, including their legacy Letterlike Symbols exceptions. Unicode
math alphabet styles can carry meaning, and Greek variants need deliberate
mapping; see [Unicode TR25, revision 15](https://www.unicode.org/reports/tr25/tr25-15.pdf).
Freeze an actual Unicode data version for the inventory rather than treating a
proposed report draft as normative coverage.

For script styles, start with the approved family rather than a new design.
Generate optical derivatives with documented changes to apertures, counters,
spacing and fragile strokes. Encode two `ssty` optical levels when needed and
verify the selected glyphs. The [registered ssty feature](https://learn.microsoft.com/en-us/typography/opentype/spec/features_pt#tag-ssty)
uses optical alternates rather than doing the size reduction itself. Keep
actual point scaling separate. An initial proof experiment may compare
script ratios 80/60 and conventional 70/50; choose values from reading proofs,
not from the assumption that either pair is ideal. Cover display, text,
script and scriptscript, with cramped forms exercised through nested fractions
and radicals. Engine-specific layouts may differ; require correct outcomes
and separate baselines rather than pixel identity between engines.

## Proof matrix and regression acceptance

Freeze a finite corpus from the coverage inventory before implementation.
Every release runs both engines, with the pinned text configuration and no
development fallback fonts. At minimum:

| Proof group | Cases |
| --- | --- |
| Identity and styles | Every command and codepoint; Latin/Greek/numerals in every supported alphabet, Greek variants, dotless forms, blackboard/script/fraktur/sans/mono, negations and composite aliases |
| Real pages | Baskerville prose with dense inline math and displays at 8, 10, 11 and 12 pt; regular/italic/bold prose; enlarged inspection plus 100% working size and distance/texture views |
| Scripts and accents | Deep subscripts/superscripts, simultaneous scripts, limits/nolimits, adjacent italic/upright, hat/tilde/wide versions, dot/vector accents, nested accents and dotless bases |
| Structures | Nested fractions, binomials, roots with degrees, aligned equations, cases, matrices, multline/split, named operators, punctuation and multiline delimiters |
| Growth | Requests immediately below/at/above every size transition and at least one multi-extender construction in both axes; asymmetric tall/deep contents; narrow-to-wide arrows with labels |
| Integration | `article` and AMS classes; canonical loader; documented older preamble order; explicit ISO option; text-vs-symbol alphabets; declared unsupported engine/order failure messages |

Acceptance is layered. All structural failures block a release; visual
acceptance remains a recorded human design judgment:

1. **Coverage:** exact inventory coverage, correct classes/mappings, all
   MATH/GSUB references present, and no `.notdef` substitutions or wrong
   variant aliases. Exercise all aliases, not just one sample from a family.
2. **Execution:** zero undefined commands, missing-character messages, font
   substitution or synthetic-style warnings. Use `-halt-on-error`, strict
   missing-character tracing, and a log parser. Keep narrowly documented
   exceptions separate from general suppression.
3. **Font provenance in output:** record resolved filenames and hashes from
   TeX's recorder and inspect `pdffonts`. A font merely being loaded does not
   prove it rendered a glyph. Use LuaTeX node inspection for actual math
   font/glyph use, plus PDF per-glyph font inspection or isolated symbol PDFs
   on XeTeX. Maintain an allowlist by semantic role: authored math versus
   intended text/operator alphabets. Reject Latin Modern Math, AMS MSAM/MSBM,
   or any unrelated math face rendering an in-scope symbol. Subset prefixes
   and renamed fonts require resource-to-source mapping, not name matching
   alone. Test the detector with a deliberately injected fallback.
4. **Geometry:** deterministic units/metrics, ordered growth variants,
   valid assembly connectors and sufficient overlap, no uncovered reference,
   no clipping or broken joins across transition sizes. Distinguish intended
   touching constructions from accidental collisions. Save measured boxes
   and high-resolution renders at the failing size.
5. **Reading/design:** approve rhythm, mathematical identity, script survival,
   rule weight, accent alignment and prose/math color at realistic size.
   Keep raster baselines per engine/rendering stack and inspect material
   differences; antialiasing tolerance must not mask a missing glyph or
   fallback. Set numerical budgets after measuring a frozen approved pilot,
   not after seeing an inconvenient regression.

The historical 92.54% enlargement overlap is evidence of raster consistency,
not a release threshold for the full family. A font can have a valid MATH table,
compile cleanly and still fail the design gate.

## Provenance, licenses and packaging

Record a manifest chain: approved master hash → crop rectangle → independent
enlargement request/model/output hash → tracing parameters/SVG hash → optical
edits → glyph source → compiled font hash. Record engineered constructions
against their root grammar rule and component sources. Human corrections need
an author/date/reason and before/after proof, not an undocumented replacement.

Generated PNGs are project design evidence inspired by references; do not
credit them as foundry-authored assets or imply endorsement. Preserve actual
reference-font authorship separately. Never copy commercial reference outlines
into the new font merely because the files are installed. The inspected Storm
regular file embeds an EULA describing ownership and restricted transfer of
converted software; acquisition/license entitlement was not established by
this inspection. Keep those binaries user-supplied and document permitted
proof/embedding use before public distribution. Current foundry information
also distinguishes licensing arrangements: [Storm help](https://www.stormtype.com/help).

Treat licenses as artifact-specific. The local GFS package includes an OFL 1.1
notice and reserved name; Berenis metadata identifies GPL v2-or-later with a
font exception. These are inventory facts, not authorization to mix their
geometry into the master-derived design. Review the exact notices if any code,
outlines or metrics are intentionally adopted. `OS/2.fsType` is embedding
metadata, not a grant to redistribute or modify everything in the file;
the [OpenType OS/2 specification](https://learn.microsoft.com/en-us/typography/opentype/spec/os2#fstype)
ties embedding to the same underlying license obligations. Set the new font's
license/name/copyright records to its actual provenance; do not inherit a
donor font's claims. Select font, code and documentation licenses explicitly
once the source ledger is complete.

## Bounded implementation sequence

1. **Freeze the contract:** approve the unified root composition, pinned
   text reference, semantic inventory, target sizes, supported commands/styles,
   license boundary and finite generation budget. No image call is authorized
   by this planning document.
2. **Engineer a small pilot:** adopt immutable Greek evidence explicitly;
   fit shared metrics and spacing for a diagnostic group, plus one accent,
   radical, fraction, integral and extensible delimiter derived from the
   approved grammar. Produce a real test OTF with MATH and both-engine proofs.
3. **Freeze pilot acceptance:** inspect smooth curves, working-size pages,
   semantic variants and actual font use. Record the metric budgets and
   design decisions before broadening the glyph set.
4. **Build fixed coverage batches:** complete the frozen repertoire in
   recorded groups, each rooted in the same approved composition. Stop each
   batch at its stated size/budget; failures become named issues rather than
   automatic image retries or a new council campaign.
5. **Complete constructions and optical engineering:** finish constants,
   script glyphs, accents, growth recipes and audited command shims. Run the
   fixed corpus and resolve the resulting bounded issue list.
6. **Package and release review:** rebuild from source, audit licenses and
   font use, inspect every release proof, and publish artifacts only with
   accurately scoped coverage and limitations. A technically passing build
   remains a candidate until its visual design is accepted.

No fourth Greek round, arena match, evaluator retry or unbounded generation
loop is implied by this sequence. The earlier arena and its designer agents
remain stopped.

## Local environment and remaining gaps

Observed: LuaHBTeX 1.17.0 and XeTeX 0.999995 from TeX Live 2023/Debian;
`unicode-math` 0.8r (2023-08-13); `amsmath` and `amssymb` installed. The project
`.venv/bin/python` provides Python 3.12.3 and fontTools 4.68.0; system Python
does not import fontTools. `pdffonts`, `pdftotext`, `pdftoppm`, `mutool`,
`otfinfo`, Fontconfig and standard math control fonts are available.
`fontforge` and the `hb-shape` executable were not found in PATH; neither is
essential if the reproducible builder uses fontTools and TeX proofs. Freeze
the actual chosen builder/renderer versions rather than inventing an
installation dependency.

Still needed: approved full-family root, pinned final text choice and license
entitlement record, frozen full AMS mapping inventory, font source/build system
for these raster-derived outlines, spacing/optical metrics, all MATH tables
and construction parts, automated actual-font-use audit and accepted
working-size proof baselines. Existing traced SVGs and earlier inherited OTFs
do not fill these gaps. This planning pass changes no run, font or image.
