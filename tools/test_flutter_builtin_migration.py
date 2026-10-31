"""Fail-closed tests for the experimental Flutter 3.47 AGP 9 host migrator."""
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "integrations/flutter/migration/prepare_host.py"
spec = importlib.util.spec_from_file_location("aya_flutter_prepare_host", SCRIPT)
migrator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(migrator)


class BuiltinKotlinHostTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.source = self.base / "source"
        self.trial = self.base / "trial"
        self.host = self.trial / "example"
        for rel in ("ci-host",):
            (self.source / rel).mkdir(parents=True)
        (self.source / "ci-host/aya-guide.md").write_text("fixture guide")
        (self.source / "ci-host/main.dart").write_text("void main() {}")
        for rel in ("android/app/src/main", "android/gradle/wrapper", "lib"):
            (self.host / rel).mkdir(parents=True)
        (self.host / "pubspec.yaml").write_text(
            "name: example\nversion: 1.0.0+1\ndependencies:\n  flutter:\n    sdk: flutter\n"
        )
        (self.host / "android/settings.gradle.kts").write_text(
            'plugins {\n  id("com.android.application") version "8.11.1" apply false\n}\n'
        )
        (self.host / "android/app/build.gradle.kts").write_text(
            'plugins {\n  id("com.android.application")\n'
            '  id("kotlin-android")\n}\n'
            'android {\n  kotlinOptions {\n    jvmTarget = "17"\n  }\n}\n'
        )
        (self.host / "android/gradle/wrapper/gradle-wrapper.properties").write_text(
            "distributionUrl=https\\://services.gradle.org/distributions/gradle-8.14-all.zip\n"
        )
        (self.host / "android/gradle.properties").write_text(
            "org.gradle.jvmargs=-Xmx2048m\nandroid.builtInKotlin=false\nandroid.newDsl=false\n"
        )
        p = patch.multiple(migrator, SOURCE=self.source, TRIAL=self.trial, HOST=self.host)
        p.start()
        self.addCleanup(p.stop)

    def test_configures_true_builtin_kotlin_without_touching_original_guide(self):
        migrator.configure()
        settings = (self.host / "android/settings.gradle.kts").read_text()
        self.assertIn('version "9.0.1"', settings)
        self.assertIn("AYA_STAGING_MAVEN", settings)
        app = (self.host / "android/app/build.gradle.kts").read_text()
        self.assertNotIn('id("kotlin-android")', app)
        self.assertNotIn("kotlinOptions", app)
        self.assertIn("kotlin {", app)
        self.assertIn("JvmTarget.JVM_17", app)
        self.assertIn("path: ..", (self.host / "pubspec.yaml").read_text())
        self.assertEqual((self.host / "android/app/src/main/assets/aya-guide.md").read_text(),
                         "fixture guide")
        props = (self.host / "android/gradle.properties").read_text()
        self.assertEqual(props.count("android.builtInKotlin=true"), 1)
        self.assertNotIn("android.builtInKotlin=false", props)
        self.assertIn("gradle-9.1.0-all.zip",
                      (self.host / "android/gradle/wrapper/gradle-wrapper.properties").read_text())

    def test_changed_flutter_host_version_fails_without_packing_unmatched_guide(self):
        pub = self.host / "pubspec.yaml"
        pub.write_text(pub.read_text().replace("1.0.0+1", "1.0.1+2"))
        with self.assertRaisesRegex(RuntimeError, "app version changed"):
            migrator.configure()
        self.assertFalse(
            (self.host / "android/app/src/main/assets/aya-guide.md").exists())

    def test_missing_agp_anchor_fails_loudly(self):
        settings = self.host / "android/settings.gradle.kts"
        settings.write_text("plugins {}")
        with self.assertRaisesRegex(RuntimeError, "AGP version"):
            migrator.configure()

    def test_candidate_never_applies_legacy_kgp_or_hardcodes_host_agp(self):
        source = (ROOT / "integrations/flutter/migration/modern.android.gradle").read_text()
        self.assertIn("kotlin {", source)
        self.assertIn("compilerOptions", source)
        self.assertNotIn("apply plugin: 'kotlin-android'", source)
        self.assertNotIn("kotlinOptions", source)
        self.assertNotIn("com.android.tools.build:gradle:", source)
        pub = (ROOT / "integrations/flutter/migration/modern.pubspec.yaml").read_text()
        self.assertIn('sdk: ">=3.12.0 <4.0.0"', pub)
        self.assertIn('flutter: ">=3.44.0"', pub)
        # Retained legacy plugin remains exactly source-controlled and
        # independently buildable until migration acceptance.
        legacy = (ROOT / "integrations/flutter/aya_flutter/pubspec.yaml").read_text()
        self.assertIn('flutter: ">=3.19.0"', legacy)


if __name__ == "__main__":
    unittest.main()
