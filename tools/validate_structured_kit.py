#!/usr/bin/env python3
"""Offline structural validation of source-derived AYA structured-artifact kits.

A passing check never establishes actual host importer or recipient compatibility.
"""
from __future__ import annotations
import argparse
import re
from pathlib import Path

MAX_BYTES = 1024 * 1024
HEADINGS = (
    "Artifact output contract", "Field semantics and bounds",
    "Interactions and precedence", "State preservation and migration",
    "Worked valid and invalid examples", "Agent clarification and safety",
    "Host import and recovery",
)
FIELDS = (
    "schema_version", "app_id", "app_version", "schema_revision",
    "artifact_extension", "artifact_mime", "source_revision", "owner",
)
METADATA = re.compile(r"([a-z][a-z0-9_]*):\s*(.*?)\s*")
EXTENSION = re.compile(r"\.[a-z0-9][a-z0-9._-]{0,15}\Z")
MIME = re.compile(r"[A-Za-z0-9][A-Za-z0-9!#$&^_.+-]*/[A-Za-z0-9][A-Za-z0-9!#$&^_.+-]*\Z")
PLACEHOLDER = re.compile(r"<(?:TODO|REPLACE|APP_ID|APP_VERSION|INSERT)[^>\n]{0,80}>")

def validate(text: str, *, app_id: str | None = None,
             app_version: str | None = None, schema_revision: str | None = None,
             extension: str | None = None, mime_type: str | None = None) -> dict[str, str]:
    """Check bounded kit syntax and optional *independently obtained* host identity."""
    if len(text.encode("utf-8")) > MAX_BYTES:
        raise ValueError("structured kit exceeds 1 MiB")
    lines = text.removeprefix("\ufeff").splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("missing structured kit frontmatter")
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration as exc:
        raise ValueError("unterminated structured kit frontmatter") from exc
    values: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip():
            continue
        match = METADATA.fullmatch(line)
        if match is None:
            raise ValueError("malformed structured kit metadata")
        key, val = match.groups()
        if key in values:
            raise ValueError(f"duplicate structured kit metadata: {key}")
        values[key] = val.strip().strip('"').strip("'")
    if any(not values.get(key) for key in FIELDS):
        raise ValueError("missing required structured kit metadata")
    if values["schema_version"] != "aya-structured-kit/v1":
        raise ValueError("unsupported structured kit schema")
    if not EXTENSION.fullmatch(values["artifact_extension"]):
        raise ValueError("invalid structured artifact extension")
    if not MIME.fullmatch(values["artifact_mime"]):
        raise ValueError("invalid structured artifact MIME")
    for field, expected in (("app_id", app_id), ("app_version", app_version),
                            ("schema_revision", schema_revision),
                            ("artifact_extension", extension),
                            ("artifact_mime", mime_type)):
        if expected is not None and values[field] != expected:
            raise ValueError(f"structured kit {field} differs from expected host value")
    if PLACEHOLDER.search(text):
        raise ValueError("unresolved structured kit placeholder")
    seen: list[str] = []
    bodies: list[list[str]] = []
    for line in lines[end + 1:]:
        if line.startswith("## "):
            seen.append(line[3:].strip())
            bodies.append([])
        elif bodies:
            bodies[-1].append(line)
        elif line.strip():
            raise ValueError("content before first structured kit section")
    if tuple(seen) != HEADINGS:
        raise ValueError("missing, repeated or reordered structured kit sections")
    if any(not "".join(body).strip() for body in bodies):
        raise ValueError("structured kit contains an empty section")
    return values

def validate_file(path: Path, **kwargs: str | None) -> dict[str, str]:
    if path.is_symlink() or not path.is_file():
        raise ValueError("structured kit must be a regular file")
    with path.open("rb") as handle:
        raw = handle.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("structured kit exceeds 1 MiB")
    return validate(raw.decode("utf-8", "strict"), **kwargs)

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kit", type=Path)
    parser.add_argument("--app-id")
    parser.add_argument("--app-version")
    parser.add_argument("--schema-revision")
    parser.add_argument("--extension")
    parser.add_argument("--mime-type")
    args = parser.parse_args()
    meta = validate_file(args.kit, app_id=args.app_id, app_version=args.app_version,
                         schema_revision=args.schema_revision, extension=args.extension,
                         mime_type=args.mime_type)
    print("Structured kit structurally valid:", meta["app_id"], meta["app_version"],
          meta["schema_revision"], meta["artifact_extension"], meta["artifact_mime"])
    print("NOT verified: actual host importer, schema semantics or assistant ingestion")

if __name__ == "__main__":
    main()
