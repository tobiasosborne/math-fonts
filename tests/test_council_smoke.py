import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

import jsonschema

SPEC = importlib.util.spec_from_file_location(
    "council_smoke", Path(__file__).resolve().parents[1] / "tools/council_smoke.py")
council = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(council)


def ballot(member="sol"):
    return {
        "member": member,
        "image_receipts": council.IMAGE_IDS,
        "control": {"preference": "tie", "evidence": "Same visible shapes and spacing."},
        "assessments": [
            {"side": side, "criteria": [
                {"id": cid, "score": 3, "ideal": "Even fitting at reading size.",
                 "observation": "P2.1 at 10 pt has a gap beside the relation.",
                 "gap_to_ideal": "Local spacing interrupts rhythm.",
                 "editorial_justification": "An unresolved gap prevents 4.",
                 "next_move": "Reduce the affected sidebearing.",
                 "verification": "Check P2.1 without new collisions.",
                 "preserve": "Keep stroke weight.", "source_ids": ["P02"]}
                for cid in council.CRITERIA],
             "editorial_verdict": "polished",
             "better_vs_featureworthy": "Usable, but fitting is not feature-ready.",
             "positive_editorial_case": "The weight is coherent.",
             "publication_blockers": [
                 {"problem": "Uneven fitting", "evidence": "P2.1",
                  "change": "Reduce the gap", "reason": "Restore rhythm",
                  "verification": "Repeat the pair contexts", "preserve": "Weight"}]}
            for side in "AB"],
        "preference": "tie", "next_move": "Test the local spacing correction."}


class CouncilValidationTests(unittest.TestCase):
    def test_complete_constructive_ballot(self):
        council.validate(ballot(), "sol", {"P02"})

    def test_incomplete_or_duplicated_coverage_rejected(self):
        for mutate in [
            lambda b: b["image_receipts"].pop(),
            lambda b: b["assessments"][0]["criteria"].__setitem__(1, copy.deepcopy(b["assessments"][0]["criteria"][0])),
            lambda b: b["assessments"][1].__setitem__("side", "A"),
        ]:
            b = copy.deepcopy(ballot())
            mutate(b)
            with self.assertRaises((ValueError, jsonschema.ValidationError)):
                council.validate(b, "sol", {"P02"})

    def test_unjustified_scores_and_rejections_rejected(self):
        for field in ["next_move", "verification", "preserve", "editorial_justification"]:
            b = copy.deepcopy(ballot())
            b["assessments"][0]["criteria"][0][field] = ""
            with self.assertRaises(jsonschema.ValidationError):
                council.validate(b, "sol", {"P02"})
        b = ballot()
        b["assessments"][0]["publication_blockers"] = []
        with self.assertRaises(ValueError):
            council.validate(b, "sol", {"P02"})

    def test_invalid_scores_unknown_sources_and_control_failure(self):
        for score in [True, 0, 6, 3.5, None]:
            b = copy.deepcopy(ballot())
            b["assessments"][0]["criteria"][0]["score"] = score
            with self.assertRaises((ValueError, jsonschema.ValidationError)):
                council.validate(b, "sol", {"P02"})
        with self.assertRaises(ValueError):
            council.validate(ballot(), "sol", set())
        b = ballot()
        b["control"]["preference"] = "X"
        with self.assertRaises(ValueError):
            council.validate(b, "sol", {"P02"})

    def test_missing_member_and_hidden_regression_prevent_promotion(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            for name in ["packet", "private", "ballots"]:
                (run / name).mkdir()
            (run / "packet/manifest.json").write_text(json.dumps({"images": []}))
            (run / "packet/sources.json").write_text(json.dumps({"sources": [{"id": "P02"}]}))
            (run / "private/provenance.json").write_text(json.dumps({"key": {"A": "incumbent", "B": "trial"}}))
            for member in ["sol", "opus"]:
                (run / "ballots" / f"{member}.json").write_text(json.dumps(ballot(member)))
            result = council.aggregate(run)
            self.assertFalse(result["round_complete"])
            self.assertFalse(result["trial_passes_iteration_rule"])
            b = copy.deepcopy(ballot("muse"))
            for c in b["assessments"][1]["criteria"]:
                c["score"] = 4
            b["assessments"][1]["criteria"][0]["score"] = 2
            (run / "ballots/muse.json").write_text(json.dumps(b))
            result = council.aggregate(run)
            self.assertTrue(result["round_complete"])
            self.assertGreater(result["means"]["B"], result["means"]["A"])
            self.assertFalse(result["trial_passes_iteration_rule"])
            self.assertEqual(result["regressions"], [{"member": "muse", "criterion": "R1"}])


if __name__ == "__main__":
    unittest.main()
