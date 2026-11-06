"""Dependency-free negative and positive tests for the spatial manifest contract."""
import copy
import json
from pathlib import Path
import unittest

from tools.validate_spatial_composition import validate

FIXTURE = Path(__file__).resolve().parent.parent / "docs/spatial/examples/mechanical-room.json"


class SpatialCompositionTests(unittest.TestCase):
    def setUp(self):
        self.packet = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def assert_rejected(self, edit):
        packet = copy.deepcopy(self.packet)
        edit(packet)
        errors = validate(packet)
        self.assertTrue(errors, "Unsafe edit unexpectedly accepted")

    def test_valid_example(self):
        self.assertEqual([], validate(self.packet))

    def test_unknown_version(self):
        self.assert_rejected(lambda x: x.update(format="aya-spatial-composition/v2"))

    def test_unknown_asset(self):
        self.assert_rejected(lambda x: x["operations"][1].update(assetId="missing"))

    def test_duplicate_target(self):
        self.assert_rejected(lambda x: x["operations"].append(copy.deepcopy(x["operations"][0])))

    def test_protected_target(self):
        self.assert_rejected(lambda x: x["constraints"].update(protectedAnnotationIds=["B"]))

    def test_bad_coordinates(self):
        self.assert_rejected(lambda x: x["annotations"][1]["geometry"].update(x=0.9))

    def test_degenerate_polygon(self):
        self.assert_rejected(lambda x: x["annotations"][0]["geometry"]["vertices"].__setitem__(2, {"x":0.39,"y":0.83}))

    def test_duplicate_label(self):
        self.assert_rejected(lambda x: x["annotations"][2].update(label="existing BOILER"))

    def test_traversal(self):
        self.assert_rejected(lambda x: x["source"].update(path="source/../secrets.jpg"))

    def test_mime_mismatch(self):
        self.assert_rejected(lambda x: x["source"].update(mime="image/png"))

    def test_bad_hash(self):
        self.assert_rejected(lambda x: x["source"].update(sha256="123"))

    def test_no_asset_for_add(self):
        self.assert_rejected(lambda x: x["operations"][2].pop("assetId"))

    def test_false_engineering_claim(self):
        self.assert_rejected(lambda x: x["constraints"].update(engineeringVerified=True))

    def test_missing_source(self):
        self.assert_rejected(lambda x: x.pop("source"))

    def test_extra_unsupported_field(self):
        self.assert_rejected(lambda x: x.update(backgroundUpload=True))


if __name__ == "__main__":
    unittest.main()
