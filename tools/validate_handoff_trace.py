#!/usr/bin/env python3
"""Offline checker for SDK-independent AYA handoff lifecycle event traces.

Inputs contain event NAMES only, never question text, guide bodies, URI,
recipient identifiers or agent replies. Passing means only that the supplied
developer trace has the correct local order and negative-case structure.
This cannot establish that an Android app actually emitted those events.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SCHEMA = "aya-interaction-trace/v1"
SCENARIOS = (
    "review_share",
    "review_copy",
    "cancel",
    "version_mismatch",
    "no_receiver",
    "no_activity",
)
EVENTS = frozenset((
    "reference_validated", "reference_rejected", "question_opened",
    "review_opened", "review_edited", "review_approved",
    "review_cancelled", "copy_requested", "copy_succeeded",
    "share_requested", "chooser_opened", "share_unavailable",
    "activity_detached", "local_rejected",
))
APP_ID = re.compile(r"^[A-Za-z][A-Za-z0-9_]*(?:\.[A-Za-z][A-Za-z0-9_]*)+$")
VERSION = re.compile(r"^[0-9A-Za-z][0-9A-Za-z._+-]{0,63}$")
MAX_BYTES = 32 * 1024


class TraceValidationError(ValueError):
    pass


def _keys(obj: object, expected: set[str], context: str) -> dict:
    if not isinstance(obj, dict) or set(obj) != expected:
        raise TraceValidationError(context + " fields must be exactly " +
                                   ", ".join(sorted(expected)))
    return obj


def _after(events: list[str], earlier: str, later: str) -> bool:
    return earlier in events and later in events and events.index(earlier) < events.index(later)


def _ordered(events: list[str], required: tuple[str, ...], label: str) -> None:
    positions = []
    for event in required:
        if event not in events:
            raise TraceValidationError(label + " missing event: " + event)
        positions.append(events.index(event))
    if positions != sorted(positions) or len(set(positions)) != len(positions):
        raise TraceValidationError(label + " events are not in required order")


def check_case(scenario: str, events: list[str]) -> None:
    if not isinstance(events, list) or not events or len(events) > 24 or any(
        not isinstance(e, str) or e not in EVENTS for e in events
    ):
        raise TraceValidationError(scenario + " has invalid or excessive event names")
    if any(events.count(e) > 1 for e in EVENTS if e != "review_edited"):
        raise TraceValidationError(scenario + " contains duplicate terminal/state events")

    if scenario in ("review_share", "review_copy", "cancel", "no_receiver"):
        _ordered(events, ("reference_validated", "review_opened"), scenario)
        if "reference_rejected" in events or "activity_detached" in events:
            raise TraceValidationError(scenario + " cannot claim a validated active review after refusal")

    for event in ("share_requested", "copy_requested"):
        if event in events and not _after(events, "review_approved", event):
            raise TraceValidationError(scenario + " dispatched or copied without approval")
    if "chooser_opened" in events and not _after(events, "share_requested", "chooser_opened"):
        raise TraceValidationError(scenario + " claimed chooser before share request")
    if "copy_succeeded" in events and not _after(events, "copy_requested", "copy_succeeded"):
        raise TraceValidationError(scenario + " claimed copy before explicit request")
    if "share_unavailable" in events and not _after(events, "share_requested", "share_unavailable"):
        raise TraceValidationError(scenario + " claimed share failure before request")
    if "review_edited" in events:
        _ordered(events, ("review_opened", "review_edited"), scenario)
        if "review_approved" in events and events.index("review_edited") > events.index("review_approved"):
            raise TraceValidationError(scenario + " edit after approval")
    if "review_cancelled" in events and any(
        e in events for e in ("review_approved", "share_requested", "copy_requested",
                             "chooser_opened", "copy_succeeded")
    ):
        raise TraceValidationError(scenario + " performed an action after cancellation")

    required = {
        "review_share": ("reference_validated", "review_opened", "review_approved",
                         "share_requested", "chooser_opened"),
        "review_copy": ("reference_validated", "review_opened", "review_approved",
                        "copy_requested", "copy_succeeded"),
        "cancel": ("reference_validated", "review_opened", "review_cancelled"),
        "version_mismatch": ("reference_rejected", "local_rejected"),
        "no_receiver": ("reference_validated", "review_opened", "review_approved",
                        "share_requested", "share_unavailable",
                        "copy_requested", "copy_succeeded"),
        "no_activity": ("activity_detached", "local_rejected"),
    }[scenario]
    _ordered(events, required, scenario)
    allowed = {
        "review_share": {"reference_validated", "question_opened", "review_opened",
                         "review_edited", "review_approved", "share_requested", "chooser_opened"},
        "review_copy": {"reference_validated", "question_opened", "review_opened",
                        "review_edited", "review_approved", "copy_requested", "copy_succeeded"},
        "cancel": {"reference_validated", "question_opened", "review_opened",
                   "review_edited", "review_cancelled"},
        "version_mismatch": {"reference_rejected", "local_rejected"},
        "no_receiver": {"reference_validated", "question_opened", "review_opened",
                        "review_edited", "review_approved", "share_requested",
                        "share_unavailable", "copy_requested", "copy_succeeded"},
        "no_activity": {"activity_detached", "local_rejected"},
    }[scenario]
    unknown_for_case = set(events) - allowed
    if unknown_for_case:
        raise TraceValidationError(scenario + " has contradictory events: " +
                                   ", ".join(sorted(unknown_for_case)))


def validate(data: object) -> tuple[str, str]:
    root = _keys(data, {"schema", "host", "cases"}, "Root")
    if root["schema"] != SCHEMA:
        raise TraceValidationError("Unsupported trace schema")
    host = _keys(root["host"], {"app_id", "app_version", "source_revision", "platform"}, "Host")
    if not isinstance(host["app_id"], str) or not APP_ID.fullmatch(host["app_id"]):
        raise TraceValidationError("Invalid host application ID")
    if not isinstance(host["app_version"], str) or not VERSION.fullmatch(host["app_version"]):
        raise TraceValidationError("Invalid host version")
    if not isinstance(host["source_revision"], str) or not re.fullmatch(
        r"[A-Za-z0-9_.-]{1,100}", host["source_revision"]
    ):
        raise TraceValidationError("Invalid source revision")
    if host["platform"] != "android":
        raise TraceValidationError("This handoff conformance trace is Android-only")
    cases = root["cases"]
    if not isinstance(cases, list) or len(cases) != len(SCENARIOS):
        raise TraceValidationError("Trace must include each of six scenarios exactly once")
    seen = set()
    for raw in cases:
        case = _keys(raw, {"scenario", "events"}, "Case")
        scenario = case["scenario"]
        if not isinstance(scenario, str) or scenario not in SCENARIOS or scenario in seen:
            raise TraceValidationError("Duplicate or unknown scenario")
        seen.add(scenario)
        check_case(scenario, case["events"])
    if seen != set(SCENARIOS):
        raise TraceValidationError("Missing required negative/positive scenarios")
    return host["app_id"], host["app_version"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trace", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.trace.stat().st_size > MAX_BYTES:
            raise TraceValidationError("Trace file exceeds metadata-only size limit")
        data = json.loads(args.trace.read_text(encoding="utf-8"))
        app, version = validate(data)
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        print("AYA interaction trace: FAIL: " + str(exc), file=sys.stderr)
        return 1
    print(f"AYA interaction trace: PASS: supplied event sequence structure for {app}@{version}")
    print("Scope: offline developer-supplied trace consistency only. No device, recipient, "
          "source truth, instrumentation or independent AYA certification established.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
