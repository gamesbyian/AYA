#!/usr/bin/env python3
"""Verify the first-party Godot test APK actually launches on an Android emulator.

Godot's synthetic host emits the fixed, payload-free marker only after its
Android plugin singleton and Ask card are constructed. A successful APK build
cannot substitute for this runtime observation. No assistant app is contacted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import zipfile
from pathlib import Path
from typing import Callable

PACKAGE = "dev.aya.godot.cihost"
READY_MARKER = "AYA_CI_GODOT_RUNTIME_READY"
FAILED_MARKER = "AYA_CI_GODOT_RUNTIME_FAIL"
SCENARIOS = (("412x892", "1.0"), ("320x700", "2.0"))
MAX_LOG_CHARS = 800
MAX_REPORT_BYTES = 16 * 1024


class EmulatorSmokeError(ValueError):
    pass


def inspect_log(log: str, package: str = PACKAGE) -> tuple[bool, bool]:
    """Return (observed ready, observed failure) from fresh emulator logcat."""
    if not isinstance(log, str):
        raise EmulatorSmokeError("Android logcat response is not text")
    ready = any(READY_MARKER in line for line in log.splitlines())
    failed = any(FAILED_MARKER in line for line in log.splitlines())
    # The program-specific marker is authoritative, not a generic unrelated
    # emulator crash. A fatal Godot/AYA crash must be investigated separately.
    for index, line in enumerate(log.splitlines()):
        if "FATAL EXCEPTION" not in line:
            continue
        follow = "\n".join(log.splitlines()[index:index + 12])
        if package in follow or "dev.aya.godot" in follow:
            failed = True
    return ready, failed


def verify_apk(apk: Path) -> str:
    if not apk.is_file() or apk.is_symlink():
        raise EmulatorSmokeError("Expected a real regular Godot-generated APK")
    if apk.stat().st_size < 1024 or not zipfile.is_zipfile(apk):
        raise EmulatorSmokeError("Godot export artifact is not a valid APK ZIP")
    digest = hashlib.sha256()
    with apk.open("rb") as handle:
        for data in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(data)
    return digest.hexdigest()


def smoke(
    apk: Path,
    *,
    run: Callable = subprocess.run,
    pause: Callable[[float], None] = time.sleep,
    max_polls: int = 25,
    poll_seconds: float = 2.0,
    scenarios: tuple[tuple[str, str], ...] = SCENARIOS,
) -> dict:
    if not 1 <= max_polls <= 100 or not 0 <= poll_seconds <= 5:
        raise EmulatorSmokeError("Invalid bounded emulator polling configuration")
    digest = verify_apk(apk)
    if not scenarios:
        raise EmulatorSmokeError("At least one runtime layout is required")

    def adb(*args: str, allow_failure: bool = False) -> str:
        try:
            result = run(
                ["adb", *args], capture_output=True, text=True,
                check=False, timeout=90,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise EmulatorSmokeError("ADB invocation failed: " + args[0]) from exc
        if result.returncode != 0:
            if allow_failure:
                return ""
            raise EmulatorSmokeError("ADB command failed: " + " ".join(args[:3]) +
                                     " (exit " + str(result.returncode) + ")")
        return result.stdout or ""

    adb("wait-for-device")
    if adb("shell", "getprop", "sys.boot_completed").strip() != "1":
        raise EmulatorSmokeError("Emulator is not fully booted")
    if "Success" not in adb("install", "-r", str(apk)):
        raise EmulatorSmokeError("Android did not confirm APK installation")
    if "package:" not in adb("shell", "pm", "path", PACKAGE):
        raise EmulatorSmokeError("Expected Godot test package was not installed")

    outcomes = []
    try:
        for size, scale in scenarios:
            if not re.fullmatch(r"[1-9]\d{1,3}x[1-9]\d{1,3}", size):
                raise EmulatorSmokeError("Invalid emulator display size")
            if scale not in ("1.0", "2.0"):
                raise EmulatorSmokeError("Unknown font-scale scenario")
            adb("shell", "wm", "size", size)
            adb("shell", "wm", "density", "160")
            adb("shell", "settings", "put", "system", "font_scale", scale)
            adb("shell", "am", "force-stop", PACKAGE)
            adb("logcat", "-c")
            adb("shell", "monkey", "-p", PACKAGE, "-c",
                "android.intent.category.LAUNCHER", "1")
            observed = False
            for _ in range(max_polls):
                log = adb("logcat", "-d", "-v", "brief", "-t", "3000")
                ready, failed = inspect_log(log)
                if failed:
                    raise EmulatorSmokeError(
                        f"Native Godot plugin/runtime failure marker at {size} scale {scale}"
                    )
                pid = adb("shell", "pidof", "-s", PACKAGE, allow_failure=True).strip()
                if ready and pid and all(part.isdecimal() for part in pid.split()):
                    observed = True
                    break
                pause(poll_seconds)
            if not observed:
                raise EmulatorSmokeError(
                    f"Godot Android runtime marker and live process not observed "
                    f"at {size} scale {scale}"
                )
            outcomes.append({
                "size_px": size,
                "density_dpi": 160,
                "android_font_scale": scale,
                "godot_script_marker": READY_MARKER,
                "native_singleton_and_card": "observed",
                "process_alive": True,
            })
    finally:
        # Reset the disposable emulator, even when the runtime test fails.
        for args in (
            ("shell", "am", "force-stop", PACKAGE),
            ("shell", "wm", "size", "reset"),
            ("shell", "wm", "density", "reset"),
            ("shell", "settings", "put", "system", "font_scale", "1.0"),
        ):
            try:
                adb(*args, allow_failure=True)
            except EmulatorSmokeError:
                pass

    return {
        "schema": "aya-godot-emulator-smoke/v1",
        "kind": "observed_first_party_android_emulator",
        "apk_sha256": digest,
        "package": PACKAGE,
        "layouts": outcomes,
        "editor_or_physical_device_tested": False,
        "actual_assistant_ingestion_tested": False,
        "local_review_or_share_tested": False,
        "limitations": (
            "Shows Android app process survival, a real Godot scene, an available "
            "native AYA singleton and a constructed enabled card. Does not prove "
            "user interaction, TalkBack accessibility, chooser or recipient receipt."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apk", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args(argv)
    if args.report.is_symlink():
        parser.exit(2, "AYA Godot emulator smoke: unsafe symlinked report\n")
    try:
        result = smoke(args.apk)
        args.report.parent.mkdir(parents=True, exist_ok=True)
        encoded = json.dumps(result, sort_keys=True, indent=2) + "\n"
        if len(encoded.encode("utf-8")) > MAX_REPORT_BYTES:
            raise EmulatorSmokeError("Evidence report unexpectedly large")
        args.report.write_text(encoded, encoding="utf-8")
    except (OSError, EmulatorSmokeError) as exc:
        print("AYA Godot emulator smoke: FAIL: " + str(exc)[:MAX_LOG_CHARS],
              file=sys.stderr)
        return 1
    print("AYA Godot emulator smoke: PASS: real process/scene/bridge/card on "
          "two emulator layouts; recipient and user-interaction unverified")
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as report:
            report.write("### Godot Android runtime smoke\n\n")
            report.write("Observed a live first-party Godot process, available "
                         "native AYA singleton and enabled Ask card at "
                         "412x892 and 320x700 (200% Android font setting).\n\n")
            report.write("No assistant app, local review, TalkBack or physical "
                         "device acceptance is implied.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
