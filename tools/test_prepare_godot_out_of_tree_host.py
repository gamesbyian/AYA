"""Test clean Godot packed consumer copy, rejection and source boundaries."""
import tempfile
import unittest
from pathlib import Path

from prepare_godot_out_of_tree_host import (
    ADDON_FILES, FIXTURE_FILES, HostPreparationError, prepare,
)


class GodotConsumerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.fixture = self.root / "fixture"
        self.addon = self.root / "staged addon"
        self.dest = self.root / "consumer with spaces"
        for file in FIXTURE_FILES:
            path = self.fixture / file
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("first-party fixture " + file)
        for file in ADDON_FILES:
            path = self.addon / file
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"AAR compiled artifact" if file.endswith(".aar") else
                             ("addon " + file).encode())

    def run_prepare(self):
        return prepare(self.fixture, self.addon, self.dest)

    def test_copies_only_explicit_files_from_compiled_addon(self):
        (self.fixture / "android/build").mkdir(parents=True)
        (self.fixture / "android/build/build.gradle").write_text("stale")
        (self.fixture / ".godot").mkdir()
        (self.fixture / ".godot/generated").write_text("stale")
        (self.addon / "bin/debug/rogue.aar").write_bytes(b"foreign")
        report = self.run_prepare()
        self.assertEqual(report["schema"], "aya-godot-packaged-consumer/v1")
        self.assertTrue(report["synthetic_host"])
        self.assertFalse(report["compiled_godot_export"])
        self.assertFalse(report["actual_recipient_verified"])
        self.assertFalse((self.dest / "android").exists())
        self.assertFalse((self.dest / ".godot").exists())
        self.assertFalse((self.dest / "addons/AYA/bin/debug/rogue.aar").exists())
        for name in FIXTURE_FILES:
            self.assertEqual((self.fixture / name).read_bytes(),
                             (self.dest / name).read_bytes())
        for name in ADDON_FILES:
            self.assertEqual((self.addon / name).read_bytes(),
                             (self.dest / "addons/AYA" / name).read_bytes())

    def test_existing_destination_refused_without_overwrite(self):
        self.dest.mkdir()
        (self.dest / "foreign.txt").write_text("user file")
        with self.assertRaisesRegex(HostPreparationError, "must not already exist"):
            self.run_prepare()
        self.assertEqual((self.dest / "foreign.txt").read_text(), "user file")

    def test_refuses_missing_required_addon_binary(self):
        (self.addon / "bin/release/aya-release.aar").unlink()
        with self.assertRaisesRegex(HostPreparationError, "Missing"):
            self.run_prepare()
        self.assertFalse(self.dest.exists())

    def test_refuses_symlinked_fixture_file(self):
        path = self.fixture / "ci-host/aya-guide.md"
        path.unlink()
        path.symlink_to(self.fixture / "project.godot")
        with self.assertRaisesRegex(HostPreparationError, "symlinked"):
            self.run_prepare()
        self.assertFalse(self.dest.exists())

    def test_refuses_symlinked_native_binary(self):
        path = self.addon / "bin/debug/aya-debug.aar"
        path.unlink()
        path.symlink_to(self.fixture / "project.godot")
        with self.assertRaisesRegex(HostPreparationError, "symlinked"):
            self.run_prepare()

    def test_refuses_empty_or_unreasonably_large_binary(self):
        path = self.addon / "bin/debug/aya-debug.aar"
        path.write_bytes(b"")
        with self.assertRaisesRegex(HostPreparationError, "Invalid source size"):
            self.run_prepare()
        path.write_bytes(b"x" * (12 * 1024 * 1024 + 1))
        with self.assertRaisesRegex(HostPreparationError, "Invalid source size"):
            self.run_prepare()

    def test_destination_cannot_be_inside_fixture_or_addon(self):
        with self.assertRaisesRegex(HostPreparationError, "outside fixture"):
            prepare(self.fixture, self.addon, self.fixture / "new")
        with self.assertRaisesRegex(HostPreparationError, "outside fixture"):
            prepare(self.fixture, self.addon, self.addon / "new")

    def test_source_symlinked_parent_is_not_allowed(self):
        # Source directory traversal is grounded to the verified source root.
        outside = self.root / "foreign"
        outside.mkdir()
        (outside / "runtime_probe_card.gd").write_text("foreign")
        folder = self.fixture / "ci-host"
        for file in list(folder.iterdir()):
            file.unlink()
        folder.rmdir()
        folder.symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(HostPreparationError, "escapes source root"):
            self.run_prepare()


if __name__ == "__main__":
    unittest.main()
