#!/usr/bin/env python3
"""Produce a bounded, factual GitHub Actions validation failure index.

The GitHub runner supplies stage outcomes. No log scraping, inferred root
cause, private artifact content or external request is needed.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

SCHEMA = "aya-ci-failure/v1"
STAGE = re.compile(r"^[a-z][a-z0-9_]{0,63}$")
REPO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
SHA = re.compile(r"^[a-fA-F0-9]{40,64}$")
RUN_ID = re.compile(r"^[1-9][0-9]*$")
ALLOWED = {"success", "failure", "cancelled", "skipped"}
MAX_STAGES = 64


class DigestError(ValueError):
    pass


def make_digest(outcomes: dict, environment: dict[str, str] | None = None) -> dict:
    if not isinstance(outcomes, dict) or not outcomes or len(outcomes) > MAX_STAGES:
        raise DigestError("Stage outcomes must be a nonempty bounded JSON object")
    if any(not isinstance(key, str) or not STAGE.fullmatch(key) or
           not isinstance(value, str) or value not in ALLOWED
           for key, value in outcomes.items()):
        raise DigestError("Unknown stage ID or invalid observed outcome")
    env = os.environ if environment is None else environment
    repo = env.get("GITHUB_REPOSITORY", "")
    sha = env.get("GITHUB_SHA", "")
    run = env.get("GITHUB_RUN_ID", "")
    attempt = env.get("GITHUB_RUN_ATTEMPT", "")
    run_url = f"https://github.com/{repo}/actions/runs/{run}" if (
        REPO.fullmatch(repo) and RUN_ID.fullmatch(run)
    ) else None
    stage_records = [{"stage": key, "outcome": value} for key, value in outcomes.items()]
    failures = [item for item in stage_records if item["outcome"] == "failure"]
    interrupted = [item for item in stage_records if item["outcome"] == "cancelled"]
    return {
        "schema": SCHEMA,
        "kind": "observed_runner_step_outcomes",
        "repository": repo if REPO.fullmatch(repo) else None,
        "commit_sha": sha if SHA.fullmatch(sha) else None,
        "workflow": (env.get("GITHUB_WORKFLOW", "") or None),
        "job": (env.get("GITHUB_JOB", "") or None),
        "run_id": int(run) if RUN_ID.fullmatch(run) else None,
        "attempt": int(attempt) if RUN_ID.fullmatch(attempt) else None,
        "run_url": run_url,
        "stages": stage_records,
        "failed_stages": [item["stage"] for item in failures],
        "cancelled_stages": [item["stage"] for item in interrupted],
        "first_observed_failure": failures[0]["stage"] if failures else None,
        "root_error": None,
        "root_error_limit": (
            "Stage outcomes identify where a failure occurred; no log excerpt "
            "or root cause has been independently established."
        ),
        "reproduce_from": ".github/workflows/reference-guide.yml",
        "next_action": (
            "Open the exact failed step in the linked job log and reproduce "
            "its command from the checked-in workflow before diagnosing or retrying."
        ),
    }


def write_digest(output: Path, outcomes: dict, environment: dict[str, str] | None = None) -> dict:
    result = make_digest(outcomes, environment)
    if output.is_symlink():
        raise DigestError("Do not replace symlinked diagnostic output")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outcomes-json", required=True,
                        help="JSON mapping step ID to observed GitHub Actions outcome")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        outcomes = json.loads(args.outcomes_json)
        result = write_digest(args.output, outcomes)
    except (OSError, json.JSONDecodeError, DigestError) as exc:
        print(f"AYA CI failure index: FAIL: {exc}", file=sys.stderr)
        return 1
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        failed = ", ".join(result["failed_stages"]) or "(none observed)"
        with open(summary, "a", encoding="utf-8") as f:
            f.write("### AYA reference check: observed failure stages\n\n")
            f.write(f"Failed: **{failed}**. The first root error remains unverified.\n\n")
            if result["run_url"]:
                f.write(f"[View the exact workflow run]({result['run_url']})\n\n")
            f.write("See the uploaded `aya-ci-failure.json` for stage outcomes and next action.\n")
    print(f"AYA CI failure index: wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
