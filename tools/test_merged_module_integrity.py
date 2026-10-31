"""Regression guard against a merge accidentally deleting independent AYA modules.

Structural checks complement, and do not replace, Android device tests,
reference audits or independently verified host import behaviour.
"""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class MergedModuleIntegrityTest(unittest.TestCase):
    def test_output_return_module_is_not_erased_by_adapter_merges(self):
        for relative in (
            "aya/src/main/java/dev/aya/android/AyaOutputImport.kt",
            "aya/src/main/java/dev/aya/android/AyaImportDialogs.kt",
            "aya/src/main/java/dev/aya/android/AyaShareTargetHints.kt",
            "docs/OUTPUT_RETURN_IMPORT.md",
            "docs/output/aya-output-envelope-v1.schema.json",
            "sample/src/androidTest/java/dev/aya/sample/AyaOutputImportTest.kt",
        ):
            with self.subTest(path=relative):
                self.assertTrue((ROOT / relative).is_file(), relative)
        card = (ROOT / "aya/src/main/java/dev/aya/android/AyaCardView.kt").read_text()
        self.assertIn("onImportRequested", card)
        self.assertIn("onAskRequested", card)
        self.assertIn("questionHint", card)

    def test_editor_adapters_share_canonical_review_instead_of_forking_it(self):
        compose = (ROOT / "aya-compose/src/main/java/dev/aya/compose/AyaCompose.kt").read_text()
        xml = (ROOT / "aya/src/main/java/dev/aya/android/AyaXmlCardView.kt").read_text()
        self.assertIn("AyaCardView(", compose)
        self.assertIn("AyaCardView(", xml)
        self.assertNotIn("ACTION_SEND", compose)
        self.assertNotIn("ACTION_SEND", xml)
        generator = (ROOT / "tools/component_codegen.py").read_text()
        for fmt in ('"kotlin"', '"compose"', '"android-xml"'):
            self.assertIn(fmt, generator)

    def test_espresso_regression_is_not_replaced_by_brittle_window_lookup(self):
        source = (ROOT / "sample/src/androidTest/java/dev/aya/sample/QuestionFlowTest.kt").read_text()
        self.assertIn("androidx.test.espresso.Espresso", source)
        self.assertNotIn("dumpWindowHierarchy", source)


if __name__ == "__main__":
    unittest.main()
