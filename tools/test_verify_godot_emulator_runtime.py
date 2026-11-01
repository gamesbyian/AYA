"""Offline, deterministic Android emulator smoke protocol negative controls."""
import io
import struct
import zlib
import tempfile
import unittest
import zipfile
from pathlib import Path
from subprocess import CompletedProcess

from verify_godot_emulator_runtime import (
    EmulatorSmokeError, FAILED_MARKER, PACKAGE, READY_MARKER,
    inspect_log, png_dimensions, png_has_visible_content, smoke, verify_apk,
)


def fake_png(width, height, blank=False):
    def chunk(kind, data):
        checksum = zlib.crc32(kind + data) & 0xffffffff
        return (struct.pack(">I", len(data)) + kind + data +
                struct.pack(">I", checksum))
    dark = b"\x00\x00\x00\xff"
    light = b"\xff\xff\xff\xff"
    row = dark * width if blank else dark * (width // 2) + light * (width - width // 2)
    raw = (b"\x00" + row) * height
    return (
        b"\x89PNG\r\n\x1a\n" +
        chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)) +
        chunk(b"IDAT", zlib.compress(raw, level=6)) +
        chunk(b"IEND", b"")
    )


class FakeADB:
    def __init__(self, *, marker=READY_MARKER, pid="3212", installed=True,
                 booted=True, fail_install=False, corrupt_png=False,
                 immersive_supported=True, focused_window=None,
                 blank_png=False, blank_first=0):
        self.commands = []
        self.marker = marker
        self.pid = pid
        self.installed = installed
        self.booted = booted
        self.fail_install = fail_install
        self.corrupt_png = corrupt_png
        self.immersive_supported = immersive_supported
        self.immersive_value = "null"
        self.focused_window = focused_window
        self.blank_png = blank_png
        self.blank_first = blank_first
        self.screenshot_calls = 0

    def __call__(self, args, **kwargs):
        self.commands.append(tuple(args))
        command = " ".join(args)
        if "exec-out screencap -p" in command:
            sizes = [c[-1] for c in self.commands if
                     len(c) == 5 and c[1:4] == ("shell", "wm", "size")
                     and c[-1] != "reset"]
            size = sizes[-1] if sizes else "412x892"
            width, height = (int(x) for x in size.split("x"))
            self.screenshot_calls += 1
            blank = self.blank_png or self.screenshot_calls <= self.blank_first
            image = b"not a PNG" if self.corrupt_png else fake_png(width, height, blank=blank)
            return CompletedProcess(args, 0, image, b"")
        if "dumpsys window displays" in command:
            focused = self.focused_window or (
                "Window{9a0 u0 " + PACKAGE + "/org.godotengine.godot.GodotActivity}"
            )
            out = "mCurrentFocus=" + focused + "\n"
        elif "settings get secure immersive_mode_confirmations" in command:
            out = self.immersive_value + "\n"
        elif "settings put secure immersive_mode_confirmations" in command:
            if self.immersive_supported:
                self.immersive_value = args[-1]
            out = ""
        elif "settings delete secure immersive_mode_confirmations" in command:
            self.immersive_value = "null"
            out = ""
        elif "getprop sys.boot_completed" in command:
            out = "1\n" if self.booted else "0\n"
        elif "install -r" in command:
            out = "Failure\n" if self.fail_install else "Success\n"
        elif "pm path" in command:
            out = ("package:/data/app/" + PACKAGE + "/base.apk\n") if self.installed else ""
        elif "pidof -s" in command:
            if not self.pid:
                return CompletedProcess(args, 1, "", "")
            out = self.pid + "\n"
        elif "logcat -d" in command:
            out = "I/Godot: " + self.marker + "\n" if self.marker else "I/Godot: launching\n"
        else:
            out = ""
        return CompletedProcess(args, 0, out, "")


class GodotEmulatorSmokeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.apk = Path(self.tmp.name) / "godot-debug.apk"
        with zipfile.ZipFile(self.apk, "w") as archive:
            archive.writestr("AndroidManifest.xml", b"fixture" * 250)
            archive.writestr("assets/aya-guide.md", b"not-actual-guide" * 75)

    def execute(self, runner=None, **kwargs):
        options = {"poll_seconds": 0, "max_polls": 2}
        options.update(kwargs)
        return smoke(self.apk, run=runner or FakeADB(), pause=lambda _: None,
                     **options)

    def test_two_launches_with_distinct_font_and_size_settings(self):
        fake = FakeADB()
        evidence = self.execute(fake)
        self.assertEqual(evidence["schema"], "aya-godot-emulator-smoke/v1")
        self.assertEqual(len(evidence["apk_sha256"]), 64)
        self.assertEqual(len(evidence["layouts"]), 2)
        self.assertEqual([p["size_px"] for p in evidence["layouts"]],
                         ["412x892", "320x700"])
        self.assertEqual([p["android_font_scale"] for p in evidence["layouts"]],
                         ["1.0", "2.0"])
        self.assertEqual(sum(" monkey " in " ".join(c) for c in fake.commands), 2)
        self.assertIn(("adb", "shell", "wm", "size", "reset"), fake.commands)
        self.assertNotIn(("adb", "shell", "input", "tap"), fake.commands)
        self.assertFalse(evidence["actual_assistant_ingestion_tested"])
        self.assertFalse(evidence["local_review_or_share_tested"])

    def test_system_immersive_overlay_is_disabled_then_setting_restored(self):
        fake = FakeADB()
        self.execute(fake, screenshots_dir=Path(self.tmp.name) / "screens")
        confirm = ("adb", "shell", "settings", "put", "secure",
                   "immersive_mode_confirmations", "confirmed")
        self.assertIn(confirm, fake.commands)
        self.assertLess(fake.commands.index(confirm),
                        next(i for i, cmd in enumerate(fake.commands)
                             if "monkey" in cmd))
        self.assertIn(("adb", "shell", "settings", "delete", "secure",
                       "immersive_mode_confirmations"), fake.commands)
        self.assertEqual(fake.immersive_value, "null")

    def test_rejects_unsuppressed_system_immersive_overlay(self):
        fake = FakeADB(immersive_supported=False)
        with self.assertRaisesRegex(EmulatorSmokeError, "immersive first-use overlay"):
            self.execute(fake, screenshots_dir=Path(self.tmp.name) / "screens")
        self.assertFalse((Path(self.tmp.name) / "screens").exists())
        self.assertIn(("adb", "shell", "wm", "size", "reset"), fake.commands)

    def test_system_dialog_covering_card_prevents_visual_acceptance(self):
        fake = FakeADB(focused_window=(
            "Window{123 u0 Application Not Responding: "
            "com.google.android.apps.nexuslauncher}"
        ))
        folder = Path(self.tmp.name) / "screens"
        with self.assertRaisesRegex(EmulatorSmokeError,
                                    "system dialog or non-host window"):
            self.execute(fake, screenshots_dir=folder)
        self.assertFalse(folder.exists())
        self.assertIn(("adb", "shell", "wm", "size", "reset"), fake.commands)

    def test_missing_foreground_focus_prevents_visual_acceptance(self):
        fake = FakeADB(focused_window="Window{456 u0 com.android.systemui/Overlay}")
        with self.assertRaisesRegex(EmulatorSmokeError,
                                    "system dialog or non-host window"):
            self.execute(fake, screenshots_dir=Path(self.tmp.name) / "screens")

    def test_blank_frames_are_not_accepted_as_visual_evidence(self):
        fake = FakeADB(blank_png=True)
        folder = Path(self.tmp.name) / "screens"
        with self.assertRaisesRegex(EmulatorSmokeError, "blank/unrendered"):
            self.execute(fake, screenshots_dir=folder)
        self.assertFalse(folder.exists())
        self.assertEqual(fake.screenshot_calls, 4)
        self.assertIn(("adb", "shell", "wm", "size", "reset"), fake.commands)

    def test_first_unrendered_frame_can_recover_on_later_capture(self):
        fake = FakeADB(blank_first=1)
        folder = Path(self.tmp.name) / "screens"
        results = self.execute(fake, screenshots_dir=folder)
        self.assertEqual(results["layouts"][0]["screenshot"]["capture_attempts"], 2)
        self.assertEqual(results["layouts"][1]["screenshot"]["capture_attempts"], 1)
        self.assertEqual(fake.screenshot_calls, 3)
        self.assertTrue(all(p["screenshot"]["fixture_contrast_detected"]
                            for p in results["layouts"]))

    def test_image_content_check_rejects_uniform_black_or_white(self):
        self.assertFalse(png_has_visible_content(fake_png(50, 30, blank=True)))
        self.assertTrue(png_has_visible_content(fake_png(50, 30)))
        with self.assertRaisesRegex(EmulatorSmokeError, "image data"):
            valid = fake_png(50, 30)
            png_has_visible_content(valid.replace(b"IDAT", b"IXAT", 1))

    def test_visual_evidence_uses_actual_binary_png_and_two_distinct_layouts(self):
        fake = FakeADB()
        folder = Path(self.tmp.name) / "screens"
        evidence = self.execute(fake, screenshots_dir=folder)
        self.assertEqual(len(list(folder.glob("*.png"))), 2)
        for item in evidence["layouts"]:
            screen = item["screenshot"]
            self.assertEqual(screen["visual_accessibility_reviewed"], False)
            self.assertEqual(len(screen["sha256"]), 64)
            png = (folder / screen["file"]).read_bytes()
            self.assertEqual(png_dimensions(png),
                             (screen["width_px"], screen["height_px"]))
        self.assertEqual(sum("exec-out screencap -p" in " ".join(c)
                             for c in fake.commands), 2)

    def test_cannot_silently_accept_corrupted_or_missing_png(self):
        with self.assertRaisesRegex(EmulatorSmokeError, "Invalid or unreasonably"):
            png_dimensions(b"broken")
        fake = FakeADB(corrupt_png=True)
        with self.assertRaisesRegex(EmulatorSmokeError, "Invalid or unreasonably"):
            self.execute(fake, screenshots_dir=Path(self.tmp.name) / "screens")

    def test_png_crc_and_chunk_integrity(self):
        good = fake_png(412, 892)
        bad = bytearray(good)
        bad[30] ^= 1  # IHDR checksum, without altering the dimensions
        with self.assertRaisesRegex(EmulatorSmokeError, "CRC mismatch"):
            png_dimensions(bytes(bad))
        with self.assertRaisesRegex(EmulatorSmokeError, "IEND"):
            png_dimensions(good[:-12])
        with self.assertRaisesRegex(EmulatorSmokeError, "trailing"):
            png_dimensions(good + b"extra data")

    def test_symlinked_screenshot_destination_is_rejected(self):
        folder = Path(self.tmp.name) / "screens"
        folder.mkdir()
        private = folder / "private.txt"
        private.write_text("do not touch")
        (folder / "godot_412x892_font100.png").symlink_to(private)
        with self.assertRaisesRegex(EmulatorSmokeError, "Refusing to overwrite"):
            self.execute(FakeADB(), screenshots_dir=folder)
        self.assertEqual(private.read_text(), "do not touch")

    def test_existing_screenshot_is_never_overwritten(self):
        folder = Path(self.tmp.name) / "screens"
        folder.mkdir()
        path = folder / "godot_412x892_font100.png"
        path.write_text("foreign")
        with self.assertRaisesRegex(EmulatorSmokeError, "Refusing to overwrite"):
            self.execute(FakeADB(), screenshots_dir=folder)
        self.assertEqual(path.read_text(), "foreign")

    def test_rejects_absent_or_invalid_apk(self):
        with self.assertRaisesRegex(EmulatorSmokeError, "valid APK ZIP"):
            self.apk.write_bytes(b"not an APK" * 200)
            verify_apk(self.apk)
        self.apk.unlink()
        with self.assertRaisesRegex(EmulatorSmokeError, "regular Godot"):
            verify_apk(self.apk)

    def test_symlinked_apk_is_rejected(self):
        raw = self.apk.with_name("true.apk")
        self.apk.rename(raw)
        self.apk.symlink_to(raw)
        with self.assertRaisesRegex(EmulatorSmokeError, "real regular"):
            verify_apk(self.apk)

    def test_missing_boot_or_package_refuses(self):
        with self.assertRaisesRegex(EmulatorSmokeError, "fully booted"):
            self.execute(FakeADB(booted=False))
        with self.assertRaisesRegex(EmulatorSmokeError, "not installed"):
            self.execute(FakeADB(installed=False))
        with self.assertRaisesRegex(EmulatorSmokeError, "did not confirm"):
            self.execute(FakeADB(fail_install=True))

    def test_missing_marker_or_dead_process_is_not_a_pass(self):
        with self.assertRaisesRegex(EmulatorSmokeError, "marker and live process"):
            self.execute(FakeADB(marker=""))
        with self.assertRaisesRegex(EmulatorSmokeError, "marker and live process"):
            self.execute(FakeADB(pid=""))

    def test_failure_marker_trumps_success(self):
        fake = FakeADB(marker=READY_MARKER + "\nE/Godot: " + FAILED_MARKER)
        with self.assertRaisesRegex(EmulatorSmokeError, "failure marker"):
            self.execute(fake)
        self.assertIn(("adb", "shell", "wm", "size", "reset"), fake.commands)

    def test_app_specific_crash_fails_even_if_ready_marker_present(self):
        log = ("I/Godot: " + READY_MARKER + "\n"
               "E/AndroidRuntime: FATAL EXCEPTION: main\n"
               "E/AndroidRuntime: Process: " + PACKAGE + ", PID: 31\n")
        self.assertEqual(inspect_log(log), (True, True))
        self.assertEqual(inspect_log(
            "E/AndroidRuntime: FATAL EXCEPTION: other\n"
            "E/AndroidRuntime: Process: org.example.elsewhere\n"),
            (False, False))

    def test_rejects_unbounded_or_missing_scenario_configuration(self):
        with self.assertRaisesRegex(EmulatorSmokeError, "bounded"):
            self.execute(FakeADB(), max_polls=0)
        with self.assertRaisesRegex(EmulatorSmokeError, "At least one"):
            self.execute(FakeADB(), scenarios=())
        with self.assertRaisesRegex(EmulatorSmokeError, "display size"):
            self.execute(FakeADB(), scenarios=(("../unsafe", "1.0"),))


if __name__ == "__main__":
    unittest.main()
