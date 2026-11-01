"""Prevent a required AYA PR baseline from disappearing due to path filters."""
import unittest
from pathlib import Path

WORKFLOWS = Path(__file__).resolve().parents[1] / ".github" / "workflows"
REFERENCE = WORKFLOWS / "reference-guide.yml"


class RequiredPRGateTest(unittest.TestCase):
    def test_reference_suite_runs_for_every_pull_request(self):
        source = REFERENCE.read_text(encoding="utf-8")
        self.assertEqual(source.count("  pull_request:\n"), 1)
        trigger = source.split("  pull_request:\n", 1)[1].split("\njobs:", 1)[0]
        self.assertNotIn("    paths:", trigger)
        self.assertNotIn("    paths-ignore:", trigger)
        self.assertNotIn("    branches:", trigger)
        self.assertIn("  docs:", source)
        self.assertIn("python3 -m unittest discover -s tools -p 'test_*.py'", source)

    def test_baseline_keeps_security_portability_and_independent_packet_checks(self):
        source = REFERENCE.read_text(encoding="utf-8")
        for required in (
            "tools.test_module_portability",
            "tools/validate_guide.py",
            "tools/audit_reference.py",
            "tools/packet_compiler.py",
            "tools/validate_understanding.py",
            "tools/validate_translation_kit.py",
            "tools/validate_filesystem_kit.py",
            "tools/ci_failure_digest.py",
        ):
            self.assertIn(required, source)

    def test_main_push_does_not_dispatch_for_unrelated_changes(self):
        source = REFERENCE.read_text(encoding="utf-8")
        push = source.split("  push:\n", 1)[1].split("  pull_request:\n", 1)[0]
        self.assertIn("    branches: [main]", push)
        self.assertIn("    paths:", push)
        self.assertIn("'docs/**'", push)


if __name__ == "__main__":
    unittest.main()
