#!/usr/bin/env python3
"""Plan or safely install one AYA component into an existing Android project.

Deliberately does NOT generate app-specific product facts, edit Gradle, install an
SDK, or attempt to contact an assistant. Dry-run is the default. Apply creates
only explicitly listed files and refuses conflicting existing content.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

from component_codegen import ComponentError, android_xml_snippet, compose_snippet, kotlin_snippet, validate

MODULE = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")
PACKAGE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+$")


def component_stem(value: str) -> str:
    name = re.sub(r"[^a-z0-9_]+", "_", value.lower()).strip("_")
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:10]
    return f"{name}_{digest}"


def assert_safe_path(root: Path, destination: Path) -> None:
    """Never write through a symlink or a path outside the chosen project."""
    try:
        relative = destination.relative_to(root)
    except ValueError as exc:
        raise ComponentError("Output path escapes the project directory") from exc
    current = root
    for piece in relative.parts:
        current = current / piece
        if current.is_symlink():
            raise ComponentError(f"Symlink in output path: {current}")
    if not destination.resolve().is_relative_to(root.resolve()):
        raise ComponentError("Output path resolves outside the project directory")


def plan(
    project: Path, module: str, manifest: dict[str, Any],
    mode: str, package: str | None = None
) -> dict[Path, str]:
    config = validate(manifest)
    if not MODULE.fullmatch(module):
        raise ComponentError("Module must be a single safe Android module directory name")
    if not project.is_dir():
        raise ComponentError("Project directory does not exist")
    root = project.resolve()
    src = root / module / "src" / "main"
    if not src.is_dir() or src.is_symlink():
        raise ComponentError("Expected an existing Android module with src/main; no files written")
    stem = component_stem(config["id"])

    if mode in ("kotlin", "compose"):
        if not package or not PACKAGE.fullmatch(package):
            raise ComponentError("Kotlin mode needs a valid dotted --package")
        relative = Path(*package.split("."))
        output = src / "java" / relative / f"AyaComponent_{'Compose_' if mode == 'compose' else ''}{stem}.kt"
        body = f"package {package}\n\n" + (compose_snippet(config) if mode == "compose" else kotlin_snippet(config))
    elif mode == "android-xml":
        if config["presentation"]["kind"] != "card":
            raise ComponentError("Android XML supports visible cards only, not headless actions")
        output = src / "res" / "layout" / f"aya_component_{stem}.xml"
        body = android_xml_snippet(config)
    else:
        raise ComponentError("Unsupported host mode")

    record = root / ".aya" / "components" / f"{stem}.json"
    payload = json.dumps(config, sort_keys=True, ensure_ascii=False, indent=2) + "\n"
    for path in (output, record):
        assert_safe_path(root, path)
    return {output: body, record: payload}


def apply_plan(root: Path, files: dict[Path, str]) -> list[str]:
    """Idempotent for identical files, all conflicts checked before creating."""
    root = root.resolve()
    for path, expected in files.items():
        assert_safe_path(root, path)
        if path.exists():
            if not path.is_file() or path.read_text(encoding="utf-8") != expected:
                raise ComponentError(f"Conflicting existing file; will not overwrite: {path}")
    created: list[Path] = []
    try:
        for path, expected in files.items():
            assert_safe_path(root, path)
            if path.exists():
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            assert_safe_path(root, path)
            with path.open("x", encoding="utf-8", newline="\n") as f:
                created.append(path)
                f.write(expected)
        return [str(p.relative_to(root)) for p in created]
    except Exception:
        # Roll back only the newly created files; never delete pre-existing work.
        for path in created:
            path.unlink(missing_ok=True)
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-dir", type=Path, required=True)
    parser.add_argument("--module", default="app")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--mode", choices=("kotlin", "compose", "android-xml"), required=True)
    parser.add_argument("--package", help="Kotlin package for the generated source")
    parser.add_argument("--apply", action="store_true", help="create non-conflicting files; default is dry-run")
    args = parser.parse_args(argv)
    try:
        config = json.loads(args.manifest.read_text(encoding="utf-8"))
        changes = plan(args.project_dir, args.module, config, args.mode, args.package)
        root = args.project_dir.resolve()
        created = apply_plan(root, changes) if args.apply else []
        report = {
            "status": "applied" if args.apply else "dry-run",
            "component_id": config["id"],
            "mode": args.mode,
            "files": [str(p.relative_to(root)) for p in changes],
            "created": created,
            "follow_up": [
                "Add the version-compatible AYA Android SDK dependency to the host build.",
                "Author, independently audit and bundle an exact-installed-version AYA-RAS guide at the declared asset path.",
                "Connect the generated function or XML layout to the intended host screen.",
                "Test the editable local review and user-controlled Copy/Share on a real Android build.",
                "Verify accessibility and any actual host-owned file import separately."
            ],
            "caveat": "Generated wiring is not proof of host guide accuracy, recipient ingestion or an installed plugin."
        }
        print(json.dumps(report, indent=2))
        return 0
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError, ComponentError) as exc:
        print(f"AYA scaffolding refused: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
