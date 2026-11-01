"""Optional Unity graph-node package guard, no engine acceptance claim."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "integrations" / "unity" / "com.aya.handoff"
UNIT = PACKAGE / "VisualScripting" / "AyaOpenReviewedHelpUnit.cs"
ASMDEF = PACKAGE / "VisualScripting" / "Aya.Handoff.VisualScripting.asmdef"
WORKFLOW = ROOT / ".github" / "workflows" / "unity.yml"


class UnityVisualScriptingContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.unit = UNIT.read_text(encoding="utf-8")
        cls.asmdef = json.loads(ASMDEF.read_text(encoding="utf-8"))
        cls.workflow = WORKFLOW.read_text(encoding="utf-8")
        cls.package = json.loads((PACKAGE / "package.json").read_text(encoding="utf-8"))

    def test_unit_is_real_custom_graph_api_not_only_invoke_member(self):
        for fragment in (
            "class AyaOpenReviewedHelpUnit : Unit",
            '[UnitCategory("AYA/Help")]',
            "ControlInput(", "ControlOutput(", "ValueInput<AyaUnityHelpButton>(",
            "flow.GetValue<AyaUnityHelpButton>(card)",
            "host.OpenHelp();",
            "Requirement(card, enter);",
            "Succession(enter, returned);",
        ):
            self.assertIn(fragment, self.unit, fragment)

    def test_optional_package_avoids_visual_scripting_requirement_for_normal_host(self):
        self.assertEqual(self.asmdef["name"], "Aya.Handoff.VisualScripting")
        self.assertEqual(self.asmdef["defineConstraints"],
                         ["AYA_VISUAL_SCRIPTING_AVAILABLE"])
        self.assertFalse(self.asmdef["autoReferenced"])
        self.assertIn("Aya.Handoff", self.asmdef["references"])
        self.assertIn("Unity.VisualScripting.Flow", self.asmdef["references"])
        definitions = self.asmdef["versionDefines"]
        self.assertEqual(len(definitions), 1)
        self.assertEqual(definitions[0]["name"], "com.unity.visualscripting")
        self.assertEqual(definitions[0]["define"], "AYA_VISUAL_SCRIPTING_AVAILABLE")
        self.assertNotIn("com.unity.visualscripting",
                         self.package.get("dependencies", {}))

    def test_graph_never_claims_async_android_review_or_assistant_receipt(self):
        self.assertIn('ControlOutput("returned")', self.unit)
        self.assertNotIn('ControlOutput("success")', self.unit)
        self.assertNotIn("AyaAndroidHelp.OpenHelp(", self.unit)
        for forbidden in ("SendMessage", "AssistantResponse", "onReply", "autoImport"):
            self.assertNotIn(forbidden, self.unit)

    def test_ci_compiles_real_unit_source_with_explicit_stub_limitations(self):
        csproj = (ROOT / "tools" / "unity-managed-syntax" /
                  "VisualScriptingSmoke.csproj").read_text(encoding="utf-8")
        self.assertIn("../../integrations/unity/com.aya.handoff/VisualScripting/AyaOpenReviewedHelpUnit.cs", csproj)
        self.assertIn("VisualScriptingApiStubs.cs", csproj)
        self.assertIn("VisualScriptingSmokeMain.cs", csproj)
        self.assertIn("VisualScriptingSmoke.csproj", self.workflow)
        self.assertIn("-p:DefineConstants=UNITY_EDITOR", self.workflow)
        self.assertIn("-p:DefineConstants=UNITY_ANDROID", self.workflow)
        self.assertEqual(self.workflow.count("'tools/unity-managed-syntax/**'"), 2)
        self.assertEqual(self.workflow.count("'tools/test_unity_visual_scripting.py'"), 2)


if __name__ == "__main__":
    unittest.main()
