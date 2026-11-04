import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from validate_guide import REQUIRED_SECTIONS, validate

EXAMPLE = pathlib.Path(__file__).resolve().parents[1] / "docs/reference/EXAMPLE_PARCELPAD.md"


class ReferenceValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.good = EXAMPLE.read_text(encoding="utf-8")

    def test_complete_example_passes(self):
        result = validate(self.good)
        self.assertTrue(result["ok"], result["errors"])
        self.assertEqual(result["sections_found"], len(REQUIRED_SECTIONS))

    def test_ios_reference_requires_explicit_platform(self):
        ios = self.good.replace("platform: android", "platform: ios")
        accepted = validate(ios, expected_platform="ios")
        self.assertTrue(accepted["ok"], accepted["errors"])
        self.assertFalse(validate(ios)["ok"], "Android default must remain strict")
        self.assertFalse(validate(self.good, expected_platform="ios")["ok"])
        with self.assertRaises(ValueError):
            validate(ios, expected_platform="unknown")

    def test_ios_real_bundle_id_hyphens_are_allowed(self):
        ios = self.good.replace("platform: android", "platform: ios")
        ios = ios.replace("app_id: ", "app_id: ", 1)
        original = validate(self.good)
        original_id = original["metadata"]["app_id"]
        hyphenated = ios.replace(f"app_id: {original_id}", "app_id: com.example.aya-host")
        result = validate(hyphenated, expected_platform="ios")
        self.assertTrue(result["ok"], result["errors"])
        self.assertFalse(validate(hyphenated)["ok"], "Android default must reject iOS identity/platform")
        for invalid in ("com.example.bad_id", "com/example/app", "com.example.app!", "com..example"):
            candidate = hyphenated.replace("app_id: com.example.aya-host", f"app_id: {invalid}")
            self.assertFalse(validate(candidate, expected_platform="ios")["ok"], invalid)

    def test_case_wrong_platform_is_rejected_for_runtime_parity(self):
        upper = self.good.replace("platform: android", "platform: Android")
        self.assertFalse(validate(upper)["ok"])
        ios_upper = self.good.replace("platform: android", "platform: IOS")
        self.assertFalse(validate(ios_upper, expected_platform="ios")["ok"])

    def test_missing_section_fails(self):
        result = validate(self.good.replace("## Navigation map", "## Navigation"))
        self.assertFalse(result["ok"])
        self.assertTrue(any("Navigation map" in x for x in result["errors"]))

    def test_reordered_and_extra_major_sections_fail(self):
        swapped = (self.good.replace("## Navigation map", "## TEMP-HEADING")
                   .replace("## Quick orientation", "## Navigation map")
                   .replace("## TEMP-HEADING", "## Quick orientation"))
        self.assertTrue(any("in order" in msg for msg in validate(swapped)["errors"]))
        extra = self.good.replace(
            "## Navigation map", "## Extra section\nNot a defined AYA-RAS section.\n\n## Navigation map"
        )
        self.assertTrue(any("in order" in msg for msg in validate(extra)["errors"]))

    def test_hollow_or_subheading_only_section_fails(self):
        before, after = self.good.split("## Troubleshooting\n", 1)
        section, suffix = after.split("\n## Limitations and unsupported behavior", 1)
        self.assertTrue(section.strip())
        for body in ("\n", "\n### ERR-001\n"):
            with self.subTest(body=body):
                changed = (before + "## Troubleshooting\n" + body +
                           "\n## Limitations and unsupported behavior" + suffix)
                self.assertTrue(any("no substantive content" in msg
                                    for msg in validate(changed)["errors"]))

    def test_missing_version_fails(self):
        result = validate(self.good.replace("app_version_min: 1.0.0\n", ""))
        self.assertFalse(result["ok"])

    def test_unresolved_placeholder_fails(self):
        result = validate(self.good + "\n<change-me-now>\n")
        self.assertFalse(result["ok"])

    def test_suspected_secret_assignment_fails(self):
        result = validate(self.good + "\npassword: superSecret123456\n")
        self.assertFalse(result["ok"])

    def test_missing_frontmatter_fails(self):
        result = validate("# No metadata")
        self.assertFalse(result["ok"])


if __name__ == "__main__":
    unittest.main()
