# Typeface practice: evidence and proposed research plan

Research date: 2026-10-29. Scope: practice for a future math-font council, not a font design or an executed review. Source IDs and access conditions are in sources.json; the locally captured Adobe manual is an accessible primary technical artifact, not a grant of redistribution rights.

## Starting point and boundary

The sublimité state-of-design document is about an editor's physical text size, rendering, and UI hierarchy; its rubric grades still screenshots and its council uses absolute scoring and blind A/B comparisons. The research.json findings concern that editor's design and implementation. These are useful for evidence discipline, named observations, blind comparison, and separating constraints from scores, but neither its editor-specific pixel sizes, performance constraints, its periodical persona, nor its UI taste are evidence for the shape of a mathematical typeface. Do not import its scoring or no-regression rule as established project policy. The archived project remains historical and untouched.

## Source observations

- [P01, pp. 17–19, especially p. 18] Adobe describes optical size as coordinated changes in fit, counters, proportions, contrast and weight; small and large designs need different adjustments, possibly nonlinear. Its 1200 dpi proofing recommendation belongs to its 1997 multiple-master print workflow, not a universal modern screen requirement.
- [P02, current web chapter, opening paragraphs] Glyphs describes spacing as establishing a line's even rhythm and kerning as adjustments to particular pairs. The parent research pass directly verified the current online Spacing chapter; the original broken PDF URL was replaced in the registry. The chapter says fitting depends on design and script, with no fixed sidebearing rule.
- [P03, “Extremum points”, “Harmony”] Glyphs recommends economical paths, appropriate extrema and smooth joins, with exceptions for shallow curves. The visible shape is the point; node count alone is not quality.
- [P04, “Step 2: Curve fitting”] Glyphs offers common handle proportions as practical observations and explicitly says to adjust for the design. They are not a universal pass/fail range.
- [P05, “Source Serif gets optical sizes”] Frank Grießhammer explains that small text benefits from more open spacing and that optical sizes also change proportions and detail. This is design-specific guidance, not proof that any particular math script size is legible.
- [P06, Marian 1757, p. 38 of 69] Paul Barnes describes his revival as based on Baskerville's 1757 Virgil; the collection's broader Marian treatment is deliberately conceptual. A modern interpretation demonstrates an approach, not the original punches or a prescribed metric.
- [P07, “Romulus Greek” discussion] Typotheque describes the danger of forcing Latin contrast logic onto Greek shapes. Greek in mathematical notation has distinct conventions and roles; native-script review helps but cannot alone establish mathematical correctness.
- [P08, “Filling in the Gaps”, “Optical Sizes”] Robert Slimbach describes harmonizing Latin, Greek and Cyrillic in Adobe Aldine and making optical adjustments; his cited native review concerned Cyrillic. This supports expert cross-script review, not a claim that Greek was reviewed by a particular person.
- [P09, “Kerning”] Glyphs notes both negative adjustments for excessive gaps and positive adjustments for collisions. Mathematical formula spacing may be controlled by the math layout engine, so ordinary prose kerning is not a substitute for testing shaped formulas.

## Proposed criteria and review protocol (project proposals, not source mandates)

1. **Shape and voice:** compare a named historical specimen at matched apparent size, plus enlarged outlines; look for stroke stress, contrast, serifs, terminals, counters and individual character identities. Explain intentional departures for math and screen use. Treat specimen ink spread and reproduction as uncertainties. No universal Baskerville width, angle, handle or x-height ratio is imposed [P03, P04, P06].
2. **Rhythm and colour:** inspect alternating straight/round sequences, real words and paragraphs, then expressions with varied symbols. Identify visible holes, clumps, collisions and uneven density; adjust sidebearings before isolated pair kerning [P02, P09]. A proposed pass requires no unexplained recurring defect in the agreed proof set; this is a project threshold, not a published typographic standard.
3. **Curves and details:** inspect enlarged joins for bumps and unintended inflections, and at use size for counters closing, weak hairlines or distracting terminals. Record a crop and a plausible remedy for each finding; avoid numerical curve rules [P03, P04].
4. **Size robustness:** use actual rendering and intended output at text, superscript and subscript sizes, alongside enlarged inspection. Compare explicit sizes and devices; do not assume a single scaled outline or a legacy print DPI proves success [P01, P05]. Script sizing and MATH table behavior require separate technical research.
5. **Italic and Greek:** review italic as a designed companion, including slope, joins and overhangs in mixed formula contexts; compare Greek glyphs individually and in meaningful Greek as well as mathematical contexts. Request expert Greek and mathematical review, distinguish text Greek from mathematical variants, and do not infer form from Latin similarity [P07, P08].
6. **Evidence and adjudication:** prepare fixed, reproducible proof strings and render settings before review, anonymize candidates for paired comparison, and require reviewers to cite a glyph, context, size and crop. Record disagreement and confidence; include independent technical checks as hard gates. Proposal: a candidate cannot advance with an unresolved collision or missing required glyph, and any qualitative score must include a concrete observation. No scores or thresholds are calibrated yet.

## Implementation plan for a later authorized phase

1. Agree intended mathematical repertoire, target sizes, rendering environments and accessibility needs; identify original Baskerville specimens and provenance before choosing a historical reference.
2. Assemble a versioned proof corpus: running text, spacing strings and difficult pairs; italic/roman boundaries; Greek text and math variants; fractions, limits, scripts, radicals and delimiters. Establish expected shaping through separately researched math standards.
3. Specify reproducible specimen generation, metadata, image scale and comparison protocol; collect visual and technical baselines before defining numerical gates.
4. Draft anchored criteria with domain specialists, pilot blinded reviews, record inter-reviewer disagreements and calibrate against real examples. Use measurements diagnostically, not as proxies for aesthetic success.
5. Only after authorization, build the hillclimb with traceable candidate changes, immutable inputs and reports, independent hard checks, and human adjudication. No council has been run here.

## Limits and further reading

These sources provide practitioner guidance, not controlled evidence that a proposed threshold improves mathematical reading. Historical scans, dedicated math layout sources, accessible original Baskerville specimens and formal Greek mathematical convention need a separate research round. Fred Smeijers, *Counterpunch* (1996); Walter Tracy, *Letters of Credit* (1986); and Karen Cheng, *Designing Type* (2005) are canonical print references worth consulting in legitimate copies; their contents and editions were not independently checked here and no copies are included.
