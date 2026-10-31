#!/usr/bin/env python3
"""Validate a proposed AYA behavioural compatibility evidence record.

Purely structural release-readiness audit. Never certifies real-world claims,
collects user prompts, follows evidence URLs or contacts receiving AI apps.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from typing import Any

REQUIRED = frozenset({
    "installed_version_identity",
    "source_backed_scope",
    "explicit_user_initiation",
    "editable_review",
    "cancel_without_share",
    "manual_copy_fallback",
    "reject_missing_stale_guide",
    "read_only_attachment",
    "provider_neutrality",
    "truthful_return_use",
    "no_answer_monitoring",
    "accessibility_lifecycle",
})
VALID_STATUSES = {"pass", "fail", "unverified", "not_applicable"}
VALID_METHODS = {"instrumentation", "manual-device", "source-audit", "unverified"}


class CompatibilityError(ValueError):
    pass


def nonblank_text(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip() or "\x00" in value:
        raise CompatibilityError(f"{path} must be nonblank text")
    return value


def strict_object(value: Any, allowed: set[str], required: set[str], path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise CompatibilityError(f"{path} must be an object")
    missing = required - value.keys()
    unknown = value.keys() - allowed
    if missing or unknown:
        raise CompatibilityError(
            f"{path}: missing={sorted(missing)} unsupported={sorted(unknown)}"
        )
    return value


def evaluate(manifest: Any) -> dict[str, Any]:
    m = strict_object(manifest, {"schema_version", "implementation", "cases"},
                      {"schema_version", "implementation", "cases"}, "manifest")
    if m["schema_version"] != "aya-compatibility/v1":
        raise CompatibilityError("Unsupported compatibility schema revision")
    impl = strict_object(
        m["implementation"],
        {"app_id", "app_version", "implementation_kind", "platform", "reviewer", "tested_at_utc"},
        {"app_id", "app_version", "implementation_kind", "platform", "reviewer", "tested_at_utc"},
        "implementation",
    )
    for field in ("app_id", "app_version", "reviewer", "tested_at_utc"):
        nonblank_text(impl[field], f"implementation.{field}")
    if impl["implementation_kind"] not in ("aya-sdk", "self-implemented"):
        raise CompatibilityError("Unknown implementation kind")
    if impl["platform"] != "android":
        raise CompatibilityError("AYA compatibility/v1 covers Android only")
    try:
        stamp = dt.datetime.fromisoformat(impl["tested_at_utc"].replace("Z", "+00:00"))
        if stamp.tzinfo is None or stamp.utcoffset() is None:
            raise ValueError("A timezone-aware timestamp is required")
    except ValueError as exc:
        raise CompatibilityError("tested_at_utc must be an offset-aware ISO timestamp") from exc
    entries = m["cases"]
    if not isinstance(entries, list) or len(entries) != len(REQUIRED):
        raise CompatibilityError("Exactly one entry is required for each of the 12 cases")

    seen: set[str] = set()
    incomplete: list[str] = []
    for case in entries:
        row = strict_object(case, {"id", "status", "test_method", "notes", "evidence_refs"},
                            {"id", "status", "test_method", "notes"}, "case")
        case_id = nonblank_text(row["id"], "case.id")
        if case_id not in REQUIRED or case_id in seen:
            raise CompatibilityError(f"Unknown or duplicate case ID: {case_id}")
        seen.add(case_id)
        status, method = row["status"], row["test_method"]
        if status not in VALID_STATUSES or method not in VALID_METHODS:
            raise CompatibilityError(f"Invalid status/test method for {case_id}")
        notes = row["notes"]
        if not isinstance(notes, str):
            raise CompatibilityError(f"notes must be text for {case_id}")
        refs = row.get("evidence_refs", [])
        if not isinstance(refs, list) or any(
            not isinstance(r, str) or not r.strip() for r in refs
        ):
            raise CompatibilityError(f"evidence_refs must be nonblank strings for {case_id}")
        if status == "not_applicable":
            if case_id != "read_only_attachment":
                raise CompatibilityError("Only file-specific read-only attachment checks can be N/A")
            if method == "unverified" or len(notes.strip()) < 20 or not refs:
                raise CompatibilityError("N/A requires reviewed proof of a text-only transport")
        if status == "pass" and (
            method == "unverified" or len(notes.strip()) < 20 or not refs
        ):
            raise CompatibilityError(f"Pass requires real method, explanatory notes and evidence: {case_id}")
        if status in ("fail", "unverified") or (
            status == "pass" and not refs
        ):
            incomplete.append(case_id)
    if seen != REQUIRED:
        raise CompatibilityError("Missing compatibility cases: " + repr(sorted(REQUIRED - seen)))
    return {
        "status": "incomplete" if incomplete else "ready_for_independent_review",
        "app_id": impl["app_id"],
        "app_version": impl["app_version"],
        "implementation_kind": impl["implementation_kind"],
        "incomplete_cases": sorted(incomplete),
        "scope_note": "Structural self-reported record only; no certification or recipient proof.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--allow-incomplete", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = evaluate(json.loads(args.manifest.read_text(encoding="utf-8")))
    except (OSError, ValueError, UnicodeError) as exc:
        print(f"AYA compatibility record refused: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0 if result["status"] != "incomplete" or args.allow_incomplete else 1


if __name__ == "__main__":
    raise SystemExit(main())
