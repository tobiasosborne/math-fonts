#!/usr/bin/env python3
"""Validate and summarize saved smoke ballots. Does not invoke any model."""
import argparse
import hashlib
import json
import statistics
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "runs/smoke-2026-10-29"
MEMBERS = ("opus", "sol", "muse")
CRITERIA = [f"R{i}" for i in range(1, 9)]
IMAGE_IDS = ["A-P1", "A-P2", "B-P1", "B-P2", "control-X", "control-Y"]


def obj(fields):
    return {"type": "object", "properties": fields, "required": list(fields),
            "additionalProperties": False}


def schema():
    text = {"type": "string", "minLength": 1}
    criterion = obj({"id": {"enum": CRITERIA},
                     "score": {"type": ["integer", "null"], "minimum": 1, "maximum": 5},
                     **{k: text for k in ["ideal", "observation", "gap_to_ideal",
                                          "editorial_justification", "next_move",
                                          "verification", "preserve"]},
                     "source_ids": {"type": "array", "minItems": 1,
                                    "uniqueItems": True, "items": text}})
    blocker = obj({k: text for k in ["problem", "evidence", "change", "reason",
                                   "verification", "preserve"]})
    assessment = obj({"side": {"enum": ["A", "B"]},
                      "criteria": {"type": "array", "minItems": 8, "maxItems": 8,
                                   "items": criterion},
                      "editorial_verdict": {"enum": ["unresolved", "functional", "polished",
                          "distinguished_but_not_feature_ready", "feature_ready"]},
                      "better_vs_featureworthy": text, "positive_editorial_case": text,
                      "publication_blockers": {"type": "array", "maxItems": 3,
                                               "items": blocker}})
    return obj({"member": {"enum": list(MEMBERS)},
                "image_receipts": {"type": "array", "minItems": 6, "maxItems": 6,
                                   "uniqueItems": True, "items": {"enum": IMAGE_IDS}},
                "control": obj({"preference": {"enum": ["X", "Y", "tie", "not_assessable"]},
                                "evidence": text}),
                "assessments": {"type": "array", "minItems": 2, "maxItems": 2,
                                "items": assessment},
                "preference": {"enum": ["A", "B", "tie", "not_assessable"]},
                "next_move": text})


def validate(ballot, member, source_ids):
    jsonschema.Draft202012Validator(schema()).validate(ballot)
    if ballot["member"] != member:
        raise ValueError("Member identity mismatch")
    if {x["side"] for x in ballot["assessments"]} != {"A", "B"}:
        raise ValueError("Both unique sides are required")
    if set(ballot["image_receipts"]) != set(IMAGE_IDS):
        raise ValueError("Incomplete image receipt list")
    if ballot["control"]["preference"] != "tie":
        raise ValueError("Identical-image control failed or was not assessable")
    for assessment in ballot["assessments"]:
        if {c["id"] for c in assessment["criteria"]} != set(CRITERIA):
            raise ValueError("Each criterion must appear once per side")
        for c in assessment["criteria"]:
            if not set(c["source_ids"]) <= source_ids:
                raise ValueError("Unknown source IDs")
            if c["score"] is None:
                raise ValueError("Incomplete assessment: non-assessable criterion")
        if assessment["editorial_verdict"] != "feature_ready" and not assessment["publication_blockers"]:
            raise ValueError("A below-feature verdict needs constructive blockers")
        if assessment["editorial_verdict"] == "feature_ready" and assessment["publication_blockers"]:
            raise ValueError("Feature-ready verdict contradicts unresolved blockers")
    return ballot


def aggregate(run=RUN):
    manifest = json.loads((run / "packet/manifest.json").read_text())
    for item in manifest["images"]:
        assert hashlib.sha256((run / "packet" / item["path"]).read_bytes()).hexdigest() == item["sha256"]
    for name, checksum in manifest.get("documents", {}).items():
        assert hashlib.sha256((run / "packet" / name).read_bytes()).hexdigest() == checksum
    source_ids = {s["id"] for s in json.loads((run / "packet/sources.json").read_text())["sources"]}
    ballots, errors = {}, {}
    for member in MEMBERS:
        path = run / "ballots" / f"{member}.json"
        try:
            ballots[member] = validate(json.loads(path.read_text()), member, source_ids)
        except (OSError, ValueError, jsonschema.ValidationError) as error:
            errors[member] = str(error)[:1200]
    complete = not errors and len(ballots) == len(MEMBERS)
    key = json.loads((run / "private/provenance.json").read_text())["key"]
    sides = {name: side for side, name in key.items()}
    regressions, scores = [], {}
    for member, ballot in ballots.items():
        pair = {a["side"]: {c["id"]: c["score"] for c in a["criteria"]}
                for a in ballot["assessments"]}
        scores[member] = pair
        regressions.extend({"member": member, "criterion": cid}
                           for cid in CRITERIA
                           if pair[sides["trial"]][cid] < pair[sides["incumbent"]][cid])
    means = {side: statistics.mean(scores[m][side][cid] for m in scores for cid in CRITERIA)
             for side in "AB"} if scores else {}
    promote = bool(complete and means[sides["trial"]] > means[sides["incumbent"]] and not regressions)
    result = {"round_complete": complete, "errors": errors, "means": means,
              "regressions": regressions, "trial_passes_iteration_rule": promote,
              "promotion_executed": False, "key": key,
              "preferences": {m: b["preference"] for m, b in ballots.items()},
              "scope": "One smoke fixture; no adoption as fresh project baseline and no further rounds."}
    if (run / "audit.json").exists():
        audit = json.loads((run / "audit.json").read_text())
        result["automatic_design_promotion_ready"] = audit["automatic_design_promotion_ready"]
        result["coordinator_audit"] = "audit.json"
    (run / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    lines = ["# Council smoke round — 2026-10-29", "",
             f"Round complete: **{complete}**. Three requested members; no automatic retries.", "",
             "This is a copied archived-font fixture and one width experiment, not the new font baseline.",
             "The absolute standard is the hypothetical perfect font and top-periodical feature readiness.", "",
             f"Unblinded identity: {key}. Trial passes iteration rule: **{promote}**. No promotion executed.", "",
             "Scores are model opinions; 144 dpi screen proofs do not establish print or reader performance.", ""]
    if (run / "coordinator-review.md").exists():
        lines += ["Read [the coordinator's outcome and evidence audit](coordinator-review.md) first.",
                  "Ballot completeness does not establish perceptual reliability or automatic promotion readiness.", ""]
    if errors:
        lines += ["## Incomplete or invalid ballots", ""]
        lines += [f"- {m}: {e}" for m, e in errors.items()]
    if ballots:
        lines += ["## Absolute scores", "", "| Member / side | " + " | ".join(CRITERIA) + " | Mean | Verdict |",
                  "|---|" + "---|" * 10]
        for m, b in ballots.items():
            for a in b["assessments"]:
                vals = scores[m][a["side"]]
                lines.append(f"| {m} / {a['side']} | " + " | ".join(str(vals[c]) for c in CRITERIA)
                             + f" | {statistics.mean(vals.values()):.2f} | {a['editorial_verdict']} |")
        for m, b in ballots.items():
            lines += ["", f"## {m}", "", f"Preference: **{b['preference']}**. Control: {b['control']['evidence']}", ""]
            for a in b["assessments"]:
                lines += [f"### Side {a['side']}: better versus feature-worthy", "", a["better_vs_featureworthy"], "",
                          "Positive editorial case: " + a["positive_editorial_case"], ""]
                for n, blocker in enumerate(a["publication_blockers"], 1):
                    lines += [f"{n}. **{blocker['problem']}** {blocker['evidence']}",
                              f"   Change: {blocker['change']} Reason: {blocker['reason']}",
                              f"   Verify: {blocker['verification']} Preserve: {blocker['preserve']}", ""]
            lines += ["Next coherent experiment: " + b["next_move"], ""]
    (run / "report.md").write_text("\n".join(lines) + "\n")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["schema", "aggregate"])
    args = parser.parse_args()
    if args.action == "schema":
        print(json.dumps(schema(), indent=2))
    else:
        print(json.dumps(aggregate(), indent=2))
