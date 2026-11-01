"""Offline, deterministic Android emulator smoke protocol negative controls."""
import io
import tempfile
import unittest
import zipfile
from pathlib import Path
from subprocess import CompletedProcess

from verify_godot_emulator_runtime import (
    EmulatorSmokeError, FAILED_MARKER, PACKAGE, READY_MARKER,
    inspect_log, smoke, verify_apk,
)


class FakeADB:
    def __init__(self, *, marker=READY_MARKER, pid="3212", installed=True,
                 booted=True, fail_install=False):
        self.commands = []
        self.marker = marker
        self.pid = pid
        self.installed = installed
        self.booted = booted
        self.fail_install = fail_install

    def __call__(self, args, **kwargs):
        self.commands.append(tuple(args))
        command = " ".join(args)
        if "getprop sys.boot_completed" in command:
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
