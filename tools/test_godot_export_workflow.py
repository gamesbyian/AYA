"""The real Godot APK gate must not degrade to Kotlin-only sample packaging."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "godot-export.yml"
PRESET = ROOT / "integrations" / "godot" / "export_presets.cfg"


class GodotExportWorkflowContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = WORKFLOW.read_text(encoding="utf-8")
        cls.preset = PRESET.read_text(encoding="utf-8")
        cls.project_settings = (ROOT / "integrations" / "godot" / "project.godot").read_text(encoding="utf-8")

    def test_actual_godot_editor_and_gradle_build_required(self):
        for expected in (
            "Godot_v4.5.1-stable_linux.x86_64.zip",
            "Godot_v4.5.1-stable_export_templates.tpz",
            "godot-editor/Godot_v4.5.1-stable_linux.x86_64",
            "--headless --path integrations/godot --export-debug Android",
            "integrations/godot/out/aya-godot-host-debug.apk",
            "gradle_build/use_gradle_build=true",
        ):
            self.assertIn(expected, self.workflow + self.preset)

    def test_source_triggers_and_test_helper_changes_are_covered(self):
        for path in (
            "integrations/godot/**", "aya-godot/**", "aya/**",
            "tools/stage_godot_android_guide.py",
            "tools/verify_android_manifest_metadata.py",
            ".github/workflows/godot-export.yml",
        ):
            self.assertEqual(self.workflow.count("'" + path + "'"), 2, path)
        self.assertIn("workflow_dispatch:", self.workflow)

    def test_external_templates_are_pinned_and_cachable(self):
        for digest in (
            "1998af37f1387684e2c211cdb483daf492fc64dc6b12096bddcdca25b6910c86",
            "02ec53d1cc7dbb9cc6355393c61b9ab43d1244751a124f10248a4802830788cd",
        ):
            self.assertIn(digest, self.workflow)
        self.assertIn("sha256sum -c -", self.workflow)
        self.assertIn("actions/cache/restore@v4", self.workflow)
        self.assertIn("actions/cache/save@v4", self.workflow)
        self.assertIn("cancel-in-progress:", self.workflow)

    def test_exact_guide_and_every_native_bridge_gate_is_verified(self):
        for expected in (
            "tools/validate_guide.py --strict",
            "tools/audit_reference.py",
            "tools/stage_godot_android_guide.py",
            "tools/verify_flutter_host_apk.py",
            "tools/verify_android_adapter_apk.py",
            "tools/verify_android_manifest_metadata.py",
            "dev.aya.godot.AyaGodotPlugin",
            "dev.aya.android.AyaShareSelectionReceiver",
        ):
            self.assertIn(expected, self.workflow)
        self.assertIn('package/unique_name="dev.aya.godot.cihost"', self.preset)
        self.assertIn('version/name="1.0.0"', self.preset)
        self.assertIn('gradle_build/min_sdk="24"', self.preset)

    def test_android_texture_import_enabled_for_headless_export(self):
        # Godot 4.5 export_plugin.cpp returns invalid with no diagnostic
        # when ETC2/ASTC import was never enabled on a desktop Linux host.
        self.assertIn("textures/vram_compression/import_etc2_astc=true",
                      self.project_settings)

    def test_one_expensive_godot_export_job(self):
        self.assertEqual(self.workflow.count("    runs-on: ubuntu-latest"), 1)
        self.assertEqual(self.workflow.count("--export-debug Android"), 1)
        self.assertNotIn("continue-on-error: true", self.workflow)
        self.assertIn("Scope: actual Godot 4.5.1 debug Android export", self.workflow)


if __name__ == "__main__":
    unittest.main()
