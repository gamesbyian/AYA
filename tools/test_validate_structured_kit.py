"""Negative controls for the offline AYA structured-kit validator."""
import tempfile
import unittest
from pathlib import Path
from validate_structured_kit import HEADINGS, validate, validate_file

def fixture() -> str:
    header = """---
schema_version: aya-structured-kit/v1
app_id: dev.example.chart
app_version: 1.0
schema_revision: chart-3
artifact_extension: .json
artifact_mime: application/json
source_revision: fictional-build-1
owner: fictional developer
---
"""
    return header + "\n".join(
        f"## {heading}\nFictional source-derived content for {heading}."
        for heading in HEADINGS
    )

class StructuredKitValidatorTest(unittest.TestCase):
    def test_accepts_complete_fictional_kit_with_host_expectations(self):
        result = validate(fixture(), app_id="dev.example.chart", app_version="1.0",
                          schema_revision="chart-3", extension=".json",
                          mime_type="application/json")
        self.assertEqual(result["artifact_extension"], ".json")
        self.assertEqual(validate("\ufeff" + fixture()), result)

    def test_stale_or_foreign_kit_rejected(self):
        for override in (dict(app_id="dev.foreign"), dict(app_version="2.0"),
                         dict(schema_revision="chart-4"), dict(extension=".xml"),
                         dict(mime_type="application/xml")):
            with self.subTest(override=override), self.assertRaisesRegex(ValueError, "differs"):
                validate(fixture(), **override)

    def test_bad_frontmatter_and_contract_rejected(self):
        changes = [
            ("---\n", "", "frontmatter"),
            ("schema_version: aya-structured-kit/v1", "schema_version: something-else", "unsupported"),
            ("owner: fictional developer", "", "missing required"),
            ("owner: fictional developer", "owner: x\nowner: y", "duplicate"),
            ("artifact_extension: .json", "artifact_extension: ../json", "extension"),
            ("artifact_mime: application/json", "artifact_mime: bad format", "MIME"),
            ("source_revision: fictional-build-1", "source_revision: <TODO>", "placeholder"),
            ("## Interactions and precedence", "## Other", "sections"),
        ]
        for original, modified, error in changes:
            with self.subTest(error=error), self.assertRaisesRegex(ValueError, error):
                validate(fixture().replace(original, modified, 1))

    def test_empty_section_and_duplicate_sections_rejected(self):
        body = fixture().replace(
            "## Field semantics and bounds\nFictional source-derived content for Field semantics and bounds.",
            "## Field semantics and bounds\n\n")
        with self.assertRaisesRegex(ValueError, "empty section"):
            validate(body)
        with self.assertRaisesRegex(ValueError, "sections"):
            validate(fixture() + "\n## Host import and recovery\nDuplicate")

    def test_size_invalid_utf8_symlink_and_missing_file_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "1 MiB"):
            validate(fixture() + "x" * (1024 * 1024))
        with tempfile.TemporaryDirectory() as folder:
            good = Path(folder) / "kit.md"
            good.write_bytes(fixture().encode())
            self.assertEqual(validate_file(good)["app_id"], "dev.example.chart")
            link = Path(folder) / "link.md"
            link.symlink_to(good)
            with self.assertRaisesRegex(ValueError, "regular"):
                validate_file(link)
            with self.assertRaisesRegex(ValueError, "regular"):
                validate_file(Path(folder) / "missing.md")
            good.write_bytes(b"\xff\xfe")
            with self.assertRaises(UnicodeDecodeError):
                validate_file(good)

if __name__ == "__main__":
    unittest.main()
