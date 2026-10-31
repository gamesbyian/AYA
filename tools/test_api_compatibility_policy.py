"""Guard documented AYA native API policy against accidental source drift.

This static test supplements Gradle API and installed-app acceptance tests;
it does not prove binary compatibility or recipient ingestion.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AYA = ROOT / "aya/src/main/java/dev/aya/android/Aya.kt"
VERIFIER = ROOT / "aya/src/main/java/dev/aya/android/AyaReferenceVerifier.kt"
ACTIONS = ROOT / "aya/src/main/java/dev/aya/android/AyaComponentAction.kt"
POLICY = ROOT / "docs/API_COMPATIBILITY.md"


class NativeApiPolicyTest(unittest.TestCase):
    def test_documented_public_surface_still_exists(self):
        source = AYA.read_text()
        for api in (
            "ask", "launch", "launchBundled", "launchCreativeBundled",
            "launchTranslationBundled", "launchFilesystemBundled",
        ):
            with self.subTest(api=api):
                self.assertRegex(source, rf"\bfun\s+{api}\s*\(")
                self.assertIn(f"`Aya.{api}`", POLICY.read_text())
        for result in ("QuestionOpened", "PreviewOpened", "Rejected"):
            self.assertIn(result, source)
        self.assertIn("AyaComponentAction.Help", ACTIONS.read_text() +
                      POLICY.read_text())

    def test_manual_source_paths_are_not_secretly_version_guarded(self):
        source = AYA.read_text()
        start = source.index("    fun launch(activity: Activity, request: AyaRequest)")
        end = source.index("\n    }", start) + 6
        self.assertNotIn("AyaReferenceVerifier.verify", source[start:end])
        policy = POLICY.read_text()
        self.assertIn("Legacy/manual", policy)
        self.assertIn("No automatic version guard", policy)

    def test_v1_guide_guards_and_explicit_locale_limit_are_documented(self):
        code = VERIFIER.read_text()
        self.assertIn('values["app_id"] != installedPackageId', code)
        self.assertIn("min != installedVersion || max != installedVersion", code)
        self.assertIn('"locale"', code)
        self.assertNotIn("requestedLocale", code)
        docs = POLICY.read_text()
        self.assertIn("does not", docs)
        self.assertIn("locale", docs)
        self.assertIn("explicitly", docs)
        self.assertIn("AYA-RAS v1", docs)


if __name__ == "__main__":
    unittest.main()
