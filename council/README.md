# Council smoke harness

The first fixture lives in `runs/smoke-2026-10-29/`. It compares a byte-identical
copy of the archived v0.150 OTF with one deliberately narrow experiment:
wider `+`, `−` and `=` outlines and advances, preserving stroke weight and
vertical placement. The parameter is a trial hypothesis, not a typographic
standard. No archived builder is imported or run; all other outlines and
advances are checked unchanged. This fixture does not adopt the old font as
the fresh project's baseline.

## Bounded execution

The run contract allows one candidate edit, one paired assessment, and one
actual judge evaluation per requested member: Opus, GPT-6.1 Sol, and Muse
Wonder Full. The shorthand `opus` was rejected by T3 before a task launched;
capability lookup resolved that requested family to advertised `claude-opus-5-5`.
This creates four dispatch requests but at most three actual judge evaluations,
with no repeated assessment. The correction is recorded in `contract.json`.
No automatic judgment retry, debate, repair round or continuation is allowed.
Every below-feature verdict must include concrete constructive
feedback in that same ballot. Stop after this round regardless of quality.

The 1,800-word response target is a prompt instruction, not a provider-enforced
token cap. Record actual usage only if T3 exposes it. The finite number of
one-shot calls is the enforced orchestration bound for this smoke run.

Each delegate sees six image files and the same pinned rubric, prompt and
source registry. Neutral labels and withheld rationale provide protocol
blinding; a shared checkout is not a security boundary. Judges are told not
to access the private key or other ballots. Do not claim enforced isolation.

## Files and commands

```sh
uv venv .venv
uv pip install --python .venv/bin/python -r council/requirements-smoke.txt
.venv/bin/python tools/prepare_smoke.py
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python tools/council_smoke.py aggregate
```

Preparation refuses to overwrite an existing run. The current run is already
prepared: do not rerun preparation to inspect results. Its proof source, raw
build logs, input fonts, identity key, notices and PDFs are in `private/`.
That directory is gitignored because it contains supplied/derived fonts and
font-embedded PDFs; preserve a filesystem copy if moving this experiment.

Judge execution uses T3 Code delegates, not a CLI subprocess or hidden model
call in these scripts. The delegate task carries the packet paths, output path,
schema and one-shot contract. Saving an evaluation JSON does not invoke a model.
Only dispatch the authorized members for a new round on an explicit instruction.

`packet/` holds PNG proofs, an identical-image pair, pinned instructions and
manifest. `ballots/<member>.json` contains raw structured judgments.
`result.json` records completeness, model scores, regressions and iteration
eligibility; `report.md` presents the constructive critiques. No promotion is
executed by aggregation. Missing/invalid members make the round incomplete.

The five offline tests exercise missing evidence, criterion coverage, required
constructive feedback, scores, source IDs, controls and regressions concealed
by an increasing mean. These tests do not establish that model judgments are
correct. The live smoke run tests image access and usable criticism; two pages
in one engine are not full repertoire, cross-engine or print certification.
