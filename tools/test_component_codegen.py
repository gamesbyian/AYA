"""Offline tests for AYA's help-only declarative component and generator."""
import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

from component_codegen import ComponentError, kotlin_function_name, kotlin_quote, kotlin_snippet, validate

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "docs/components/examples/sample-help-card.json"


class ComponentCodegenTest(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def test_example_card_valid_and_emits_guards(self):
        self.assertIs(validate(self.manifest), self.manifest)
        source = kotlin_snippet(self.manifest)
        self.assertIn("AyaCardView(", source)
        self.assertIn("guideAsset = \"aya-guide.md\"", source)
        self.assertIn("outputInstructions = ", source)
        self.assertIn("AyaCardDensity.STANDARD", source)
        self.assertNotIn("Aya.launch(", source)

    def test_valid_action_uses_typed_guarded_path(self):
        self.manifest["presentation"] = {"kind": "action", "askQuestion": False}
        code = kotlin_snippet(self.manifest)
        self.assertIn("AyaComponentAction.Help(", code)
        self.assertIn("askQuestion = false", code)
        self.assertIn("text = question", code)
        self.assertNotIn("ACTION_SEND", code)

    def test_rejects_unimplemented_operation(self):
        self.manifest["operation"] = "filesystem_automation"
        with self.assertRaises(ComponentError):
            validate(self.manifest)

    def test_rejects_unexpected_parameters(self):
        self.manifest["autoSend"] = True
        with self.assertRaises(ComponentError):
            validate(self.manifest)
        del self.manifest["autoSend"]
        self.manifest["presentation"]["autoImport"] = True
        with self.assertRaises(ComponentError):
            validate(self.manifest)

    def test_rejects_path_traversal_and_absolute_assets(self):
        for asset in ("/aya-guide.md", "../aya-guide.md", "guides/../aya-guide.md", "a//guide.md", "a\\guide.md", "note.txt"):
            m = copy.deepcopy(self.manifest)
            m["guideAsset"] = asset
            with self.subTest(asset=asset), self.assertRaises(ComponentError):
                validate(m)

    def test_schema_asset_pattern_matches_generator(self):
        import re
        schema = json.loads(
            (ROOT / "docs/components/aya-component-v1.schema.json").read_text(encoding="utf-8")
        )
        pattern = re.compile(schema["properties"]["guideAsset"]["pattern"])
        for good in ("aya-guide.md", "references/aya-help.md"):
            self.assertIsNotNone(pattern.fullmatch(good))
            self.manifest["guideAsset"] = good
            validate(self.manifest)
        for bad in ("../guide.md", "a//guide.md", "a\\\\file.md", "a.foo.md"):
            self.assertIsNone(pattern.fullmatch(bad))
            self.manifest["guideAsset"] = bad
            with self.assertRaises(ComponentError):
                validate(self.manifest)

    def test_mandatory_output_guidance(self):
        self.manifest["presentation"]["outputInstructions"] = "  "
        with self.assertRaises(ComponentError):
            validate(self.manifest)

    def test_kotlin_strings_never_interpolate_or_break_syntax(self):
        quoted = kotlin_quote('hello $token "quote" \\ next\nline')
        self.assertIn("\\$token", quoted)
        self.assertIn('\\"quote\\"', quoted)
        self.assertIn("\\\\ next", quoted)
        self.assertIn("\\nline", quoted)

    def test_multiple_cards_have_unique_stable_function_names(self):
        a = kotlin_function_name("install", "screen.a")
        b = kotlin_function_name("install", "screen-a")
        self.assertNotEqual(a, b)
        self.assertEqual(a, kotlin_function_name("install", "screen.a"))
        self.assertTrue(a.startswith("installAyaComponent_"))
        self.assertIn(a, kotlin_snippet({**self.manifest, "id": "screen.a"}))

    def test_bad_action_boolean_rejected(self):
        self.manifest["presentation"] = {"kind": "action", "askQuestion": "false"}
        with self.assertRaises(ComponentError):
            validate(self.manifest)

    def test_cli_validates_without_platform_dependencies(self):
        outcome = subprocess.run(
            [sys.executable, str(ROOT / "tools/component_codegen.py"), str(EXAMPLE), "--check"],
            text=True, capture_output=True, check=False
        )
        self.assertEqual(outcome.returncode, 0, outcome.stderr)
        self.assertIn("Valid AYA component/v1", outcome.stdout)


if __name__ == "__main__":
    unittest.main()
