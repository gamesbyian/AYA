#!/usr/bin/env python3
"""Summarize bounded iOS simulator File Provider logs without hiding XCTest failures.

Usage: summarize_apple_fileprovider.py <simulator-log-path> <markdown-output-path>

Never include user document contents, paths, or arbitrary OS log messages in the
generated summary. Log lines can contain private data. This aggregates counts
of a few known provider error signatures, not proof of one root cause.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


def summarize(log: str) -> dict[str, int]:
    lines = log.splitlines()
    return {
        "LocalStorage unresolved item IDs (-1005)": sum(
            "NSFileProviderErrorNonExistentItemIdentifier" in line
            and "com.apple.FileProvider.LocalStorage" in line
            for line in lines
        ),
        "DocumentManager failed opening URL (code 2)": sum(
            "DocumentManager.Service" in line and "Failed opening URL: 2" in line
            for line in lines
        ),
        "LocalStorage indexing hard timeouts": sum(
            "com.apple.FileProvider.LocalStorage" in line
            and "took too long to perform: indexOneBatchInDomain" in line
            for line in lines
        ),
        "LocalStorage extension launch/communication failures": sum(
            "com.apple.FileProvider.LocalStorage" in line
            and (
                "Failed to create extensionProcess" in line
                or "Couldn’t communicate with a helper application" in line
            )
            for line in lines
        ),
        "iCloud authentication errors (nonlocal control)": sum(
            "com.apple.CloudDocs.iCloudDriveFileProvider" in line
            and "You need to authenticate before accessing this item" in line
            for line in lines
        ),
    }


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: summarize_apple_fileprovider.py LOG SUMMARY_MD", file=sys.stderr)
        return 2
    log_path, output_path = map(Path, sys.argv[1:])
    text = log_path.read_text(encoding="utf-8", errors="replace")
    counts = summarize(text)
    report = [
        "### iOS simulator File Provider diagnostic summary",
        "",
        "| Signature | Events in captured window |",
        "| --- | ---: |",
    ]
    report += [f"| {label} | {count} |" for label, count in counts.items()]
    report += [
        "",
        f"Captured lines: {len(text.splitlines())}.",
        "These are simulator OS log observations, not assertions about any "
        "particular fixture or proof that AYA caused the failures.",
        "Review XCUITest failures and timestamps alongside the retained "
        "bounded raw File Provider log. The original XCTest result stays authoritative.",
        "",
    ]
    output_path.write_text("\n".join(report), encoding="utf-8")
    print("\n".join(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
