"""Structural guards for Unity Android AYA source preview, not Unity Editor QA."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UNITY = ROOT / "integrations/unity/com.aya.handoff"
NATIVE = ROOT / "aya-unity/src/main/java/dev/aya/unity/AyaUnityBridge.kt"


class UnitySourceContractTest(unittest.TestCase):
    def test_native_bridge_reuses_canonical_guarded_help_action(self):
        code = NATIVE.read_text()
        self.assertIn("AyaComponentAction.Help(", code)
        self.assertIn(").launch(activity, text = question)", code)
        self.assertIn("Looper.getMainLooper()", code)
        self.assertIn("activity.isFinishing", code)
        self.assertIn("activity.isDestroyed", code)
        self.assertIn("JSONObject()", code)
        self.assertNotIn("ACTION_SEND", code)
        self.assertNotIn("startActivity(", code)
        self.assertNotIn("UnitySendMessage", code)
        self.assertNotIn("onAgentAnswered", code)

    def test_java_bridge_and_project_staging(self):
        build = (ROOT / "aya-unity/build.gradle.kts").read_text()
        self.assertIn('implementation(project(":aya"))', build)
        self.assertIn('stageUnityPlugin', build)
        self.assertIn('":aya:assembleDebug"', build)
        self.assertIn('":aya:assembleRelease"', build)
        settings = (ROOT / "settings.gradle.kts").read_text()
        self.assertIn('":aya-unity"', settings)

    def test_upm_package_and_assembly_definitions(self):
        package = json.loads((UNITY / "package.json").read_text())
        self.assertEqual(package["name"], "dev.aya.handoff")
        self.assertIn("preview", package["version"])
        runtime = json.loads((UNITY / "Runtime/Aya.Handoff.asmdef").read_text())
        editor = json.loads((UNITY / "Editor/Aya.Handoff.Editor.asmdef").read_text())
        self.assertEqual(runtime["name"], "Aya.Handoff")
        self.assertEqual(editor["includePlatforms"], ["Editor"])

    def test_unity_thread_lifecycle_and_unsupported_fallback(self):
        code = (UNITY / "Runtime/AyaAndroidHelp.cs").read_text()
        for token in (
            "SynchronizationContext.Current",
            'GetStatic<AndroidJavaObject>("currentActivity")',
            'activity.Call("runOnUiThread"',
            'CallStatic<string>(',
            "unityContext.Post(",
            "retainedActivity.Dispose()",
            "#if UNITY_ANDROID && !UNITY_EDITOR",
            "ParseLocalResult",
            "Unknown local AYA status.",
        ):
            self.assertIn(token, code)
        self.assertNotIn("Application.OpenURL", code)
        self.assertNotIn("UnityWebRequest", code)
        self.assertNotIn("onAgentReply", code)

    def test_help_button_requires_truthful_host_copy(self):
        code = (UNITY / "Runtime/AyaUnityHelpButton.cs").read_text()
        for field in ("description", "attachmentDisclosure", "outputInstructions"):
            self.assertIn("string.IsNullOrWhiteSpace(" + field + ")", code)
        self.assertIn("if (pending) return;", code)
        self.assertIn("SetQuestionText(string text)", code)
        self.assertIn("public void OpenHelp()", code)
        self.assertIn('onLocalStatus?.Invoke("rejected"', code)
        self.assertIn("hostHasQuestionField ? questionText : null", code)

    def test_ui_editor_does_not_claim_compatibility(self):
        editor = (UNITY / "Editor/AyaUnityHelpButtonEditor.cs").read_text()
        self.assertIn("DrawDefaultInspector()", editor)
        self.assertIn("BuildTarget.Android", editor)
        self.assertIn("onLocalStatus", (UNITY / "Runtime/AyaUnityHelpButton.cs").read_text())


if __name__ == "__main__":
    unittest.main()
