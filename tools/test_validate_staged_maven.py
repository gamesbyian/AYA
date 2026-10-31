import io
import tempfile
import unittest
import zipfile
from pathlib import Path

from validate_staged_maven import REQUIRED_CLASSES, check

NS = 'xmlns="http://maven.apache.org/POM/4.0.0"'


def pom(artifact: str, version: str, dependency: str = '') -> str:
    return f"""<project {NS}>
      <modelVersion>4.0.0</modelVersion>
      <groupId>dev.aya</groupId><artifactId>{artifact}</artifactId><version>{version}</version>
      <dependencies>{dependency}</dependencies>
    </project>"""


def aar_fixture(artifact, *, missing_class=None, entry_override=None) -> bytes:
    class_bytes = io.BytesIO()
    with zipfile.ZipFile(class_bytes, "w") as output:
        for cls in REQUIRED_CLASSES[artifact]:
            if cls != missing_class:
                output.writestr(cls, b"classfile fixture bytes")
    result = io.BytesIO()
    with zipfile.ZipFile(result, "w") as output:
        output.writestr("AndroidManifest.xml", b"<manifest/>")
        output.writestr("classes.jar", class_bytes.getvalue())
        if entry_override:
            output.writestr(entry_override, b"foreign path")
    return result.getvalue()


class StagedMavenTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.version = '0.1.0-preview.1'
        for artifact in ('aya-android', 'aya-compose'):
            folder = self.root / 'dev' / 'aya' / artifact / self.version
            folder.mkdir(parents=True)
            (folder / f'{artifact}-{self.version}.aar').write_bytes(aar_fixture(artifact))
            dependency = '' if artifact == 'aya-android' else f"""<dependency>
              <groupId>dev.aya</groupId><artifactId>aya-android</artifactId>
              <version>{self.version}</version></dependency>"""
            (folder / f'{artifact}-{self.version}.pom').write_text(
                pom(artifact, self.version, dependency))

    def artifact_path(self, name):
        return self.root / 'dev' / 'aya' / name / self.version / f'{name}-{self.version}.aar'

    def test_valid_coordinates_dependencies_and_published_classes(self):
        self.assertEqual(len(check(self.root, self.version)), 4)

    def test_missing_aar_refuses(self):
        self.artifact_path('aya-compose').unlink()
        with self.assertRaises(ValueError):
            check(self.root, self.version)

    def test_rejects_placeholder_bytes_instead_of_real_aar(self):
        self.artifact_path('aya-android').write_bytes(b'fixture-aar')
        with self.assertRaisesRegex(ValueError, "Corrupt published AAR"):
            check(self.root, self.version)

    def test_rejects_missing_required_compiled_class(self):
        self.artifact_path('aya-android').write_bytes(
            aar_fixture('aya-android', missing_class='dev/aya/android/AyaReferenceVerifier.class'))
        with self.assertRaisesRegex(ValueError, "Missing compiled dev/aya/android/AyaReferenceVerifier.class"):
            check(self.root, self.version)

    def test_rejects_unsafe_aar_entries(self):
        for path in ('../foreign', '/absolute', 'folder\\foreign'):
            with self.subTest(path=path):
                self.artifact_path('aya-compose').write_bytes(
                    aar_fixture('aya-compose', entry_override=path))
                with self.assertRaisesRegex(ValueError, "Unsafe AAR"):
                    check(self.root, self.version)

    def test_rejects_damaged_classes_jar(self):
        path = self.artifact_path('aya-android')
        with zipfile.ZipFile(path, 'w') as output:
            output.writestr('AndroidManifest.xml', b'<manifest/>')
            output.writestr('classes.jar', b'bad jar bytes')
        with self.assertRaisesRegex(ValueError, "Corrupt published AAR"):
            check(self.root, self.version)

    def test_rejects_pathological_zip_member_counts_before_decompression(self):
        path = self.artifact_path('aya-compose')
        with zipfile.ZipFile(path, 'w') as output:
            output.writestr('AndroidManifest.xml', b'<manifest/>')
            output.writestr('classes.jar', b'placeholder')
            for index in range(20_001):
                output.writestr(f'padding/{index}', b'')
        with self.assertRaisesRegex(ValueError, 'expansion exceeds inspection budget'):
            check(self.root, self.version)

    def test_bad_compose_dependency_refuses(self):
        path = self.root / 'dev/aya/aya-compose/0.1.0-preview.1/aya-compose-0.1.0-preview.1.pom'
        path.write_text(path.read_text().replace('0.1.0-preview.1</version></dependency>',
                                                   '0.1.0-preview.0</version></dependency>'))
        with self.assertRaises(ValueError):
            check(self.root, self.version)

    def test_snapshot_version_refuses(self):
        with self.assertRaises(ValueError):
            check(self.root, '0.1.0-SNAPSHOT')


if __name__ == '__main__':
    unittest.main()
