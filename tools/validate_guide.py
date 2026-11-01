#!/usr/bin/env python3
"""Offline AYA-RAS v1 structural linter (stdlib only). No sensitive data uploaded.

Checks structure, basic version metadata, unresolved placeholders and obvious
secret-shaped assignments. This is a necessary gate, not behavioral verification.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

REQUIRED_META = (
    "schema_version", "app_id", "app_name", "app_version_min",
    "app_version_max", "platform", "locale", "guide_revision",
    "source_revision", "last_verified_utc", "owner"
)
REQUIRED_SECTIONS = (
    "Scope and version", "Quick orientation", "Navigation map",
    "Task recipes", "Features and settings", "Troubleshooting",
    "Limitations and unsupported behavior", "Privacy and data handling",
    "Glossary and synonyms", "Evidence and provenance",
    "Unknowns and escalation", "Assistant answer policy"
)
STATUSES = ("AVAILABLE", "CONDITIONAL", "EXPERIMENTAL", "PLANNED", "REMOVED", "UNKNOWN", "UNSUPPORTED")
SECRET_ASSIGNMENT = re.compile(
    r"(?im)^\s*(?:api[_ -]?key|password|secret|access[_ -]?token|private[_ -]?key)"
    r"\s*[:=]\s*(?!<|redacted|not applicable|none|n/a)(\S.{5,})$"
)
PLACEHOLDER = re.compile(r"<[A-Za-z][^>\n]{2,80}>")
HEADER = re.compile(r"(?m)^## (.+?)\s*$")
META_LINE = re.compile(r"^([a-z][a-z0-9_]*):\s*(.*?)\s*$")


def validate(text: str) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    if text.startswith("\ufeff"):
        errors.append("UTF-8 BOM is not permitted.")
        text = text.lstrip("\ufeff")
    lines = text.splitlines()
    fields: dict[str, str] = {}
    if not lines or lines[0].strip() != "---":
        errors.append("Missing opening YAML-like metadata delimiter '---' on first line.")
        body = text
    else:
        try:
            end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
            for line in lines[1:end]:
                if not line.strip():
                    continue
                match = META_LINE.fullmatch(line)
                if not match:
                    errors.append(f"Invalid metadata entry: {line[:100]}")
                    continue
                key, value = match.groups()
                if key in fields:
                    errors.append(f"Duplicate metadata key: {key}")
                fields[key] = value.strip().strip('"').strip("'")
            body = "\n".join(lines[end + 1:])
        except StopIteration:
            errors.append("Missing closing metadata delimiter '---'.")
            body = text

    for key in REQUIRED_META:
        if not fields.get(key):
            errors.append(f"Missing metadata: {key}")
    if fields.get("schema_version") != "aya-reference/v1":
        errors.append("schema_version must be aya-reference/v1.")
    if fields.get("platform", "").lower() != "android":
        errors.append("platform must be android for the current AYA Android library.")
    if fields.get("app_id") and not re.fullmatch(r"[a-zA-Z_][\w]*(\.[a-zA-Z_][\w]*)+", fields["app_id"]):
        errors.append("app_id must be a dotted Android package identifier.")
    if fields.get("app_version_min") and fields.get("app_version_max"):
        if fields["app_version_min"] != fields["app_version_max"]:
            warnings.append("Version range spans multiple releases; verify that every instruction applies to the whole range.")
    if fields.get("last_verified_utc"):
        try:
            stamp = dt.datetime.fromisoformat(fields["last_verified_utc"].replace("Z", "+00:00"))
            if stamp.tzinfo is None or stamp.utcoffset() != dt.timedelta(0):
                raise ValueError("not UTC")
            if stamp > dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=1):
                errors.append("last_verified_utc cannot be in the future.")
        except ValueError:
            errors.append("last_verified_utc must be ISO 8601 with UTC timezone.")
    headers = HEADER.findall(body)
    for section in REQUIRED_SECTIONS:
        if headers.count(section) != 1:
            errors.append(f"Expected exactly one '## {section}' heading; found {headers.count(section)}.")
    if headers != list(REQUIRED_SECTIONS):
        errors.append("Major reference sections must be the twelve expected headings in order.")
    matches = list(HEADER.finditer(body))
    for index, heading in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        content = body[heading.end():end]
        if not any(line.strip() and not line.lstrip().startswith("#")
                   for line in content.splitlines()):
            errors.append(f"Section has no substantive content: {heading.group(1)}.")
    if not re.search(r"(?m)^# [^#\n]+", body):
        errors.append("Missing descriptive document title '# ...'.")
    if PLACEHOLDER.search(body) or any(PLACEHOLDER.search(v) for v in fields.values()):
        errors.append("Unresolved <placeholder> found. Complete the guide before shipping.")
    if SECRET_ASSIGNMENT.search(text):
        errors.append("Possible credential assignment found; replace with safe synthetic text.")
    if not re.search(r"(?m)^### TASK-[0-9]{3,}\b", body):
        warnings.append("No TASK-### procedure found; confirm this is appropriate.")
    if not re.search(r"(?m)^### F-[0-9]{3,}\b", body):
        warnings.append("No F-### feature entry found; confirm this is appropriate.")
    if not re.search(r"(?m)^### ERR-[0-9]{3,}\b", body):
        warnings.append("No ERR-### troubleshooting entry found; confirm this is appropriate.")
    if not any(f"[{status}]" in body for status in STATUSES):
        warnings.append("No explicit feature status labels found.")
    if len(body.strip()) < 1200:
        warnings.append("Guide is very short; a full product likely needs much more operational coverage.")
    return {"ok": not errors, "metadata": fields, "errors": errors, "warnings": warnings,
            "sections_found": len(set(headers).intersection(REQUIRED_SECTIONS))}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("guide", type=Path, help="UTF-8 Markdown guide to verify")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable report")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures")
    args = parser.parse_args(argv)
    try:
        result = validate(args.guide.read_text(encoding="utf-8"))
    except (OSError, UnicodeError) as exc:
        print(f"Cannot read guide: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"{args.guide}: {'PASS' if result['ok'] else 'FAIL'} "
              f"({result['sections_found']}/{len(REQUIRED_SECTIONS)} sections)")
        for issue in result["errors"]:
            print(f"  ERROR: {issue}")
        for issue in result["warnings"]:
            print(f"  WARN:  {issue}")
    return 1 if (not result["ok"] or (args.strict and result["warnings"])) else 0


if __name__ == "__main__":
    raise SystemExit(main())
