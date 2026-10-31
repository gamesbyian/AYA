"""Independent structural checks for optional AYA behavioural evidence."""
import copy
import json
import tempfile
import subprocess
import sys
import unittest
from pathlib import Path

from check_component_compatibility import CompatibilityError, evaluate

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "docs/components/conformance/examples/unverified-fictional.json"


class CompatibilityContractTest(unittest.TestCase):
    def setUp(self):
        self.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_fictional_sample_is_explicitly_incomplete(self):
        outcome = evaluate(self.fixture)
        self.assertEqual(outcome["status"], "incomplete")
        self.assertEqual(len(outcome["incomplete_cases"]), 12)

    def test_duplicate_case_ids_refused(self):
        self.fixture["cases"][1]["id"] = self.fixture["cases"][0]["id"]
        with self.assertRaises(CompatibilityError):
            evaluate(self.fixture)

    def test_unsubstantiated_pass_cannot_clear_a_case(self):
        self.fixture["cases"][0]["status"] = "pass"
        with self.assertRaises(CompatibilityError):
            evaluate(self.fixture)

    def test_only_file_specific_check_can_be_na(self):
        self.fixture["cases"][0].update({
            "status": "not_applicable",
            "test_method": "source-audit",
            "notes": "Verified text-only transport with no file grants.",
            "evidence_refs": ["test:fictional"],
        })
        with self.assertRaises(CompatibilityError):
            evaluate(self.fixture)

    def test_full_evidence_is_review_ready_not_certification(self):
        good = copy.deepcopy(self.fixture)
        for row in good["cases"]:
            row.update({
                "status": "pass",
                "test_method": "instrumentation",
                "notes": "Independent release-scoped Android test observed expected behaviour.",
                "evidence_refs": ["test:fictional"],
            })
        outcome = evaluate(good)
        self.assertEqual(outcome["status"], "ready_for_independent_review")
        self.assertIn("no certification", outcome["scope_note"])

    def test_default_cli_rejects_incomplete_but_draft_option_reports_it(self):
        path = ROOT / "tools/check_component_compatibility.py"
        a = subprocess.run([sys.executable, str(path), str(FIXTURE)],
                           text=True, capture_output=True, check=False)
        b = subprocess.run([sys.executable, str(path), str(FIXTURE), "--allow-incomplete"],
                           text=True, capture_output=True, check=False)
        self.assertEqual(a.returncode, 1, a.stderr)
        self.assertEqual(b.returncode, 0, b.stderr)
        self.assertIn('"status": "incomplete"', b.stdout)

    def test_unknown_fields_or_naive_timestamps_fail_closed(self):
        self.fixture["extra"] = "override"
        with self.assertRaises(CompatibilityError):
            evaluate(self.fixture)
        self.fixture.pop("extra")
        self.fixture["implementation"]["tested_at_utc"] = "2026-10-30T12:00:00"
        with self.assertRaises(CompatibilityError):
            evaluate(self.fixture)


if __name__ == "__main__":
    unittest.main()
