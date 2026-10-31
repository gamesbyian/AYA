#!/usr/bin/env python3
"""Deterministically assemble modular AYA-RAS reference sources into one guide.

Input directory:
  00-header.md: complete YAML-like metadata envelope and document title.
  10-orientation.md, 20-workflows.md, ...: Markdown body fragments.

Fragments are concatenated in lexicographic filename order. Nothing is fetched
over the network; symlinks are rejected to avoid accidentally including secrets.
The output is checked with validate_guide.py before writing.
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from validate_guide import validate
from packet_compiler import compile_packet, parse_date, read_json

MAX_BYTES = 2 * 1024 * 1024


def assemble(source_dir: Path, packet_fragment: str | None = None) -> str:
    if not source_dir.is_dir():
        raise ValueError(f"Source directory not found: {source_dir}")
    sources = sorted(source_dir.glob("*.md"))
    if not sources:
        raise ValueError("No Markdown source files found.")
    if sources[0].name != "00-header.md":
        raise ValueError("First source must be 00-header.md (metadata and title).")
    for source in sources:
        if source.is_symlink():
            raise ValueError(f"Refusing to read a symlink: {source}")
        if source.stat().st_size > MAX_BYTES:
            raise ValueError(f"Source exceeds max guide size: {source}")
    joined = "\n\n".join(
        source.read_text(encoding="utf-8").strip() for source in sources
    ).strip() + "\n"
    if packet_fragment is not None:
        if not packet_fragment.strip() or packet_fragment.lstrip().startswith("---"):
            raise ValueError("Expected compiled Markdown packet fragment")
        joined = joined.rstrip() + "\n\n" + packet_fragment.strip() + "\n"
    if len(joined.encode("utf-8")) > MAX_BYTES:
        raise ValueError("Assembled guide exceeds AYA prototype 2 MiB limit.")
    report = validate(joined)
    if not report["ok"]:
        raise ValueError("Invalid guide: " + " | ".join(report["errors"]))
    return joined


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_dir", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--packet-source", type=Path)
    parser.add_argument("--packet-inventory", type=Path)
    parser.add_argument("--packet-profiles", type=Path)
    parser.add_argument("--packet-profile", choices=["help", "creative", "structured", "translation"])
    parser.add_argument("--packet-select", action="append", default=[])
    parser.add_argument("--packet-as-of")
    args = parser.parse_args()
    try:
        packet = None
        packet_paths = (args.packet_source, args.packet_inventory,
                        args.packet_profiles, args.packet_profile)
        if any(v is not None for v in packet_paths):
            if not all(v is not None for v in packet_paths):
                raise ValueError("Specify all packet source, inventory, profiles and profile")
            source = read_json(args.packet_source)
            inventory = read_json(args.packet_inventory)
            profiles = read_json(args.packet_profiles)
            stamp = parse_date(args.packet_as_of, "as-of") if args.packet_as_of else None
            packet, _ = compile_packet(source, inventory, profiles,
                                       args.packet_profile, args.packet_select,
                                       fragment=True, as_of=stamp)
        result = assemble(args.source_dir, packet)
        if packet is not None:
            guide_meta = validate(result)["metadata"]
            host = source["host"]
            if guide_meta.get("app_id") != host["app_id"] or any(
                guide_meta.get(k) != host["app_version"]
                for k in ("app_version_min", "app_version_max")
            ) or guide_meta.get("source_revision") != host["source_revision"]:
                raise ValueError("Packet host identity, revision or version differs from AYA-RAS guide")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result, encoding="utf-8", newline="\n")
    except (OSError, UnicodeError, ValueError) as error:
        parser.exit(1, f"Cannot build reference: {error}\n")
    digest = hashlib.sha256(result.encode("utf-8")).hexdigest()
    print(f"Built {args.output} ({len(result.encode('utf-8'))} bytes; SHA-256 {digest})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
