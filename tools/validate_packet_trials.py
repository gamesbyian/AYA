#!/usr/bin/env python3
"""Validate independent, controlled assistant trials for an exact AYA packet.

No provider API, live-account access, synthetic "AI scoring", or production
conversation monitoring. Reviewers establish truth against the actual host.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
from pathlib import Path

PROFILES = {"help", "creative", "structured", "translation", "filesystem"}
VERDICTS = {"pass", "fail", "unknown"}
SEVERITIES = {"P0", "P1", "P2", "P3"}
LEDGER_V1 = "aya-packet-trials/v1"
LEDGER_V2 = "aya-packet-trials/v2"
EVIDENCE_KINDS = {"real_recipient", "synthetic_fixture", "documentation_only"}
TRANSPORTS = {
    "text_only", "text_and_txt_reference", "txt_reference_only",
    "image_attachment", "multiple_attachments", "process_text"
}
ATTACHMENT_TRANSPORTS = TRANSPORTS - {"text_only", "process_text"}
ANDROID_PACKAGE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+")
SHA256 = re.compile(r"[a-fA-F0-9]{64}")


class TrialError(ValueError):
    pass


def require_string(data, key, context):
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise TrialError(f"{context}: missing nonempty {key}")
    return value


def assess_trials(ledger: dict, packet: bytes, strict: bool = True) -> dict:
    version = ledger.get("schema_version")
    if version not in (LEDGER_V1, LEDGER_V2):
        raise TrialError("Unsupported trial ledger version")
    is_v2 = version == LEDGER_V2
    digest = hashlib.sha256(packet).hexdigest()
    if ledger.get("packet_sha256") != digest:
        raise TrialError("Ledger must refer to the exact evaluated packet bytes")
    profile = ledger.get("profile")
    if not isinstance(profile, str) or profile not in PROFILES:
        raise TrialError("Unknown profile")
    require_string(ledger, "host_app_version", "ledger")
    cases = ledger.get("cases")
    if not isinstance(cases, list) or not cases:
        raise TrialError("Trial ledger has no cases")
    counts = {key: 0 for key in VERDICTS}
    seen = set()
    ingested = 0
    high_risk_failures = []
    real_recipient_trials = 0
    unqualified_cases = []
    for case in cases:
        if not isinstance(case, dict):
            raise TrialError("Trial case must be object")
        identifier = require_string(case, "id", "case")
        if identifier in seen:
            raise TrialError("Duplicate trial ID: " + identifier)
        seen.add(identifier)
        for key in ("user_goal", "expected_result", "recipient", "recipient_version",
                    "android_version", "tested_at_utc", "reviewer", "evidence_ref"):
            require_string(case, key, identifier)
        try:
            timestamp = dt.datetime.fromisoformat(case["tested_at_utc"].replace("Z", "+00:00"))
            if timestamp.utcoffset() != dt.timedelta(0):
                raise ValueError("not UTC")
        except ValueError as exc:
            raise TrialError("Test timestamp must be UTC: " + identifier) from exc
        if type(case.get("attachment_ingested")) is not bool:
            raise TrialError("Actual attachment ingestion must be recorded: " + identifier)
        if type(case.get("host_outcome_verified")) is not bool:
            raise TrialError("Host outcome validation must be recorded: " + identifier)
        if (not isinstance(case.get("verdict"), str) or case["verdict"] not in VERDICTS or
                not isinstance(case.get("severity"), str) or case["severity"] not in SEVERITIES):
            raise TrialError("Invalid verdict or severity: " + identifier)
        if not isinstance(case.get("forbidden_claims"), list) or not all(
                isinstance(x, str) for x in case["forbidden_claims"]):
            raise TrialError("Missing forbidden-claims list: " + identifier)
        if is_v2:
            kind = case.get("evidence_kind")
            if not isinstance(kind, str) or kind not in EVIDENCE_KINDS:
                raise TrialError("Invalid or missing trial evidence kind: " + identifier)
            transport = case.get("transport")
            if not isinstance(transport, str) or transport not in TRANSPORTS:
                raise TrialError("Invalid or missing recipient transport: " + identifier)
            if type(case.get("recipient_input_verified")) is not bool:
                raise TrialError("Actual recipient input receipt must be recorded: " + identifier)
            if transport not in ATTACHMENT_TRANSPORTS and case["attachment_ingested"]:
                raise TrialError("Text-only transport cannot claim attachment ingestion: " +
                                 identifier)
            if kind == "real_recipient":
                real_recipient_trials += 1
                pkg = require_string(case, "recipient_package", identifier)
                if not ANDROID_PACKAGE.fullmatch(pkg):
                    raise TrialError("Invalid recipient Android package: " + identifier)
                sdk = case.get("android_api_level")
                if type(sdk) is not int or not 21 <= sdk <= 99:
                    raise TrialError("Invalid Android API level: " + identifier)
                if case.get("device_kind") not in ("physical_android", "android_emulator"):
                    raise TrialError("Missing real-device/emulator classification: " + identifier)
                host_hash = require_string(case, "host_artifact_sha256", identifier)
                if not SHA256.fullmatch(host_hash):
                    raise TrialError("Invalid host artifact SHA-256: " + identifier)
            else:
                unqualified_cases.append(identifier)
            if case["verdict"] == "pass" and (
                    not case["recipient_input_verified"] or
                    not case["host_outcome_verified"] or
                    (transport in ATTACHMENT_TRANSPORTS and not case["attachment_ingested"])):
                raise TrialError("Cannot claim pass without verified recipient input and host outcome: " +
                                 identifier)
        elif case.get("verdict") == "pass" and (
                not case["attachment_ingested"] or not case["host_outcome_verified"]):
            raise TrialError("Cannot claim pass without ingestion and independently checked outcome: " +
                             identifier)
        if case["attachment_ingested"]:
            ingested += 1
        counts[case["verdict"]] += 1
        if case["verdict"] == "fail" and case["severity"] in {"P0", "P1"}:
            high_risk_failures.append(identifier)
    # Legacy v1 records remain readable but cannot establish a release gate:
    # they lack any declared boundary between fixtures and real recipient QA.
    if not is_v2:
        unqualified_cases = [case["id"] for case in cases]
    release_ready = (
        is_v2 and not unqualified_cases and real_recipient_trials > 0 and
        counts["fail"] == 0 and counts["unknown"] == 0
    )
    report = {
        "schema_version": version,
        "packet_sha256": digest, "profile": profile,
        "cases": len(cases), "attachments_confirmed_ingested": ingested,
        "passed": counts["pass"], "failed": counts["fail"],
        "unknown": counts["unknown"], "critical_failures": high_risk_failures,
        "real_recipient_trials": real_recipient_trials,
        "unqualified_trial_ids": unqualified_cases,
        "release_gate_pass": release_ready
    }
    if strict and not release_ready:
        raise TrialError("Packet trial release gate failed: " + json.dumps(report))
    return report


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("ledger", type=Path)
    p.add_argument("--packet", required=True, type=Path)
    p.add_argument("--allow-unverified", action="store_true",
                   help="Report unknown/failed cases without claiming release readiness")
    args = p.parse_args(argv)
    try:
        ledger = json.loads(args.ledger.read_text(encoding="utf-8"))
        report = assess_trials(ledger, args.packet.read_bytes(), not args.allow_unverified)
        print(json.dumps(report, indent=2))
        return 0
    except (OSError, UnicodeError, json.JSONDecodeError, TrialError) as exc:
        p.exit(1, f"AYA packet trial validation failed: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
