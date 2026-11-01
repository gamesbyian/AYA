"""Negative and successful tests for a truly out-of-tree packed Expo host."""
import io
import json
import tarfile
import tempfile
import unittest
from pathlib import Path

from prepare_expo_packed_host import PackedHostError, prepare

MODULE_FILES = (
    "android/build.gradle", "android/src/main/java/dev/aya/expo/AyaExpoModule.kt",
    "expo-module.config.json", "src/index.ts", "src/AyaHelpCard.tsx", "src/native.ts"
)


class PackedExpoHostTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.fixture = self.root / "fixture"
        self.fixture.mkdir()
        self.dest = self.root / "host with spaces"
        self.module = self.root / "aya-expo-0.1.0-dev.1.tgz"
        self.guide = self.root / "aya-expo-guide-0.1.0-dev.1.tgz"
        for filename in ("App.tsx", "app.json", "aya-guide.md"):
            (self.fixture / filename).write_text("source: " + filename)
        self.package = {
            "name": "aya-expo-ci-host",
            "dependencies": {
                "aya-expo": "file:..",
                "aya-expo-guide": "file:../../guide-plugin",
                "expo": "~57.0.31"
            }
        }
        self.write_package()
        self.write_tgz(self.module, "aya-expo",
                       MODULE_FILES)
        self.write_tgz(self.guide, "aya-expo-guide",
                       ("app.plugin.js", "guide_asset.cjs"))

    def write_package(self):
        (self.fixture / "package.json").write_text(json.dumps(self.package))

    def write_tgz(self, path, name, extra, *, version="0.1.0-dev.1", symlink=False):
        with tarfile.open(path, "w:gz") as archive:
            entries = {"package/package.json": json.dumps({
                "name": name, "version": version
            }).encode()}
            entries.update({f"package/{file}": b"checked-in source" for file in extra})
            for filename, body in entries.items():
                info = tarfile.TarInfo(filename)
                info.size = len(body)
                archive.addfile(info, io.BytesIO(body))
            if symlink:
                info = tarfile.TarInfo("package/foreign")
                info.type = tarfile.SYMTYPE
                info.linkname = "../../outside"
                archive.addfile(info)

    def run_prepare(self):
        return prepare(self.fixture, self.dest, self.module, self.guide)

    def test_isolated_host_contains_only_explicit_fixture_and_packed_dependencies(self):
        (self.fixture / "node_modules").mkdir()
        (self.fixture / "node_modules" / "stale.js").write_text("must not copy")
        (self.fixture / "android").mkdir()
        (self.fixture / "android" / "build.gradle").write_text("stale")
        result = self.run_prepare()
        self.assertEqual(result["versions"]["aya-expo"], "0.1.0-dev.1")
        host = json.loads((self.dest / "package.json").read_text())
        for name in ("aya-expo", "aya-expo-guide"):
            self.assertTrue(host["dependencies"][name].startswith("file:///"))
            self.assertTrue(host["dependencies"][name].endswith(".tgz"))
        self.assertEqual(host["dependencies"]["expo"], "~57.0.31")
        self.assertFalse((self.dest / "node_modules").exists())
        self.assertFalse((self.dest / "android").exists())
        self.assertEqual((self.dest / "aya-guide.md").read_text(),
                         (self.fixture / "aya-guide.md").read_text())

    def test_fails_if_existing_host_would_be_overwritten(self):
        self.dest.mkdir()
        with self.assertRaisesRegex(PackedHostError, "Destination must be absent"):
            self.run_prepare()

    def test_fails_if_fixture_references_wrong_module_source(self):
        self.package["dependencies"]["aya-expo"] = "file:/tmp/unknown"
        self.write_package()
        with self.assertRaisesRegex(PackedHostError, "source dependency contract"):
            self.run_prepare()

    def test_fails_if_undeclared_local_dependency_exists(self):
        self.package["dependencies"]["extra"] = "file:../secret"
        self.write_package()
        with self.assertRaisesRegex(PackedHostError, "Undeclared local dependency"):
            self.run_prepare()

    def test_fails_if_package_name_is_wrong(self):
        self.write_tgz(self.guide, "malicious-guide",
                       ("app.plugin.js", "guide_asset.cjs"))
        with self.assertRaisesRegex(PackedHostError, "Incorrect package name"):
            self.run_prepare()

    def test_fails_if_required_native_module_source_was_not_packed(self):
        self.write_tgz(self.module, "aya-expo", ("src/index.ts",))
        with self.assertRaisesRegex(PackedHostError, "Missing packaged source"):
            self.run_prepare()

    def test_fails_if_tarball_contains_symlink(self):
        self.write_tgz(self.guide, "aya-expo-guide",
                       ("app.plugin.js", "guide_asset.cjs"), symlink=True)
        with self.assertRaisesRegex(PackedHostError, "Unsafe or unexpected"):
            self.run_prepare()

    def test_fails_if_fixture_guide_is_symlink(self):
        (self.fixture / "aya-guide.md").unlink()
        (self.fixture / "aya-guide.md").symlink_to(self.fixture / "app.json")
        with self.assertRaisesRegex(PackedHostError, "Unsafe or absent"):
            self.run_prepare()

    def test_fails_if_package_leaks_test_or_node_modules(self):
        self.write_tgz(self.module, "aya-expo", MODULE_FILES + ("node_modules/secret.js",))
        with self.assertRaisesRegex(PackedHostError, "leaked into npm"):
            self.run_prepare()

    def test_rejects_non_semantic_package_versions(self):
        self.write_tgz(self.module, "aya-expo",
                       MODULE_FILES,
                       version="not-a-version")
        with self.assertRaisesRegex(PackedHostError, "Incorrect package name or version"):
            self.run_prepare()


if __name__ == "__main__":
    unittest.main()
