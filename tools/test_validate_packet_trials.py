import copy
import hashlib
import sys
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from validate_packet_trials import TrialError, assess_trials


def sample(packet: bytes, verdict="pass"):
    return {
        "schema_version": "aya-packet-trials/v1",
        "packet_sha256": hashlib.sha256(packet).hexdigest(),
        "profile": "creative",
        "host_app_version": "1.0.0",
        "cases": [{
            "id": "CASE-001",
            "user_goal": "Generate compatible square artwork",
            "expected_result": "Image fits host import contract",
            "recipient": "controlled synthetic assistant fixture",
            "recipient_version": "fixture-v1",
            "android_version": "fixture-only",
            "tested_at_utc": "2026-10-30T00:00:00Z",
            "attachment_ingested": verdict == "pass",
            "host_outcome_verified": verdict == "pass",
            "reviewer": "synthetic unit-test reviewer",
            "evidence_ref": "unit-test fixture, NOT real QA",
            "verdict": verdict,
            "severity": "P1",
            "forbidden_claims": ["Already installed into host"]
        }]
    }


def declared_real_sample(packet: bytes, verdict="pass", transport="text_and_txt_reference"):
    # Synthetic assertions for validator structure. These values are NOT QA evidence.
    ledger = sample(packet, verdict)
    ledger["schema_version"] = "aya-packet-trials/v2"
    case = ledger["cases"][0]
    case.update({
        "evidence_kind": "real_recipient",
        "transport": transport,
        "recipient_package": "org.example.testreceiver",
        "android_api_level": 35,
        "device_kind": "android_emulator",
        "host_artifact_sha256": "0" * 64,
        "recipient_input_verified": verdict == "pass",
    })
    return ledger


class PacketTrialTests(unittest.TestCase):
    def setUp(self):
        self.packet = b"synthetic packet bytes only"

    def test_legacy_v1_is_readable_but_cannot_claim_release_readiness(self):
        report = assess_trials(sample(self.packet), self.packet, strict=False)
        self.assertEqual(report["passed"], 1)
        self.assertFalse(report["release_gate_pass"])
        self.assertEqual(report["unqualified_trial_ids"], ["CASE-001"])
        with self.assertRaisesRegex(TrialError, "release gate failed"):
            assess_trials(sample(self.packet), self.packet)

    def test_v2_synthetic_or_documentation_trial_never_passes_release(self):
        for kind in ("synthetic_fixture", "documentation_only"):
            ledger = declared_real_sample(self.packet)
            case = ledger["cases"][0]
            case["evidence_kind"] = kind
            with self.subTest(kind=kind):
                report = assess_trials(ledger, self.packet, strict=False)
                self.assertEqual(report["passed"], 1)
                self.assertFalse(report["release_gate_pass"])
                with self.assertRaisesRegex(TrialError, "release gate failed"):
                    assess_trials(ledger, self.packet)

    def test_v2_structurally_real_claim_is_possible_but_not_qa_proof(self):
        # This only checks self-reported ledger shape, NOT physical/assistant truth.
        ledger = declared_real_sample(self.packet)
        result = assess_trials(ledger, self.packet)
        self.assertTrue(result["release_gate_pass"])
        self.assertEqual(result["real_recipient_trials"], 1)
        self.assertFalse(result["unqualified_trial_ids"])

    def test_filesystem_profile_uses_same_strict_real_outcome_gate(self):
        ledger = declared_real_sample(self.packet)
        ledger["profile"] = "filesystem"
        ledger["cases"][0]["user_goal"] = "Create a safe file cleanup recipe"
        ledger["cases"][0]["expected_result"] = "Host parser accepts recipe and explicit review"
        self.assertEqual("filesystem", assess_trials(ledger, self.packet)["profile"])
        ledger["cases"][0]["attachment_ingested"] = False
        with self.assertRaisesRegex(TrialError, "Cannot claim pass"):
            assess_trials(ledger, self.packet)
        ledger["cases"][0]["verdict"] = "unknown"
        self.assertFalse(assess_trials(ledger, self.packet, strict=False)["release_gate_pass"])

    def test_text_only_real_declared_receipt_does_not_require_attachment(self):
        ledger = declared_real_sample(self.packet, transport="text_only")
        ledger["cases"][0]["attachment_ingested"] = False
        self.assertTrue(assess_trials(ledger, self.packet)["release_gate_pass"])
        ledger["cases"][0]["recipient_input_verified"] = False
        with self.assertRaisesRegex(TrialError, "Cannot claim pass"):
            assess_trials(ledger, self.packet)

    def test_reference_transport_without_actual_ingestion_rejected(self):
        ledger = declared_real_sample(self.packet)
        ledger["cases"][0]["attachment_ingested"] = False
        with self.assertRaisesRegex(TrialError, "Cannot claim pass"):
            assess_trials(ledger, self.packet)

    def test_real_evidence_requires_verifiable_android_metadata(self):
        base = declared_real_sample(self.packet)
        changes = [
            ("recipient_package", "not-a-package"),
            ("android_api_level", True),
            ("android_api_level", 0),
            ("device_kind", "browser"),
            ("host_artifact_sha256", "not-a-digest"),
            ("transport", "copy-magic"),
            ("evidence_kind", "unclassified"),
        ]
        for key, invalid in changes:
            with self.subTest(key=key, invalid=invalid), self.assertRaises(TrialError):
                ledger = copy.deepcopy(base)
                ledger["cases"][0][key] = invalid
                assess_trials(ledger, self.packet)

    def test_unqualified_mixed_ledger_cannot_be_promoted_by_real_case(self):
        ledger = declared_real_sample(self.packet)
        fixture = copy.deepcopy(ledger["cases"][0])
        fixture["id"] = "CASE-002"
        fixture["evidence_kind"] = "synthetic_fixture"
        ledger["cases"].append(fixture)
        report = assess_trials(ledger, self.packet, strict=False)
        self.assertEqual(report["real_recipient_trials"], 1)
        self.assertEqual(report["unqualified_trial_ids"], ["CASE-002"])
        self.assertFalse(report["release_gate_pass"])

    def test_unknown_profile_still_rejected(self):
        ledger = sample(self.packet)
        ledger["profile"] = "unrecognized"
        with self.assertRaisesRegex(TrialError, "Unknown profile"):
            assess_trials(ledger, self.packet)

    def test_wrong_packet_bytes_are_rejected(self):
        with self.assertRaisesRegex(TrialError, "exact evaluated packet"):
            assess_trials(sample(self.packet), b"changed packet")

    def test_unknown_or_failed_trials_block_release(self):
        with self.assertRaisesRegex(TrialError, "release gate failed"):
            assess_trials(sample(self.packet, "unknown"), self.packet)
        report = assess_trials(sample(self.packet, "unknown"), self.packet, strict=False)
        self.assertFalse(report["release_gate_pass"])

    def test_no_success_claim_without_ingestion_and_host_verification(self):
        ledger = sample(self.packet)
        ledger["cases"][0]["host_outcome_verified"] = False
        with self.assertRaisesRegex(TrialError, "Cannot claim pass"):
            assess_trials(ledger, self.packet)

    def test_duplicate_ids_rejected(self):
        ledger = sample(self.packet)
        ledger["cases"].append(copy.deepcopy(ledger["cases"][0]))
        with self.assertRaisesRegex(TrialError, "Duplicate trial"):
            assess_trials(ledger, self.packet)

    def test_high_risk_failure_rejected_even_when_unverified_allowed(self):
        ledger = sample(self.packet, "fail")
        report = assess_trials(ledger, self.packet, strict=False)
        self.assertEqual(report["critical_failures"], ["CASE-001"])
        self.assertFalse(report["release_gate_pass"])


if __name__ == "__main__":
    unittest.main()
