# Frozen mathematical coverage sources

The [2026-10-29 snapshot](2026-10-29/source-index.json) retains the actual
primary-source bytes used by the planning inventory: LaTeX core declarations,
AMS font/symbol/math/operator definitions, unicode-math mappings/compatibility,
Unicode 17 character properties and standardized variants. Individual files
retain their upstream headers and notices. Retrieval URLs, byte counts and
SHA-256 values are recorded in the index.

Reproduce the planning inventory without fetching moving upstream URLs:

```sh
.venv/bin/python tools/build_ams_inventory.py \
  --sources-dir research/coverage/2026-10-29 \
  --output /tmp/baskerville-ams-inventory-reproduction.json
```

Compare with [the adopted inventory](../../design/ams-glyph-inventory.json).
This is exact scope evidence, not a license to reuse existing font outlines
and not proof of completed font coverage. The new outlines still derive from
the one approved unified design image.
