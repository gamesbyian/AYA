#!/usr/bin/env python3
"""Create a self-verifiable metadata manifest for an unpublished AYA Maven preview.

This is a checksum+source revision inventory, NOT a signed attestation, a
reproducible-build guarantee, or a claim about app/device/AI compatibility.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

CHECKSUM_LINE = re.compile(r"^([0-9a-f]{64})  ([^\r\n]+)$")
COMMIT = re.compile(r"^[0-9a-f]{40}$")
VERSION = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z][0-9A-Za-z.-]*)?$")
ARTIFACTS = ("aya-android", "aya-compose")


class PreviewManifestError(ValueError):
    pass


def create_manifest(root: Path, checksums: Path, version: str, commit: str) -> dict:
    if not VERSION.fullmatch(version) or version.endswith("-SNAPSHOT"):
        raise PreviewManifestError("A fixed non-SNAPSHOT preview version is required")
    if not COMMIT.fullmatch(commit):
        raise PreviewManifestError("Source commit must be an exact lowercase 40-hex Git SHA")
    lines = checksums.read_text(encoding="utf-8").splitlines()
    if not lines:
        raise PreviewManifestError("Missing Maven SHA-256 inventory")
    entries = []
    seen = set()
    for line in lines:
        match = CHECKSUM_LINE.fullmatch(line)
        if match is None:
            raise PreviewManifestError("Invalid checksum entry syntax")
        digest, relative = match.groups()
        parts = relative.split("/")
        if (relative.startswith("/") or chr(92) in relative or
            any(part in ("", ".", "..") for part in parts)):
            raise PreviewManifestError("Unsafe checksum path")
        if relative in seen:
            raise PreviewManifestError("Duplicate checksum path")
        seen.add(relative)
        expected_prefix = f"dev/aya/"
        if not relative.startswith(expected_prefix):
            raise PreviewManifestError("Unexpected artifact namespace")
        path = root.joinpath(*parts)
        cursor = root
        for part in parts:
            cursor = cursor / part
            if cursor.is_symlink():
                raise PreviewManifestError("Maven artifact symlinks are not accepted")
        if not path.is_file():
            raise PreviewManifestError(f"Missing checksummed artifact {relative}")
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != digest:
            raise PreviewManifestError(f"SHA-256 mismatch: {relative}")
        entries.append({
            "path": relative,
            "size_bytes": path.stat().st_size,
            "sha256": actual,
        })
    expected = {
        f"dev/aya/{artifact}/{version}/{artifact}-{version}.{ext}"
        for artifact in ARTIFACTS for ext in ("aar", "pom")
    }
    if seen != expected:
        raise PreviewManifestError(
            "Manifest must cover exactly the validated core and Compose AAR/POM pairs")
    return {
        "schema_version": "aya-maven-preview-manifest/v1",
        "distribution_status": "unpublished-preview",
        "source_commit": commit,
        "maven_version": version,
        "artifacts": sorted(entries, key=lambda item: item["path"]),
        "limitations": [
            "Checksums describe files in this folder, not signed provenance",
            "Build reproducibility and physical-device/recipient behavior are unverified",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", required=True, type=Path)
    p.add_argument("--checksums", required=True, type=Path)
    p.add_argument("--version", required=True)
    p.add_argument("--source-commit", required=True)
    p.add_argument("--output", required=True, type=Path)
    args = p.parse_args(argv)
    try:
        manifest = create_manifest(args.root, args.checksums, args.version, args.source_commit)
    except (OSError, UnicodeError, PreviewManifestError) as exc:
        print(f"AYA preview manifest: FAIL: {exc}", file=sys.stderr)
        return 2
    args.output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n",
                           encoding="utf-8")
    print(f"AYA preview manifest: PASS: {manifest['maven_version']}, " +
          f"{len(manifest['artifacts'])} checksummed files at {manifest['source_commit']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
