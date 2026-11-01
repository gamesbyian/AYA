"""Guard against reintroducing a shared generic FileProvider manifest node.

Android's manifest merger keys <provider> by android:name. If AYA and
another SDK both declare androidx.core.content.FileProvider directly, merging
their distinct authorities/path metadata fails or silently discards one.
"""
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "aya" / "src" / "main" / "AndroidManifest.xml"
SOURCE = ROOT / "aya" / "src" / "main" / "java" / "dev" / "aya" / "android" / "AyaFileProvider.kt"
NS = "{http://schemas.android.com/apk/res/android}"


class AyaProviderIsolationTest(unittest.TestCase):
    def test_manifest_declares_exactly_one_distinct_aya_provider(self):
        root = ET.parse(MANIFEST).getroot()
        app = root.find("application")
        self.assertIsNotNone(app)
        providers = app.findall("provider")
        self.assertEqual(len(providers), 1)
        provider = providers[0]
        self.assertEqual(provider.get(NS + "name"), "dev.aya.android.AyaFileProvider")
        self.assertEqual(provider.get(NS + "authorities"), "${applicationId}.aya.files")
        self.assertEqual(provider.get(NS + "exported"), "false")
        self.assertEqual(provider.get(NS + "grantUriPermissions"), "true")
        metadata = provider.findall("meta-data")
        self.assertEqual(len(metadata), 1)
        self.assertEqual(metadata[0].get(NS + "name"),
                         "android.support.FILE_PROVIDER_PATHS")
        self.assertEqual(metadata[0].get(NS + "resource"), "@xml/aya_file_paths")
        self.assertNotEqual(provider.get(NS + "name"),
                            "androidx.core.content.FileProvider")

    def test_provider_is_plain_androidx_subclass_without_overridden_security(self):
        source = SOURCE.read_text(encoding="utf-8")
        self.assertIn("class AyaFileProvider : FileProvider()", source)
        for disallowed in ("override fun openFile", "override fun query",
                           "override fun attachInfo", "override fun getType",
                           "override fun onCreate", "override fun getUriForFile"):
            self.assertNotIn(disallowed, source)

    def test_aya_uri_authority_is_unchanged(self):
        share = (ROOT / "aya" / "src" / "main" / "java" / "dev" / "aya" /
                 "android" / "AyaShareIntents.kt").read_text(encoding="utf-8")
        self.assertIn(".aya.files", share)
        instrumented = (ROOT / "aya" / "src" / "androidTest" / "java" /
                        "dev" / "aya" / "android" /
                        "AyaShareIntentsTest.kt").read_text(encoding="utf-8")
        self.assertIn("ayaProviderIsIndependentAndNotExported", instrumented)
        self.assertIn("AyaFileProvider::class.java.name", instrumented)


if __name__ == "__main__":
    unittest.main()
