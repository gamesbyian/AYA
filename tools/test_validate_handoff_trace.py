"""SDK-free handoff trace validator tests: event order, negatives, privacy scope."""
from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from validate_handoff_trace import (
    SCHEMA, TraceValidationError, main, validate,
    check_case,
)

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "docs/conformance/examples/lantern-trace.json"


class InteractionTraceTest(unittest.TestCase):
    def setUp(self):
        self.doc = json.loads(SAMPLE.read_text(encoding="utf-8"))

    def case(self, name):
        return next(x for x in self.doc["cases"] if x["scenario"] == name)

    def test_full_fictional_example_validates(self):
        self.assertEqual(validate(self.doc), ("org.example.lantern", "1.2.3"))
        self.assertEqual(self.doc["schema"], SCHEMA)

    def test_no_payload_fields_can_be_smuggled(self):
        for field in ("question", "assistantReply", "recipient", "guide", "uri", "secret"):
            with self.subTest(field=field):
                doc = copy.deepcopy(self.doc)
                doc["cases"][0][field] = "arbitrary"
                with self.assertRaises(TraceValidationError):
                    validate(doc)

    def test_rejects_no_review_or_early_share(self):
        for sequence in (
            ["reference_validated", "share_requested", "chooser_opened"],
            ["reference_validated", "review_opened", "share_requested",
             "review_approved", "chooser_opened"],
            ["reference_validated", "review_opened", "review_approved",
             "chooser_opened", "share_requested"],
        ):
            with self.subTest(events=sequence), self.assertRaises(TraceValidationError):
                check_case("review_share", sequence)

    def test_rejects_copy_without_explicit_approval(self):
        events = ["reference_validated", "review_opened",
                  "copy_requested", "review_approved", "copy_succeeded"]
        with self.assertRaises(TraceValidationError):
            check_case("review_copy", events)

    def test_question_composer_and_edit_must_precede_terminal_review(self):
        share = ["reference_validated", "review_opened", "question_opened",
                 "review_approved", "share_requested", "chooser_opened"]
        with self.assertRaises(TraceValidationError):
            check_case("review_share", share)
        cancelled = ["reference_validated", "review_opened", "review_cancelled",
                     "review_edited"]
        with self.assertRaises(TraceValidationError):
            check_case("cancel", cancelled)
        changed_after_approval = ["reference_validated", "review_opened",
                                  "review_edited", "review_approved",
                                  "review_edited", "share_requested", "chooser_opened"]
        with self.assertRaises(TraceValidationError):
            check_case("review_share", changed_after_approval)

    def test_cancel_cannot_have_side_effects(self):
        for extra in ("share_requested", "copy_requested", "review_approved"):
            with self.subTest(extra=extra):
                events = ["reference_validated", "review_opened",
                          "review_cancelled", extra]
                with self.assertRaises(TraceValidationError):
                    check_case("cancel", events)

    def test_version_mismatch_cannot_open_review(self):
        for extra in ("reference_validated", "review_opened", "share_requested"):
            with self.subTest(extra=extra), self.assertRaises(TraceValidationError):
                check_case("version_mismatch",
                           ["reference_rejected", "local_rejected", extra])

    def test_no_receiver_must_offer_copy_fallback(self):
        events = ["reference_validated", "review_opened", "review_approved",
                  "share_requested", "share_unavailable"]
        with self.assertRaises(TraceValidationError):
            check_case("no_receiver", events)

    def test_no_activity_is_rejection_only(self):
        with self.assertRaises(TraceValidationError):
            check_case("no_activity",
                       ["activity_detached", "local_rejected", "review_opened"])

    def test_duplicate_terminal_events_and_reordered_actions_rejected(self):
        events = self.case("review_share")["events"]
        with self.assertRaises(TraceValidationError):
            check_case("review_share", events + ["chooser_opened"])
        with self.assertRaises(TraceValidationError):
            check_case("review_share", events + ["share_requested"])

    def test_duplicate_or_missing_case_is_invalid(self):
        doc = copy.deepcopy(self.doc)
        doc["cases"][0] = copy.deepcopy(doc["cases"][1])
        with self.assertRaises(TraceValidationError):
            validate(doc)
        doc = copy.deepcopy(self.doc)
        doc["cases"].pop()
        with self.assertRaises(TraceValidationError):
            validate(doc)

    def test_bad_platform_identity_or_schema_rejected(self):
        for path, value in (
            (("schema",), "aya-interaction-trace/v0"),
            (("host", "platform"), "ios"),
            (("host", "app_id"), "org-no-dots"),
            (("host", "app_version"), ""),
            (("host", "source_revision"), "private/path/with/separators"),
        ):
            doc = copy.deepcopy(self.doc)
            if len(path) == 1:
                doc[path[0]] = value
            else:
                doc[path[0]][path[1]] = value
            with self.subTest(path=path), self.assertRaises(TraceValidationError):
                validate(doc)

    def test_rejects_unrecognized_recipient_events(self):
        events = self.case("review_share")["events"]
        with self.assertRaises(TraceValidationError):
            check_case("review_share", events + ["agent_replied"])

    def test_cli_rejects_large_file_and_missing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "trace.json"
            path.write_text(" " * 40000)
            self.assertEqual(main([str(path)]), 1)
            self.assertEqual(main([str(Path(tmp) / "absent.json")]), 1)


if __name__ == "__main__":
    unittest.main()
