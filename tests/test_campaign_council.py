import copy
import importlib.util
import json
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

import jsonschema

SPEC = importlib.util.spec_from_file_location(
    "campaign_council", Path(__file__).resolve().parents[1] / "tools/campaign_council.py")
council = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(council)


def ballot(member):
    return {"member": member, "seen_images": ["A", "B", "control-X", "control-Y"],
            "control": {"preference": "tie", "evidence": "Matching shapes."},
            "criteria": [{"id": cid, "ideal": "Resolved shape and rhythm.",
                          "score_a": 2, "score_b": 2,
                          "observation_a": "P2 root join has a dark spot.",
                          "observation_b": "P2 transition looks smoother.",
                          "anchor_reason": "An unresolved family keeps both below 3.",
                          "remaining_gap": "Small-size joins still need refining.",
                          "next_move": "Refine the entry stroke.", "source_ids": ["P03"]}
                         for cid in council.CRITERIA],
            "observed_change": "A different root join.", "preference": "B",
            "verdict_a": "functional", "verdict_b": "functional",
            "better_vs_featureworthy": "A better join does not resolve the family.",
            "publication_blockers": [{k: "Specific proof and design guidance."
                                     for k in ["problem", "evidence", "change", "why", "verify", "preserve"]}],
            "next_experiment": "Test a curved entry at 8 and 10 pt."}


class CampaignTests(unittest.TestCase):
    def test_campaign_focus_is_frozen_and_tampering_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            for name in ["docs", "council", "research/typography", "campaign/round-1/packet"]:
                (base / name).mkdir(parents=True)
            for name in ["docs/rubric.md", "council/judge-prompt.md"]:
                (base / name).write_text("Fixed standard")
            (base / "research/typography/sources.json").write_text('{"sources": []}')
            (base / "campaign/evaluation-focus.md").write_text("Greek counters and fitting")
            run = base / "campaign/round-1"
            (run / "packet/manifest.json").write_text('{"images": []}')
            with patch.object(council, "ROOT", base):
                lock = council.freeze(run)
                self.assertIn("evaluation-focus.md", lock["documents"])
                with self.assertRaises(ValueError): council.freeze(run)
                (run / "packet/evaluation-focus.md").write_text("Changed standard")
                with self.assertRaises(AssertionError): council.aggregate(run)

    def test_invalid_or_unjustified_ballot(self):
        for mutate in [
            lambda b: b["criteria"][0].__setitem__("score_a", True),
            lambda b: b["criteria"][0].__setitem__("anchor_reason", ""),
            lambda b: b["criteria"][0].__setitem__("next_move", ""),
            lambda b: b["criteria"].__setitem__(1, copy.deepcopy(b["criteria"][0])),
            lambda b: b.__setitem__("publication_blockers", []),
            lambda b: b.__setitem__("verdict_b", "feature_ready"),
            lambda b: b["control"].__setitem__("preference", "X"),
        ]:
            value = copy.deepcopy(ballot("sol")); mutate(value)
            with self.assertRaises((ValueError, jsonschema.ValidationError)):
                council.validate(value, "sol", ["A", "B", "control-X", "control-Y"], {"P03"})

    def test_preference_breaks_score_plateau_but_regression_blocks_it(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            for name in ["packet", "private", "ballots"]: (run / name).mkdir()
            (run / "packet/council-lock.json").write_text(json.dumps({"documents": {}}))
            (run / "packet/manifest.json").write_text(json.dumps({"images": []}))
            # Empty images are used only as a storage fixture, not a live proof packet.
            (run / "packet/sources.json").write_text(json.dumps({"sources": [{"id": "P03"}]}))
            (run / "private/provenance.json").write_text(json.dumps({"key": {"A": "incumbent", "B": "candidate"}}))
            for member in council.MEMBERS:
                b = ballot(member); b["seen_images"] = []
                if member == "muse": b["preference"] = "tie"
                (run / "ballots" / f"{member}.json").write_text(json.dumps(b))
            result = council.aggregate(run)
            self.assertTrue(result["round_complete"])
            self.assertEqual(result["means"]["A"], result["means"]["B"])
            self.assertTrue(result["preference_eligible"])
            b = ballot("sol"); b["seen_images"] = []; b["criteria"][0]["score_b"] = 1
            (run / "ballots/sol.json").write_text(json.dumps(b))
            self.assertFalse(council.aggregate(run)["preference_eligible"])
            (run / "ballots/muse.json").unlink()
            self.assertFalse(council.aggregate(run)["round_complete"])


if __name__ == "__main__": unittest.main()
