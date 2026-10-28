"""Integrity checks for the research-informed, non-gold cross-category prompt bank.

These tests assert structural provenance and stable coverage only. They do not
assert that any named app supports a feature or that the assistant answers well.
"""
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "docs/reference/examples/cross_category_batch2_147.json"
CHALLENGES = set("HOPNSATLER")


class CrossCategoryBatchTwoFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_metadata_does_not_claim_gold_answers_or_rankings(self):
        data = self.data
        self.assertEqual(data["schema_version"], "aya-cross-category-prompts/v1")
        self.assertEqual(data["evidence_status"], "UNVERIFIED_PROMPTS_NOT_GOLD_ANSWERS")
        self.assertIn("not been independently verified", data["source_description"])

    def test_21_categories_seven_questions_each(self):
        categories = self.data["categories"]
        self.assertEqual(len(categories), 21)
        self.assertEqual(sum(len(c["questions"]) for c in categories), 147)
        self.assertEqual(len({c["app"] for c in categories}), 21)
        self.assertEqual(len({c["id"] for c in categories}), 21)

    def test_stable_ids_questions_and_valid_challenges(self):
        ids = []
        for category_index, category in enumerate(self.data["categories"], 1):
            self.assertEqual(category["id"], f"C{category_index:02}")
            self.assertTrue(category["category"].strip())
            for question_index, case in enumerate(category["questions"], 1):
                case_id = f"B2-{category_index:02}-{question_index:02}"
                self.assertEqual(case["id"], case_id)
                self.assertTrue(case["question"].strip().endswith("?"))
                self.assertGreater(len(case["question"]), 20)
                self.assertTrue(case["challenges"])
                self.assertEqual(len(case["challenges"]), len(set(case["challenges"])))
                self.assertTrue(set(case["challenges"]) <= CHALLENGES)
                ids.append(case_id)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(set(self.data["meaning_of_challenges"]), CHALLENGES)


if __name__ == "__main__":
    unittest.main()
