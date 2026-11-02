"""Guard impact-scoped native adapter workflows against costly test-only rebuilds.

GitHub Actions evaluates ordered path patterns, including ! exclusions. This is
a deliberately narrow test of the concrete AYA source paths, not a YAML parser.
"""
import fnmatch
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / ".github" / "workflows"
ADAPTERS = (
    "app-inventor", "expo-module", "expo-packed-host", "flutter",
    "flutter-builtin-kotlin", "flutter-external", "godot-export",
    "unity", "unity-apk",
)


def filtered_paths(name):
    source = (ROOT / (name + ".yml")).read_text(encoding="utf-8")
    header = source.split("\njobs:", 1)[0]
    # Workflow path globs are quoted in current checked-in files.
    return re.findall(r"(?m)^\s+- ['\"]([^'\"]+)['\"]\s*$", header)


def triggers(patterns, changed_path):
    selected = False
    for pattern in patterns:
        excluded = pattern.startswith("!")
        expression = pattern[1:] if excluded else pattern
        if fnmatch.fnmatchcase(changed_path, expression):
            selected = not excluded
    return selected


class AdapterPathScopeTests(unittest.TestCase):
    def test_no_adapter_exports_for_core_unit_or_instrumented_test_only_edits(self):
        for workflow in ADAPTERS:
            with self.subTest(workflow=workflow):
                patterns = filtered_paths(workflow)
                self.assertEqual(2, patterns.count("aya/**"))
                self.assertEqual(2, patterns.count("!aya/src/test/**"))
                self.assertEqual(2, patterns.count("!aya/src/androidTest/**"))
                for changed in ("aya/src/test/java/dev/aya/android/Example.kt",
                                "aya/src/androidTest/java/dev/aya/android/Example.kt"):
                    self.assertFalse(triggers(patterns, changed), changed)
                # Actual runtime library changes MUST still dispatch each adapter.
                self.assertTrue(triggers(patterns,
                    "aya/src/main/java/dev/aya/android/Aya.kt"))

    def test_core_unit_and_emulator_lanes_remain_sensitive_to_test_edits(self):
        for lane in ("android", "android-emulator"):
            with self.subTest(lane=lane):
                patterns = filtered_paths(lane)
                self.assertTrue(triggers(patterns,
                    "aya/src/test/java/dev/aya/android/AyaTest.kt"))
                self.assertTrue(triggers(patterns,
                    "aya/src/androidTest/java/dev/aya/android/AyaTest.kt"))
                self.assertTrue(triggers(patterns,
                    "aya/src/main/java/dev/aya/android/Aya.kt"))


if __name__ == "__main__":
    unittest.main()
