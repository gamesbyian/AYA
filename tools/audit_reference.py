#!/usr/bin/env python3
"""Offline AYA cross-check: independent product inventory ↔ guide ↔ gold questions.

Only validates internally declared structure and consistency. It cannot prove
that inventory discovery was exhaustive, source references genuine, or that an
AI assistant can answer the questions. Never sends documents over the network.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from validate_guide import validate

IDS = re.compile(r"^(TASK|F|ERR)-[0-9]{3,}$")
HEADING = re.compile(r"(?m)^###\s+((?:TASK|F|ERR)-[0-9]{3,}):\s*(.+?)\s*$")
LABEL = re.compile(r"\[(AVAILABLE|CONDITIONAL|EXPERIMENTAL|PLANNED|REMOVED|UNKNOWN|UNSUPPORTED)\]")
ALLOWED_STATUSES = {"AVAILABLE", "CONDITIONAL", "EXPERIMENTAL", "PLANNED", "REMOVED", "UNKNOWN", "UNSUPPORTED"}
ALLOWED_KIND = {"TASK": "task", "F": "feature", "ERR": "error"}
RISK = {"low", "medium", "high"}
SUPPORT = {"answerable", "conditional", "unsupported", "unknown"}


def reference_entries(guide: str) -> tuple[dict[str, dict[str, str]], list[str]]:
    """Extract labeled entries, detect duplicate IDs, preserve body for evidence checks."""
    hits = list(HEADING.finditer(guide))
    entries: dict[str, dict[str, str]] = {}
    errors: list[str] = []
    for index, match in enumerate(hits):
        identifier, heading = match.groups()
        if identifier in entries:
            errors.append(f"Duplicate guide ID: {identifier}")
        block = guide[match.end(): hits[index + 1].start() if index + 1 < len(hits) else len(guide)]
        status = LABEL.search(heading)
        entries[identifier] = {
            "status": status.group(1) if status else "",
            "heading": heading.strip(),
            "body": block,
        }
    return entries, errors


def audit(guide: str, inventory: dict[str, Any], questions: dict[str, Any] | None = None) -> dict[str, Any]:
    report = validate(guide)
    errors: list[str] = list(report["errors"])
    warnings: list[str] = list(report["warnings"])
    entries, entry_errors = reference_entries(guide)
    errors.extend(entry_errors)

    if inventory.get("schema_version") != "aya-inventory/v1":
        errors.append("Inventory schema_version must be aya-inventory/v1.")
    metadata = report["metadata"]
    for guide_field, inventory_field in (("app_id", "app_id"), ("source_revision", "source_revision")):
        if metadata.get(guide_field) != inventory.get(inventory_field):
            errors.append(f"Guide/inventory {guide_field} mismatch.")
    version = str(inventory.get("app_version", ""))
    # Exact-revision guarantee. Ranges are allowed only with independent version verification.
    if version and metadata.get("app_version_min") == metadata.get("app_version_max"):
        if version != metadata.get("app_version_min"):
            errors.append("Inventory app_version does not match guide's exact version.")
    items = inventory.get("items")
    if not isinstance(items, list) or not items:
        errors.append("Inventory must contain a nonempty items array.")
        items = []
    ids: set[str] = set()
    reviewed: int = 0
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append(f"Inventory item {index} must be an object.")
            continue
        identifier = item.get("id")
        if not isinstance(identifier, str) or not IDS.fullmatch(identifier):
            errors.append(f"Invalid inventory ID at item {index}: {identifier!r}")
            continue
        if identifier in ids:
            errors.append(f"Duplicate inventory ID: {identifier}")
        ids.add(identifier)
        expected_kind = ALLOWED_KIND[identifier.split("-")[0]]
        if item.get("kind") != expected_kind:
            errors.append(f"{identifier}: kind must be {expected_kind}.")
        if item.get("status") not in ALLOWED_STATUSES:
            errors.append(f"{identifier}: invalid or missing status.")
        if item.get("criticality") not in RISK:
            errors.append(f"{identifier}: criticality must be low/medium/high.")
        for field in ("title", "source_ref"):
            if not isinstance(item.get(field), str) or not item[field].strip():
                errors.append(f"{identifier}: missing {field}.")
        if identifier not in entries:
            errors.append(f"Inventory item {identifier} has no guide entry.")
            continue
        reviewed += 1
        entry = entries[identifier]
        if expected_kind != "error" and entry["status"] != item.get("status"):
            errors.append(f"{identifier}: guide status {entry['status'] or '(missing)'} != inventory {item.get('status')}.")
        if not re.search(r"(?im)^\s*[-*]\s*Evidence\s*:", entry["body"]):
            errors.append(f"{identifier}: guide entry missing '- Evidence:' line.")
        if expected_kind == "task":
            if not re.search(r"(?m)^\s*1\.\s+\S", entry["body"]):
                errors.append(f"{identifier}: task lacks a numbered step starting at 1.")
            for field in ("Start", "Expect"):
                if not re.search(rf"(?im)^\s*[-*]\s*{field}\s*:", entry["body"]):
                    errors.append(f"{identifier}: task lacks '- {field}:' field.")

    for identifier in sorted(entries.keys() - ids):
        warnings.append(f"Guide entry {identifier} is not independently inventoried.")

    q_count = 0
    if questions is not None:
        if questions.get("schema_version") != "aya-questions/v1":
            errors.append("Question schema_version must be aya-questions/v1.")
        if questions.get("app_id") != inventory.get("app_id"):
            errors.append("Question set/inventory app_id mismatch.")
        if str(questions.get("guide_revision")) != str(metadata.get("guide_revision")):
            errors.append("Question set/guide revision mismatch.")
        cases = questions.get("cases")
        if not isinstance(cases, list) or not cases:
            errors.append("Question set must contain nonempty cases array.")
            cases = []
        question_ids: set[str] = set()
        for index, case in enumerate(cases):
            if not isinstance(case, dict):
                errors.append(f"Question case {index} must be an object.")
                continue
            q_id = case.get("id")
            if not isinstance(q_id, str) or not re.fullmatch(r"Q-[0-9]{3,}", q_id):
                errors.append(f"Invalid question case ID at {index}.")
                continue
            if q_id in question_ids:
                errors.append(f"Duplicate question case ID: {q_id}")
            question_ids.add(q_id)
            if not isinstance(case.get("question"), str) or not case["question"].strip():
                errors.append(f"{q_id}: missing question.")
            if case.get("support_status") not in SUPPORT:
                errors.append(f"{q_id}: invalid support_status.")
            if case.get("risk") not in RISK:
                errors.append(f"{q_id}: invalid risk.")
            if not isinstance(case.get("expected_behavior"), str) or not case["expected_behavior"].strip():
                errors.append(f"{q_id}: missing expected_behavior.")
            links = case.get("evidence_ids")
            if not isinstance(links, list) or not links:
                errors.append(f"{q_id}: must cite one or more evidence_ids.")
            else:
                for link in links:
                    if link not in ids or link not in entries:
                        errors.append(f"{q_id}: evidence reference {link!r} missing from inventory or guide.")
            if not isinstance(case.get("forbidden_claims"), list):
                errors.append(f"{q_id}: forbidden_claims must be a list (can be empty).")
        q_count = len(cases)

    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "inventory_items": len(ids),
        "guide_entries": len(entries),
        "inventory_entries_covered": reviewed,
        "question_cases": q_count,
        "coverage_ratio": round(reviewed / len(ids), 4) if ids else 0,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("guide", type=Path)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--questions", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failure.")
    args = parser.parse_args(argv)
    try:
        guide = args.guide.read_text(encoding="utf-8")
        inventory = json.loads(args.inventory.read_text(encoding="utf-8"))
        questions = json.loads(args.questions.read_text(encoding="utf-8")) if args.questions else None
        if not isinstance(inventory, dict) or (questions is not None and not isinstance(questions, dict)):
            raise ValueError("Inventory and question files must be JSON objects.")
        result = audit(guide, inventory, questions)
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"Cannot audit reference: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"{'PASS' if result['ok'] else 'FAIL'}: {args.guide} "
              f"inventory={result['inventory_entries_covered']}/{result['inventory_items']}, "
              f"guide entries={result['guide_entries']}, cases={result['question_cases']}")
        for error in result["errors"]:
            print(f"  ERROR: {error}")
        for warning in result["warnings"]:
            print(f"  WARN: {warning}")
    return int(not result["ok"] or (args.strict and bool(result["warnings"])))


if __name__ == "__main__":
    raise SystemExit(main())
