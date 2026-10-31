"""Guard AYA's reusable modules against unrelated real-host coupling.

This is a narrow regression check, supplementing semantic portability review
defined in docs/MODULE_PORTABILITY.md.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXTENSIONS = {".md", ".json", ".kt", ".java", ".dart", ".gd", ".py", ".xml", ".yml", ".yaml"}
IGNORE = {"tools/test_module_portability.py"}
# Known historical leaks. This test lives in tools; no AYA module depends on it.
UNRELATED_HOSTS = re.compile(
    r"\b(?:ROYGBIV|Wallgen|Chunks|Expository|Glimpse|UR[- ]?Recomp|Uniracers|Plex)\b"
    r"|github\.com/gamesbyian/(?!AYA(?:/|\b))[\w.-]+",
    re.IGNORECASE,
)


class ModulePortabilityTest(unittest.TestCase):
    def test_no_unrelated_real_host_name_or_repository_in_aya_modules(self):
        violations = []
        for file in ROOT.rglob("*"):
            if not file.is_file() or file.suffix not in EXTENSIONS:
                continue
            relative = file.relative_to(ROOT).as_posix()
            if relative in IGNORE or any(part.startswith(".git") for part in file.parts):
                continue
            try:
                content = file.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for lineno, line in enumerate(content.splitlines(), start=1):
                if UNRELATED_HOSTS.search(line):
                    violations.append(f"{relative}:{lineno}")
        self.assertFalse(violations, "Unrelated host/project references: " + ", ".join(violations))

    def test_guard_rejects_real_host_references(self):
        self.assertRegex("A named project: ROYGBIV", UNRELATED_HOSTS)
        self.assertRegex("https://github.com/gamesbyian/wallgen/tree/branch", UNRELATED_HOSTS)
        self.assertNotRegex("https://github.com/gamesbyian/AYA/issues/3", UNRELATED_HOSTS)
        self.assertNotRegex("HarborFiles and ParcelPad are fictional", UNRELATED_HOSTS)


if __name__ == "__main__":
    unittest.main()
