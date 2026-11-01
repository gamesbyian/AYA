"""Prevent duplicate Flutter APK compilation while protecting distinct native gates."""
import unittest
from pathlib import Path

WORKFLOWS = Path(__file__).resolve().parents[1] / ".github" / "workflows"


class FlutterCIGatesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (WORKFLOWS / "flutter.yml").read_text(encoding="utf-8")
        cls.external = (WORKFLOWS / "flutter-external.yml").read_text(encoding="utf-8")
        cls.migration = (WORKFLOWS / "flutter-builtin-kotlin.yml").read_text(encoding="utf-8")

    def test_source_job_provides_fast_dart_and_host_reference_checks(self):
        for expected in (
            "flutter analyze", "flutter test", "flutter pub get",
            "tools/component_codegen.py", "tools/validate_guide.py",
            "tools/audit_reference.py", "tools/test_verify_flutter_host_apk.py",
        ):
            self.assertIn(expected, self.source, expected)
        self.assertNotIn("flutter build apk", self.source)
        self.assertNotIn("gradle :aya:publish", self.source)
        self.assertNotIn("gradle/actions/setup-gradle", self.source)
        self.assertNotIn("actions/setup-java", self.source)

    def test_primary_out_of_tree_host_still_compiles_real_apk(self):
        for expected in (
            "external-source-host:",
            'flutter-version: \'3.47.9\'',
            "gradle :aya:publishReleasePublicationToStagingRepository",
            "flutter build apk --debug",
            "tools/verify_flutter_host_apk.py",
            "tools/verify_android_adapter_apk.py",
            "AyaShareSelectionReceiver",
            'HOST="$RUNNER_TEMP/aya-flutter-consumer"',
        ):
            self.assertIn(expected, self.external, expected)

    def test_distinct_migration_lane_remains_and_checks_legacy_kotlin(self):
        for expected in (
            "builtin-kotlin-actual-host:", "test_flutter_builtin_migration.py",
            "prepare_host.py prepare", "flutter build apk --debug",
            "android.builtInKotlin=true",
            "tools/verify_flutter_host_apk.py",
            "tools/verify_android_adapter_apk.py",
        ):
            self.assertIn(expected, self.migration, expected)

    def test_shared_code_and_workflow_change_triggers_remain(self):
        for lane, self_name in (
            (self.source, ".github/workflows/flutter.yml"),
            (self.external, ".github/workflows/flutter-external.yml"),
            (self.migration, ".github/workflows/flutter-builtin-kotlin.yml"),
        ):
            for path in ("aya/**", "integrations/flutter/aya_flutter/android/**", self_name):
                if lane is self.external and path == "integrations/flutter/aya_flutter/android/**":
                    # This lane uses the broader source package path.
                    path = "integrations/flutter/aya_flutter/**"
                self.assertEqual(lane.count("'" + path + "'"), 2, path)


if __name__ == "__main__":
    unittest.main()
