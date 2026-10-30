import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).parent))
from validate_translation_kit import parse, validate, placeholders

ROOT = Path(__file__).resolve().parents[1]
KIT = ROOT / "docs/translation/examples/parcelpad-translation-kit.md"
SCHEMA = ROOT / "docs/translation/examples/parcelpad-output.schema.json"
PACK = ROOT / "docs/translation/examples/parcelpad-pirate.pack.json"

class TranslationKitAuthoringTests(unittest.TestCase):
    def test_example_is_internally_consistent(self):
        self.assertEqual((5, 5), validate(KIT, SCHEMA, PACK))

    def test_duplicate_and_missing_sections_rejected(self):
        text = KIT.read_text(encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "metadata"):
            parse(text.replace("owner: Fictional", "owner: Other\nowner: Fictional"))
        with self.assertRaisesRegex(ValueError, "H2"):
            parse(text.replace("## Agent instructions", "## Other instructions"))

    def test_example_cannot_change_approved_placeholders(self):
        with tempfile.TemporaryDirectory() as tmp:
            changed = json.loads(PACK.read_text(encoding="utf-8"))
            changed["entries"]["parcel.files.count"] = "Some parcels aboard"
            path = Path(tmp) / "bad.json"
            path.write_text(json.dumps(changed), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "placeholder drift"):
                validate(KIT, SCHEMA, path)

    def test_example_cannot_invent_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            changed = json.loads(PACK.read_text(encoding="utf-8"))
            changed["entries"]["invented.label"] = "New!"
            path = Path(tmp) / "bad.json"
            path.write_text(json.dumps(changed), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unknown pack keys"):
                validate(KIT, SCHEMA, path)

    def test_named_icu_tokens_are_recognized(self):
        self.assertEqual({"count"}, placeholders("{count, plural, one {# parcel} other {# parcels}}"))

if __name__ == "__main__":
    unittest.main()
