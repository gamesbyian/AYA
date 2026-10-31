import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from validate_filesystem_kit import parse_kit, validate, validate_schema, validate_snapshot

BASE = Path(__file__).resolve().parents[1] / "docs/filesystem/examples"
SCHEMA = json.loads((BASE / "harborfiles-recipe.schema.json").read_text())
RECIPE = json.loads((BASE / "harborfiles-delete.recipe.json").read_text())
SNAP = json.loads((BASE / "harborfiles-snapshot.json").read_text())


class FilesystemKitTests(unittest.TestCase):
    def test_fixtures(self):
        verdict = validate(BASE / "harborfiles-kit.md",
                           BASE / "harborfiles-recipe.schema.json",
                           BASE / "harborfiles-delete.recipe.json",
                           BASE / "harborfiles-snapshot.json")
        self.assertEqual("complete", verdict["snapshot_status"])

    def test_wrong_action_and_unsafe_approval_reject(self):
        for mutation in (("action", "type", "shell"),
                         ("execution", "require_approval", False),
                         ("preconditions", "require_complete_scan", False)):
            item = copy.deepcopy(RECIPE)
            item[mutation[0]][mutation[1]] = mutation[2]
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                validate_schema(SCHEMA, item)

    def test_unknown_keys_and_missing_guard_reject(self):
        item = copy.deepcopy(RECIPE)
        item["action"]["command"] = "rm -rf /"
        with self.assertRaises(ValueError):
            validate_schema(SCHEMA, item)
        item = copy.deepcopy(RECIPE)
        del item["preconditions"]["protected_basename_must_exist"]
        with self.assertRaises(ValueError):
            validate_schema(SCHEMA, item)

    def test_partial_scan_can_be_reported_but_complete_errors_reject(self):
        item = copy.deepcopy(SNAP)
        item["scan"]["status"] = "partial"
        item["scan"]["errors"] = [{"kind": "permission", "path": "/private"}]
        validate_snapshot(item, "dev.harborfiles.demo", "1.0.0")
        item["scan"]["status"] = "complete"
        with self.assertRaisesRegex(ValueError, "complete scan"):
            validate_snapshot(item, "dev.harborfiles.demo", "1.0.0")

    def test_stale_app_identity_reject(self):
        with self.assertRaisesRegex(ValueError, "identity"):
            validate_snapshot(SNAP, "dev.other.app", "1.0.0")
        with self.assertRaisesRegex(ValueError, "identity"):
            validate_snapshot(SNAP, "dev.harborfiles.demo", "2.0.0")

    def test_missing_and_duplicate_sections_reject(self):
        kit = (BASE / "harborfiles-kit.md").read_text()
        for mutated in (kit.replace("## Intent clarification", "## No clarification"),
                        kit.replace("owner: Fictional", "owner: Duplicate\nowner: Fictional")):
            with self.assertRaises(ValueError):
                parse_kit(mutated)

    def test_snapshot_schema_rejects_unknown_fields_and_oversize_entries(self):
        schema = json.loads((BASE.parent / "schemas/aya-filesystem-snapshot-v1.schema.json").read_text())
        item = copy.deepcopy(SNAP)
        item["credentials"] = "secret"
        with self.assertRaises(ValueError):
            validate_schema(schema, item)
        item = copy.deepcopy(SNAP)
        item["entries"] = item["entries"] * 1000
        with self.assertRaises(ValueError):
            validate_schema(schema, item)


if __name__ == "__main__":
    unittest.main()
