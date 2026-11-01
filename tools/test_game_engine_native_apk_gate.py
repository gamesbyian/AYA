"""Keep both AYA game-engine bridges in the same real APK packaging gate."""
import unittest
from pathlib import Path

WORKFLOW = (
    Path(__file__).resolve().parents[1] / ".github" / "workflows" / "unity-apk.yml"
)


class GameEngineAPKGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.content = WORKFLOW.read_text(encoding="utf-8")

    def test_godot_and_unity_code_changes_dispatch_single_packaging_job(self):
        for path in ("aya-godot/**", "aya-unity/**", "aya/**", "sample/**",
                     "tools/verify_android_manifest_metadata.py",
                     ".github/workflows/unity-apk.yml"):
            self.assertEqual(self.content.count("'" + path + "'"), 2, path)
        self.assertEqual(self.content.count("    runs-on: ubuntu-latest"), 1)
        self.assertEqual(self.content.count(":sample:assembleDebug"), 1)

    def test_both_native_bridges_and_scoped_receiver_are_defined_in_actual_dex(self):
        for symbol in ("project(':aya-godot')", "project(':aya-unity')",
                       "dev.aya.godot.AyaGodotPlugin",
                       "dev.aya.unity.AyaUnityBridge",
                       "dev.aya.android.AyaShareSelectionReceiver",
                       "tools/verify_android_adapter_apk.py"):
            self.assertIn(symbol, self.content)
        self.assertIn("tools/verify_flutter_host_apk.py", self.content)

    def test_v2_plugin_registration_metadata_is_binary_inspected(self):
        self.assertIn("--name org.godotengine.plugin.v2.AYA", self.content)
        self.assertIn("--value dev.aya.godot.AyaGodotPlugin", self.content)
        self.assertIn("tools/verify_android_manifest_metadata.py", self.content)

    def test_claims_are_not_engine_export_or_assistant_receipt(self):
        self.assertIn("neither a Unity nor a Godot engine-generated Android export",
                      self.content)


if __name__ == "__main__":
    unittest.main()
