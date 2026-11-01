#!/usr/bin/env python3
"""Inspect the *built* Rush 2 AYA .aix, including repacked native AAR/DEX.

S1 packaging evidence only: real App Inventor-produced APK manifest merging,
Activity.assets access, AndroidX runtime compatibility and provider/share
behavior require independent S2+ and physical-device acceptance.
"""
from __future__ import annotations

import argparse
import io
import json
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from verify_android_adapter_apk import AdapterApkError, defined_classes_in_dex

NS = "{http://schemas.android.com/apk/res/android}"
PREFIX = "dev.aya.appinventor/"
REPACK = "dev.aya.appinventor.repacked"
AAR_NAME = REPACK + ".aya-debug.aar"
FILE_PATHS = "dev_aya_appinventor_repacked_aya_file_paths"
PROVIDER = REPACK + ".dev.aya.android.AyaFileProvider"
RECEIVER = REPACK + ".dev.aya.android.AyaShareSelectionReceiver"
CORE_ACTION = REPACK.replace(".", "/") + "/dev/aya/android/AyaComponentAction$Help.class"
MAX_AIX = 16 * 1024 * 1024
MAX_ENTRY = 12 * 1024 * 1024


class AIXError(ValueError):
    pass


def _zip_file(archive: zipfile.ZipFile, name: str) -> bytes:
    members = [member for member in archive.infolist() if member.filename == name]
    if len(members) != 1 or members[0].file_size > MAX_ENTRY:
        raise AIXError("Missing, duplicate or oversized package member: " + name)
    return archive.read(members[0])


def _check_members(archive: zipfile.ZipFile) -> None:
    names = []
    for info in archive.infolist():
        path = info.filename
        if (not path or path.startswith("/") or ".." in path.split("/") or
                "\\" in path or info.is_dir() or info.file_size > MAX_ENTRY or
                ((info.external_attr >> 16) & 0o170000) == 0o120000):
            raise AIXError("Unsafe or oversized ZIP member")
        names.append(path)
    if not names or len(names) != len(set(names)):
        raise AIXError("Empty or duplicate package members")


def _json_list(archive: zipfile.ZipFile, filename: str) -> list:
    try:
        value = json.loads(_zip_file(archive, filename))
    except (ValueError, UnicodeDecodeError) as exc:
        raise AIXError("Invalid package descriptor: " + filename) from exc
    if not isinstance(value, list) or len(value) != 1 or not isinstance(value[0], dict):
        raise AIXError("Expected exactly one AYA extension descriptor")
    return value


def verify_aix(path: Path) -> dict:
    if path.is_symlink() or not path.is_file() or not 1024 <= path.stat().st_size <= MAX_AIX:
        raise AIXError("Expected a bounded, regular AYA AIX output")
    try:
        with zipfile.ZipFile(path) as aix:
            _check_members(aix)
            expected = {
                PREFIX + "components.json",
                PREFIX + "classes.jar",
                PREFIX + "files/AndroidRuntime.jar",
                PREFIX + "files/component_build_infos.json",
                PREFIX + "aars/" + AAR_NAME,
            }
            if not expected.issubset(aix.namelist()):
                raise AIXError("Missing Rush 2 AIX native extension members")
            component = _json_list(aix, PREFIX + "components.json")[0]
            if component.get("type") != "dev.aya.appinventor.AyaHelp":
                raise AIXError("Incorrect App Inventor component class")
            methods = {item.get("name") for item in component.get("methods", [])
                       if isinstance(item, dict)}
            events = {item.get("name") for item in component.get("events", [])
                      if isinstance(item, dict)}
            if methods != {"HostIdentity", "OpenHelp"} or events != {"LocalStatus"}:
                raise AIXError("Expected guarded help and local-only status blocks")

            info = _json_list(aix, PREFIX + "files/component_build_infos.json")[0]
            if (info.get("type") != component["type"] or
                    info.get("libraries") != [AAR_NAME] or
                    info.get("permissions") != [] or info.get("queries") != []):
                raise AIXError("Unexpected extension component/native library or permissions")
            activities = info.get("activities")
            if not isinstance(activities, list) or len(activities) != 2:
                raise AIXError("AYA provider and chooser receiver must be declared")
            try:
                trees = [ET.fromstring('<root xmlns:android="http://schemas.android.com/apk/res/android">' +
                                        activity + '</root>')[0] for activity in activities]
            except (ET.ParseError, IndexError, TypeError) as exc:
                raise AIXError("Malformed AYA App Inventor component manifest declarations") from exc
            providers = [item for item in trees if item.tag == "provider"]
            receivers = [item for item in trees if item.tag == "receiver"]
            if (len(providers) != 1 or len(receivers) != 1 or
                    providers[0].get(NS + "name") != PROVIDER or
                    providers[0].get(NS + "authorities") != "%packageName%.aya.files" or
                    providers[0].get(NS + "exported") != "false" or
                    providers[0].get(NS + "grantUriPermissions") != "true" or
                    receivers[0].get(NS + "name") != RECEIVER or
                    receivers[0].get(NS + "exported") != "false"):
                raise AIXError("Repacked AYA sharing provider/receiver declaration mismatch")
            meta = list(providers[0])
            if (len(meta) != 1 or meta[0].tag != "meta-data" or
                    meta[0].get(NS + "name") != "android.support.FILE_PROVIDER_PATHS" or
                    meta[0].get(NS + "resource") != "@xml/" + FILE_PATHS):
                raise AIXError("AYA scoped native FileProvider path metadata missing")

            with zipfile.ZipFile(io.BytesIO(_zip_file(aix, PREFIX + "classes.jar"))) as classes:
                _check_members(classes)
                dex = _zip_file(classes, "classes.dex")
                definitions = defined_classes_in_dex(dex)
                if "dev.aya.appinventor.AyaHelp" not in definitions:
                    raise AIXError("AYA extension class not defined in compiled DEX")

            with zipfile.ZipFile(io.BytesIO(_zip_file(aix, PREFIX + "aars/" + AAR_NAME))) as aar:
                _check_members(aar)
                try:
                    manifest = ET.fromstring(_zip_file(aar, "AndroidManifest.xml"))
                except ET.ParseError as exc:
                    raise AIXError("Invalid repacked native AAR manifest") from exc
                if manifest.get("package") != REPACK + ".dev.aya.android":
                    raise AIXError("Incorrect native AAR relocated package")
                app = manifest.find("application")
                if app is None:
                    raise AIXError("Missing native AAR application manifest")
                a_provider = app.find("provider")
                a_receiver = app.find("receiver")
                if (a_provider is None or a_receiver is None or
                        a_provider.get(NS + "name") != PROVIDER or
                        a_provider.get(NS + "authorities") != "${applicationId}.aya.files" or
                        a_provider.get(NS + "exported") != "false" or
                        a_receiver.get(NS + "name") != RECEIVER or
                        a_receiver.get(NS + "exported") != "false"):
                    raise AIXError("Repacked AAR manifest does not match extension declarations")
                paths = "res/xml/" + FILE_PATHS + ".xml"
                try:
                    root = ET.fromstring(_zip_file(aar, paths))
                except ET.ParseError as exc:
                    raise AIXError("Invalid scoped AYA native provider XML") from exc
                if (root.tag != "paths" or len(root) != 1 or
                        root[0].tag != "cache-path" or
                        root[0].get("name") != "aya_help" or
                        root[0].get("path") != "aya/"):
                    raise AIXError("Unsafe or missing scoped AYA cache-file path")
                with zipfile.ZipFile(io.BytesIO(_zip_file(aar, "classes.jar"))) as native:
                    _check_members(native)
                    for name in (CORE_ACTION, PROVIDER.replace(".", "/") + ".class",
                                 RECEIVER.replace(".", "/") + ".class"):
                        try:
                            compiled = _zip_file(native, name)
                        except AIXError as exc:
                            raise AIXError("Missing native AYA compiled class: " + name) from exc
                        if not compiled:
                            raise AIXError("Empty native AYA compiled class: " + name)
    except (zipfile.BadZipFile, OSError, AdapterApkError) as exc:
        raise AIXError("Malformed built AIX or native code archive") from exc
    return {
        "schema": "aya-appinventor-aix-integrity/v1",
        "component": "dev.aya.appinventor.AyaHelp",
        "method_blocks": sorted(methods),
        "local_event_blocks": sorted(events),
        "native_provider": PROVIDER,
        "native_receiver": RECEIVER,
        "resource": FILE_PATHS + ".xml",
        "compiled_extension_dex": True,
        "repacked_native_aar_classes": True,
        "permission_declarations": 0,
        "evidence": "Rush 2 built AIX only, not a consuming App Inventor Android APK",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--aix", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        details = verify_aix(args.aix)
    except (OSError, AIXError) as exc:
        print("AYA App Inventor AIX: FAIL: " + str(exc), file=sys.stderr)
        return 1
    print("AYA App Inventor AIX: PASS: " + json.dumps(details, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
