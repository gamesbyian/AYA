"""Cross-language fixture parity for AYA-RAS iOS structural reference guards.

The developer linter checks authoring conventions; the installed runtime
additionally checks exact bundle/version identity. Those are intentionally
different questions, encoded by two expected outcomes for each shared case.
"""
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "integrations/apple/AYAApple/Tests/AYAProtocolTests/Fixtures"
sys.path.insert(0, str(ROOT / "tools"))
from validate_guide import validate


class AppleReferenceParityTests(unittest.TestCase):
    def test_same_reference_mutations_as_swift(self):
        guide = (FIXTURE / "reference-ios.md").read_text(encoding="utf-8")
        matrix = json.loads((FIXTURE / "cases.json").read_text(encoding="utf-8"))
        self.assertEqual(matrix["schema"], "aya-reference-parity/v1")
        self.assertGreaterEqual(len(matrix["cases"]), 10)
        seen = set()
        for case in matrix["cases"]:
            with self.subTest(case=case["id"]):
                self.assertNotIn(case["id"], seen)
                seen.add(case["id"])
                candidate = guide
                if "find" in case:
                    self.assertIn(case["find"], candidate)
                    self.assertEqual(candidate.count(case["find"]), 1)
                    candidate = candidate.replace(case["find"], case["replace"], 1)
                lint_result = validate(candidate, expected_platform="ios")
                self.assertEqual(lint_result["ok"], case["offlineAccepts"],
                                 f"{case['id']}: {lint_result['errors']}")
                self.assertIsInstance(case["runtimeAccepts"], bool)
                # A present guide is always still the wrong OS for the Android linter.
                if case["id"] == "exact-ios-guide":
                    self.assertFalse(validate(candidate)["ok"])

    def test_bad_fixture_matrix_is_not_a_quiet_success(self):
        matrix = json.loads((FIXTURE / "cases.json").read_text(encoding="utf-8"))
        self.assertTrue(all(isinstance(x["offlineAccepts"], bool) and
                            isinstance(x["runtimeAccepts"], bool)
                            for x in matrix["cases"]))
        self.assertTrue(any(x["offlineAccepts"] and not x["runtimeAccepts"]
                            for x in matrix["cases"]),
                        "Installed identity guards must be tested independently")


if __name__ == "__main__":
    unittest.main()
