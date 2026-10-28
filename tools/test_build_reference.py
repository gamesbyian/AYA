import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from build_reference import assemble

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


if __name__ == "__main__":
    unittest.main()
