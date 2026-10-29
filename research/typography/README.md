# Typography evidence base

Research round: 2026-10-29. Three parallel GPT-6.1 Terra researchers covered mathematical typography, foundry practice, and contemporary evaluation. The coordinating pass inspected Sublimite, audited key citations, added professional specimens and supplementary sources, and synthesized the proposal.

**Read first:** [council rubric](../../docs/rubric.md) · [implementation plan](../../docs/hillclimb-plan.md) · [Sublimite analysis](../sublimite/README.md).

## Current council direction

The user's subsequent instruction sets an absolute editorial bar: grade
aggressively against a hypothetical perfect math font and explain what separates
“better” from a featured new design in a leading typography periodical.
[Rubric 0.3](../../docs/rubric.md) and the
[judge prompt](../../council/judge-prompt.md) implement that direction. The
research reports below preserve the initial researchers' proposals; their
suggested expert-calibration prerequisites are superseded. Practitioner sources
inform the critique, while expert annotation or a reader study is not required
to start the council or hillclimb.

## What is here

- [Mathematical typography](math/report.md): Knuth, AMS, Beeton/STIX, Vieth, Unicode, and OpenType MATH.
- [Foundry practice](practice/report.md): Adobe optical-size design, Glyphs outline/fitting guidance, Biľak on script integrity, and revival examples.
- [Contemporary evaluation](frontier/report.md): optical axes, actual-engine QA, individual reading differences, and limits of model judgment.
- [Supplement and citation audit](supplement/report.md): Edmondson proofing practice, professional STIX charts, historical material, advanced math engine work, and resolved/flagged citations.
- [Consolidated source registry](sources.json): stable IDs, locators, access/copy status, source URLs and local resource hashes. Area registries retain researcher provenance.

## How this informs the rubric

The strongest direct math-design guidance is Barbara Beeton’s account of STIX’s review criteria (M08 §7): distinguish symbols in isolation, retain hairlines at small sizes, preserve meaningful weight differences, and review related forms together. Edmondson’s proofing practice (S01), the current Glyphs spacing handbook (P02), and the Adobe/Source Serif optical-size accounts (P01/P05) establish concrete craft and proofing questions. MATH specifies layout data, not beauty. Vieth’s comparisons and the local STIX charts show legitimate variety.

The contemporary thread is coordinated optical design, multi-script integrity, and joint font/engine evaluation—not a fashion prescription. Foundational practice remains relevant; publication recency alone does not make a standard. Hagen/Sundqvist (S06), Vieth’s 2023 survey (S07), Biľak’s 2023 essay (P07), and Adobe Aldine’s current family description (S08) extend the historical/design foundations. The detailed Aldine specimen P08 remains an unverified-access lead.

“Ground truth” means traceable primary resources and real specimens here. It does **not** mean the proposed ratings have expert validation, or that practitioner advice supplies universal numerical thresholds. The corpus has no expert-labeled calibration set yet. Print books not actually consulted and inaccessible/index-only leads cannot support an adopted acceptance rule.

## Local resources and copying scope

Resources include the Unicode math report, Adobe’s optical-size technical manual, official STIX Two Math/Text charts, STIX project history/notices, tool documentation with licenses, and a public-domain historical account with primary letter facsimiles. Notes summarize copyrighted web essays rather than copying them wholesale. The historical facsimiles are handwriting, not original printed type specimens.

Keep each item’s notices and access restrictions. Public access does not imply a blanket right to republish: the Adobe manual is retained as a local research reference with redistribution permission unverified. No third-party content is relicensed by these project notes. The Gutenberg HTML keeps its edition terms; only two illustration files are captured, so it is not a complete offline illustrated edition. Official STIX charts are glyph charts, not assembled-equation proofs.

Every captured artifact in the consolidated registry was SHA-256 checked. The source registries record the actual retrieved snapshot, which can differ from the latest release. The existing font-project archive remains unchanged and is not an active dependency.

## Source map

| ID | Author / source | Primary item and locator | Area |
|---|---|---|---|
| M01 | Donald E. Knuth | [Typesetting Concrete Mathematics](https://tug.org/tugboat/tb10-1/tb23knut.pdf) — pp. 31–40 | math |
| M02 | William J. LeVeque | [Font development at the American Mathematical Society](https://www.tug.org/TUGboat/tb02-2/tb03complete.pdf) — p. 39 | math |
| M03 | Microsoft | [OpenType MATH table](https://learn.microsoft.com/en-us/typography/opentype/spec/math) — MathConstants, MathGlyphInfo, MathVariants, layout tags | math |
| M04 | Barbara Beeton, Asmus Freytag, Murray Sargent III | [Unicode support for mathematics, revision 15](https://www.unicode.org/reports/tr25/tr25-15.pdf) — §2.2, §3 | math |
| M05 | STIX Fonts project | [STIX Fonts README and FONTLOG](https://github.com/stipub/stixfonts) — README; FONTLOG release history | math |
| M06 | Ulrik Vieth | [OpenType math font development: Progress and challenges](https://www.tug.org/TUGboat/tb33-3/tb105vieth.pdf) — §4.3–4.9, printed pp. 304–306 | math |
| M07 | Antonis Tsolomitis | [The NewComputerModern font family](https://tug.org/TUGboat/tb42-1/tb130complete.pdf) — p. 52, introduction | math |
| M08 | Barbara Beeton | [The STIX Project — From Unicode to fonts](https://tug.org/TUGboat/tb28-3/tb90beet.pdf) — §7, printed p. 302 (article pp. 299–304) | math |
| P01 | Adobe Systems | [Designing Multiple Master Typefaces](https://partners.adobe.com/public/developer/en/font/5091.Design_MM_Fonts.pdf) — pp. 17–19 | practice |
| P02 | Glyphs | [Spacing — Glyphs Handbook (current web edition)](https://handbook.glyphsapp.com/spacing/) — Opening paragraphs under Spacing; related Kerning chapter P09 | practice |
| P03 | Glyphs | [Drawing good paths](https://glyphsapp.com/learn/drawing-good-paths) — Extremum points; Harmony | practice |
| P04 | Glyphs | [Harmonization](https://glyphsapp.com/learn/harmonization) — Step 2: Curve fitting | practice |
| P05 | Frank Grießhammer / Adobe | [Source Serif gets optical sizes](https://blog.adobe.com/en/publish/2021/03/04/source-serif-gets-optical-sizes) — article body | practice |
| P06 | Paul Barnes / Commercial Type | [Marian Collection](https://commercialtype.com/uploads/0816/a78211661e73a5f0f931ee4b093d79d5772a8e776b3fef864e3f8f76f17b4073/Marian-collection.pdf) — Marian 1757 section; internal page label 38 of 69 (PDF has 73 physical pages) | practice |
| P07 | Peter Biľak / Typotheque | [Typeface design beyond a single script](https://www.typotheque.com/articles/typeface-design-beyond-a-single-script) — Romulus Greek discussion | practice |
| P08 | Robert Slimbach / Adobe | [Adobe Aldine: A contemporary interpretation of the humanist book types](https://assets.fonts.adobe.com/v4k131cywewadll0ib768wamdlq3) — Filling in the Gaps; Optical Sizes | practice |
| P09 | Glyphs | [Kerning](https://handbook.glyphsapp.com/kerning/) — Kerning introduction | practice |
| F01 | Microsoft | [Registered design-variation axis tag: opsz](https://learn.microsoft.com/en-us/typography/opentype/otspec182/dvaraxistag_opsz) — Axis definition; Additional information | frontier |
| F02 | Microsoft | [Recommendations for OpenType Fonts](https://learn.microsoft.com/en-us/typography/opentype/spec/recom) — Families with Optical Size Variants | frontier |
| F03 | Microsoft | [MATH — mathematical typesetting table](https://learn.microsoft.com/en-us/typography/opentype/otspec190/math) — MathConstants; MathGlyphInfo; MathVariants | frontier |
| F04 | Wallace et al. | [Towards Individuated Reading Experiences](https://jeffhuang.com/papers/Readability_TOCHI22.pdf) — sections 4–6; Figure 13 | frontier |
| F05 | Font Bakery contributors | [Font Bakery README](https://github.com/fonttools/fontbakery/blob/main/README.md) — README; License | frontier |
| F06 | fontTools contributors | [fontTools README](https://github.com/fonttools/fonttools/blob/main/README.rst) — README | frontier |
| F07 | Google Fonts contributors | [Diffenator 2 README](https://github.com/googlefonts/diffenator2/blob/main/README.md) — Features; Caveats; Usage | frontier |
| F08 | Microsoft | [Font selection](https://learn.microsoft.com/en-us/windows/win32/directwrite/font-selection) — Typographic font selection and optical size | frontier |
| S01 | James Edmondson / OH no Type Company | [Proof It!](https://ohnotype.co/blog/proof-it) — What the hell is a proof?; Every drawn character; Paragraphs or headlines; Spacing strings; Going Goldilocks | supplement |
| S02 | RoboFont documentation team | [Introduction to spacing](https://doc.robofont.com/documentation/tutorials/spacing-intro/) — The basics; Spacing vs. Kerning; Spacing the lowercase/uppercase | supplement |
| S03 | STI Pub companies / Tiro Typeworks | [STIX Two Math and Text code charts](https://github.com/stipub/stixfonts/tree/bea1dc9a3cc2d8b57e412dfd0f448a84382dfe46/docs) — Math and Text glyph charts; source commit bea1dc9a3cc2d8b57e412dfd0f448a84382dfe46 | supplement |
| S04 | Josiah Henry Benton (1914), reproducing historical letters by John Baskerville | [John Baskerville, Type-Founder and Printer, 1706–1775](https://www.gutenberg.org/cache/epub/71072/pg71072-images.html) — printed pp. 10–12, 25–29; illustrations images/004.jpg and images/005.jpg; Gutenberg terms at end | supplement |
| S05 | Lianmin Zheng et al. | [Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena](https://arxiv.org/abs/2306.05685v4) — abstract; limitations and bias experiments | supplement |
| S06 | Hans Hagen and Mikael P. Sundqvist | [New directions in math fonts](https://tug.org/TUGboat/tb43-3/tb135hagen-mathchange.pdf) — printed pp. 300–310; §1, runtime font fixes and engine changes | supplement |
| S07 | Ulrik Vieth | [An updated survey of OpenType math fonts](https://tug.org/TUGboat/tb44-2/tb137vieth-otmath.pdf) — pp. 213–225; completeness and design choices, especially math alphabet families | supplement |
| S08 | Robert Slimbach / Adobe Originals | [Adobe Aldine family description](https://fonts.adobe.com/fonts/adobe-aldine) — About / Description | supplement |
| S09 | Columbia University Libraries, Rare Book and Manuscript Library | [Baskerville Virgil-title page](https://exhibitions.library.columbia.edu/exhibits/show/lit_hum/item/6284) — object 1080728; shelfmark O17.En1 B29 1757v; original filename 110119093.tif | supplement |

## Next implementation work

Build actual font proofs, wire the council to the committed rubric and prompt,
then iterate on its ranked publication blockers. See the
[implementation plan](../../docs/hillclimb-plan.md). Additional historical
specimens and expert or reader feedback can enrich the evidence as work proceeds.
