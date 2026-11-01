#!/usr/bin/env python3
"""Validate an exact Android application metadata pair in a compiled APK.

Inspect the final binary manifest using Android SDK aapt. Text appearing in
another element or in a class string is not evidence of a v2 plugin registration.
This proves packaging only, not Android lifecycle or assistant ingestion.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ELEMENT_RE = re.compile(r"^(\s*)E:\s+([A-Za-z0-9_.:-]+)(?:\s|$)")
ATTR_RE = re.compile(
    r'^\s*A:\s+android:(name|value)(?:\([^)]*\))?="([^"]*)"'
)


class MetadataError(ValueError):
    pass


def parse_application_metadata(xmltree: str) -> list[tuple[str, str]]:
    """Return paired name/value from <application><meta-data> only.

    Honor indentation in aapt's binary XML tree. Deliberately ignore values in
    activities, receivers and other tags, including detached name/value pairs.
    """
    stack: list[tuple[int, str]] = []
    entries: list[tuple[str, str]] = []
    current: dict[str, str] | None = None

    def close_meta() -> None:
        nonlocal current
        if current is not None and "name" in current and "value" in current:
            entries.append((current["name"], current["value"]))
        current = None

    for line in xmltree.splitlines():
        m = ELEMENT_RE.match(line)
        if m:
            indentation, tag = m.groups()
            depth = len(indentation)
            while stack and stack[-1][0] >= depth:
                if stack[-1][1] == "meta-data" and current is not None:
                    close_meta()
                stack.pop()
            parent = stack[-1][1] if stack else None
            if tag == "meta-data" and parent == "application":
                current = {}
            stack.append((depth, tag))
            continue
        m = ATTR_RE.match(line)
        if (m and current is not None and stack and
                stack[-1][1] == "meta-data"):
            key, value = m.groups()
            if key in current:
                raise MetadataError("Duplicate Android metadata attribute: " + key)
            current[key] = value
    if current is not None:
        close_meta()
    return entries


def check_metadata(
    apk: Path, aapt: str, name: str, value: str,
    *, command_runner=subprocess.run
) -> None:
    if not apk.is_file() or not aapt or not name or not value:
        raise MetadataError("APK, aapt, metadata name and value are all required")
    proc = command_runner(
        [aapt, "dump", "xmltree", str(apk), "AndroidManifest.xml"],
        capture_output=True, text=True, check=False,
    )
    if proc.returncode:
        raise MetadataError("Android binary manifest inspection failed: " +
                            (proc.stderr or "")[:350])
    matches = [pair for pair in parse_application_metadata(proc.stdout)
               if pair[0] == name]
    if len(matches) != 1 or matches[0][1] != value:
        raise MetadataError("Required Android application metadata is missing, "
                            "duplicated or has an unexpected value: " + name)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apk", type=Path, required=True)
    parser.add_argument("--aapt", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--value", required=True)
    args = parser.parse_args(argv)
    try:
        check_metadata(args.apk, args.aapt, args.name, args.value)
    except (OSError, MetadataError) as exc:
        print(f"Android metadata: FAIL: {exc}", file=sys.stderr)
        return 1
    print(f"Android metadata: PASS: exact application registration for {args.name}")
    print("Scope: binary manifest structure only, not plugin loading or device behavior")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
