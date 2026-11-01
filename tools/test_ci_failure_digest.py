"""Contract tests for bounded, non-speculative CI failure metadata."""
import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from ci_failure_digest import DigestError, main, make_digest, write_digest


ENV = {
    "GITHUB_REPOSITORY": "gamesbyian/AYA",
    "GITHUB_SHA": "a" * 40,
    "GITHUB_RUN_ID": "12345",
    "GITHUB_RUN_ATTEMPT": "2",
    "GITHUB_WORKFLOW": "Reference authoring checks",
    "GITHUB_JOB": "docs",
}


class CIFailureDigestTests(unittest.TestCase):
    def test_valid_failure_has_run_identity_and_no_fabricated_cause(self):
        outcomes = {
            "guide": "success",
            "packet": "failure",
            "translation": "skipped",
            "all_tests": "failure",
        }
        result = make_digest(outcomes, ENV)
        self.assertEqual(result["schema"], "aya-ci-failure/v1")
        self.assertEqual(result["failed_stages"], ["packet", "all_tests"])
        self.assertEqual(result["first_observed_failure"], "packet")
        self.assertEqual(result["run_url"],
                         "https://github.com/gamesbyian/AYA/actions/runs/12345")
        self.assertEqual(result["attempt"], 2)
        self.assertIsNone(result["root_error"])
        self.assertIn("unverified", result["root_error_limit"])
        self.assertEqual(result["stages"][0]["outcome"], "success")

    def test_missing_invalid_host_metadata_never_produces_guessed_url(self):
        result = make_digest({"guide": "failure"}, {
            "GITHUB_REPOSITORY": "../../wrong",
            "GITHUB_SHA": "not-a-sha",
            "GITHUB_RUN_ID": "NaN",
        })
        self.assertIsNone(result["repository"])
        self.assertIsNone(result["commit_sha"])
        self.assertIsNone(result["run_url"])

    def test_no_observed_failure_does_not_invent_one(self):
        result = make_digest({"compile": "success", "other": "skipped"}, ENV)
        self.assertEqual(result["failed_stages"], [])
        self.assertIsNone(result["first_observed_failure"])
        self.assertIsNone(result["root_error"])

    def test_invalid_outcomes_are_rejected(self):
        for payload in ({}, [], None,
                        {"../../external": "failure"}, {"s": "recipient_answered"},
                        {"s": ["failure"]}, {"s": None},
                        {f"stage_{i}": "success" for i in range(65)}):
            with self.subTest(payload=str(payload)[:30]):
                with self.assertRaises(DigestError):
                    make_digest(payload, ENV)

    def test_written_json_is_parseable_and_preserves_explicit_stage_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "evidence" / "failure.json"
            write_digest(path, {"stage_b": "failure", "stage_a": "cancelled"}, ENV)
            read = json.loads(path.read_text())
            self.assertEqual(read["stages"][0]["stage"], "stage_b")
            self.assertEqual(read["cancelled_stages"], ["stage_a"])
            self.assertTrue(path.read_text().endswith("\n"))

    def test_symlinked_report_destination_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "real.json").write_text("original")
            (root / "link.json").symlink_to(root / "real.json")
            with self.assertRaisesRegex(DigestError, "symlinked"):
                write_digest(root / "link.json", {"stage": "failure"}, ENV)
            self.assertEqual((root / "real.json").read_text(), "original")

    def test_cli_emits_human_summary_and_artifact_without_raw_log_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "aya-ci-failure.json"
            summary = Path(tmp) / "summary.md"
            with patch.dict(os.environ, {**ENV, "GITHUB_STEP_SUMMARY": str(summary)}):
                with contextlib.redirect_stdout(io.StringIO()):
                    code = main(["--outcomes-json", '{"guide":"failure","tests":"skipped"}',
                                 "--output", str(path)])
            self.assertEqual(code, 0)
            self.assertIn("guide", summary.read_text())
            self.assertIn("first root error remains unverified", summary.read_text())
            raw = path.read_text()
            self.assertNotIn("secret", raw)
            self.assertEqual(json.loads(raw)["first_observed_failure"], "guide")

    def test_cli_invalid_json_fails_without_artifact(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "out.json"
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(main(["--outcomes-json", "[]", "--output", str(path)]), 1)
            self.assertFalse(path.exists())


if __name__ == "__main__":
    unittest.main()
