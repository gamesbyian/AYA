"""Source/digest identity tests for the unsigned AYA Maven preview manifest."""
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from maven_preview_provenance import ProvenanceError, build_manifest, main, write_manifest
from test_validate_staged_maven import aar_fixture, pom
from validate_staged_maven import check


class MavenPreviewProvenanceTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "maven"
        self.version = "0.1.0-preview.1"
        for artifact in ("aya-android", "aya-compose"):
            folder = self.root / "dev" / "aya" / artifact / self.version
            folder.mkdir(parents=True)
            (folder / f"{artifact}-{self.version}.aar").write_bytes(aar_fixture(artifact))
            dep = "" if artifact == "aya-android" else (
                "<dependency><groupId>dev.aya</groupId>"
                "<artifactId>aya-android</artifactId>"
                f"<version>{self.version}</version></dependency>"
            )
            (folder / f"{artifact}-{self.version}.pom").write_text(
                pom(artifact, self.version, dep)
            )
        digests = check(self.root, self.version)
        self.checksums = Path(self.tmp.name) / "aya-staging-sha256.txt"
        self.checksums.write_text(
            "".join(f"{digest}  {name}\n" for name, digest in sorted(digests.items()))
        )
        self.kwargs = {
            "repository": "gamesbyian/AYA",
            "run_id": "987654",
            "attempt": "1",
            "java": 'openjdk version "17.0.21" 2026-10-31',
            "gradle": "Gradle 8.9"
        }

    def manifest(self, **changes):
        data = dict(self.kwargs)
        data.update(changes)
        return build_manifest(self.root, self.version, "a" * 40,
                              self.checksums, **data)

    def test_valid_unsigned_provenance_has_all_digest_files_and_limits(self):
        result = self.manifest()
        self.assertEqual(result["schema"], "aya-maven-preview-evidence/v1")
        self.assertEqual(len(result["artifacts_sha256"]), 4)
        self.assertEqual(result["source_commit"], "a" * 40)
        self.assertEqual(result["workflow_run_url"],
                         "https://github.com/gamesbyian/AYA/actions/runs/987654")
        self.assertFalse(result["validation"]["signed_attestation"])
        self.assertFalse(result["validation"]["public_repository_upload"])
        self.assertIn("not a signed attestation", result["limitations"])

    def test_wrong_source_commit_rejected(self):
        with self.assertRaisesRegex(ProvenanceError, "complete source commit"):
            build_manifest(self.root, self.version, "short", self.checksums,
                           **self.kwargs)

    def test_checksum_manifest_must_match_all_verified_bytes(self):
        self.checksums.write_text(self.checksums.read_text().replace("a", "0", 1))
        with self.assertRaisesRegex(ProvenanceError, "differs from verified"):
            self.manifest()

    def test_missing_staged_binary_fails(self):
        (self.root / f"dev/aya/aya-compose/{self.version}/aya-compose-{self.version}.aar").unlink()
        with self.assertRaises(ValueError):
            self.manifest()

    def test_bad_workflow_identity_fails(self):
        for data in ({"repository": "../../spoof"},
                     {"run_id": "NaN"}, {"attempt": "-1"}):
            with self.subTest(data=data), self.assertRaises(ProvenanceError):
                self.manifest(**data)

    def test_unknown_toolchain_fails_without_fabrication(self):
        for data in ({"java": ""}, {"gradle": "Gradle 8.9\nSECRET=bad"}):
            with self.subTest(data=data), self.assertRaisesRegex(
                ProvenanceError, "toolchain identity"
            ):
                self.manifest(**data)

    def test_refuses_to_replace_linked_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "original.json").write_text("foreign")
            (root / "link.json").symlink_to(root / "original.json")
            with self.assertRaisesRegex(ProvenanceError, "symlinked"):
                write_manifest(root / "link.json", self.manifest())
            self.assertEqual((root / "original.json").read_text(), "foreign")

    def test_cli_writes_parsable_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp) / "manifest.json"
            args = [
                "--root", str(self.root),
                "--version", self.version,
                "--checksums", str(self.checksums),
                "--source-sha", "b" * 40,
                "--repository", "gamesbyian/AYA",
                "--run-id", "123",
                "--attempt", "2",
                "--java", "OpenJDK 17",
                "--gradle", "Gradle 8.9",
                "--output", str(destination)
            ]
            with redirect_stdout(io.StringIO()):
                self.assertEqual(main(args), 0)
            value = json.loads(destination.read_text())
            self.assertEqual(value["source_commit"], "b" * 40)
            self.assertEqual(value["workflow_run_attempt"], 2)


if __name__ == "__main__":
    unittest.main()
