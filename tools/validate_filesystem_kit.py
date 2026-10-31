#!/usr/bin/env python3
"""Strict offline fixture checks for AYA filesystem kit (stdlib only).

The real host MUST validate recipes with its own importer and prove effects via
backend-specific tests. This checker cannot certify a real filesystem engine.
"""
import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

HEADINGS = [
    "Recipe output schema", "Backend capabilities", "Discovery and snapshot semantics",
    "Intent clarification", "Safety and execution", "Worked examples",
    "Agent instructions", "Host import instructions",
]
META = ("schema_version", "app_id", "app_version", "schema_revision", "source_revision", "owner")
SNAPSHOT = "aya-filesystem-snapshot/v1"


def read(path):
    raw = Path(path).read_bytes()
    if len(raw) > 1024 * 1024:
        raise ValueError("input too large")
    return raw.decode("utf-8-sig", "strict")


def load_json(path):
    return json.loads(read(path))


def parse_kit(kit):
    lines = kit.splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("kit frontmatter absent")
    try:
        end = lines.index("---", 1)
    except ValueError as e:
        raise ValueError("incomplete frontmatter") from e
    fields = {}
    for line in lines[1:end]:
        if not line.strip():
            continue
        found = re.fullmatch(r"([a-z][a-z0-9_]*):\s*(.*?)\s*", line)
        if not found:
            raise ValueError("malformed frontmatter")
        k, v = found.groups()
        if k in fields:
            raise ValueError("duplicate kit metadata")
        fields[k] = v.strip('"').strip("'")
    if any(not fields.get(k) for k in META):
        raise ValueError("missing kit metadata")
    if fields["schema_version"] != "aya-filesystem-kit/v1":
        raise ValueError("unsupported kit format")
    body = "\n".join(lines[end + 1:])
    headings = re.findall(r"^## (.*?)\s*$", body, re.M)
    if headings != HEADINGS:
        raise ValueError("kit headings missing, repeated or reordered")
    sections = {}
    for i, title in enumerate(HEADINGS):
        start = body.index("## " + title) + len("## " + title)
        stop = body.index("## " + HEADINGS[i + 1]) if i + 1 < len(HEADINGS) else len(body)
        sections[title] = body[start:stop].strip()
        if len(sections[title]) < 35:
            raise ValueError("kit section too thin: " + title)
    if re.search(r"<(?:TODO|REPLACE|APP_ID|APP_VERSION|INSERT)[^>\n]{0,80}>", kit):
        raise ValueError("unresolved kit placeholder")
    found = re.search(r"^\x60{3}json\n(.*?)\n\x60{3}\s*$",
                      sections["Recipe output schema"], re.M | re.S)
    if not found:
        raise ValueError("recipe schema JSON block missing")
    return fields, sections, json.loads(found.group(1))


def validate_schema(schema, value, path="$"):
    """A bounded JSON Schema subset sufficient for repository fixtures.

    This does NOT replace a full 2020-12 validator in a real host importer.
    """
    if "const" in schema and value != schema["const"]:
        raise ValueError(path + " violates const")
    if "enum" in schema and value not in schema["enum"]:
        raise ValueError(path + " violates enum")
    mapping = {"object": dict, "array": list, "string": str,
               "integer": int, "boolean": bool, "null": type(None)}
    types = schema.get("type")
    if types:
        types = types if isinstance(types, list) else [types]
        if not any(isinstance(value, mapping[t]) and
                   not (t == "integer" and isinstance(value, bool)) for t in types):
            raise ValueError(path + " wrong type")
    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                raise ValueError(path + " missing " + key)
        allowed = schema.get("properties", {})
        if schema.get("additionalProperties") is False and set(value) - set(allowed):
            raise ValueError(path + " unknown key")
        for k, v in value.items():
            if k in allowed:
                validate_schema(allowed[k], v, path + "." + k)
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0) or len(value) > schema.get("maxItems", 999999999):
            raise ValueError(path + " wrong item count")
        if schema.get("uniqueItems") and len({json.dumps(x, sort_keys=True) for x in value}) != len(value):
            raise ValueError(path + " duplicate items")
        for i, item in enumerate(value):
            validate_schema(schema.get("items", {}), item, path + "[" + str(i) + "]")
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0) or len(value) > schema.get("maxLength", 999999999):
            raise ValueError(path + " invalid string length")
    if isinstance(value, int) and not isinstance(value, bool):
        if value < schema.get("minimum", float("-inf")):
            raise ValueError(path + " below minimum")


def validate_snapshot(snapshot, app_id, version):
    if snapshot.get("schema_version") != SNAPSHOT:
        raise ValueError("snapshot version")
    if snapshot.get("app_id") != app_id or snapshot.get("app_version") != version:
        raise ValueError("snapshot app identity mismatch")
    try:
        utc = datetime.fromisoformat(snapshot["generated_at_utc"].replace("Z", "+00:00"))
        if utc.tzinfo is None or utc.utcoffset() != timezone.utc.utcoffset(utc):
            raise ValueError("not UTC")
    except (KeyError, TypeError, ValueError) as e:
        raise ValueError("invalid snapshot timestamp") from e
    scan = snapshot["scan"]
    if scan["status"] == "complete" and scan["errors"]:
        raise ValueError("complete scan with failures")
    if scan["truncated"] and not scan.get("truncation_reason"):
        raise ValueError("truncated without reason")
    if len(snapshot["entries"]) > 2500:
        raise ValueError("too many snapshot entries")


def validate(kit_path, schema_path, example_path, snapshot_path):
    kit_text = read(kit_path)
    fields, sections, embedded = parse_kit(kit_text)
    schema = load_json(schema_path)
    if embedded != schema:
        raise ValueError("embedded and standalone schema mismatch")
    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        raise ValueError("unexpected schema dialect")
    if not all(x in sections["Agent instructions"].lower() for x in ("clarif", "credential", "schema")):
        raise ValueError("agent guidance incomplete")
    if not all(x in sections["Safety and execution"].lower() for x in ("approval", "preview", "scan")):
        raise ValueError("safety requirements missing")
    recipe = load_json(example_path)
    validate_schema(schema, recipe)
    snapshot_raw = Path(snapshot_path).read_bytes()
    if len(snapshot_raw) > 512 * 1024:
        raise ValueError("snapshot exceeds 512 KiB")
    snapshot = json.loads(snapshot_raw.decode("utf-8-sig"))
    snapshot_schema = load_json(Path(__file__).resolve().parents[1] /
                                "docs/filesystem/schemas/aya-filesystem-snapshot-v1.schema.json")
    validate_schema(snapshot_schema, snapshot)
    validate_snapshot(snapshot, fields["app_id"], fields["app_version"])
    return {"kit": str(kit_path), "schema_revision": fields["schema_revision"],
            "snapshot_status": snapshot["scan"]["status"], "recipe_keys": len(recipe)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("kit")
    parser.add_argument("--schema", required=True)
    parser.add_argument("--example", required=True)
    parser.add_argument("--snapshot", required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(validate(args.kit, args.schema, args.example, args.snapshot), sort_keys=True))
    except (OSError, UnicodeError, ValueError, KeyError, TypeError) as e:
        parser.exit(1, "Filesystem kit validation failed: " + str(e) + "\n")


if __name__ == "__main__":
    main()
