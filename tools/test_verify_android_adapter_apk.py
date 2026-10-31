"""Synthetic binary DEX fixtures for AYA adapter APK packaging verifier."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import struct
import tempfile
import unittest
import zipfile
from pathlib import Path

from verify_android_adapter_apk import (
    AdapterApkError,
    defined_classes_in_dex,
    verify_adapter_classes,
    main,
)


def dex_for_class(name: str, *, define: bool = True) -> bytes:
    """Minimal sections: class_def -> type_id -> descriptor string_id."""
    descriptor = ("L" + name.replace(".", "/") + ";").encode("ascii")
    off_strings, off_types, off_classes, off_text = 0x70, 0x74, 0x78, 0x98
    result = bytearray(off_text + 1 + len(descriptor) + 1)
    result[0:8] = b"dex\n039\x00"
    struct.pack_into("<II", result, 0x38, 1, off_strings)
    struct.pack_into("<II", result, 0x40, 1, off_types)
    struct.pack_into("<II", result, 0x60, 1 if define else 0, off_classes)
    struct.pack_into("<I", result, off_strings, off_text)
    struct.pack_into("<I", result, off_types, 0)
    struct.pack_into("<I", result, off_classes, 0)
    # All fixture descriptors are fewer than 128 UTF-16 code units.
    result[off_text] = len(descriptor)
    result[off_text + 1:off_text + 1 + len(descriptor)] = descriptor
    return bytes(result)


class AndroidAdapterApkVerifierTest(unittest.TestCase):
    CLASS = "dev.aya.expo.AyaExpoModule"
    CORE = "dev.aya.android.AyaShareSelectionReceiver"

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.apk = Path(self.temp.name) / "app-debug.apk"

    def make_apk(self, dex_entries):
        with zipfile.ZipFile(self.apk, "w") as archive:
            for name, blob in dex_entries:
                archive.writestr(name, blob)

    def test_dex_class_def_is_detected(self):
        self.assertEqual(defined_classes_in_dex(dex_for_class(self.CLASS)), {self.CLASS})

    def test_multidex_class_definitions(self):
        self.make_apk([
            ("classes.dex", dex_for_class(self.CORE)),
            ("classes2.dex", dex_for_class(self.CLASS)),
        ])
        self.assertEqual(
            verify_adapter_classes(self.apk, [self.CORE, self.CLASS]),
            {self.CORE, self.CLASS},
        )

    def test_descriptor_string_alone_is_not_a_class_definition(self):
        self.make_apk([("classes.dex", dex_for_class(self.CLASS, define=False))])
        with self.assertRaisesRegex(AdapterApkError, "not defined"):
            verify_adapter_classes(self.apk, [self.CLASS])

    def test_missing_class_rejected(self):
        self.make_apk([("classes.dex", dex_for_class(self.CORE))])
        with self.assertRaisesRegex(AdapterApkError, "AyaExpoModule"):
            verify_adapter_classes(self.apk, [self.CLASS])

    def test_bad_class_name_rejected(self):
        self.make_apk([("classes.dex", dex_for_class(self.CLASS))])
        for value in ("", "../relative", "Foo", "java.lang.Foo;"):
            with self.subTest(value=value), self.assertRaisesRegex(AdapterApkError, "valid"):
                verify_adapter_classes(self.apk, [value])

    def test_class_type_index_out_of_range(self):
        dex = bytearray(dex_for_class(self.CLASS))
        struct.pack_into("<I", dex, 0x78, 99)
        with self.assertRaisesRegex(AdapterApkError, "type index"):
            defined_classes_in_dex(bytes(dex))

    def test_truncated_string_table_rejected(self):
        dex = bytearray(dex_for_class(self.CLASS))
        struct.pack_into("<I", dex, 0x3C, 0xFFFFFFFF)
        with self.assertRaises(AdapterApkError):
            defined_classes_in_dex(bytes(dex))

    def test_truncated_string_descriptor_rejected(self):
        dex = bytearray(dex_for_class(self.CLASS))
        dex[-1] = ord("X")
        with self.assertRaisesRegex(AdapterApkError, "unterminated"):
            defined_classes_in_dex(bytes(dex))

    def test_duplicate_dex_entries_rejected(self):
        with zipfile.ZipFile(self.apk, "w") as archive:
            archive.writestr("classes.dex", dex_for_class(self.CLASS))
            with contextlib.redirect_stderr(io.StringIO()):
                archive.writestr("classes.dex", dex_for_class(self.CLASS))
        with self.assertRaisesRegex(AdapterApkError, "Duplicate"):
            verify_adapter_classes(self.apk, [self.CLASS])

    def test_no_root_dex_rejected(self):
        self.make_apk([("other/classes.dex", dex_for_class(self.CLASS))])
        with self.assertRaisesRegex(AdapterApkError, "Expected"):
            verify_adapter_classes(self.apk, [self.CLASS])

    def test_nonzip_rejected(self):
        self.apk.write_bytes(b"not an APK")
        with self.assertRaisesRegex(AdapterApkError, "ZIP"):
            verify_adapter_classes(self.apk, [self.CLASS])

    def test_cli_pass_and_fail(self):
        self.make_apk([("classes.dex", dex_for_class(self.CLASS))])
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(["--apk", str(self.apk), "--class", self.CLASS]), 0)
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(["--apk", str(self.apk), "--class", self.CORE]), 1)


if __name__ == "__main__":
    unittest.main()
