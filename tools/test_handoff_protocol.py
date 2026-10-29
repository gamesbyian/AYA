import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "docs/protocol/aya-handoff-v1.schema.json"
SAMPLE = ROOT / "docs/protocol/examples/image-request.json"

class HandoffProtocolFixturesTest(unittest.TestCase):
    """Structural smoke tests for the published schema/fixture.

    Full consumer schema validation is a separate integration responsibility.
    No non-stdlib jsonschema dependency is installed by the project's CI.
    """

    def test_schema_identifies_v1_with_strict_top_level(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual("aya-handoff/v1", schema["properties"]["protocol"]["const"])
        self.assertFalse(schema["additionalProperties"])
        for name in ("host", "request", "reference", "privacy"):
            self.assertIn(name, schema["required"])
        self.assertEqual(True, schema["properties"]["privacy"]["properties"]["noAgentResponseCollection"]["const"])

    def test_package_id_pattern_requires_real_dots(self):
        import re
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        pattern = schema["properties"]["host"]["properties"]["packageId"]["pattern"]
        self.assertIsNotNone(re.fullmatch(pattern, "dev.aya.sample"))
        self.assertIsNone(re.fullmatch(pattern, "devXayaXsample"))

    def test_sample_has_consistent_dimensions_and_no_sensitive_uri(self):
        data = json.loads(SAMPLE.read_text(encoding="utf-8"))
        self.assertEqual("aya-handoff/v1", data["protocol"])
        self.assertEqual("generate_image", data["operation"])
        image = data["outputRequirements"]["image"]
        self.assertEqual(
            image["preferredWidthPx"] * image["aspectHeight"],
            image["preferredHeightPx"] * image["aspectWidth"]
        )
        self.assertEqual(["image/png", "image/jpeg"], image["acceptedMimeTypes"])
        self.assertTrue(all(data["privacy"].values()))
        self.assertFalse(any(k in data for k in ("credentials", "callback", "resultUri")))
        self.assertNotIn("content://", SAMPLE.read_text(encoding="utf-8"))
