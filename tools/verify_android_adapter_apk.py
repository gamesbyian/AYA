#!/usr/bin/env python3
"""Verify that expected Android adapter classes are *defined* in an APK's DEX.

This is build-artifact evidence only. It neither invokes the UI nor proves
Android recipient ingestion or physical-device behavior. Unlike scanning for
class-name bytes, this follows each DEX class_defs -> type_ids -> string_ids.
"""
from __future__ import annotations

import argparse
import re
import struct
import sys
import zipfile
from pathlib import Path

CLASS_NAME = re.compile(r"^[A-Za-z_$][A-Za-z0-9_$]*(?:\.[A-Za-z_$][A-Za-z0-9_$]*)+$")
DEX_NAME = re.compile(r"^classes(?:[2-9][0-9]*)?\.dex$")
MAX_DEX_BYTES = 128 * 1024 * 1024
MAX_DEX_FILES = 64


class AdapterApkError(ValueError):
    """Invalid APK/DEX or missing compiled adapter class."""


def _u32(data: bytes, offset: int) -> int:
    if offset < 0 or offset + 4 > len(data):
        raise AdapterApkError("DEX table entry extends beyond file")
    return struct.unpack_from("<I", data, offset)[0]


def _check_table(data: bytes, size: int, offset: int, width: int, name: str) -> None:
    if size < 0 or offset < 0 or (size and offset < 0x70):
        raise AdapterApkError("Malformed DEX " + name + " table")
    if size * width > len(data) or offset + size * width > len(data):
        raise AdapterApkError("Truncated DEX " + name + " table")


def _skip_uleb128(data: bytes, offset: int) -> int:
    for _ in range(5):
        if offset >= len(data):
            raise AdapterApkError("Truncated DEX string length")
        byte = data[offset]
        offset += 1
        if not byte & 0x80:
            return offset
    raise AdapterApkError("Invalid DEX string length")


def defined_classes_in_dex(data: bytes) -> set[str]:
    if len(data) < 0x70 or data[:4] != b"dex\n" or data[7] != 0:
        raise AdapterApkError("Not a standard Android DEX file")
    strings, strings_off = _u32(data, 0x38), _u32(data, 0x3C)
    types, types_off = _u32(data, 0x40), _u32(data, 0x44)
    classes, classes_off = _u32(data, 0x60), _u32(data, 0x64)
    _check_table(data, strings, strings_off, 4, "string_ids")
    _check_table(data, types, types_off, 4, "type_ids")
    _check_table(data, classes, classes_off, 32, "class_defs")
    found = set()
    for idx in range(classes):
        type_id = _u32(data, classes_off + 32 * idx)
        if type_id >= types:
            raise AdapterApkError("DEX class type index out of range")
        string_id = _u32(data, types_off + 4 * type_id)
        if string_id >= strings:
            raise AdapterApkError("DEX descriptor string index out of range")
        start = _u32(data, strings_off + 4 * string_id)
        pos = _skip_uleb128(data, start)
        end = data.find(b"\x00", pos)
        if end == -1:
            raise AdapterApkError("DEX descriptor string is unterminated")
        raw = data[pos:end]
        try:
            desc = raw.decode("ascii")
        except UnicodeDecodeError as exc:
            raise AdapterApkError("Invalid DEX class descriptor encoding") from exc
        if desc.startswith("L") and desc.endswith(";"):
            found.add(desc[1:-1].replace("/", "."))
    return found


def verify_adapter_classes(apk: Path, required: list[str]) -> set[str]:
    if not required or any(not CLASS_NAME.fullmatch(item) for item in required):
        raise AdapterApkError("Provide valid, nonempty dotted Java class names")
    found = set()
    try:
        with zipfile.ZipFile(apk) as archive:
            entries = [info for info in archive.infolist()
                       if DEX_NAME.fullmatch(info.filename)]
            if not entries or len(entries) > MAX_DEX_FILES:
                raise AdapterApkError("Expected 1-64 root Android classes*.dex files")
            if len({entry.filename for entry in entries}) != len(entries):
                raise AdapterApkError("Duplicate DEX entries in APK")
            for entry in entries:
                if entry.file_size > MAX_DEX_BYTES:
                    raise AdapterApkError("DEX exceeds bounded inspection limit")
                found.update(defined_classes_in_dex(archive.read(entry)))
    except zipfile.BadZipFile as exc:
        raise AdapterApkError("APK is not a valid ZIP container") from exc
    missing = set(required) - found
    if missing:
        raise AdapterApkError("Native adapter classes are not defined in APK DEX: " +
                              ", ".join(sorted(missing)))
    return set(required)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apk", type=Path, required=True)
    parser.add_argument("--class", dest="classes", action="append", required=True,
                        help="Dotted native class name (repeat for multiple classes)")
    args = parser.parse_args(argv)
    try:
        found = verify_adapter_classes(args.apk, args.classes)
    except (OSError, AdapterApkError) as exc:
        print("AYA Android adapter DEX: FAIL: " + str(exc), file=sys.stderr)
        return 1
    print("AYA Android adapter DEX: PASS: defined classes " +
          ", ".join(sorted(found)))
    print("Scope: compiled APK class definitions only; no recipient/device acceptance")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
