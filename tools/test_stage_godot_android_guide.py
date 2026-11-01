"""Fail-closed raw APK guide staging tests for Godot's 4.5 Gradle template."""
import shutil
import tempfile
import unittest
from pathlib import Path

from stage_godot_android_guide import StageError, stage

ROOT = Path(__file__).resolve().parents[1]
SOURCE_GUIDE = ROOT / "integrations/godot/ci-host/aya-guide.md"
SOURCE_PRESETS = ROOT / "integrations/godot/export_presets.cfg"


class GodotAndroidGuideTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.project = self.root / "Godot CI host with spaces"
        self.project.mkdir()
        shutil.copyfile(SOURCE_PRESETS, self.project / "export_presets.cfg")
        self.build = self.project / "android" / "build"
        self.build.mkdir(parents=True)
        (self.build / "build.gradle").write_text("plugins { id 'com.android.application' }")
        self.guide = self.root / "source.md"
        shutil.copyfile(SOURCE_GUIDE, self.guide)

    def rewrite(self, old, new):
        path = self.project / "export_presets.cfg"
        text = path.read_text()
        self.assertIn(old, text)
        path.write_text(text.replace(old, new))

    def test_stages_exact_bytes_and_check_only_is_idempotent(self):
        target = stage(self.project, self.guide)
        self.assertEqual(target, self.build / "assets" / "aya-guide.md")
        self.assertEqual(target.read_bytes(), self.guide.read_bytes())
        self.assertEqual(stage(self.project, self.guide, check_only=True), target)
        self.assertEqual(stage(self.project, self.guide), target)

    def test_check_only_does_not_create_guide(self):
        with self.assertRaisesRegex(StageError, "staging was not requested"):
            stage(self.project, self.guide, check_only=True)
        self.assertFalse((self.build / "assets").exists())

    def test_mismatched_host_identity_refuses_before_writing(self):
        self.rewrite('package/unique_name="dev.aya.godot.cihost"',
                     'package/unique_name="dev.unrelated.app"')
        with self.assertRaisesRegex(StageError, "differ from Godot export preset"):
            stage(self.project, self.guide)

    def test_mismatched_host_version_refuses_before_writing(self):
        self.rewrite('version/name="1.0.0"', 'version/name="2.0.0"')
        with self.assertRaisesRegex(StageError, "differ from Godot export preset"):
            stage(self.project, self.guide)

    def test_non_gradle_preset_refuses(self):
        self.rewrite("gradle_build/use_gradle_build=true",
                     "gradle_build/use_gradle_build=false")
        with self.assertRaisesRegex(StageError, "must use the Godot Gradle build"):
            stage(self.project, self.guide)

    def test_missing_template_refuses(self):
        (self.build / "build.gradle").unlink()
        with self.assertRaisesRegex(StageError, "Install the Godot 4.5"):
            stage(self.project, self.guide)

    def test_lower_min_sdk_refuses(self):
        self.rewrite('gradle_build/min_sdk="24"', 'gradle_build/min_sdk="23"')
        with self.assertRaisesRegex(StageError, "min SDK 24"):
            stage(self.project, self.guide)

    def test_missing_version_or_duplicate_android_preset_refuses(self):
        self.rewrite('version/name="1.0.0"', 'version/name=""')
        with self.assertRaisesRegex(StageError, "must be explicit"):
            stage(self.project, self.guide)
        shutil.copyfile(SOURCE_PRESETS, self.project / "export_presets.cfg")
        preset = (self.project / "export_presets.cfg")
        extra = preset.read_text().replace("preset.0", "preset.1")
        preset.write_text(preset.read_text() + "\n" + extra)
        with self.assertRaisesRegex(StageError, "Exactly one"):
            stage(self.project, self.guide)

    def test_no_implicit_foreign_file_overwrite(self):
        target = self.build / "assets" / "aya-guide.md"
        target.parent.mkdir()
        target.write_text("foreign user file")
        with self.assertRaisesRegex(StageError, "refusing silent overwrite"):
            stage(self.project, self.guide)
        self.assertEqual(target.read_text(), "foreign user file")

    def test_symlinked_target_parent_refuses(self):
        other = self.root / "other"
        other.mkdir()
        (self.build / "assets").symlink_to(other, target_is_directory=True)
        with self.assertRaisesRegex(StageError, "symlinked"):
            stage(self.project, self.guide)
        self.assertEqual(list(other.iterdir()), [])

    def test_stale_or_malformed_guide_refuses(self):
        original = self.guide.read_text()
        self.guide.write_text(original.replace(
            "app_version_min: 1.0.0", "app_version_min: 9.9.9"
        ))
        with self.assertRaisesRegex(StageError, "differ from Godot export preset"):
            stage(self.project, self.guide)
        self.guide.write_text(original.replace(
            "## Assistant answer policy", "## Unrelated section"
        ))
        with self.assertRaisesRegex(StageError, "strict AYA-RAS"):
            stage(self.project, self.guide)

    def test_invalid_encoding_refuses(self):
        self.guide.write_bytes(b"\xff\xfe\x00")
        with self.assertRaisesRegex(StageError, "strict UTF-8"):
            stage(self.project, self.guide)


if __name__ == "__main__":
    unittest.main()
