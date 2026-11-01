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
import struct
import re
import subprocess
import sys
import time
import zipfile
import zlib
from pathlib import Path
from typing import Callable

PACKAGE = "dev.aya.godot.cihost"
READY_MARKER = "AYA_CI_GODOT_RUNTIME_READY"
FAILED_MARKER = "AYA_CI_GODOT_RUNTIME_FAIL"
FRAME_MARKER = "AYA_CI_GODOT_FRAME"
FRAME_PATTERN = re.compile(r"AYA_CI_GODOT_FRAME dark=(\d+) light=(\d+) valid=([01])")
SCENARIOS = (("412x892", "1.0"), ("320x700", "2.0"))
MAX_LOG_CHARS = 800
MAX_REPORT_BYTES = 16 * 1024
MAX_SCREENSHOT_BYTES = 8 * 1024 * 1024
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
PNG_END = b"\x00\x00\x00\x00IEND\xaeB\x60\x82"


class EmulatorSmokeError(ValueError):
    pass


def png_dimensions(data: bytes) -> tuple[int, int]:
    """Validate bounded PNG chunk framing and CRC without decoding pixels."""
    if not isinstance(data, bytes) or not 60 <= len(data) <= MAX_SCREENSHOT_BYTES:
        raise EmulatorSmokeError("Invalid or unreasonably large screenshot bytes")
    if not data.startswith(PNG_SIGNATURE):
        raise EmulatorSmokeError("Android screencap returned malformed PNG framing")
    position = len(PNG_SIGNATURE)
    width = height = 0
    saw_idat = False
    while position < len(data):
        if len(data) - position < 12:
            raise EmulatorSmokeError("Incomplete screenshot PNG chunk")
        length = struct.unpack(">I", data[position:position + 4])[0]
        end = position + 12 + length
        if length > MAX_SCREENSHOT_BYTES or end > len(data):
            raise EmulatorSmokeError("Invalid screenshot PNG chunk length")
        kind = data[position + 4:position + 8]
        payload = data[position + 8:position + 8 + length]
        actual_crc = struct.unpack(">I", data[end - 4:end])[0]
        if zlib.crc32(kind + payload) & 0xffffffff != actual_crc:
            raise EmulatorSmokeError("Screenshot PNG chunk CRC mismatch")
        if position == len(PNG_SIGNATURE):
            if kind != b"IHDR" or length != 13:
                raise EmulatorSmokeError("Screenshot PNG is missing its IHDR")
            width, height = struct.unpack(">II", payload[:8])
            if not 1 <= width <= 4096 or not 1 <= height <= 4096:
                raise EmulatorSmokeError("Screenshot has invalid dimensions")
        elif kind == b"IHDR":
            raise EmulatorSmokeError("Duplicate screenshot PNG IHDR")
        if kind == b"IDAT" and length:
            saw_idat = True
        if kind == b"IEND":
            if length or not saw_idat or end != len(data):
                raise EmulatorSmokeError("Incomplete or trailing screenshot PNG data")
            return width, height
        position = end
    raise EmulatorSmokeError("Screenshot PNG has no terminating IEND")


MAX_DECODED_SCREENSHOT_BYTES = 24 * 1024 * 1024


def png_has_visible_content(data: bytes) -> bool:
    """Require a visible light/dark UI contrast in our specific synthetic host.

    Android's screenshot service can return a perfectly valid, completely
    black frame before Godot presents any rendered pixels. This is deliberately
    a *test-fixture* guard, not a general accessibility or text-readability test.
    """
    width, height = png_dimensions(data)
    if (data[24] != 8 or data[25] not in (2, 6) or
            data[26:29] != b"\x00\x00\x00"):
        raise EmulatorSmokeError("Unsupported Android PNG pixel encoding")
    channels = 4 if data[25] == 6 else 3
    stride = width * channels
    expected = (stride + 1) * height
    if expected > MAX_DECODED_SCREENSHOT_BYTES:
        raise EmulatorSmokeError("Decoded screenshot exceeds size limit")
    compressed = []
    pos = len(PNG_SIGNATURE)
    while pos < len(data):
        length = struct.unpack(">I", data[pos:pos + 4])[0]
        if data[pos + 4:pos + 8] == b"IDAT":
            compressed.append(data[pos + 8:pos + 8 + length])
        pos += 12 + length
    try:
        stream = zlib.decompressobj()
        raw = stream.decompress(b"".join(compressed), expected + 1)
        raw += stream.flush()
    except zlib.error as exc:
        raise EmulatorSmokeError("Android PNG image data cannot be decoded") from exc
    if len(raw) != expected or not stream.eof or stream.unused_data:
        raise EmulatorSmokeError("Android PNG decompressed image is incomplete")
    offset = 0
    previous = bytearray(stride)
    dark = light = 0
    for _ in range(height):
        filter_type = raw[offset]
        row = bytearray(raw[offset + 1:offset + 1 + stride])
        offset += stride + 1
        if filter_type not in (0, 1, 2, 3, 4):
            raise EmulatorSmokeError("Unsupported screenshot PNG scanline filter")
        if filter_type:
            for i in range(stride):
                left = row[i - channels] if i >= channels else 0
                above = previous[i]
                upper_left = previous[i - channels] if i >= channels else 0
                if filter_type == 1:
                    predictor = left
                elif filter_type == 2:
                    predictor = above
                elif filter_type == 3:
                    predictor = (left + above) // 2
                else:
                    p = left + above - upper_left
                    da, db, dc = abs(p - left), abs(p - above), abs(p - upper_left)
                    predictor = (left if da <= db and da <= dc else
                                 above if db <= dc else upper_left)
                row[i] = (row[i] + predictor) & 0xff
        for i in range(0, stride, channels):
            if channels == 4 and row[i + 3] < 128:
                continue
            brightness = max(row[i:i + 3])
            if brightness <= 20:
                dark += 1
            elif brightness >= 80:
                light += 1
        if dark >= 32 and light >= 32:
            return True
        previous = row
    return False


def capture_synthetic_screenshot(
    size: str, scale: str, destination: Path, *, run: Callable = subprocess.run,
    pause: Callable[[float], None] = time.sleep,
) -> dict:
    """Capture visible pixels from our fixture, never another user app."""
    if destination.is_symlink() or destination.exists():
        raise EmulatorSmokeError("Refusing to overwrite existing screenshot")
    target_width, target_height = (int(part) for part in size.split("x"))
    blob = b""
    width = height = 0
    attempts = 0
    # Godot can emit its scene-ready marker before the Vulkan first frame has
    # been presented. Bounded retries verify pixels, not just process liveness.
    for attempts in range(1, 5):
        try:
            result = run(["adb", "exec-out", "screencap", "-p"],
                         capture_output=True, check=False, timeout=40)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise EmulatorSmokeError("Could not capture synthetic Godot screen") from exc
        if result.returncode != 0:
            raise EmulatorSmokeError("ADB screencap command failed")
        blob = result.stdout
        width, height = png_dimensions(blob)
        if sorted((width, height)) != sorted((target_width, target_height)):
            raise EmulatorSmokeError(
                f"Screenshot dimensions {width}x{height} mismatch requested {size}"
            )
        if png_has_visible_content(blob):
            break
        if attempts < 4:
            pause(2.0)
    else:
        raise EmulatorSmokeError(
            f"Android screenshot remains blank/unrendered after 4 captures at {size}"
        )
    if destination.parent.is_symlink():
        raise EmulatorSmokeError("Refusing symlinked screenshot directory")
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation prevents symlink following and foreign-file overwrite.
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(destination, flags, 0o600)
    except FileExistsError as exc:
        raise EmulatorSmokeError("Refusing to overwrite existing screenshot") from exc
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(blob)
    except OSError:
        destination.unlink(missing_ok=True)
        raise
    return {
        "file": destination.name,
        "width_px": width,
        "height_px": height,
        "orientation": "portrait" if height >= width else "landscape",
        "sha256": hashlib.sha256(blob).hexdigest(),
        "capture_attempts": attempts,
        "fixture_contrast_detected": True,
        "capture": "adb exec-out screencap -p from disposable first-party fixture",
        "visual_accessibility_reviewed": False,
    }



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



def parse_synthetic_viewport_frame(log: str) -> dict:
    """Parse only bounded synthetic pixel counts; no private log text."""
    rows = [line for line in log.splitlines() if FRAME_MARKER in line]
    if len(rows) != 1:
        raise EmulatorSmokeError("Godot viewport pixel diagnostic missing or duplicated")
    match = FRAME_PATTERN.search(rows[0])
    if match is None:
        raise EmulatorSmokeError("Malformed Godot viewport pixel diagnostic")
    dark, light, declared_valid = (int(part) for part in match.groups())
    if (dark > 4096 or light > 4096 or dark + light > 4096 or
            declared_valid != int(dark >= 16 and light >= 16)):
        raise EmulatorSmokeError("Inconsistent Godot viewport pixel diagnostic")
    return {
        "dark_samples": dark, "light_samples": light,
        "visible_contrast": bool(declared_valid),
        "sample_grid": "64x64 first-party synthetic Godot viewport",
    }


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
    max_polls: int = 40,
    poll_seconds: float = 2.0,
    scenarios: tuple[tuple[str, str], ...] = SCENARIOS,
    screenshots_dir: Path | None = None,
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

    # First immersive launch can show a system "Viewing full screen" overlay,
    # leaving screenshots of the OS instead of the tested AYA card.
    previous_immersive = adb(
        "shell", "settings", "get", "secure",
        "immersive_mode_confirmations", allow_failure=True,
    ).strip()
    outcomes = []
    try:
        adb("shell", "settings", "put", "secure",
            "immersive_mode_confirmations", "confirmed")
        if adb("shell", "settings", "get", "secure",
               "immersive_mode_confirmations").strip() != "confirmed":
            raise EmulatorSmokeError(
                "Could not suppress Android immersive first-use overlay"
            )
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
            launch_feedback = adb("shell", "monkey", "-p", PACKAGE, "-c",
                                  "android.intent.category.LAUNCHER", "1")
            observed = False
            last_log = ""
            last_pid = ""
            for _ in range(max_polls):
                log = adb("logcat", "-d", "-v", "brief", "-t", "10000")
                last_log = log
                ready, failed = inspect_log(log)
                if failed:
                    raise EmulatorSmokeError(
                        f"Native Godot plugin/runtime failure marker at {size} scale {scale}"
                    )
                pid = adb("shell", "pidof", "-s", PACKAGE, allow_failure=True).strip()
                last_pid = pid
                if ready and pid and all(part.isdecimal() for part in pid.split()):
                    observed = True
                    break
                pause(poll_seconds)
            if not observed:
                # Factual, bounded diagnostics from this dedicated CI emulator;
                # don't infer the cause from a missing marker alone.
                relevant = [
                    line.strip() for line in last_log.splitlines()
                    if any(word in line.lower() for word in
                           ("godot", "aya_ci_", "fatal exception", "androidruntime"))
                ][-10:]
                activity = adb("shell", "dumpsys", "activity", "activities",
                               allow_failure=True)
                resumed = [
                    line.strip() for line in activity.splitlines()
                    if "resumedactivity" in line.lower() or PACKAGE in line
                ][-3:]
                raise EmulatorSmokeError(
                    f"Godot Android runtime marker and live process not observed "
                    f"at {size} scale {scale}; last_pid={last_pid or 'absent'}, "
                    f"launch={launch_feedback.strip()[:100]!r}, "
                    f"recent_godot_log={str(relevant)[-340:]}, "
                    f"activity={str(resumed)[-170:]}"
                )
            screenshot = None
            if screenshots_dir is not None:
                # Report only the disposable fixture's public geometry,
                # never screenshot input or host/user payload content.
                geometry_log = adb("logcat", "-d", "-v", "brief", "-t",
                                   "10000", allow_failure=True)
                geometry = [
                    line.strip()[-240:] for line in geometry_log.splitlines()
                    if "AYA_CI_GODOT_GEOMETRY" in line
                ][-2:]
                godot_frame = parse_synthetic_viewport_frame(geometry_log)
                # Process readiness does not prove the AYA card is foreground.
                # A system fullscreen confirmation or Launcher ANR can hide it.
                windows = adb("shell", "dumpsys", "window", "displays")
                focused = [
                    line.strip() for line in windows.splitlines()
                    if "mCurrentFocus=" in line
                ]
                if (len(focused) != 1 or PACKAGE not in focused[0] or
                        "Application Not Responding" in focused[0]):
                    state = focused[0][:180] if focused else "not reported"
                    raise EmulatorSmokeError(
                        f"Android system dialog or non-host window obscures "
                        f"AYA screenshot at {size}; focused_window={state}; "
                        f"synthetic_geometry={geometry}; "
                        f"godot_viewport={godot_frame}"
                    )
                name = f"godot_{size}_font{int(float(scale) * 100)}.png"
                try:
                    screenshot = capture_synthetic_screenshot(
                        size, scale, screenshots_dir / name, run=run, pause=pause
                    )
                    if not godot_frame["visible_contrast"]:
                        raise EmulatorSmokeError(
                            "Android screenshot has contrast but synthetic Godot viewport does not"
                        )
                    screenshot["synthetic_godot_frame"] = godot_frame
                except EmulatorSmokeError as exc:
                    raise EmulatorSmokeError(
                        f"{exc}; synthetic_geometry={geometry}; "
                        f"godot_viewport={godot_frame}; "
                        f"diagnosis={'Godot viewport is also blank/low contrast' if not godot_frame['visible_contrast'] else 'Godot viewport contains UI pixels; Android capture/compositor remains blank'}"
                    ) from exc
            outcomes.append({
                "screenshot": screenshot,
                "size_px": size,
                "density_dpi": 160,
                "android_font_scale": scale,
                "godot_script_marker": READY_MARKER,
                "native_singleton_and_card": "observed",
                "process_alive": True,
            })
    finally:
        # Restore test-only Android setting even if runtime or screenshot fails.
        try:
            if previous_immersive and previous_immersive != "null":
                adb("shell", "settings", "put", "secure",
                    "immersive_mode_confirmations", previous_immersive,
                    allow_failure=True)
            else:
                adb("shell", "settings", "delete", "secure",
                    "immersive_mode_confirmations", allow_failure=True)
        except EmulatorSmokeError:
            pass
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
    parser.add_argument("--screenshots-dir", type=Path, default=None,
                        help="Optional artifact directory for disposable AYA-only screens")
    args = parser.parse_args(argv)
    if args.report.is_symlink():
        parser.exit(2, "AYA Godot emulator smoke: unsafe symlinked report\n")
    try:
        result = smoke(args.apk, screenshots_dir=args.screenshots_dir)
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
            if args.screenshots_dir is not None:
                report.write("Bounded synthetic-scene PNG screenshots captured for "
                             "later **human visual review**; screenshot presence "
                             "alone cannot certify visibility or accessibility.\n\n")
            report.write("No assistant app, local review, TalkBack or physical "
                         "device acceptance is implied.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
