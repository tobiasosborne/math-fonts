#!/usr/bin/env python3
"""Freeze/validate compact paired ballots. Model calls are T3-orchestrated."""
import argparse
import hashlib
import json
import statistics
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
MEMBERS = ("opus", "sol", "muse")
CRITERIA = [f"R{i}" for i in range(1, 9)]
VERDICTS = ["unresolved", "functional", "polished", "distinguished_but_not_feature_ready", "feature_ready"]


def obj(fields):
    return {"type": "object", "properties": fields, "required": list(fields),
            "additionalProperties": False}


def schema():
    text = {"type": "string", "minLength": 1}
    score = {"type": ["integer", "null"], "minimum": 1, "maximum": 5}
    criterion = obj({"id": {"enum": CRITERIA}, "ideal": text,
                     "score_a": score, "score_b": score,
                     "observation_a": text, "observation_b": text,
                     "anchor_reason": text, "remaining_gap": text, "next_move": text,
                     "source_ids": {"type": "array", "minItems": 1,
                                    "uniqueItems": True, "items": text}})
    blocker = obj({k: text for k in ["problem", "evidence", "change", "why", "verify", "preserve"]})
    return obj({"member": {"enum": list(MEMBERS)},
                "seen_images": {"type": "array", "uniqueItems": True, "items": text},
                "control": obj({"preference": {"enum": ["X", "Y", "tie", "not_assessable"]},
                                "evidence": text}),
                "criteria": {"type": "array", "minItems": 8, "maxItems": 8, "items": criterion},
                "observed_change": text,
                "preference": {"enum": ["A", "B", "tie", "not_assessable"]},
                "verdict_a": {"enum": VERDICTS}, "verdict_b": {"enum": VERDICTS},
                "better_vs_featureworthy": text,
                "publication_blockers": {"type": "array", "maxItems": 3, "items": blocker},
                "next_experiment": text})


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def freeze(run):
    packet = run / "packet"
    manifest = json.loads((packet / "manifest.json").read_text())
    if (packet / "council-lock.json").exists():
        raise ValueError("Refusing to change an already frozen council packet")
    for item in manifest["images"]:
        assert sha(packet / item["path"]) == item["sha256"], item
    inputs = {"rubric.md": ROOT / "docs/rubric.md",
              "judge-prompt.md": ROOT / "council/judge-prompt.md",
              "sources.json": ROOT / "research/typography/sources.json"}
    # Optional campaign-specific scope is pinned just like the common rubric.
    if (run.parent / "evaluation-focus.md").exists():
        inputs["evaluation-focus.md"] = run.parent / "evaluation-focus.md"
    for name, source in inputs.items():
        (packet / name).write_bytes(source.read_bytes())
    (packet / "schema.json").write_text(json.dumps(schema(), indent=2) + "\n")
    lock = {"rubric_version": "0.3", "documents": {name: sha(packet / name)
             for name in [*inputs, "schema.json", "manifest.json"]}}
    (packet / "council-lock.json").write_text(json.dumps(lock, indent=2) + "\n")
    (run / "ballots").mkdir(exist_ok=True)
    return lock


def validate(ballot, member, image_ids, source_ids):
    jsonschema.Draft202012Validator(schema()).validate(ballot)
    if ballot["member"] != member:
        raise ValueError("Member identity mismatch")
    if set(ballot["seen_images"]) != set(image_ids):
        raise ValueError("Every packet image must be seen")
    if ballot["control"]["preference"] != "tie":
        raise ValueError("Identical-image control failed or was not assessed")
    if {c["id"] for c in ballot["criteria"]} != set(CRITERIA):
        raise ValueError("Each criterion must appear once")
    for c in ballot["criteria"]:
        if c["score_a"] is None or c["score_b"] is None:
            raise ValueError("Incomplete assessment")
        if not set(c["source_ids"]) <= source_ids:
            raise ValueError("Unknown source reference")
    if ballot["verdict_a"] != "feature_ready" or ballot["verdict_b"] != "feature_ready":
        if not ballot["publication_blockers"]:
            raise ValueError("Below-feature judgment requires constructive feedback")
    for side in "ab":
        if ballot[f"verdict_{side}"] == "feature_ready" and any(
                c[f"score_{side}"] < 4 for c in ballot["criteria"]):
            raise ValueError("Feature-ready contradicts a substantial criterion gap")
    return ballot


def aggregate(run):
    packet = run / "packet"
    lock = json.loads((packet / "council-lock.json").read_text())
    for name, checksum in lock["documents"].items():
        assert sha(packet / name) == checksum, name
    manifest = json.loads((packet / "manifest.json").read_text())
    for item in manifest["images"]:
        assert sha(packet / item["path"]) == item["sha256"], item["id"]
    ids = [i["id"] for i in manifest["images"]]
    sources = {s["id"] for s in json.loads((packet / "sources.json").read_text())["sources"]}
    key = json.loads((run / "private/provenance.json").read_text())["key"]
    candidate = next(side for side, name in key.items() if name in ["candidate", "trial"])
    incumbent = next(side for side in "AB" if side != candidate)
    ballots, errors, regressions = {}, {}, []
    for member in MEMBERS:
        try:
            ballot = validate(json.loads((run / "ballots" / f"{member}.json").read_text()),
                              member, ids, sources)
            ballots[member] = ballot
            for c in ballot["criteria"]:
                if c[f"score_{candidate.lower()}"] < c[f"score_{incumbent.lower()}"]:
                    regressions.append({"member": member, "criterion": c["id"]})
        except (OSError, ValueError, jsonschema.ValidationError) as error:
            errors[member] = str(error)[:800]
    complete = len(ballots) == 3 and not errors
    preferences = {m: b["preference"] for m, b in ballots.items()}
    wins = sum(p == candidate for p in preferences.values())
    losses = sum(p == incumbent for p in preferences.values())
    result = {"round_complete": complete, "errors": errors, "key": key,
              "preferences": preferences, "candidate_preferences": wins,
              "incumbent_preferences": losses, "score_regressions": regressions,
              "preference_eligible": complete and wins >= 2 and losses == 0 and not regressions,
              "means": {side: statistics.mean(c[f"score_{side.lower()}"]
                         for b in ballots.values() for c in b["criteria"])
                         for side in "AB"} if ballots else {},
              "promotion_requires": "Designer engineering pass and parent evidence audit; no automatic publication claim."}
    (run / "council-result.json").write_text(json.dumps(result, indent=2) + "\n")
    lines = [f"# {run.name}: council result", "", "Rubric 0.3; ratings are model judgments, not percentages of perfection.",
             "", f"Complete: {complete}. Private key revealed after judging: {key}.", "",
             f"Preferences: {preferences}. Score regressions: {regressions or 'none'}.",
             "", f"Candidate eligible under frozen preference rule: {result['preference_eligible']}.", ""]
    for member, b in ballots.items():
        lines += [f"## {member}", "", f"A: {b['verdict_a']}; B: {b['verdict_b']}; preference: {b['preference']}.",
                  "", "Observed change: " + b["observed_change"], "", b["better_vs_featureworthy"], "",
                  "| Criterion | A | B | Anchor justification / remaining gap |", "|---|---|---|---|"]
        for c in b["criteria"]:
            lines.append(f"| {c['id']} | {c['score_a']} | {c['score_b']} | {c['anchor_reason']} {c['remaining_gap']} |")
        lines += [""]
        for n, x in enumerate(b["publication_blockers"], 1):
            lines += [f"{n}. **{x['problem']}** {x['evidence']}",
                      f"   Change: {x['change']} Why: {x['why']}",
                      f"   Verify: {x['verify']} Preserve: {x['preserve']}", ""]
        lines += ["Next experiment: " + b["next_experiment"], ""]
    for member, error in errors.items():
        lines += [f"## {member}: invalid or missing ballot", "", error, ""]
    (run / "council-report.md").write_text("\n".join(lines))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["freeze", "aggregate"])
    parser.add_argument("run", type=Path)
    args = parser.parse_args()
    print(json.dumps(freeze(args.run) if args.action == "freeze" else aggregate(args.run), indent=2))
