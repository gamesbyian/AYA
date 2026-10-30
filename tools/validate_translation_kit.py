#!/usr/bin/env python3
"""Validate an AYA Translation Kit fixture (stdlib only).

Authoring checks are not a replacement for a host runtime importer or an ICU parser.
"""
import argparse
import json
import re
from pathlib import Path

REQUIRED = [
    "Output schema", "Source catalog", "Rosetta and glossary",
    "Style and meaning constraints", "Worked examples",
    "Agent instructions", "Host import instructions",
]
FIELDS = [
    "schema_version", "app_id", "app_version", "catalog_revision",
    "source_revision", "source_locale", "owner",
]

def parse(text):
    lines = text.lstrip("\ufeff").splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("missing frontmatter")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError("incomplete frontmatter") from exc
    metadata = {}
    for line in lines[1:end]:
        if not line.strip():
            continue
        match = re.fullmatch(r"([a-z][a-z0-9_]*):\s*(.*?)\s*", line)
        if not match:
            raise ValueError("malformed metadata")
        k, v = match.groups()
        if k in metadata:
            raise ValueError("duplicate metadata: " + k)
        metadata[k] = v.strip().strip('"').strip("'")
    if any(not metadata.get(k) for k in FIELDS):
        raise ValueError("missing required metadata")
    if metadata["schema_version"] != "aya-translation-kit/v1":
        raise ValueError("unsupported version")
    body = "\n".join(lines[end + 1:])
    headings = re.findall(r"^## (.+?)\s*$", body, flags=re.M)
    if headings != REQUIRED:
        raise ValueError("missing, repeated or reordered H2 sections")
    sections = {}
    for i, title in enumerate(REQUIRED):
        start = body.index("## " + title) + len("## " + title)
        stop = body.index("## " + REQUIRED[i + 1]) if i + 1 < len(REQUIRED) else len(body)
        sections[title] = body[start:stop]
    def json_block(section):
        found = re.search(r"^\x60{3}json\s*\n(.*?)\n\x60{3}\s*$", sections[section], re.M | re.S)
        if not found:
            raise ValueError("missing fenced JSON in " + section)
        return json.loads(found.group(1))
    return metadata, sections, json_block("Output schema"), json_block("Source catalog")

def placeholders(text):
    # Named ICU tokens, not full ICU grammar validation.
    return set(re.findall(r"\{([A-Za-z_][A-Za-z0-9_]*)(?=[,}])", text))

def validate(kit_path, schema_path, example_path):
    raw = Path(kit_path).read_bytes()
    if len(raw) > 1024 * 1024:
        raise ValueError("kit over 1 MiB")
    text = raw.decode("utf-8", "strict")
    meta, sections, schema, catalog = parse(text)
    standalone_schema = json.loads(Path(schema_path).read_text(encoding="utf-8"))
    if schema != standalone_schema:
        raise ValueError("embedded and standalone schemas differ")
    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        raise ValueError("unexpected schema dialect")
    ids = [row["id"] for row in catalog["strings"]]
    if len(ids) != len(set(ids)) or not ids:
        raise ValueError("missing or duplicate source IDs")
    allowed = schema["properties"]["entries"]["properties"]
    if set(allowed) != set(ids):
        raise ValueError("schema keys differ from catalog")
    if catalog["catalog_revision"] != meta["catalog_revision"]:
        raise ValueError("catalog revision drift")
    if catalog["source_locale"] != meta["source_locale"]:
        raise ValueError("source locale drift")
    for row in catalog["strings"]:
        if not row.get("source") or not row.get("description") or not row.get("safety"):
            raise ValueError("source entry lacks meaning or safety classification")
        expected = {p["name"] for p in row.get("placeholders", [])}
        if placeholders(row["source"]) != expected:
            raise ValueError("placeholder metadata mismatch: " + row["id"])
    pack = json.loads(Path(example_path).read_text(encoding="utf-8"))
    for key in schema.get("required", []):
        if key not in pack:
            raise ValueError("missing pack property: " + key)
    for key, spec in schema["properties"].items():
        if "const" in spec and pack.get(key) != spec["const"]:
            raise ValueError("wrong constant: " + key)
        if "enum" in spec and pack.get(key) not in spec["enum"]:
            raise ValueError("invalid enum: " + key)
    if set(pack) - set(schema["properties"]):
        raise ValueError("unknown top-level properties")
    entries = pack["entries"]
    if not isinstance(entries, dict) or not entries:
        raise ValueError("empty entries")
    if set(entries) - set(allowed):
        raise ValueError("unknown pack keys")
    source_by_id = {r["id"]: r for r in catalog["strings"]}
    for key, value in entries.items():
        if not isinstance(value, str) or not value.strip():
            raise ValueError("empty or nontext translation: " + key)
        if placeholders(value) != placeholders(source_by_id[key]["source"]):
            raise ValueError("placeholder drift: " + key)
    if "\x60\x60\x60json" not in sections["Worked examples"]:
        raise ValueError("missing worked example")
    return len(ids), len(entries)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("kit")
    parser.add_argument("--schema", required=True)
    parser.add_argument("--example", required=True)
    args = parser.parse_args()
    strings, translated = validate(args.kit, args.schema, args.example)
    print(f"Translation Kit fixture valid: {strings} keys, {translated} sample entries.")
