"""Synthetic ZIP and aapt negative controls for Flutter native APK packaging."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import Mock
from zipfile import ZipFile

from verify_flutter_host_apk import ApkVerificationError, check_apk

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "integrations/flutter/aya_flutter/ci-host/aya-guide.md"
APP_ID = "com.example.aya_flutter_ci_host"


def fake_runner(*, name=APP_ID, version="1.0.0", provider=True, receiver=True):
    def run(argv, **_):
        if argv[2] == "badging":
            return Mock(returncode=0, stdout=(
                f"package: name='{name}' versionCode='1' versionName='{version}'\n"
            ), stderr="")
        manifest = (("androidx.core.content.FileProvider\n" +
                      name + ".aya.files\n") if provider else "")
        if receiver:
            manifest += "dev.aya.android.AyaShareSelectionReceiver\n"
        return Mock(returncode=0, stdout=manifest, stderr="")
    return run


class FlutterHostApkVerificationTests(TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.apk = Path(self.tmp.name) / "test.apk"
        self.guide = FIXTURE.read_bytes()
        with ZipFile(self.apk, "w") as z:
            z.writestr("assets/aya-guide.md", self.guide)

    def check(self, runner=None):
        return check_apk(self.apk, FIXTURE, "/fake/aapt",
                         command_runner=runner or fake_runner())

    def test_exact_guide_and_merged_native_components(self):
        self.assertEqual(self.check(), (APP_ID, "1.0.0"))

    def test_rejects_missing_or_altered_reference(self):
        for content in (None, b"stale reference"):
            with self.subTest(content=content):
                with ZipFile(self.apk, "w") as z:
                    if content is not None:
                        z.writestr("assets/aya-guide.md", content)
                with self.assertRaises(ApkVerificationError):
                    self.check()

    def test_rejects_duplicate_guide_path(self):
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            with ZipFile(self.apk, "w") as z:
                z.writestr("assets/aya-guide.md", self.guide)
                z.writestr("assets/aya-guide.md", self.guide)
        with self.assertRaises(ApkVerificationError):
            self.check()

    def test_rejects_wrong_package_or_version(self):
        for runner in (
            fake_runner(name="dev.example.other"),
            fake_runner(version="9.9.9"),
        ):
            with self.subTest(runner=runner):
                with self.assertRaises(ApkVerificationError):
                    self.check(runner)

    def test_rejects_missing_provider_or_receiver(self):
        for runner in (fake_runner(provider=False),
                       fake_runner(receiver=False)):
            with self.subTest(runner=runner):
                with self.assertRaises(ApkVerificationError):
                    self.check(runner)

    def test_rejects_bad_aapt_output(self):
        with self.assertRaises(ApkVerificationError):
            self.check(lambda *_a, **_k: Mock(
                returncode=1, stdout="", stderr="bad archive"))
