"""Deterministic checksum/source provenance checks for unpublished Maven previews."""
import hashlib
import tempfile
import unittest
from pathlib import Path

from write_maven_preview_manifest import create_manifest, PreviewManifestError

VERSION = "0.1.0-preview.1"
SOURCE = "a" * 40


class PreviewManifestTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "maven"
        self.root.mkdir()
        self.checksums = Path(self.temp.name) / "sha256.txt"
        lines = []
        for artifact in ("aya-android", "aya-compose"):
            for ext in ("aar", "pom"):
                relative = f"dev/aya/{artifact}/{VERSION}/{artifact}-{VERSION}.{ext}"
                target = self.root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((relative + "-fixture").encode())
                digest = hashlib.sha256(target.read_bytes()).hexdigest()
                lines.append(f"{digest}  {relative}")
        self.checksums.write_text("\n".join(reversed(lines)) + "\n")

    def check(self, **kwargs):
        return create_manifest(kwargs.get("root", self.root),
                               kwargs.get("checksums", self.checksums),
                               kwargs.get("version", VERSION),
                               kwargs.get("commit", SOURCE))

    def test_deterministic_sorted_provenance(self):
        first = self.check()
        second = self.check()
        self.assertEqual(first, second)
        self.assertEqual(first["schema_version"], "aya-maven-preview-manifest/v1")
        self.assertEqual(first["distribution_status"], "unpublished-preview")
        self.assertEqual(first["source_commit"], SOURCE)
        self.assertEqual(len(first["artifacts"]), 4)
        paths = [item["path"] for item in first["artifacts"]]
        self.assertEqual(paths, sorted(paths))
        self.assertTrue(all(item["size_bytes"] > 0 for item in first["artifacts"]))

    def test_refuses_modified_bytes(self):
        next(self.root.rglob("*.aar")).write_bytes(b"tampered")
        with self.assertRaisesRegex(PreviewManifestError, "SHA-256 mismatch"):
            self.check()

    def test_refuses_untracked_or_missing_artifact(self):
        content = self.checksums.read_text()
        self.checksums.write_text("\n".join(content.splitlines()[1:]) + "\n")
        with self.assertRaisesRegex(PreviewManifestError, "exactly"):
            self.check()

    def test_refuses_duplicate_hash_line(self):
        text = self.checksums.read_text()
        self.checksums.write_text(text + text.splitlines()[0] + "\n")
        with self.assertRaisesRegex(PreviewManifestError, "Duplicate"):
            self.check()

    def test_refuses_wrong_version_and_commit(self):
        for version in ("0.1.0-SNAPSHOT", "not-a-version"):
            with self.subTest(version=version), self.assertRaises(PreviewManifestError):
                self.check(version=version)
        with self.assertRaisesRegex(PreviewManifestError, "source commit"):
            self.check(commit="main")

    def test_refuses_path_traversal_even_with_valid_digest(self):
        text = self.checksums.read_text()
        line = text.splitlines()[0].split("  ")[0]
        self.checksums.write_text(text + f"{line}  ../foreign.aar\n")
        with self.assertRaisesRegex(PreviewManifestError, "Unsafe checksum path"):
            self.check()

    def test_refuses_symlinked_artifact(self):
        target = next(self.root.rglob("*.aar"))
        replacement = target.with_suffix(".saved")
        target.rename(replacement)
        target.symlink_to(replacement)
        with self.assertRaisesRegex(PreviewManifestError, "symlinks"):
            self.check()


if __name__ == "__main__":
    unittest.main()
