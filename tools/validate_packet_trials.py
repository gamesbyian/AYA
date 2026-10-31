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

PROFILES = {"help", "creative", "structured", "translation"}
VERDICTS = {"pass", "fail", "unknown"}
SEVERITIES = {"P0", "P1", "P2", "P3"}


class TrialError(ValueError):
    pass


def require_string(data, key, context):
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise TrialError(f"{context}: missing nonempty {key}")
    return value


def assess_trials(ledger: dict, packet: bytes, strict: bool = True) -> dict:
    if ledger.get("schema_version") != "aya-packet-trials/v1":
        raise TrialError("Unsupported trial ledger version")
    digest = hashlib.sha256(packet).hexdigest()
    if ledger.get("packet_sha256") != digest:
        raise TrialError("Ledger must refer to the exact evaluated packet bytes")
    profile = ledger.get("profile")
    if profile not in PROFILES:
        raise TrialError("Unknown profile")
    require_string(ledger, "host_app_version", "ledger")
    cases = ledger.get("cases")
    if not isinstance(cases, list) or not cases:
        raise TrialError("Trial ledger has no cases")
    counts = {key: 0 for key in VERDICTS}
    seen = set()
    ingested = 0
    high_risk_failures = []
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
        if case.get("verdict") not in VERDICTS or case.get("severity") not in SEVERITIES:
            raise TrialError("Invalid verdict or severity: " + identifier)
        if not isinstance(case.get("forbidden_claims"), list) or not all(
                isinstance(x, str) for x in case["forbidden_claims"]):
            raise TrialError("Missing forbidden-claims list: " + identifier)
        if case.get("verdict") == "pass" and (
                not case["attachment_ingested"] or not case["host_outcome_verified"]):
            raise TrialError("Cannot claim pass without ingestion and independently checked outcome: " +
                             identifier)
        if case["attachment_ingested"]:
            ingested += 1
        counts[case["verdict"]] += 1
        if case["verdict"] == "fail" and case["severity"] in {"P0", "P1"}:
            high_risk_failures.append(identifier)
    release_ready = not high_risk_failures and counts["fail"] == 0 and counts["unknown"] == 0
    report = {
        "packet_sha256": digest, "profile": profile,
        "cases": len(cases), "attachments_confirmed_ingested": ingested,
        "passed": counts["pass"], "failed": counts["fail"],
        "unknown": counts["unknown"], "critical_failures": high_risk_failures,
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
