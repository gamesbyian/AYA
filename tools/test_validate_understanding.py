import copy
import json
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from validate_understanding import UnderstandingError, validate

EX = pathlib.Path(__file__).resolve().parents[1] / "docs/understanding/examples"


def fixture():
    return (json.loads((EX / "parcelpad-understanding.json").read_text(encoding="utf-8")),
            json.loads((EX / "parcelpad-decisions.json").read_text(encoding="utf-8")))


class ApplicationUnderstandingTests(unittest.TestCase):
    def test_valid_fictional_open_ambiguity(self):
        result = validate(*fixture())
        self.assertTrue(result["ok"])
        self.assertEqual(result["unresolved"], ["AMB-001"])

    def test_cross_app_decisions_rejected(self):
        model, records = fixture()
        records["app_id"] = "another.app"
        with self.assertRaisesRegex(UnderstandingError, "identity mismatch"):
            validate(model, records)

    def test_unknown_concept_relation_rejected(self):
        model, records = fixture()
        model["goals"][0]["concept_ids"] = ["CONCEPT-404"]
        with self.assertRaisesRegex(UnderstandingError, "Unknown/missing concepts"):
            validate(model, records)

    def test_intention_cannot_prove_available_shipped_feature(self):
        model, records = fixture()
        model["claims"][0]["truth_kind"] = "intention"
        with self.assertRaisesRegex(UnderstandingError, "Intent alone"):
            validate(model, records)

    def test_deferred_decision_cannot_be_cited_as_approval(self):
        model, records = fixture()
        model["principles"][0]["decision_ids"] = ["DEC-001"]
        with self.assertRaisesRegex(UnderstandingError, "cannot authorize"):
            validate(model, records)

    def test_affirmative_decision_needs_attributed_director(self):
        model, records = fixture()
        records["decisions"][0]["status"] = "confirmed"
        with self.assertRaisesRegex(UnderstandingError, "unknown actor"):
            validate(model, records)

    def test_deferred_cannot_mark_ambiguity_answered(self):
        model, records = fixture()
        model["ambiguities"][0]["status"] = "answered"
        with self.assertRaisesRegex(UnderstandingError, "cannot resolve"):
            validate(model, records)

    def test_duplicate_ids_rejected(self):
        model, records = fixture()
        model["concepts"].append(copy.deepcopy(model["concepts"][0]))
        with self.assertRaisesRegex(UnderstandingError, "duplicate ID"):
            validate(model, records)


if __name__ == "__main__":
    unittest.main()
