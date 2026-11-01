#!/usr/bin/env python3
"""Build an isolated first-party Godot consumer from the *staged* AYA addon.

The output must be outside both the AYA repo and its source fixture. Only a
small explicit host fixture and assembled plugin files cross the boundary.
This is S2+ synthetic portability evidence, not independent app authorship.
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

FIXTURE_FILES = (
    "project.godot", "export_presets.cfg", "aya_smoke.tscn",
    "aya_smoke.gd", "aya_export_preflight.gd",
    "ci-host/runtime_probe_card.gd", "ci-host/aya-guide.md",
    "ci-host/inventory.json", "ci-host/questions.json",
)
ADDON_FILES = (
    "plugin.cfg", "export_plugin.gd", "aya_card.gd",
    "bin/debug/aya-debug.aar", "bin/debug/aya-godot-debug.aar",
    "bin/release/aya-release.aar", "bin/release/aya-godot-release.aar",
)
MAX_TEXT_FILE = 512 * 1024
MAX_AAR_FILE = 12 * 1024 * 1024


class HostPreparationError(ValueError):
    pass


def _source_file(root: Path, relative: str, max_size: int) -> Path:
    path = root / relative
    if path.is_symlink() or not path.is_file():
        raise HostPreparationError("Missing or symlinked input: " + relative)
    resolved = path.resolve(strict=True)
    if not resolved.is_relative_to(root.resolve(strict=True)):
        raise HostPreparationError("Input escapes source root: " + relative)
    if not 0 < path.stat().st_size <= max_size:
        raise HostPreparationError("Invalid source size: " + relative)
    return path


def prepare(fixture: Path, staged_addon: Path, destination: Path) -> dict:
    fixture = fixture.resolve(strict=True)
    staged_addon = staged_addon.resolve(strict=True)
    if not fixture.is_dir() or not staged_addon.is_dir():
        raise HostPreparationError("Fixture and staged addon must be directories")
    if destination.exists() or destination.is_symlink():
        raise HostPreparationError("Destination must not already exist")
    output = destination.resolve(strict=False)
    if output.is_relative_to(fixture) or output.is_relative_to(staged_addon):
        raise HostPreparationError("Consumer must be outside fixture and staged addon")
    # The source fixture is part of the checkout; this helper is invoked with
    # the generated destination under runner.temp, never in the AYA checkout.
    repo = Path(__file__).resolve().parents[1]
    if output.is_relative_to(repo):
        raise HostPreparationError("Consumer must be outside the AYA repository")

    inputs = [(root, relative, max_size)
              for root, names, max_size in (
                  (fixture, FIXTURE_FILES, MAX_TEXT_FILE),
                  (staged_addon, ADDON_FILES, MAX_AAR_FILE),
              ) for relative in names]
    verified = [(root, name, _source_file(root, name, limit))
                for root, name, limit in inputs]

    destination.mkdir(parents=True)
    for root, name, source in verified:
        relative = Path("addons/AYA") / name if root == staged_addon else Path(name)
        output_path = destination / relative
        output_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, output_path)
    if (destination / "android").exists() or (destination / ".godot").exists():
        raise HostPreparationError("Unexpected generated files copied from source")
    return {
        "schema": "aya-godot-packaged-consumer/v1",
        "synthetic_host": True,
        "destination": str(destination),
        "fixture_file_count": len(FIXTURE_FILES),
        "staged_addon_file_count": len(ADDON_FILES),
        "compiled_godot_export": False,
        "actual_recipient_verified": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--staged-addon", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        evidence = prepare(args.fixture, args.staged_addon, args.destination)
    except (OSError, HostPreparationError) as exc:
        parser.exit(1, f"AYA Godot consumer: FAIL: {exc}\n")
    print(json.dumps(evidence, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
