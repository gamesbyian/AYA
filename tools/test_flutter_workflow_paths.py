"""Protect native Flutter CI gates while excluding prose-only edits."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ROOT / ".github/workflows/flutter.yml",
    ROOT / ".github/workflows/flutter-builtin-kotlin.yml",
]
REQUIRED = (
    "integrations/flutter/aya_flutter/android/**",
    "integrations/flutter/aya_flutter/lib/**",
    "integrations/flutter/aya_flutter/test/**",
    "integrations/flutter/aya_flutter/ci-host/**",
    "integrations/flutter/aya_flutter/pubspec.yaml",
    "integrations/flutter/migration/prepare_host.py",
    "aya/**",
)


class FlutterWorkflowTriggerTest(unittest.TestCase):
    def test_code_and_fixture_changes_still_trigger_native_ci(self):
        for file in FILES:
            source = file.read_text()
            with self.subTest(file=file.name):
                for entry in REQUIRED:
                    self.assertEqual(source.count("      - '" + entry + "'"), 2, entry)
                self.assertNotIn("      - 'integrations/flutter/**'", source)
                self.assertNotIn("      - 'integrations/flutter/migration/**'", source)
                self.assertNotIn("      - 'integrations/flutter/aya_flutter/**'", source)
                self.assertNotIn("      - 'docs/components/FLUTTER.md'", source)
                self.assertIn("      - '.github/workflows/" + file.name + "'", source)

    def test_verifier_changes_trigger_built_in_kotlin_ci(self):
        builtin = FILES[1].read_text()
        for path in (
            "tools/verify_flutter_host_apk.py",
            "tools/verify_android_adapter_apk.py",
            "tools/test_flutter_builtin_migration.py",
        ):
            self.assertEqual(builtin.count("      - '" + path + "'"), 2)

    def test_codegen_changes_trigger_flutter_source_host(self):
        source = FILES[0].read_text()
        for path in (
            "tools/component_codegen.py",
            "tools/test_component_codegen.py",
            "docs/components/examples/**",
        ):
            self.assertEqual(source.count("      - '" + path + "'"), 2)


if __name__ == "__main__":
    unittest.main()
