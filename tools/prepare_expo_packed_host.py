#!/usr/bin/env python3
"""Prepare an isolated Expo Android CI host using independently packed npm modules.

This promotes first-party packaging evidence from sibling source imports to npm
tarball installation without pretending the test host is an independent app.
It deliberately never copies node_modules or generated Android project files.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import tarfile
from pathlib import Path

HOST_FILES = ("App.tsx", "app.json", "aya-guide.md")
PACKAGES = (
    ("aya-expo", "file:..", (
        "android/build.gradle",
        "android/src/main/java/dev/aya/expo/AyaExpoModule.kt",
        "expo-module.config.json", "src/index.ts",
        "src/AyaHelpCard.tsx", "src/native.ts"
    )),
    ("aya-expo-guide", "file:../../guide-plugin", ("app.plugin.js", "guide_asset.cjs")),
)
MAX_PACKAGE_BYTES = 16 * 1024 * 1024
MAX_UNPACKED_BYTES = 64 * 1024 * 1024
UNWANTED_PACKAGE_DIRS = {"node_modules", "ci-host", "test", "tests", "build", ".git"}


class PackedHostError(ValueError):
    pass


def _tarball_metadata(path: Path, name: str, files: tuple[str, ...]) -> dict:
    if not path.is_file() or path.is_symlink() or path.suffix != ".tgz":
        raise PackedHostError("Expected regular packed npm .tgz for " + name)
    if path.stat().st_size > MAX_PACKAGE_BYTES:
        raise PackedHostError("Unreasonably large npm package: " + name)
    try:
        with tarfile.open(path, "r:gz") as archive:
            members = archive.getmembers()
            names = [item.name for item in members if item.isfile()]
            if any(
                item.issym() or item.islnk() or item.name.startswith("/")
                or ".." in Path(item.name).parts
                or not item.name.startswith("package/")
                for item in members
            ):
                raise PackedHostError("Unsafe or unexpected npm tar paths: " + name)
            if len(names) != len(set(names)):
                raise PackedHostError("Duplicate packed npm files: " + name)
            if sum(item.size for item in members) > MAX_UNPACKED_BYTES:
                raise PackedHostError("Unreasonably large unpacked npm package: " + name)
            if any(
                any(segment in UNWANTED_PACKAGE_DIRS for segment in Path(item.name).parts[1:-1])
                for item in members
            ):
                raise PackedHostError("Internal source, tests or dependencies leaked into npm package: " + name)
            missing = set(("package/package.json", *(f"package/{item}" for item in files))) - set(names)
            if missing:
                raise PackedHostError("Missing packaged source files in " + name + ": " + ", ".join(sorted(missing)))
            manifest = archive.extractfile("package/package.json")
            if manifest is None:
                raise PackedHostError("Missing npm manifest: " + name)
            data = json.load(manifest)
    except (tarfile.TarError, ValueError, UnicodeDecodeError) as exc:
        if isinstance(exc, PackedHostError):
            raise
        raise PackedHostError("Unreadable npm archive: " + name) from exc
    if data.get("name") != name or not re.fullmatch(
        r"[0-9]+\.[0-9]+\.[0-9]+(?:-[A-Za-z0-9][A-Za-z0-9.-]*)?", str(data.get("version", ""))
    ):
        raise PackedHostError("Incorrect package name or version in tarball: " + name)
    return data


def prepare(
    fixture: Path, destination: Path, module_tarball: Path, guide_tarball: Path
) -> dict:
    fixture = fixture.resolve(strict=True)
    if not fixture.is_dir():
        raise PackedHostError("Fixture must be a directory")
    if destination.exists() or destination.is_symlink():
        raise PackedHostError("Destination must be absent before creating a fresh consumer")
    for file in HOST_FILES + ("package.json",):
        source = fixture / file
        if not source.is_file() or source.is_symlink():
            raise PackedHostError("Unsafe or absent first-party fixture: " + file)
    manifest = json.loads((fixture / "package.json").read_text(encoding="utf-8"))
    dependencies = manifest.get("dependencies")
    if not isinstance(dependencies, dict):
        raise PackedHostError("Host has no explicit dependencies")

    tarballs = {"aya-expo": module_tarball.resolve(strict=True),
                "aya-expo-guide": guide_tarball.resolve(strict=True)}
    versions = {}
    for package, expected, packaged_files in PACKAGES:
        if dependencies.get(package) != expected:
            raise PackedHostError("Fixture's source dependency contract changed: " + package)
        metadata = _tarball_metadata(tarballs[package], package, packaged_files)
        versions[package] = metadata["version"]
        dependencies[package] = tarballs[package].as_uri()

    for name, value in dependencies.items():
        if isinstance(value, str) and value.startswith("file:") and name not in tarballs:
            raise PackedHostError("Undeclared local dependency in isolated host: " + name)

    destination.mkdir(parents=True)
    for file in HOST_FILES:
        shutil.copyfile(fixture / file, destination / file)
    (destination / "package.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return {"destination": str(destination), "versions": versions}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--module-tarball", type=Path, required=True)
    parser.add_argument("--guide-tarball", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        print(json.dumps(prepare(args.fixture, args.destination,
                                 args.module_tarball, args.guide_tarball), sort_keys=True))
    except (OSError, json.JSONDecodeError, PackedHostError) as exc:
        parser.exit(1, f"AYA Expo packed host: FAIL: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
