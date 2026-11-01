"""Guarantee Expo's cheap source and expensive native acceptance stay distinct."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / ".github" / "workflows"


class ExpoCIGatesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / "expo-module.yml").read_text(encoding="utf-8")
        cls.packed = (ROOT / "expo-packed-host.yml").read_text(encoding="utf-8")
        cls.js = (ROOT / "expo-packed-js.yml").read_text(encoding="utf-8")

    def test_typed_contracts_keep_fast_typescript_and_negative_cases(self):
        self.assertIn("types-and-contracts:", self.source)
        self.assertIn("npm run typecheck", self.source)
        self.assertIn("npm test", self.source)
        for critical in ("integrations/expo/aya-expo/**", "integrations/expo/guide-plugin/**",
                         "aya/**", ".github/workflows/expo-module.yml"):
            self.assertEqual(self.source.count("'" + critical + "'"), 2)

    def test_one_authoritative_native_apk_gate(self):
        self.assertNotIn("real-android-host-apk:", self.source)
        self.assertNotIn(":app:assembleDebug", self.source)
        self.assertNotIn("gradle :aya:publish", self.source)
        self.assertIn("clean-packed-consumer:", self.packed)
        for action in ("npm pack", "expo prebuild --platform android", ":app:assembleDebug",
                       "tools/verify_flutter_host_apk.py",
                       "tools/verify_android_adapter_apk.py",
                       "AyaShareSelectionReceiver"):
            self.assertIn(action, self.packed)

    def test_authoritative_native_gate_dispatched_for_all_shared_code(self):
        # Validate both pull_request and main push paths. Do not let a
        # source-only check pass when shared native API changes were untested.
        for critical in ("integrations/expo/aya-expo/**",
                         "integrations/expo/guide-plugin/**",
                         "aya/**", ".github/workflows/expo-packed-host.yml",
                         "tools/verify_flutter_host_apk.py",
                         "tools/verify_android_adapter_apk.py"):
            self.assertEqual(self.packed.count("'" + critical + "'"), 2, critical)

    def test_js_bundle_retains_independent_metro_contract(self):
        self.assertIn("npm pack", self.js)
        self.assertIn("expo export --platform android", self.js)
        self.assertIn("aya-expo-guide", self.js)


if __name__ == "__main__":
    unittest.main()
