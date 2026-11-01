"""Fail-closed source/CI contracts for the optional App Inventor AYA adapter.

Passing these checks is not evidence that an App Inventor-built consuming APK
merges the provider or can actually open native review.
"""
import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXT = ROOT / "integrations" / "app-inventor" / "aya-rush"


class AppInventorSourceContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.java = (EXT / "src/dev/aya/appinventor/AyaHelp.java").read_text()
        cls.rush = (EXT / "rush.yml").read_text()
        cls.manifest = ET.parse(EXT / "src/AndroidManifest.xml").getroot()
        cls.workflow = (ROOT / ".github/workflows/app-inventor.yml").read_text()

    def test_extension_only_exposes_guarded_help_not_a_direct_share_or_agent_api(self):
        self.assertIn("@Extension(", self.java)
        self.assertIn("extends AndroidNonvisibleComponent", self.java)
        self.assertIn("new AyaComponentAction.Help(", self.java)
        self.assertIn("@Asset String guideAsset", self.java)
        self.assertIn('SAFE_GUIDE.matcher(guideAsset)', self.java)
        self.assertIn('LocalStatus("rejected"', self.java)
        self.assertIn('LocalStatus("review_opened"', self.java)
        self.assertIn('LocalStatus("question_opened"', self.java)
        for forbidden in (
            "ACTION_SEND", "ACTION_CHOOSER", "startActivity(", "http://",
            "https://api.", "Aya.launch(", "launchUnsafe(", "sendToAssistant(",
        ):
            self.assertNotIn(forbidden, self.java)
        self.assertNotIn("onAgentResponse", self.java)

    def test_app_inventor_blocks_are_valid_named_and_nonblocking(self):
        self.assertIn("public String HostIdentity()", self.java)
        self.assertIn("public void OpenHelp(", self.java)
        self.assertIn("public void LocalStatus(", self.java)
        self.assertEqual(self.java.count("@SimpleFunction"), 2)
        self.assertEqual(self.java.count("@SimpleEvent"), 1)
        self.assertIn("Looper.getMainLooper()", self.java)
        self.assertIn('form.isDestroyed()', self.java)
        self.assertIn('getPackageInfo(form.getPackageName(), 0)', self.java)

    def test_manifest_does_not_duplicate_aya_provider_or_add_permissions(self):
        self.assertEqual(self.manifest.tag, "manifest")
        self.assertEqual(self.manifest.attrib["package"], "dev.aya.appinventor")
        self.assertEqual([x.tag for x in self.manifest], ["application"])
        self.assertEqual(len(list(self.manifest.find("application"))), 0)
        self.assertFalse((EXT / "deps" / "aya-debug.aar").exists(),
                         "Generated AAR belongs in CI, not source control")

    def test_rush_toolchain_and_library_compatibility_are_explicit(self):
        self.assertRegex(self.rush, r"(?m)^version: '0\.1\.0'$")
        self.assertIn("min_sdk: 23", self.rush)
        self.assertIn("- aya-debug.aar", self.rush)
        self.assertIn("- org.jetbrains.kotlin:kotlin-stdlib:2.0.21", self.rush)
        self.assertIn("- androidx.core:core:1.15.0", self.rush)
        self.assertIn("androidx.core:core: provided", self.rush)
        self.assertNotIn("androidx.compose", self.rush)

    def test_real_aix_builder_is_immutable_read_only_and_does_not_release(self):
        action = "shreyashsaitwal/rush-cli@8d9d79cc0573ac01bf56cb676ddf476323e10385"
        self.assertIn(action, self.workflow)
        self.assertIn("version: 2.1.2", self.workflow)
        self.assertIn("gradle :aya:assembleDebug", self.workflow)
        self.assertIn("rush build", self.workflow)
        self.assertIn("zipfile.is_zipfile(file)", self.workflow)
        self.assertIn("any(name.endswith('.dex')", self.workflow)
        self.assertIn("contents: read", self.workflow)
        self.assertNotIn("gh release create", self.workflow)
        self.assertNotIn("permissions:\n      contents: write", self.workflow)
        for path in (
            "integrations/app-inventor/**", "aya/**", "build.gradle.kts",
            ".github/workflows/app-inventor.yml"
        ):
            self.assertEqual(self.workflow.count("'" + path + "'"), 2, path)


if __name__ == "__main__":
    unittest.main()
