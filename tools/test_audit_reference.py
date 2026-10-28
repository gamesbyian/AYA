import copy
import json
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from audit_reference import audit, reference_entries

ROOT = pathlib.Path(__file__).resolve().parents[1] / "docs/reference"
GUIDE = ROOT / "EXAMPLE_PARCELPAD.md"
INVENTORY = ROOT / "examples/parcelpad_inventory.json"
QUESTIONS = ROOT / "examples/parcelpad_questions.json"


class ReferenceAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.guide = GUIDE.read_text(encoding="utf-8")
        cls.inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
        cls.questions = json.loads(QUESTIONS.read_text(encoding="utf-8"))

    def test_example_passes(self):
        result = audit(self.guide, self.inventory, self.questions)
        self.assertTrue(result["ok"], result["errors"])
        self.assertEqual(result["coverage_ratio"], 1.0)
        self.assertEqual(result["question_cases"], 5)

    def test_omitted_undocumented_feature_is_detected(self):
        changed = copy.deepcopy(self.inventory)
        changed["items"].append({
            "id": "F-404", "kind": "feature", "title": "Not in guide",
            "status": "AVAILABLE", "criticality": "high", "source_ref": "fixture"
        })
        report = audit(self.guide, changed)
        self.assertFalse(report["ok"])
        self.assertTrue(any("F-404 has no guide entry" in e for e in report["errors"]))

    def test_status_conflict_is_detected(self):
        changed = copy.deepcopy(self.inventory)
        changed["items"][3]["status"] = "AVAILABLE"
        report = audit(self.guide, changed)
        self.assertFalse(report["ok"])
        self.assertTrue(any("F-002" in e and "status" in e for e in report["errors"]))

    def test_duplicate_guide_ids_are_detected(self):
        altered = self.guide + "\n### F-001: Duplicated [AVAILABLE]\n- Evidence: fixture\n"
        report = audit(altered, self.inventory)
        self.assertFalse(report["ok"])
        self.assertTrue(any("Duplicate guide ID" in e for e in report["errors"]))

    def test_missing_evidence_detected(self):
        altered = self.guide.replace("- Evidence: fictional training scenario.", "- Source: fictional training scenario.")
        report = audit(altered, self.inventory)
        self.assertFalse(report["ok"])
        self.assertTrue(any("missing '- Evidence:'" in e for e in report["errors"]))

    def test_malformed_inventory_reports_failure_not_crash(self):
        changed = copy.deepcopy(self.inventory)
        changed["items"] = "not a list"
        report = audit(self.guide, changed)
        self.assertFalse(report["ok"])
        self.assertTrue(any("nonempty items array" in e for e in report["errors"]))

    def test_question_reference_must_exist(self):
        changed = copy.deepcopy(self.questions)
        changed["cases"][0]["evidence_ids"] = ["F-999"]
        report = audit(self.guide, self.inventory, changed)
        self.assertFalse(report["ok"])
        self.assertTrue(any("F-999" in e for e in report["errors"]))

    def test_question_revision_must_match(self):
        changed = copy.deepcopy(self.questions)
        changed["guide_revision"] = "999"
        report = audit(self.guide, self.inventory, changed)
        self.assertFalse(report["ok"])

    def test_missing_task_numbered_steps_detected(self):
        altered = self.guide.replace("1. Open the intended collection.", "First open the intended collection.")
        report = audit(altered, self.inventory)
        self.assertFalse(report["ok"])
        self.assertTrue(any("TASK-001" in e and "numbered step" in e for e in report["errors"]))

    def test_reference_entries_extract_unsupported(self):
        entries, errors = reference_entries(self.guide)
        self.assertFalse(errors)
        self.assertEqual(entries["F-003"]["status"], "UNSUPPORTED")


if __name__ == "__main__":
    unittest.main()
