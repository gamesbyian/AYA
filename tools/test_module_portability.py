"""Guard AYA's reusable modules against unrelated real-host coupling.

This is a narrow regression check, supplementing semantic portability review
defined in docs/MODULE_PORTABILITY.md.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Scan the source formats used by ALL adapters, including Expo/React Native,
# Flutter, Godot, Unity and generated Android project templates.
EXTENSIONS = {
    ".md", ".json", ".kt", ".java", ".dart", ".gd", ".py", ".xml",
    ".yml", ".yaml", ".ts", ".tsx", ".js", ".jsx", ".cjs", ".mjs",
    ".gradle", ".kts", ".cs", ".sh", ".html", ".css", ".svg",
    ".toml", ".properties",
}
IGNORE = {"tools/test_module_portability.py"}
GENERATED_OR_EXTERNAL_DIRS = {
    ".git", ".gradle", ".dart_tool", ".expo", "node_modules",
    "build", "dist", "coverage", ".next", "vendor",
}
# Known historical leaks. This test lives in tools; no AYA module depends on it.
UNRELATED_HOSTS = re.compile(
    r"\b(?:ROYGBIV|Wallgen|Chunks|Expository|Glimpse|UR[- ]?Recomp|Uniracers|Plex)\b"
    r"|(?i:github\.com/gamesbyian/)(?!(?i:AYA)(?:/|\b))[\w.-]+",
)


class ModulePortabilityTest(unittest.TestCase):
    def test_no_unrelated_real_host_name_or_repository_in_aya_modules(self):
        violations = []
        for file in ROOT.rglob("*"):
            if not file.is_file() or file.is_symlink() or file.suffix not in EXTENSIONS:
                continue
            relative_path = file.relative_to(ROOT)
            relative = relative_path.as_posix()
            if relative in IGNORE or any(
                part in GENERATED_OR_EXTERNAL_DIRS for part in relative_path.parts[:-1]
            ):
                continue
            try:
                content = file.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for lineno, line in enumerate(content.splitlines(), start=1):
                if UNRELATED_HOSTS.search(line):
                    violations.append(f"{relative}:{lineno}")
        self.assertFalse(violations, "Unrelated host/project references: " + ", ".join(violations))

    def test_all_supported_adapter_languages_are_scanned(self):
        self.assertTrue({
            ".ts", ".tsx", ".js", ".cjs", ".mjs", ".gradle", ".kts",
            ".cs", ".gd", ".dart", ".kt", ".svg",
        }.issubset(EXTENSIONS))

    def test_guard_rejects_real_host_references(self):
        self.assertRegex("A named project: ROYGBIV", UNRELATED_HOSTS)
        self.assertRegex("https://github.com/gamesbyian/wallgen/tree/branch", UNRELATED_HOSTS)
        self.assertNotRegex("https://github.com/gamesbyian/AYA/issues/3", UNRELATED_HOSTS)
        self.assertNotRegex("HarborFiles and ParcelPad are fictional", UNRELATED_HOSTS)
        self.assertNotRegex("The transfer arrives in chunks", UNRELATED_HOSTS)
        self.assertNotRegex("A glimpse of a screenshot", UNRELATED_HOSTS)


if __name__ == "__main__":
    unittest.main()
