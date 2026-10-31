import tempfile
import unittest
from pathlib import Path
from validate_staged_maven import check

NS = 'xmlns="http://maven.apache.org/POM/4.0.0"'


def pom(artifact: str, version: str, dependency: str = '') -> str:
    return f"""<project {NS}>
      <modelVersion>4.0.0</modelVersion>
      <groupId>dev.aya</groupId><artifactId>{artifact}</artifactId><version>{version}</version>
      <dependencies>{dependency}</dependencies>
    </project>"""


class StagedMavenTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.version = '0.1.0-preview.1'
        for artifact in ('aya-android', 'aya-compose'):
            folder = self.root / 'dev' / 'aya' / artifact / self.version
            folder.mkdir(parents=True)
            (folder / f'{artifact}-{self.version}.aar').write_bytes(b'fixture-aar')
            dependency = '' if artifact == 'aya-android' else f"""<dependency>
              <groupId>dev.aya</groupId><artifactId>aya-android</artifactId>
              <version>{self.version}</version></dependency>"""
            (folder / f'{artifact}-{self.version}.pom').write_text(
                pom(artifact, self.version, dependency))

    def test_valid_coordinates_and_dependencies(self):
        self.assertEqual(len(check(self.root, self.version)), 4)

    def test_missing_aar_refuses(self):
        (self.root / 'dev/aya/aya-compose/0.1.0-preview.1/aya-compose-0.1.0-preview.1.aar').unlink()
        with self.assertRaises(ValueError):
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
