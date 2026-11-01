"""Enforce one Godot AAR/editor/export owner without losing adapter verification."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"


class GodotCIOwnershipTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = (WORKFLOWS / "godot-export.yml").read_text(encoding="utf-8")

    def test_no_duplicate_editor_or_android_compiler_workflow(self):
        self.assertFalse((WORKFLOWS / "godot.yml").exists())
        self.assertEqual(self.workflow.count("    runs-on: ubuntu-latest"), 2)
        self.assertEqual(self.workflow.count("gradle :aya-godot:stageGodotAddon"), 1)
        self.assertEqual(self.workflow.count("--export-debug Android"), 1)
        self.assertIn("needs: real-godot-export", self.workflow)
        runtime = self.workflow.split("  android-emulator-runtime:", 1)[1]
        self.assertNotIn("stageGodotAddon", runtime)
        self.assertIn("actions/download-artifact@v4", runtime)
        self.assertIn("tools/verify_godot_emulator_runtime.py", runtime)

    def test_preserve_both_aar_variants_and_editor_source(self):
        for expected in (
            'for variant in debug release; do',
            'aya-$variant.aar',
            'aya-godot-$variant.aar',
            'plugin.cfg export_plugin.gd aya_card.gd',
            'aya-godot/build/godot-addon/AYA/',
            'aya-godot-debug-release-addon',
            'aya-godot-4-5-real-export-debug',
        ):
            self.assertIn(expected, self.workflow, expected)

    def test_real_headless_editor_and_binary_checks_are_retained(self):
        for required in (
            'aya_smoke.gd', 'aya_export_preflight.gd',
            '--headless --path integrations/godot --editor --import --quit',
            'tools/verify_flutter_host_apk.py',
            'tools/verify_android_adapter_apk.py',
            'tools/verify_android_manifest_metadata.py',
            'tools/verify_android_manifest_providers.py',
            'AyaShareSelectionReceiver', 'AyaFileProvider',
        ):
            self.assertIn(required, self.workflow, required)

    def test_trigger_coverage_including_native_and_gradle_infrastructure(self):
        for path in (
            'aya/**', 'aya-godot/**', 'integrations/godot/**',
            'build.gradle.kts', 'settings.gradle.kts', 'gradle.properties',
            '.github/workflows/godot-export.yml',
            'tools/stage_godot_android_guide.py',
        ):
            self.assertEqual(self.workflow.count("'"+path+"'"), 2, path)
        self.assertIn('workflow_dispatch:', self.workflow)

    def test_failures_not_suppressed(self):
        self.assertNotIn('continue-on-error: true', self.workflow)
        self.assertIn('if-no-files-found: error', self.workflow)


if __name__ == "__main__":
    unittest.main()
