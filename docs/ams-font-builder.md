# Explicit AMS font exporter

`tools/build_math_ams.py` builds a new authored CFF/MATH font without changing
the completed pilot, loading donor fonts, inventing missing glyphs, or claiming
design acceptance. It supports arbitrary explicitly sourced roles, including all
32 lowercase Greek/variant targets and both native/italic Unicode mappings.
The exporter does not draw new designs or infer semantic aliases.

For new Greek work, use an explicit `--calibration` profile measured against
the text grid. The [Greek grid method](greek-text-grid.md) separates that optical
correction from source registration. The lower-level exporter still permits an
uncalibrated build for historical reproduction; the end-to-end AMS runner now
requires calibration or its explicit historical-reproduction flag.

```sh
.venv/bin/python tools/build_math_ams.py \
  --base-sources runs/pipeline-2026-10-30/font-sources.json \
  --sources runs/ams-coverage-2026-10-30/font-sources.json \
  --output runs/ams-coverage-2026-10-30/build-01
```

The output directory must be fresh. The three output artifacts are
`BaskervilleCompanionMath-AMS.otf`, `build-manifest.json`, and normalized
`sources.json`. The Python entry point is
`build(output, sources=None, base_sources=None)`.
The manifest records the original input manifest paths and hashes. Reproduce
using those same inputs. `sources.json` is an audit snapshot, not a replacement
for the original `--base-sources` adoption: supplying every snapshot record as
a new override intentionally disables the pilot-specific growth recipes.

## Source contract

`--base-sources` explicitly adopts the frozen 15-role pilot palette, overriding
its six Greek traces with the registrations in that manifest. Its root hash and
200-pixel em are known pilot facts, recorded per glyph. Without this option,
there are no defaults: only explicitly supplied new roles are included.

`--sources` accepts a `sources` mapping keyed by role name. A `roles` mapping or
list is also accepted; list entries require unique `name` fields. A new record
replaces the entire old role record, so missing calibration cannot silently
inherit from the previous root. Every new/overridden role requires these fields:

```json
{
  "sources": {
    "gamma": {
      "codepoints": ["U+03B3", "U+1D6FE"],
      "kind": "greek",
      "curves": "glyphs/gamma/trace/curves.json",
      "source_crop_box": [100, 50, 180, 200],
      "baseline_root": 180,
      "source_em_pixels": 200,
      "registration_to_root": {
        "scale": 0.125,
        "translate_x": 105,
        "translate_y": 55
      },
      "root_sha256": "<actual 64-character lowercase SHA-256>",
      "root_image": "unified-root.png",
      "provenance": {
        "root_version": "<explicit unified-root version>",
        "registration_measurements": "<actual measurement report path>",
        "semantic_review": "<actual review status>"
      }
    }
  }
}
```

These numbers illustrate the schema and are not production calibration. The
caller must supply measured values and a real digest. Paths resolve against the
manifest directory. `root_image` is optional: when present its bytes must match
`root_sha256`; otherwise the manifest marks the root image as unverified.
Optional `curves_sha256` is checked against the actual trace bytes. Every record
retains its full explicit provenance object and all additional metadata.

`kind` is one of `greek`, `symbol`, `operator`, `delimiter`, `accent`, or
`special-alphabet`. Codepoints are scalar integers or `U+XXXX` strings. Ordinary
ASCII Latin letters/numerals, control/space/surrogate values, duplicate mappings,
conflicting role mappings, absent fields, malformed traces, nonfinite values,
nonpositive em/scales, and anisotropic registration are rejected. Greek roles
must map explicitly into the native or mathematical Greek Unicode ranges.
The codepoint assertion is the author's responsibility; geometry alone cannot
establish that a curve is the correct gamma, epsilon variant, or other symbol.

Native and mathematical italic aliases must both appear explicitly. There is
no name-to-codepoint lookup or automatic Greek mapping. Digamma has no plain
mathematical italic Unicode scalar: do not invent one or map it to bold digamma.
For epsilon/phi/kappa and other variant semantics, follow the frozen inventory's
semantic gates in `docs/ams-glyph-inventory.md`.

## Geometry and engineering

Each Potrace segment retains its original controls and every contour. For a
trace point `(x,y)`, uniform registration gives
`root = trace * scale + translate`. Font conversion is
`font_x = (root_x - crop_left) * 1000/source_em_pixels` and
`font_y = (baseline_root - root_y) * 1000/source_em_pixels`.
The per-role em therefore calibrates roots with different image scales; a v2
root must not silently borrow the pilot's 200-pixel em. Only horizontal
translation supplies ordinary sidebearings. No independent width/height fitting,
pinholes removal, outline substitution, or component dropping occurs.

The builder imports pure helpers and the authored MATH constants from
`build_math_pilot.py`; it does not modify its globals or its implementation.
Unchanged adopted pilot roles retain their finite growth forms, hat placement,
and measured roof-preserving radical recipe. Overridden roles do not inherit
those recipes. New growth/assembly/placement engineering remains a separate
explicit task. All Greek roles receive provisional italic corrections; outlined
glyphs receive provisional center attachments. GPOS and GSUB expose a `math`
script for both engines without fabricated optical substitutions.

The manifest records exact source/outline hashes, codepoints, calibrated em,
registration, root identity/verification, provenance, contour counts, bounds,
advances, derived recipes, and limitations. Fixed timestamps and sorted role
order make repeated builds from the same source inputs byte-identical. Source
paths and provenance are audit metadata, not bundled commercial font payloads.

This is an extension mechanism, not full AMS delivery. Current finite variants,
MATH metrics and script behavior remain provisional; no assemblies, `ssty`, or
math kerns are fabricated. Source availability does not establish semantic or
optical acceptance. Ordinary Storm text still comes from explicit external
configuration; no Storm letter or numeral outline enters the authored font.

## Verification

```sh
.venv/bin/python -m unittest discover -s tests -p test_math_ams.py -v
```

The tests use a conspicuously non-letter two-contour cubic fixture, labelled
test-only, to check new-role mappings, all-32-role serialization, per-source em,
uniform registration, contour retention, hashes/provenance, malformed-source
rejection, stock exclusions, MATH references, the math script, unchanged pilot
adoption, overridden growth-role isolation, reproducible binaries, and immutable
outputs. These fixtures are not font designs or coverage evidence. Run the
existing pilot tests as regression checks; production acceptance additionally
requires the real traced sources and enlarged/working-size engine proofs.
