"""Negative, no-overwrite, and idempotency tests for Android host scaffolding."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from component_scaffold import ComponentError, apply_plan, plan

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "docs/components/examples/sample-help-card.json"


class ScaffoldTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name)
        (self.project / "app/src/main").mkdir(parents=True)
        self.manifest = json.loads(SAMPLE.read_text(encoding="utf-8"))

    def test_dry_run_has_zero_writes(self):
        args = [
            sys.executable, str(ROOT / "tools/component_scaffold.py"),
            "--project-dir", str(self.project), "--manifest", str(SAMPLE),
            "--mode", "kotlin", "--package", "dev.aya.host"
        ]
        result = subprocess.run(args, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["status"], "dry-run")
        self.assertEqual(report["created"], [])
        self.assertFalse((self.project / ".aya").exists())
        self.assertFalse((self.project / "app/src/main/java").exists())

    def test_apply_idempotent_and_no_overwrite(self):
        files = plan(self.project, "app", self.manifest, "kotlin", "dev.aya.host")
        first = apply_plan(self.project, files)
        self.assertEqual(len(first), 2)
        self.assertEqual(apply_plan(self.project, files), [])
        source = next(p for p in files if p.suffix == ".kt")
        source.write_text("owner modifications", encoding="utf-8")
        with self.assertRaises(ComponentError):
            apply_plan(self.project, files)
        self.assertEqual(source.read_text(encoding="utf-8"), "owner modifications")

    def test_xml_layout_and_persisted_configuration(self):
        files = plan(self.project, "app", self.manifest, "android-xml")
        self.assertEqual({p.suffix for p in files}, {".xml", ".json"})
        self.assertIn("app:ayaQuestionInputId", next(body for path, body in files.items() if path.suffix == ".xml"))
        apply_plan(self.project, files)
        self.assertEqual(len(list(self.project.rglob("*.xml"))), 1)

    def test_wrong_module_or_package_rejected_without_side_effect(self):
        for module in ("../elsewhere", "app/../../bad", "."):
            with self.subTest(module=module), self.assertRaises(ComponentError):
                plan(self.project, module, self.manifest, "android-xml")
        for package in ("dev", "dev.aya;hack", "dev/aya"):
            with self.subTest(package=package), self.assertRaises(ComponentError):
                plan(self.project, "app", self.manifest, "kotlin", package)

    def test_existing_app_file_is_never_overwritten(self):
        files = plan(self.project, "app", self.manifest, "kotlin", "dev.aya.host")
        file = next(iter(files))
        file.parent.mkdir(parents=True)
        file.write_text("private source", encoding="utf-8")
        with self.assertRaises(ComponentError):
            apply_plan(self.project, files)
        self.assertEqual(file.read_text(encoding="utf-8"), "private source")

    def test_symlink_escape_rejected(self):
        outside = self.project / "outside"
        outside.mkdir()
        java = self.project / "app/src/main/java"
        java.symlink_to(outside, target_is_directory=True)
        with self.assertRaises(ComponentError):
            plan(self.project, "app", self.manifest, "kotlin", "dev.aya.host")
        self.assertEqual(list(outside.iterdir()), [])

    def test_action_cannot_generate_xml(self):
        action = copy.deepcopy(self.manifest)
        action["presentation"] = {"kind": "action", "askQuestion": True}
        with self.assertRaises(ComponentError):
            plan(self.project, "app", action, "android-xml")


if __name__ == "__main__":
    unittest.main()
