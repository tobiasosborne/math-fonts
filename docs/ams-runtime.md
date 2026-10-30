# Exact Storm source reuse in the AMS runtime

`tex/baskervillecompanionams.sty` extends the unchanged pilot loader. It reuses
the original external Storm fonts at runtime: no commercial outlines enter the
authored OTF or public payload. It loads neither `amssymb` nor `amsfonts` and
supplies no unrelated-font fallback. LuaLaTeX and XeLaTeX are supported.

```tex
\usepackage[
  mathfont={/absolute/path/BaskervilleCompanionMath-Pilot.otf},
  textfontdir={/absolute/path/to/Baskerville 10 Pro}
]{baskervillecompanionmath}
\usepackage{baskervillecompanionams}
```

The implementation declares **60 stock symbol commands**, including aliases,
plus literal mathematical signs and punctuation. Examples include `\leq`,
`\geq`, `\neq`/`\ne`, `\approx`, `\infty`, `\partial`, `\pm`, `\times`,
`\div`, ten directional arrows, braces, bars and brackets. Each command selects
the exact source cmap scalar through an external TU symbol family and preserves
its TeX math class. Alias commands can have distinct classes: `\centerdot` is
binary, `\cdotp` punctuation, and `\relbar` a relation. ASCII math minus uses
U+2212, never a hyphen glyph. Ordinary Latin, numerals and styled alphabets
retain the pilot's external four-face Storm routing.

Only **3 of the frozen 204 direct `amssymb` symbols** have exact source shapes
in the supplied stock font and are implemented here: `\centerdot` (U+00B7),
`\eth` (U+00F0), and `\lozenge` (U+25CA). `\Diamond`, `\yen` and `\circledR`
are additional explicitly declared AMS compatibility names. This is a concrete
runtime expansion, not full AMS coverage. For example, `\forall`, `\subset`,
`\aleph`, `\nabla` and `\boxplus` remain missing; they are not substituted by
similar characters. `\cdot` is also not mapped to U+2219 merely because a dot
is available. The frozen inventory's `\|` → single bar binding is excluded:
a single bar must not masquerade as a double-bar norm delimiter.

The six authored Greek letters remain the default. The authored sums,
integrals, radicals, hats and growing parentheses also remain in the unchanged
pilot font. Text-size literal parentheses use Storm; their delimiter codes
still select the existing authored growth. Braces, brackets, bars and arrows
are rigid stock glyphs with no size assembly. `\prod` has one stock size.
The proof exercises `align`, limits, a matrix, cases, integrals and nested
fractions, but a compiled `cases` environment does not establish adequate brace
growth: the working proof visibly has a brace that is too short for two rows.
Growth, axis alignment and spacing remain engineering and optical work.

## Authored AMS overlays and arrows

A later authored AMS build uses explicit source priority:

```tex
\usepackage[authored-overlay]{baskervillecompanionams}
```

In this mode, a scalar actually present in the authored companion wins over a
stock declaration or literal mapping. This includes intentionally retained
authored plus, minus and equals as well as new arrows. If the companion omits a
stock-supported scalar, the exact external Storm source remains active. The
original pilot without this option retains its deliberately chosen stock reuse.
The proof runner selects this option automatically for a companion whose
PostScript name differs from `BaskervilleCompanionMath-Pilot`.

One explicit allowlist declares 77 arrow names addressing 71 exact scalars.
It follows the frozen inventory's command bindings and math classes, adding
the exact from-bar names from the frozen `unicode-math-table.tex`. It includes
single/double/long arrows, harpoons, mapsto variants, pairs, hooks and multihead
variants. A name in the allowlist is not a coverage claim. Every absent form
still addresses its missing exact scalar; no legacy arrow construction or
similar head/bar shape supplies it. In particular, a family containing ordinary
single arrows does not thereby acquire twohead arrows or hooked arrows.

The first shared-component authored manifest is
`runs/ams-coverage-2026-10-30/arrows-v1/sources.json`. Its bounded 34 scalars are
U+2190–2199, U+21A4–21A7, U+21BC–21C3, U+21D0–21D5 and U+27F5–27FA.
They remain provisional component geometry. Additional pairs, twoheads and
hooks need their own correct source geometry and proof before coverage credit.

The runner derives the active source of each command and each Unicode literal
from the actual selected font cmap. It demands that every installed authored
arrow render from the exact authored PostScript name in both engines, including
arrows that Storm also contains. Named aliases and raw literals are isolated
separately. A realistic arrow page exercises chains, implication/equivalence,
mapping, diagonals, long arrows and nested scripts; paired harpoons appear only
when their exact scalar is installed. Enlarged arrow diagnostics use a separate
page. The unfinished cases brace is not on either arrow page.

The integration suite also uses a temporary renamed copy of our own authored
pilot to prove source priority on its real plus/minus/equals, while its omitted
arrows still use the pinned original Storm glyphs. This is a loader fixture,
not a new drawing or a release font. All four integration/contract tests pass
on both engines. To test a newly built real arrow font, set `AMS_RUNTIME_FONT`
to its OTF path with `RUN_AMS_RUNTIME_INTEGRATION=1`.

## Optional native Greek alternates

These explicit, local interfaces retain native Storm Greek as alternates:

```tex
$\alpha\beta\theta\nu\xi\omega$ % authored custom default
$\mathstormgreek{\alpha\beta\theta\nu\xi\omega}$ % Storm italic
$\mathstormgreekup{\alpha\beta\theta\nu\xi\omega}$ % Storm regular
$\mathstormgreek{αβθνξω}$ % literal native characters also supported
$\alpha$ % custom again; no change leaks from the alternate scope
```

There are 49 exact named Greek bindings, tested separately in both faces.
`\varepsilon` selects ε (U+03B5) and `\varphi` selects φ (U+03C6).
The stock font does not supply the distinct shapes required by `\epsilon`
(ϵ), `\phi` (ϕ), `\vartheta`, `\varkappa`, `\varrho` or `\varpi`.
These commands fail explicitly inside the native alternate rather than changing
their identities. `\varTheta`, `\digamma` and `\backepsilon` are also unavailable.
Native alternates close no gaps in the required custom Greek design.

## Reproduction and evidence

The later authored-arrow delivery is documented in
[`runs/ams-coverage-2026-10-30/README.md`](../runs/ams-coverage-2026-10-30/README.md).
Use `\usepackage[authored-overlay]{baskervillecompanionams}` with that AMS font.
It prefers an explicitly present authored glyph before stock reuse, so new arrow
geometry cannot be hidden by an existing Storm arrow. An explicit 77-name,
71-scalar arrow allowlist maps installed forms and hard-errors on missing ones;
it does not credit missing variants as covered. Vertical arrows preserve real
delimiter syntax. The full one-command build/proof/viewer is `tools/run_math_ams.py`.

The historical source-reuse-only evidence below used the original pilot and
therefore retains its three direct stock AMS symbols. The later arrow delivery
adds four exact directional harpoons, for seven direct AMS symbols. Other new
arrows are largely core LaTeX/Unicode forms; this remains partial AMS coverage.

```sh
.venv/bin/python tools/proof_ams_runtime.py \
  --text-font-dir '/external/Baskerville 10 Pro' \
  --output runs/ams-coverage-2026-10-30/runtime-new
RUN_AMS_RUNTIME_INTEGRATION=1 .venv/bin/python -m unittest discover \
  -s tests -p test_ams_runtime.py
```

The runner requires a fresh output directory and hash-pins all four supplied
Storm faces. Its default is the unchanged delivered pilot OTF; `--font` can
select a later authored BaskervilleCompanionMath MATH build. The runner reads
its exact PostScript name from the font, checks that name in the actual PDFs,
and checks every mapped source scalar against the actual original cmap before
compiling. The separate legacy baseline always uses the immutable original
pilot. Negative tests select genuinely uncovered symbols from the tested font's
cmap, so adding custom gamma does not turn a correct expansion into a false
test failure.

The retained successful result is
`runs/ams-coverage-2026-10-30/runtime-04/runtime-summary.json`:

- Both engines pass 186 isolated pages, including every stock command, every
  named native Greek binding in italic and regular, literal Greek, alternate
  scope and scripts, and all 20 original role formulas under the expanded loader.
- A separate rerun of the original, unchanged pilot proof also passes its 20
  original roles on each engine.
- MuPDF checks the actual rendered font on every isolated page and the exact
  output character for individual commands. `pdffonts` independently permits
  only the four original Storm PostScript names and the authored companion.
- XeTeX sometimes chooses a different PDF ToUnicode scalar for two source cmap
  entries that address the identical original glyph, notably U+00B7/U+2219.
  Such aliases are accepted only when the hash-pinned original font maps both
  scalars to the same glyph name. The evidence records the requested scalar,
  original glyph name, permitted same-glyph scalars and actual PDF text.
- Missing custom gamma, AMS boxplus and core forall fail with hard missing-glyph
  errors. Six missing native Greek shape variants fail with explicit package
  errors. No fallback supplies any of them.

The public summary annotates original stock reuse versus unchanged authored
work, and lists every unimplemented frozen command binding with a source reason.
Its command accounting excludes literal letters/numerals and existing named
operator recipes. All PDFs, raster proofs, logs and embedded-font diagnostics
are inside ignored `private/` directories. The public summaries for development
attempts remain truthful: runtime-01 records an overly strict ToUnicode check
failure; runtime-02 passed before escaped right-brace and native-error coverage
were added; runtime-03 passed before dynamic companion PostScript names were
accepted and upright-alternate source annotations were clarified. No immutable
pilot output was changed.

Technical success verifies sourcing and layout execution. It does not constitute
optical acceptance, complete AMS support, completed custom Greek, script optical
drawings, or arbitrary-size math constructions.
