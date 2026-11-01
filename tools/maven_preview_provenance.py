#!/usr/bin/env python3
"""Create self-describing, *unsigned* evidence for a validated Maven preview.

This records source/run identity and independently computed artifact digests;
it is not a cryptographic provenance attestation or stable public distribution.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from validate_staged_maven import check

SCHEMA = "aya-maven-preview-evidence/v1"
SHA = re.compile(r"^[a-fA-F0-9]{40,64}$")
REPOSITORY = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
RUN_ID = re.compile(r"^[1-9][0-9]*$")


class ProvenanceError(ValueError):
    pass


def build_manifest(
    root: Path, version: str, source_sha: str, checksums: Path,
    *, repository: str = "", run_id: str = "", attempt: str = "",
    java: str = "", gradle: str = ""
) -> dict:
    if not SHA.fullmatch(source_sha):
        raise ProvenanceError("A complete source commit SHA is required")
    digests = check(root, version)
    canonical = "".join(f"{digest}  {name}\n" for name, digest in sorted(digests.items()))
    if not checksums.is_file() or checksums.is_symlink():
        raise ProvenanceError("Missing or linked staged checksum manifest")
    if checksums.read_text(encoding="utf-8") != canonical:
        raise ProvenanceError("Checksum manifest differs from verified AAR/POM bytes")
    for label, value in (("Java", java), ("Gradle", gradle)):
        if not isinstance(value, str) or not value or len(value) > 160 or any(
            ord(char) < 32 or ord(char) == 127 for char in value
        ):
            raise ProvenanceError("Missing or unsafe " + label + " toolchain identity")
    if (repository and not REPOSITORY.fullmatch(repository)) or (
        run_id and not RUN_ID.fullmatch(run_id)
    ) or (attempt and not RUN_ID.fullmatch(attempt)):
        raise ProvenanceError("Malformed repository or workflow run identity")
    run_url = (
        f"https://github.com/{repository}/actions/runs/{run_id}"
        if repository and run_id else None
    )
    return {
        "schema": SCHEMA,
        "evidence_type": "unsigned_local_build_metadata",
        "source_commit": source_sha.lower(),
        "repository": repository or None,
        "workflow_run_url": run_url,
        "workflow_run_attempt": int(attempt) if attempt else None,
        "version": version,
        "coordinates": [f"dev.aya:aya-android:{version}",
                        f"dev.aya:aya-compose:{version}"],
        "java": java,
        "gradle": gradle,
        "android_compile_sdk": 35,
        "artifacts_sha256": dict(sorted(digests.items())),
        "checksums_filename": checksums.name,
        "validation": {
            "source": "tools/validate_staged_maven.py",
            "scope": "POM coordinates, matching dependencies and compiled AAR contents",
            "tests_on_device": False,
            "public_repository_upload": False,
            "signed_attestation": False
        },
        "limitations": (
            "Source SHA and toolchain values come from the producing workflow. "
            "This JSON is self-reported build metadata, not a signed attestation "
            "or proof of independent reproducibility or recipient ingestion."
        ),
    }


def write_manifest(destination: Path, result: dict) -> None:
    if destination.is_symlink():
        raise ProvenanceError("Refusing symlinked provenance destination")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n",
                           encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--checksums", type=Path, required=True)
    parser.add_argument("--source-sha", required=True)
    parser.add_argument("--repository", default="")
    parser.add_argument("--run-id", default="")
    parser.add_argument("--attempt", default="")
    parser.add_argument("--java", required=True)
    parser.add_argument("--gradle", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = build_manifest(
            args.root, args.version, args.source_sha, args.checksums,
            repository=args.repository, run_id=args.run_id, attempt=args.attempt,
            java=args.java, gradle=args.gradle
        )
        write_manifest(args.output, result)
    except (OSError, ValueError) as exc:
        print(f"AYA Maven preview evidence: FAIL: {exc}", file=sys.stderr)
        return 2
    print(f"AYA Maven preview evidence: PASS: {args.output}")
    print("Scope: unsigned local preview; no public publication or device acceptance")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
