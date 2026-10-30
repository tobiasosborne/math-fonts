# AMS expansion: shared geometry and exact source reuse

The retained pilot is extended by a **34-arrow vector family** with one shared
curved open head, shaft weight and component grammar. New arrows require no
individual image generations. The six preferred custom Greek letters remain
the default; native Storm Greek is available through explicit upright/italic
alternate scopes. Original Storm Latin and numerals remain external dependencies.

## Current delivery

`delivery-arrows-03/font/BaskervilleCompanionMath-AMS.otf` contains 67 authored
glyphs, including inherited pilot growth forms. It contains no ordinary Storm
letter or numeral outlines. The font SHA-256 is
`9cae9c369f2e20c50138a4e34f4089dde1fd1960b3bf9ae70e9d659554393878`.

`delivery-arrows-03/runtime/runtime-summary.json` records actual isolated-font
and semantic checks on LuaLaTeX and XeLaTeX. Its checks include named arrows,
Unicode literals, native Greek alternates, source priority, three script sizes,
and vertical arrows in real `\left`/`\right` delimiter syntax. An independent
20-role regression per engine still uses the immutable original pilot. Hard
negative probes reject missing custom Greek, missing shapes and native variants.

Open `delivery-arrows-03/runtime/private/viewer.html` locally for actual
Baskerville mathematical pages, enlarged diagnostics, a common-scale compiled
CFF arrow grid, zoom, negative space and removable baseline/math-axis guides.
Commercial embedded-font PDFs and rasters remain ignored/private. The compiled
arrow SVGs and authored OTF are public.

```sh
.venv/bin/python tools/run_math_ams.py \
  --output /tmp/baskerville-ams-rebuild \
  --base-sources runs/pipeline-2026-10-30/font-sources.json \
  --sources runs/ams-coverage-2026-10-30/arrows-v1/sources.json \
  --text-font-dir '/external/Baskerville 10 Pro' --dpi 200
```

The output directory must be fresh. Further explicitly calibrated source
manifests can be added with repeated `--sources`; duplicate roles are rejected.
This command performs no model calls and does not silently fill missing shapes.
Build, proof and viewer code are in `tools/run_math_ams.py`,
`tools/build_math_ams.py`, `tools/proof_ams_runtime.py` and
`tools/view_math_ams.py`.

## Design sources and limits

- `arrows-v1/` and `design/arrow-grammar.json`: 34 exact geometric derivatives
  of one family prototype; 40-unit shafts match the pilot fraction-rule weight.
  Double-shaft joins follow the actual cubic head boundary. Harpoons use exact
  half-heads. Source frames are explicitly **derived design units**, not falsely
  claimed pixel fits. See `docs/math-arrow-grammar.md`.
- `master-v2/candidate-01/`: one versioned descendant of the accepted unified
  root, with 64 untouched crops and exact semantic review. Three wrong Greek
  variants and three wrong arrow cells are quarantined. Six v1 Greek sources
  remain retained. Proposed shared scale/baselines are explicitly uncertain;
  the anchor dimension residual is 5.500 source pixels. See `docs/ams-atlas-v2.md`.
- `source-audit.json`: frozen target-by-target source availability and reuse
  audit, **not rendered coverage**. Of 204 direct `amssymb` symbols, only three
  have exact stock-source drawings. Four new directional harpoons raise the
  explicitly implemented direct-symbol count to seven; most new arrows belong
  to core LaTeX/Unicode coverage. Do not mistake 34 arrows or hundreds of test
  formulas for complete AMS support.

Hooks, successive two-heads, paired/negated arrows and arbitrary extensible
assemblies remain missing. Script optical compensation, bold drawings, complete
custom Greek and expressive alphabets remain unfinished. Rigid native braces
are visibly too short in the separate cases proof. Working-size proof success
establishes execution/source selection, not final optical acceptance.

## Retained development evidence

One expanded-root image call has been used; no arrow enlargement or correction
call was spent. Dispatch and result hashes are saved before/after that call.
`contract.json` and `state.json` bound the new run; the expired overnight timer
remains disabled.

`runtime-01` through `runtime-04` retain early exact-source runtime work.
`delivery-arrows-01` records a failed proof-generator command boundary;
`delivery-arrows-02` passes 290 checks per engine. The final `-03` adds actual
vertical delimiter parsing checks; its font bytes are unchanged. The exploratory
double-shaft draft is explicitly historical inside `arrows-v1/preclip-draft/`.
