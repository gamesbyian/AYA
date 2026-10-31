import pathlib
import json
from unittest.mock import patch
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from build_reference import assemble, main
from packet_compiler import compile_packet, read_json

EXAMPLE = pathlib.Path(__file__).resolve().parents[1] / "docs/reference/EXAMPLE_PARCELPAD.md"


class ReferenceBuildTests(unittest.TestCase):
    def test_assembles_in_sorted_order_and_validates(self):
        source = EXAMPLE.read_text(encoding="utf-8")
        cut = source.index("## Scope and version")
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / "00-header.md").write_text(source[:cut], encoding="utf-8")
            (root / "10-body.md").write_text(source[cut:], encoding="utf-8")
            built = assemble(root)
            self.assertIn("schema_version: aya-reference/v1", built)
            self.assertLess(built.index("## Scope and version"), built.index("## Assistant answer policy"))

    def test_rejects_missing_header(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / "20-body.md").write_text("# Invalid", encoding="utf-8")
            with self.assertRaises(ValueError):
                assemble(root)

    def test_rejects_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            outside = root / "outside.txt"
            outside.write_text("secret", encoding="utf-8")
            (root / "00-header.md").symlink_to(outside)
            with self.assertRaises(ValueError):
                assemble(root)


    def test_scoped_packet_fragment_preserves_aya_ras_structure(self):
        root = pathlib.Path(__file__).resolve().parents[1]
        source = read_json(root / "docs/packet/examples/parcelpad-facts.json")
        inventory = read_json(root / "docs/packet/examples/parcelpad-inventory.json")
        profiles = read_json(root / "docs/packet/examples/parcelpad-profiles.json")
        packet, report = compile_packet(source, inventory, profiles, "help",
                                        ["FACT-009"], fragment=True)
        self.assertIn("FACT-001", report["included_ids"])
        guide = EXAMPLE.read_text(encoding="utf-8")
        cut = guide.index("## Scope and version")
        with tempfile.TemporaryDirectory() as tmp:
            directory = pathlib.Path(tmp)
            (directory / "00-header.md").write_text(guide[:cut], encoding="utf-8")
            (directory / "10-body.md").write_text(guide[cut:], encoding="utf-8")
            merged = assemble(directory, packet)
            self.assertIn("### AYA task-specific verified packet", merged)
            self.assertIn("#### Source-backed host facts", merged)
            self.assertIn("## Assistant answer policy", merged)

    def test_cli_rejects_foreign_packet_identity_even_when_both_parse(self):
        root = pathlib.Path(__file__).resolve().parents[1]
        guide = EXAMPLE.read_text(encoding="utf-8")
        cut = guide.index("## Scope and version")
        with tempfile.TemporaryDirectory() as tmp:
            directory = pathlib.Path(tmp)
            (directory / "00-header.md").write_text(guide[:cut], encoding="utf-8")
            (directory / "10-body.md").write_text(guide[cut:], encoding="utf-8")
            argv = ["build_reference.py", str(directory), str(directory / "out.md"),
                    "--packet-source", str(root / "docs/packet/examples/parcelpad-facts.json"),
                    "--packet-inventory", str(root / "docs/packet/examples/parcelpad-inventory.json"),
                    "--packet-profiles", str(root / "docs/packet/examples/parcelpad-profiles.json"),
                    "--packet-profile", "help"]
            with patch("sys.argv", argv):
                with self.assertRaises(SystemExit) as error:
                    main()
            self.assertEqual(1, error.exception.code)
            self.assertFalse((directory / "out.md").exists())



if __name__ == "__main__":
    unittest.main()
