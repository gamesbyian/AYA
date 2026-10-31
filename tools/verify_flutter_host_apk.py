#!/usr/bin/env python3
"""Fail-closed build-time inspection of a Flutter host APK's native AYA guide.

This checks APK packaging and native component declarations, NOT whether a
receiving assistant ingests attachments or whether the UI works on a device.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import zipfile
from pathlib import Path

from validate_guide import validate as validate_aya_guide

PACKAGE_LINE = re.compile(
    r"(?m)^package:\s+name='(?P<id>[^']+)'\s+"
    r"versionCode='(?P<code>[^']+)'\s+versionName='(?P<version>[^']+)'"
)
GUIDE_ASSET = "assets/aya-guide.md"


class ApkVerificationError(ValueError):
    pass


def check_apk(
    apk_path: Path,
    guide_path: Path,
    aapt: str,
    *,
    command_runner=subprocess.run,
) -> tuple[str, str]:
    """Verify explicit installed identity, exact guide bytes, and AAR manifest merge."""
    guide_bytes = guide_path.read_bytes()
    try:
        guide = guide_bytes.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise ApkVerificationError("Reference guide must be strict UTF-8") from exc

    result = validate_aya_guide(guide)
    if not result["ok"] or result["warnings"]:
        raise ApkVerificationError("AYA-RAS reference lint failed: " +
                                   "; ".join(result["errors"] + result["warnings"]))
    metadata = result["metadata"]
    if metadata["app_version_min"] != metadata["app_version_max"]:
        raise ApkVerificationError("CI host reference must declare one exact version")

    try:
        with zipfile.ZipFile(apk_path) as archive:
            matched = [entry for entry in archive.infolist()
                       if entry.filename == GUIDE_ASSET]
            if len(matched) != 1:
                raise ApkVerificationError(
                    "APK must contain exactly one native assets/aya-guide.md")
            if archive.read(matched[0]) != guide_bytes:
                raise ApkVerificationError(
                    "Native APK reference differs from source-controlled guide")
    except zipfile.BadZipFile as exc:
        raise ApkVerificationError("APK is not a readable zip archive") from exc

    def aapt_dump(*args: str) -> str:
        output = command_runner(
            [aapt, "dump", *args, str(apk_path)],
            capture_output=True, text=True, check=False,
        )
        if output.returncode != 0:
            raise ApkVerificationError(
                "aapt dump " + " ".join(args) + " failed: " + output.stderr[:500])
        return output.stdout

    line = PACKAGE_LINE.search(aapt_dump("badging"))
    if line is None:
        raise ApkVerificationError("Cannot find package ID and versionName in APK")
    package_id = line.group("id")
    version = line.group("version")
    if package_id != metadata["app_id"] or version != metadata["app_version_min"]:
        raise ApkVerificationError(
            f"APK {package_id}@{version} != guide "
            f"{metadata['app_id']}@{metadata['app_version_min']}"
        )

    xml = aapt_dump("xmltree", "AndroidManifest.xml")
    for expected in (
        "androidx.core.content.FileProvider",
        package_id + ".aya.files",
        "dev.aya.android.AyaShareSelectionReceiver",
    ):
        if expected not in xml:
            raise ApkVerificationError(
                "Merged Android manifest is missing AYA component: " + expected)
    return package_id, version


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apk", type=Path, required=True)
    parser.add_argument("--guide", type=Path, required=True)
    parser.add_argument("--aapt", required=True)
    args = parser.parse_args(argv)
    try:
        package, version = check_apk(args.apk, args.guide, args.aapt)
    except (OSError, ApkVerificationError) as exc:
        print(f"AYA Flutter host APK: FAIL: {exc}", file=sys.stderr)
        return 1
    print(f"AYA Flutter host APK: PASS: {package}@{version}, "
          "exact native guide and FileProvider/receiver present")
    print("Scope: packaging identity only, not physical device or recipient acceptance")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
