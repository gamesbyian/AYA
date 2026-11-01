#!/usr/bin/env python3
"""Stage an audited exact-version AYA guide as a raw Godot 4.5 Android APK asset.

Godot res:// PCK resources are *not* equivalent to Activity.assets.open().
Only the Android 4.5 Gradle template's proven assets/ source set is supported.
Inspect the final APK separately; source staging is never release proof.
"""
from __future__ import annotations

import argparse
import configparser
import os
import tempfile
from pathlib import Path

from validate_guide import validate

PRESET_FILE = "export_presets.cfg"
TARGET = Path("android/build/assets/aya-guide.md")


class StageError(ValueError):
    pass


def _unquote(text: str) -> str:
    value = text.strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        return value[1:-1]
    return value


def _android_preset(project: Path) -> tuple[str, str]:
    path = project / PRESET_FILE
    if path.is_symlink() or not path.is_file():
        raise StageError("A real Godot export_presets.cfg file is required")
    config = configparser.ConfigParser(interpolation=None, strict=True)
    config.optionxform = str
    try:
        with path.open(encoding="utf-8") as fd:
            config.read_file(fd)
    except (OSError, configparser.Error) as exc:
        raise StageError("Unparseable Godot Android export preset") from exc
    found = []
    for section in config.sections():
        if not section.startswith("preset.") or section.endswith(".options"):
            continue
        if _unquote(config[section].get("platform", "")) != "Android":
            continue
        opts_name = section + ".options"
        if opts_name not in config:
            raise StageError("Android preset options are missing")
        opts = config[opts_name]
        if _unquote(opts.get("gradle_build/use_gradle_build", "")) != "true":
            raise StageError("Android export must use the Godot Gradle build")
        app_id = _unquote(opts.get("package/unique_name", ""))
        app_version = _unquote(opts.get("version/name", ""))
        min_sdk = _unquote(opts.get("gradle_build/min_sdk", ""))
        if min_sdk and (not min_sdk.isdecimal() or int(min_sdk) < 24):
            raise StageError("Godot Android v2 host must target min SDK 24 or higher")
        found.append((app_id, app_version))
    if len(found) != 1:
        raise StageError("Exactly one Android Gradle export preset is required")
    if not all(found[0]):
        raise StageError("Android export app ID and version must be explicit")
    return found[0]


def stage(project: Path, guide: Path, *, check_only: bool = False) -> Path:
    if project.is_symlink() or not project.is_dir():
        raise StageError("Project must be a real directory")
    project = project.resolve(strict=True)
    if guide.is_symlink() or not guide.is_file():
        raise StageError("Guide must be a regular UTF-8 source file")
    source = guide.read_bytes()
    try:
        content = source.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise StageError("Guide is not strict UTF-8") from exc
    audit = validate(content)
    if not audit["ok"] or audit["warnings"]:
        raise StageError("Guide fails strict AYA-RAS structure: " +
                         "; ".join(audit["errors"] + audit["warnings"]))
    app_id, version = _android_preset(project)
    meta = audit["metadata"]
    if (meta.get("app_id") != app_id or
            meta.get("app_version_min") != version or
            meta.get("app_version_max") != version):
        raise StageError("Guide package identity and exact version differ from Godot export preset")

    template_root = project / "android" / "build"
    build_gradle = template_root / "build.gradle"
    if not build_gradle.is_file() or build_gradle.is_symlink():
        raise StageError("Install the Godot 4.5 Gradle Android build template first")
    target = project / TARGET
    for path in (project / "android", template_root, template_root / "assets", target):
        if path.is_symlink():
            raise StageError("Refusing symlinked Godot APK-asset destination")
    if target.exists():
        if not target.is_file() or target.read_bytes() != source:
            raise StageError("Existing native guide differs; refusing silent overwrite")
        return target
    if check_only:
        raise StageError("Matching native guide is absent; staging was not requested")
    target.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temp_name = tempfile.mkstemp(prefix=".aya-guide-", dir=target.parent)
    try:
        with os.fdopen(descriptor, "wb") as fd:
            fd.write(source)
        Path(temp_name).replace(target)
    finally:
        Path(temp_name).unlink(missing_ok=True)
    return target


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--guide", type=Path, required=True)
    parser.add_argument("--check", action="store_true",
                        help="Only verify an already staged exact guide")
    args = parser.parse_args(argv)
    try:
        target = stage(args.project, args.guide, check_only=args.check)
    except (OSError, StageError) as exc:
        parser.exit(1, f"AYA Godot Android guide: FAIL: {exc}\n")
    print(f"AYA Godot Android guide: staged exact source bytes at {target}")
    print("Scope: raw source staging only; verify final APK identity and guide")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
