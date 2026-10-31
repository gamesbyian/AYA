import copy
import datetime as dt
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from packet_compiler import PacketError, compile_packet, compile_brief, read_json

ROOT = Path(__file__).resolve().parents[1] / "docs" / "packet" / "examples"
NOW = dt.datetime(2026, 10, 30, tzinfo=dt.timezone.utc)


def sources():
    return (
        read_json(ROOT / "parcelpad-facts.json"),
        read_json(ROOT / "parcelpad-inventory.json"),
        read_json(ROOT / "parcelpad-profiles.json")
    )


class PacketCompilerTests(unittest.TestCase):
    def compile(self, profile="help", selected=None, budget=2 * 1024 * 1024,
                fragment=False, inputs=None):
        return compile_packet(*(inputs or sources()), profile, selected or [],
                              budget, fragment, NOW)

    def test_all_four_profiles_compile_and_are_deterministic(self):
        for profile in ("help", "creative", "structured", "translation"):
            with self.subTest(profile=profile):
                a, report = self.compile(profile)
                b, repeat = self.compile(profile)
                self.assertEqual((a, report), (b, repeat))
                self.assertIn("aya-packet/v1", a)
                self.assertIn("Excluded entries are not evidence", a) if report["excluded"] else None
                self.assertEqual(report["sha256"], repeat["sha256"])
                self.assertGreater(report["included"], 0)

    def test_scoping_keeps_dependencies_and_mandatory_constraints(self):
        text, report = self.compile("structured", ["FACT-006"])
        self.assertTrue(set(["FACT-001", "FACT-002", "FACT-005", "FACT-006"])
                        .issubset(report["included_ids"]))
        self.assertLess(text.index("FACT-001"), text.index("FACT-006"))
        self.assertEqual(report["excluded"], 0)

    def test_scoping_does_not_call_omitted_facts_unsupported(self):
        text, report = self.compile("help", ["FACT-001"])
        self.assertIn("FACT-009", report["excluded_known_ids"])
        self.assertIn("not evidence of unsupported", text)

    def test_fragment_contains_no_second_document_frontmatter(self):
        text, _ = self.compile("creative", fragment=True)
        self.assertFalse(text.startswith("---"))
        self.assertIn("AYA task-specific verified packet", text)

    def test_size_limit_fails_without_truncation(self):
        with self.assertRaisesRegex(PacketError, "exceeds budget"):
            self.compile("translation", budget=256)

    def test_unknown_selection_is_rejected(self):
        with self.assertRaisesRegex(PacketError, "not eligible"):
            self.compile("help", ["FACT-999"])

    def test_missing_independently_inventoried_fact_fails(self):
        src, inv, profiles = copy.deepcopy(sources())
        inv["items"].pop()
        with self.assertRaisesRegex(PacketError, "omits source facts"):
            self.compile(inputs=(src, inv, profiles))

    def test_mismatched_app_version_fails(self):
        src, inv, profiles = copy.deepcopy(sources())
        inv["app_version"] = "2.0.0"
        with self.assertRaisesRegex(PacketError, "version"):
            self.compile(inputs=(src, inv, profiles))

    def test_planned_evidence_cannot_establish_shipping(self):
        src, inv, profiles = copy.deepcopy(sources())
        src["facts"][0]["evidence"]["kind"] = "plan"
        with self.assertRaisesRegex(PacketError, "plans"):
            self.compile(inputs=(src, inv, profiles))

    def test_stale_external_claims_rejected(self):
        src, inv, profiles = copy.deepcopy(sources())
        src["facts"][0]["evidence"].update(
            kind="external", fresh_until="2026-10-01T00:00:00Z")
        with self.assertRaisesRegex(PacketError, "stale"):
            self.compile(inputs=(src, inv, profiles))

    def test_cycle_rejected(self):
        src, inv, profiles = copy.deepcopy(sources())
        src["facts"][0]["depends_on"] = ["FACT-002"]
        with self.assertRaisesRegex(PacketError, "Circular"):
            self.compile(inputs=(src, inv, profiles))

    def test_unknown_evidence_and_impact_rejected(self):
        src, inv, profiles = copy.deepcopy(sources())
        src["facts"][0]["impacts"] = ["magic"]
        with self.assertRaisesRegex(PacketError, "impact"):
            self.compile(inputs=(src, inv, profiles))

    def test_does_not_silently_drop_essential_safety_facts(self):
        text, report = self.compile("translation", ["FACT-008"])
        self.assertIn("FACT-002", report["included_ids"])
        self.assertIn("permanently erases", text)

    def test_read_json_rejects_symlinks(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            source = parent / "source.json"
            source.write_text("{}", encoding="utf-8")
            symlink = parent / "link.json"
            symlink.symlink_to(source)
            with self.assertRaises(PacketError):
                read_json(symlink)


    def test_text_only_brief_contains_constraints_and_is_bounded(self):
        src, inv, prof = sources()
        text = compile_brief(src, inv, prof, "creative", ["FACT-004"], NOW)
        self.assertIn("1:1 square", text)
        self.assertIn("Import from device", text)
        self.assertIn("FACT-003", text)
        self.assertLessEqual(len(text.encode("utf-16-le")) // 2, 4000)

    def test_text_only_fails_closed_instead_of_truncating(self):
        src, inv, prof = copy.deepcopy(sources())
        src["facts"][2]["details"] = "Important constraint. " * 1000
        with self.assertRaisesRegex(PacketError, "never truncate constraints"):
            compile_brief(src, inv, prof, "creative", ["FACT-004"], NOW)

    def test_inventory_evidence_must_match_source(self):
        src, inv, prof = copy.deepcopy(sources())
        inv["items"][0]["source_ref"] = "completely unrelated source"
        with self.assertRaisesRegex(PacketError, "evidence disagree"):
            self.compile(inputs=(src, inv, prof))



if __name__ == "__main__":
    unittest.main()
