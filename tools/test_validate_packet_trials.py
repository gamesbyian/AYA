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


class PacketTrialTests(unittest.TestCase):
    def setUp(self):
        self.packet = b"synthetic packet bytes only"

    def test_structural_pass_is_not_real_model_evidence(self):
        report = assess_trials(sample(self.packet), self.packet)
        self.assertTrue(report["release_gate_pass"])
        self.assertEqual(report["passed"], 1)

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
