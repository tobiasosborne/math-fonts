# Executable AMS source audit

This is a source-availability audit, not design acceptance or a claim of full
rendered AMS coverage. It checks the frozen inventory and actual hash-pinned
external Storm faces, plus the immutable authored pilot OTF. No outlines are
read/copied, no commercial binary is published and no image call is made.

Run from the repository root:

```sh
.venv/bin/python tools/audit_ams_sources.py --probe-macros
.venv/bin/python -m unittest discover -s tests -p test_ams_sources.py
```

The full per-target and per-binding data are in [source-audit.json](source-audit.json).
All nine frozen primary-source URLs and hashes are preserved there and checked
against the local snapshots before the report is written. The native four-face
fonts must be supplied at the paths in `design/storm-reference.json`; hashes
must match. The audit reads Unicode cmap, metrics/table metadata and glyph
names, never glyph outlines.

## Counts and their meaning

| Request/evidence | Count | Interpretation |
|---|---:|---|
| Frozen distinct encoded targets | 1,196 | Package inventory, not new outline count |
| Frozen sequences | 12 | Must prove exact variant/composite shape and binding |
| Unencoded engineering requests | 717 | Size, assembly, display, bold and legacy work |
| Total targets | 1,925 | Exact target set, no alias double counting |
| Source binding rows / distinct spellings | 585 / 577 | Different packages sometimes bind the same spelling |
| Direct AMS symbol declarations | 204 | Exact frozen `amssymb` direct set |
| Ordinary serif ASCII style targets | 228 | Latin in four faces, upright/bold numerals; exact UCD decomposition |
| Additional exact native letter/math-letter slots | 4 | eth, dotless-i, italic dotless-i, ell; require explicit mapping |
| Exact rigid symbol candidates beyond pilot | 48 | Availability only; no suitability/proof claim |
| Actual inventory slots in pilot cmap | 21 | Six Greek drawings × two aliases plus nine symbol drawings |
| Current rendered baseline | 20 roles × 2 engines | Existing narrow pilot checks, not inventory-wide proof |
| New design acceptances / rendered targets from this audit | 0 / 0 | Availability is kept separate |

The Storm cmaps contain 684 regular, 610 italic, 601 bold and 601 bold-italic
entries. None supplies a MATH table. Compatibility decomposition is allowed
only for the requested math alphabet style (and the explicit italic dotless
slots). In particular, `hslash` is **not** counted from U+0127 text h-bar, and
script/fraktur/double-struck/sans/monospace requests are not satisfied by serif
ASCII letters. No approximate failed command is credited.

Only three of the 204 direct AMS declarations have exact reusable Storm slots:
`\centerdot` U+00B7, `\eth` U+00F0 and `\lozenge` U+25CA. This is source
availability, independent of whether their compatibility macro is defined.

## Greek policy and alternates

The custom pipeline Greek remains the default. All 61 native Greek slots in
each Storm face are recorded, with face name and hash, as explicit **opt-in
alternates** in `native_greek_alternates`. They receive no coverage credit for
missing custom Greek. The six retained pilot drawings are alpha, beta, theta,
nu, xi and omega. Their 12 cmap aliases are six designs, not 12 independent
design acceptances. Plain Greek aliases do not prove a separate upright design.
The older 32 heavy studies remain evidence and are not silently adopted.

There are 223 further custom Greek targets across the frozen style inventory,
including uppercase, lowercase and variants. The remaining ordinary lowercase
italic queue contains these 19 exact targets:

- `u1D6FE` 𝛾 — MATHEMATICAL ITALIC SMALL GAMMA
- `u1D6FF` 𝛿 — MATHEMATICAL ITALIC SMALL DELTA
- `u1D700` 𝜀 — MATHEMATICAL ITALIC SMALL EPSILON
- `u1D701` 𝜁 — MATHEMATICAL ITALIC SMALL ZETA
- `u1D702` 𝜂 — MATHEMATICAL ITALIC SMALL ETA
- `u1D704` 𝜄 — MATHEMATICAL ITALIC SMALL IOTA
- `u1D705` 𝜅 — MATHEMATICAL ITALIC SMALL KAPPA
- `u1D706` 𝜆 — MATHEMATICAL ITALIC SMALL LAMDA
- `u1D707` 𝜇 — MATHEMATICAL ITALIC SMALL MU
- `u1D70A` 𝜊 — MATHEMATICAL ITALIC SMALL OMICRON
- `u1D70B` 𝜋 — MATHEMATICAL ITALIC SMALL PI
- `u1D70C` 𝜌 — MATHEMATICAL ITALIC SMALL RHO
- `u1D70D` 𝜍 — MATHEMATICAL ITALIC SMALL FINAL SIGMA
- `u1D70E` 𝜎 — MATHEMATICAL ITALIC SMALL SIGMA
- `u1D70F` 𝜏 — MATHEMATICAL ITALIC SMALL TAU
- `u1D710` 𝜐 — MATHEMATICAL ITALIC SMALL UPSILON
- `u1D711` 𝜑 — MATHEMATICAL ITALIC SMALL PHI
- `u1D712` 𝜒 — MATHEMATICAL ITALIC SMALL CHI
- `u1D713` 𝜓 — MATHEMATICAL ITALIC SMALL PSI

A finite next design batch can take the first six of this queue (gamma, delta,
epsilon, zeta, eta, iota), with an explicit decision about epsilon variants.
The full custom Greek requirement includes variant-symbol targets outside this
ordinary-small-letter queue. This recommendation authorizes no image call.

## Missing and engineering requirements

The JSON includes exact ID lists in `missing_base_classes` and
`unencoded_requirements_by_class`, as well as every original engineering
construction and operator recipe. Counts are:

| Availability class | Targets |
|---|---:|
| `assembly_engineering_required` | 101 |
| `bold_dotless_mapping_required` | 4 |
| `bold_engineering_required` | 426 |
| `construction_piece_required` | 11 |
| `custom_pilot_greek` | 12 |
| `custom_pilot_symbol` | 9 |
| `display_engineering_required` | 17 |
| `external_rigid_symbol_candidate` | 48 |
| `external_storm_alphabet` | 232 |
| `geometric_construction_candidate` | 275 |
| `missing_custom_greek` | 223 |
| `missing_expressive_alphabet` | 342 |
| `missing_expressive_outline` | 55 |
| `missing_legacy_shape_or_recipe` | 13 |
| `package_recipe_required` | 1 |
| `sequence_binding_required` | 12 |
| `size_engineering_required` | 144 |

The 275 geometric candidates are a design/recipe queue, not completed geometry.
The report proposes a maximum 12-target first batch and lists all IDs so its
scope is reviewable. Rigid stock candidates should be mapped and measured
before drawing replacements. Existing pilot MATH growth tables are recorded
on relevant targets, but no unencoded size/display/assembly requirement is
credited merely because a base or provisional variant exists. All 38 named
operator recipes remain recipes, separate from encoded scalar counts.

## Private macro probe

LuaLaTeX loads the actual hybrid package and checks each of the 204 direct AMS
commands with `ifcsname` and a non-relax test. It does not expand or typeset any
of those commands. The report pins the tested loader SHA-256 and installed
`unicode-math` package version. Its TeX source, log and console output are under
the ignored `private/source-audit/` directory.

The measured baseline has **170 defined and 34 undefined** direct names.
Defined does not imply successful expansion, correct shape, correct source font
or rendered coverage. Undefined names are:

`\blacklozenge`, `\blacksquare`, `\centerdot`, `\circlearrowleft`, `\circlearrowright`, `\circledS`, `\doteqdot`, `\gvertneqq`, `\lozenge`, `\lvertneqq`, `\ngeqq`, `\ngeqslant`, `\nleqq`, `\nleqslant`, `\npreceq`, `\nshortmid`, `\nshortparallel`, `\nsubseteqq`, `\nsucceq`, `\nsupseteqq`, `\ntriangleleft`, `\ntriangleright`, `\shortmid`, `\shortparallel`, `\smallfrown`, `\smallsmile`, `\square`, `\thickapprox`, `\thicksim`, `\varpropto`, `\varsubsetneq`, `\varsubsetneqq`, `\varsupsetneq`, `\varsupsetneqq`.

The runtime implementation work may change macro availability. This report
identifies its tested loader hash; regenerate explicitly to audit a later
loader. Source availability counts remain independent of those macro changes.

Six regression tests verify the exact target/binding partition, style identity,
custom Greek priority and alternate policy, absence of implicit sequence or
engineering credit, all 204 macro probe records, and source-hash rejection.
