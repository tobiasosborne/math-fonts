# Baskerville math package: finite v1 glyph inventory

Status: planning snapshot, 2026-10-29. This is a work inventory, **not a claim of font coverage**. The machine-readable [inventory](../design/ams-glyph-inventory.json) has explicit targets, Unicode scalars/sequences, categories, command bindings, alphabet members, construction requests and source hashes. No existing run outputs were changed.

## One design root

Every target refers to `baskerville-unified-master-v1`. Its image path and every `master_cell` are currently null. The complete package must begin with **one unified design image**, continuing the accepted image-derived Greek theme in the context of Baskerville. Category sheets, production sheets and individual enlargements are derived views of that image; they are not separate category designs. The 32 Greek studies are immutable seed evidence to integrate and review, not an alternate root or completed coverage. The inventory records zero filled unified-master cells.

The root should expose Latin, Greek and their weights alongside script/fraktur/blackboard, operators, relations, arrows, delimiters, accents and large operators, at common typographic scales. Its layout can group categories for navigation while preserving a single thematic decision. The four-face Baskerville reference and registration-guide assets are tracked by [the reference manifest](../design/storm-reference.json); they are reference evidence for that one root. Mapping every requested cell and reviewing the root precede any bounded enlargement work.

## What “standard AMS mathematics” means here

`amsmath` is principally a mathematical layout package. It loads `amsbsy`, `amsopn` and `amstext`; its alignment, fraction, matrix, tagging and text facilities do not each imply new glyphs. `amssymb` names extra symbols and depends on `amsfonts`. The actual v1 target therefore combines **core LaTeX mathematics + amsmath + amsfonts/amssymb + the finite alphabet set below**. This is broader and more useful than calling amsmath a glyph list. [AMS math package](https://ctan.org/pkg/amsmath), [AMS fonts package](https://ctan.org/pkg/amsfonts).

The intended modern font interface is Unicode/OpenType MATH with LuaLaTeX or XeLaTeX and `unicode-math`. Legacy command identities are retained in the inventory because names and shapes can differ between legacy TeX and Unicode math. Legacy font/slot fields document the source definition; they are not a commitment to ship a classic 8-bit font encoding. [unicode-math user documentation](https://tug.ctan.org/macros/unicodetex/latex/unicode-math/unicode-math.pdf).

The parsed released CTAN `amsmath` source identifies itself as **2026/05/19 v2.18d**; CTAN's package landing page still displayed 2025/07/09 v2.17z during this audit. The pinned source bytes, rather than the landing-page metadata, determine this inventory. AMS font package metadata and its LaTeX support-file versions also differ: the declaration sources identify 2013/01/14 v3.01. Exact retrieval URLs and SHA-256 values are in JSON.

## Count methodology

| Counted object | Count | Meaning |
| --- | ---: | --- |
| Distinct requested Unicode scalar targets | 1,196 | One codepoint once, across aliases and selectors |
| Requested Unicode sequence targets | 12 | Six standardized variants and six negated-symbol sequences |
| Unencoded/recipe/engineering requests | 717 | Explicitly separate from Unicode coverage |
| Total v1 work records | 1,925 | Scalars + sequences + unencoded requests |
| Package/input bindings | 585 | Includes literal characters, duplicate package definitions, aliases and composites |
| Distinct input spellings | 577 | Repeated across packages counted once |
| Explicit source `let` alias bindings | 9 | Not the total number of semantically equivalent inputs |
| Alphabet selector/member requests | 802 | Inputs under 10 styles; overlaps with scalar targets |
| Named upright operator recipes | 38 | Strings/constructions, not 38 new glyphs |
| Prior Greek outline studies | 32 | Zero coverage credit |
| Unified design-master cells filled | 0 | Root remains to be authored |

These counts must not be added indiscriminately. A glyph may serve multiple encoded characters or command aliases; a recipe may need no new outline. Conversely, an encoded character can require several size, bold or assembly glyphs. **1,925 is not a final OTF physical glyph count and not an image-call authorization.**

Direct declaration extraction found 301 core declarations (including literal letters/digits/punctuation and delimiter/accents), 22 AMS font declarations (including an internal construction piece), and **all 204 direct amssymb symbol declarations**. After selected public composites and source aliases, binding totals are core 328, amsfonts 32, amssymb 210 and amsmath 15. This does not claim to enumerate every macro in amsmath. The full 2,437-scalar unicode-math reference table was used for mapping; its remainder is **excluded** from the production list.

## Finite v1 repertoire

### Alphabets and numbers

Latin `ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz` appears in every listed alphabet. Greek means all 24 capitals, all 24 lowercase letters, final sigma, the epsilon/theta/kappa/phi/rho/pi variants, the capital theta symbol, and the matching partial/nabla identities: 58 member requests per serif style including partial and nabla. Capital Greek letters that resemble Latin remain distinct Unicode semantics; shared outlines are allowed after review.

Greek letters: `Α Β Γ Δ Ε Ζ Η Θ Ι Κ Λ Μ Ν Ξ Ο Π Ρ Σ Τ Υ Φ Χ Ψ Ω` and `α β γ δ ε ζ η θ ι κ λ μ ν ξ ο π ρ σ τ υ φ χ ψ ω`.

Additional Greek/derivative forms: `ς ϵ ϑ ϰ ϕ ϱ ϖ ϴ ∂ ∇`. Upright and bold digamma forms are explicit additions. Dotless `ı ȷ` and their mathematical italic forms are explicit, with separate bold construction requests.

| Style | Latin | Greek + ∂/∇ | Digits | Selector/member requests |
| --- | ---: | ---: | ---: | ---: |
| Serif upright | 52 | 58 | 10 | 120 |
| Serif italic | 52 | 58 | — | 110 |
| Serif bold upright | 52 | 58 | 10 | 120 |
| Serif bold italic | 52 | 58 | — | 110 |
| Double-struck / blackboard | 52 | — | 10 | 62 |
| Fraktur | 52 | — | — | 52 |
| Bold fraktur | 52 | — | — | 52 |
| Script | 52 | — | — | 52 |
| Sans upright | 52 | — | 10 | 62 |
| Monospace | 52 | — | 10 | 62 |

The inventory uses explicit `sym…` selectors to specify mathematical glyph identities. Package wrappers must also establish intended `\mathrm`, `\mathit`, `\mathbf`, `\mathcal`, `\mathbb`, `\mathfrak`, `\mathsf`, `\mathtt` and bold-symbol behavior; those wrappers are not all simple aliases in unicode-math. Script lowercase, blackboard lowercase/digits and a unified full four-style Greek set are deliberate modern v1 extensions beyond the minimal historical AMS defaults. Legacy AMS blackboard is principally uppercase, plus the separately named `\Bbbk`; that limitation must not be attributed to Unicode. [AMS fonts](https://ctan.org/pkg/amsfonts).

Digits are `0123456789`: upright, bold upright, double-struck, sans and monospace. Italic and bold italic numerals have no parallel complete Unicode mathematical digit ranges and remain optional alternate designs. Subscripts and superscripts normally reuse glyphs at engine-selected sizes; they are not an instruction to add every precomposed Unicode subscript/superscript as a separate design.

### Core symbols and AMS extensions

The JSON enumerates every target; these are representative visible families:

- Arithmetic and set operators: `+ − ± ∓ × ÷ · ∗ ⋆ ∘ ∙ ∪ ∩ ⊎ ⊓ ⊔ ∧ ∨ ⊕ ⊖ ⊗ ⊘ ⊙ ⊚ ⊛ ⊞ ⊟ ⊠ ⊡ ∖`.
- Relations and negations: `= ≠ < > ≤ ≥ ≡ ∼ ≃ ≈ ≅ ≍ ∝ ≪ ≫ ≺ ≻ ≼ ≽ ∈ ∋ ∉ ⊂ ⊃ ⊆ ⊇ ⊊ ⊋ ⊢ ⊣ ⊨ ⊩ ∣ ∥ ⊥`; all explicitly declared AMS comparison, set, triangle, turnstile and negated variants are included.
- Arrows/harpoons: `← → ↔ ⇐ ⇒ ⇔ ↦ ↩ ↪ ↼ ↽ ⇀ ⇁ ⇌ ⇋ ↞ ↠ ↢ ↣ ⇇ ⇉ ⇈ ⇊ ↫ ↬ ↶ ↷ ↺ ↻ ↝ ↭ ↰ ↱` plus the core long, diagonal, vertical and AMS negated/tail/multiple arrows.
- Ordinary symbols: `∞ ∅ ℵ ℶ ℷ ℸ ℏ ℓ ℘ ℜ ℑ ∀ ∃ ∄ ¬ ⊤ ⊥ ∠ ∡ ∢ ∴ ∵ ∁ □ ■ ◊ ⬧ △ ▽ ★ ♠ ♣ ♡ ♢` and the named currency, checkmark, registered, maltese and circled-S forms.
- Accents and marks: acute, grave, dot, double/triple/quadruple dot, hat, widehat, tilde, widetilde, bar, breve, check, ring and vector/arrow accents; over/under arrows and braces; slash overlay for general negation.
- Delimiters: parentheses, brackets, braces, ceilings, floors, angle brackets, single/double vertical bars, slash/backslash, vertical arrows, groups, moustaches and AMS corners. `\lvert`/`\rvert` and `\lVert`/`\rVert` preserve delimiter class/spacing while sharing their base shapes.
- Large operators: `∑ ∏ ∐ ⋀ ⋁ ⋂ ⋃ ⨀ ⨁ ⨂ ⨄ ⨆` and integrals `∫ ∬ ∭ ∮ ⨌`; `\idotsint` is an explicit integral–dots–integral recipe.

The class in the original TeX declaration is retained even when the Unicode table categorizes the same shape differently. A binary operator, ordinary symbol and relation can share ink while requiring different spacing. The source symbol names below, rather than these illustrative Unicode strings, define the exact AMS commitment.

Named operators such as `\sin`, `\cos`, `\log`, `\exp`, `\det`, `\lim`, `\gcd`, `\Pr`, `\injlim` and `\projlim` are upright letter/spacing recipes. `\operatorname{...}` must use the matching text/operator face. Arbitrary `\text{...}` uses Baskerville text coverage and shaping; a promise of general multilingual text coverage is outside this finite math list.

### Unencoded and layout engineering budget

The 717 non-scalar work records comprise:

| Kind | Requests |
| --- | ---: |
| Bold symbol counterparts | 426 |
| Bold dotless counterparts | 4 |
| Vertical/horizontal discrete size variants | 144 |
| Extensible assembly pieces | 101 |
| Display large-operator variants | 17 |
| Legacy construction pieces | 11 |
| Legacy shape distinctions | 13 |
| Dotted-integral composite recipe | 1 |

The initial size budget specifies four larger vertical forms, three wider horizontal forms and named joining pieces where applicable, including the left/right bases used by `\xleftarrow` and `\xrightarrow`. It does not prescribe arbitrary geometric stretching. Display sums/products/integrals need designed forms and spacing. Assembly junctions need overlap, rule-weight and clipping proofs. Geometry may be shared when optically justified; the record count is an auditable initial budget, not the final minimum font size.

Regular math is the first implementation milestone. Full v1 completion also requires the designed bold MATH companion represented here; a regular OTF alone does not finish the package. Bold symbol records budget that companion rather than counting automatic emboldening as completion. Their enlarged display/construction requirements are **not** exhaustively multiplied into a final physical glyph count; that remains an engineering refinement. Working-size script/scriptscript behavior, including optional `ssty` forms, must also be proved before deciding whether additional outlines are necessary.

Coverage also requires MATH constants, italic corrections, top-accent attachments, math kerns, variants/assemblies and functional engine integration. Fractions, rules, radical vincula, matrices, alignment, limits and equation numbering need layout support, not a new codepoint per command. [OpenType MATH specification](https://learn.microsoft.com/en-us/typography/opentype/spec/math).

## Semantic gates for the current32 evidence

The trial's labels are Unicode character labels, not necessarily TeX command names:

| Trial label | Source identity | Default italic semantic target | Traditional TeX spelling |
| --- | --- | --- | --- |
| epsilon | U+03B5 ε | U+1D700 𝜀 | `\varepsilon` |
| variant-epsilon | U+03F5 ϵ | U+1D716 𝜖 | `\epsilon` |
| phi | U+03C6 φ | U+1D711 𝜑 | `\varphi` |
| variant-phi | U+03D5 ϕ | U+1D719 𝜙 | `\phi` |
| final-sigma | U+03C2 ς | U+1D70D 𝜍 | `\varsigma` |
| variant-kappa | U+03F0 ϰ | U+1D718 𝜘 | `\varkappa` |

The immutable trial README flags epsilon and kappa pairs as near duplicates and phi as possibly near duplicate. They must remain separate semantic targets until visible, working-size distinctions have been reviewed. Do not merge them because the trial looks similar or “correct” their old evidence silently. Greek omicron and Latin italic o also require distinct Unicode mappings, even if a shared outline proves appropriate.

**Weight is unresolved.** The prompts called the study regular italic, while the accepted visual result may read closer to bold italic. Every evidence row has `coverage_credit: false` and an unresolved-weight field. The italic target IDs above are semantic reference mappings, not regular-weight coverage. At the unified-master stage compare at matched cap/x-height and baseline, against Baskerville regular italic and bold italic, in enlarged and actual-size text/math proofs. Weight classification must follow that evidence before assigning the design to a regular or bold role.

Unicode scalar equality does not erase legacy distinctions: the manifest keeps separate requests for `\emptyset`/`\varnothing`, `\hbar`/`\hslash`, small/short/thick forms, and the legacy `\Join` construction. The six FE00 sequences preserve `\lvertneqq`, `\gvertneqq`, `\varsubsetneq`, `\varsupsetneq`, `\varsubsetneqq`, `\varsupsetneqq`; the six overlay sequences cover negated slanted/double comparisons and double subset relations. Standardized variation selectors and combining negation are separate mechanisms, not interchangeable aliases. [Unicode standardized variants](https://www.unicode.org/Public/17.0.0/ucd/StandardizedVariants.txt), [Unicode mathematics report](https://www.unicode.org/reports/tr25/).

## Optional extensions, outside v1

Bold script/calligraphic; separate script/calligraphic alternatives; sans italic/bold/bolditalic; italic/bolditalic and oldstyle numeral alternates; additional blackboard/script/fraktur Greek; the remaining Unicode mathematical symbols; additional optical masters; extended text languages and text ligatures. These are named options, not implied tasks or automatic generation batches. A later scope decision should add finite rows before production.

## Reproduction and primary sources

`python3 tools/build_ams_inventory.py --sources-dir /path/to/source-cache --download` downloads missing source files and writes only the inventory JSON. To reproduce this snapshot byte-for-byte, retain/cache the source bytes with the SHA-256 values in JSON; moving CTAN/GitHub URLs can later change. The script checks every extracted declaration maps to a target, all 32 studies map to italic semantic identities, all glyph rows share the unified master ID, and all six FE00 sequences occur in Unicode's standardized-variants data. It fails on an unmapped direct symbol instead of silently calling the scope complete.

The source bytes are now retained under
[`research/coverage/2026-10-29/`](../research/coverage/README.md). Use that
directory without `--download`, and an explicit new `--output`, to reproduce
this snapshot without relying on temporary caches or upstream changes.

Primary input URLs:

- [LaTeX core font declarations](https://raw.githubusercontent.com/latex3/latex2e/main/base/fontdef.dtx).
- [AMS font declarations](https://mirrors.ctan.org/fonts/amsfonts/source/amsfonts.dtx).
- [AMS symbol declarations](https://mirrors.ctan.org/fonts/amsfonts/source/amssymb.dtx).
- [amsmath source](https://mirrors.ctan.org/macros/latex/required/amsmath/amsmath.dtx).
- [AMS named-operator source](https://mirrors.ctan.org/macros/latex/required/amsmath/amsopn.dtx).
- [unicode-math symbol mapping table](https://tug.ctan.org/macros/unicodetex/latex/unicode-math/unicode-math-table.tex).
- [unicode-math compatibility definitions](https://tug.ctan.org/macros/unicodetex/latex/unicode-math/um-code-epilogue.dtx).
- [Unicode 17.0 character data](https://www.unicode.org/Public/17.0.0/ucd/UnicodeData.txt).
- [Unicode 17.0 standardized variants](https://www.unicode.org/Public/17.0.0/ucd/StandardizedVariants.txt).

Local TeX support files were also inspected; paths and hashes are retained under `local_installation_audit`. Source extraction is a coverage method, not a visual design test or proof of package compatibility. No image generation, council, arena or evaluator work is authorized by this document.

## Exact 204 amssymb direct names

The following groups contain the 204 directly declared names, once each. Grouping follows target shape categories; legacy spacing classes remain in JSON. Six additional `amssymb` source aliases are `\restriction`, `\Doteq`, `\doublecup`, `\doublecap`, `\llless`, `\gggtr`. `amsfonts` dependency names (including `\rightleftharpoons`, `\mho`, `\hbar` and corners) are separate bindings.

**alphabet (8):**

`\Bbbk` `\beth` `\daleth` `\digamma` `\eth` `\gimel` `\hslash` `\varkappa`

**arrow (28):**

`\Lleftarrow` `\Lsh` `\Rrightarrow` `\Rsh` `\circlearrowleft` `\circlearrowright` `\curvearrowleft` `\curvearrowright` `\downdownarrows` `\leftarrowtail` `\leftleftarrows` `\leftrightarrows` `\leftrightsquigarrow` `\looparrowleft` `\looparrowright` `\nLeftarrow` `\nLeftrightarrow` `\nRightarrow` `\nleftarrow` `\nleftrightarrow` `\nrightarrow` `\rightarrowtail` `\rightleftarrows` `\rightrightarrows` `\rightsquigarrow` `\twoheadleftarrow` `\twoheadrightarrow` `\upuparrows`

**binary operator (22):**

`\Cap` `\Cup` `\barwedge` `\boxdot` `\boxminus` `\boxplus` `\boxtimes` `\centerdot` `\circledast` `\circledcirc` `\circleddash` `\curlyvee` `\curlywedge` `\divideontimes` `\dotplus` `\doublebarwedge` `\intercal` `\leftthreetimes` `\ltimes` `\rightthreetimes` `\rtimes` `\veebar`

**legacy shape variant (10):**

`\nshortmid` `\nshortparallel` `\shortmid` `\shortparallel` `\smallfrown` `\smallsetminus` `\smallsmile` `\thickapprox` `\thicksim` `\varpropto`

**ordinary symbol (23):**

`\Finv` `\Game` `\backepsilon` `\backprime` `\because` `\bigstar` `\blacklozenge` `\blacksquare` `\blacktriangle` `\blacktriangledown` `\blacktriangleleft` `\blacktriangleright` `\complement` `\diagdown` `\diagup` `\lozenge` `\measuredangle` `\nexists` `\sphericalangle` `\square` `\therefore` `\triangledown` `\varnothing`

**relation (112):**

`\Bumpeq` `\Subset` `\Supset` `\Vdash` `\Vvdash` `\approxeq` `\backsim` `\backsimeq` `\between` `\bumpeq` `\circeq` `\curlyeqprec` `\curlyeqsucc` `\doteqdot` `\downharpoonleft` `\downharpoonright` `\eqcirc` `\eqsim` `\eqslantgtr` `\eqslantless` `\fallingdotseq` `\geqq` `\geqslant` `\ggg` `\gnapprox` `\gneq` `\gneqq` `\gnsim` `\gtrapprox` `\gtrdot` `\gtreqless` `\gtreqqless` `\gtrless` `\gtrsim` `\gvertneqq` `\leftrightharpoons` `\leqq` `\leqslant` `\lessapprox` `\lessdot` `\lesseqgtr` `\lesseqqgtr` `\lessgtr` `\lesssim` `\lll` `\lnapprox` `\lneq` `\lneqq` `\lnsim` `\lvertneqq` `\multimap` `\nVDash` `\nVdash` `\ncong` `\ngeq` `\ngeqq` `\ngeqslant` `\ngtr` `\nleq` `\nleqq` `\nleqslant` `\nless` `\nmid` `\nparallel` `\nprec` `\npreceq` `\nsim` `\nsubseteq` `\nsubseteqq` `\nsucc` `\nsucceq` `\nsupseteq` `\nsupseteqq` `\ntriangleleft` `\ntrianglelefteq` `\ntriangleright` `\ntrianglerighteq` `\nvDash` `\nvdash` `\pitchfork` `\precapprox` `\preccurlyeq` `\precnapprox` `\precneqq` `\precnsim` `\precsim` `\risingdotseq` `\subseteqq` `\subsetneq` `\subsetneqq` `\succapprox` `\succcurlyeq` `\succnapprox` `\succneqq` `\succnsim` `\succsim` `\supseteqq` `\supsetneq` `\supsetneqq` `\trianglelefteq` `\triangleq` `\trianglerighteq` `\upharpoonleft` `\upharpoonright` `\vDash` `\varsubsetneq` `\varsubsetneqq` `\varsupsetneq` `\varsupsetneqq` `\vartriangle` `\vartriangleleft` `\vartriangleright`

**symbol (1):**

`\circledS`

