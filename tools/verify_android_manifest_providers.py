#!/usr/bin/env python3
"""Check independent, private FileProviders in a final Android APK.

Android manifests merge <provider> by android:name, so matching provider
strings elsewhere in an APK is not evidence that both SDKs survived. This
reads the final binary manifest via Android SDK's aapt XML tree, pairs each
provider's own authority, flags and child path metadata, and rejects collisions.
It does not infer URI grant runtime behavior or receiving-app ingestion.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ELEMENT = re.compile(r"^(\s*)E:\s+([A-Za-z_][A-Za-z0-9_.:-]*)(?:\s|$)")
ATTRIBUTE = re.compile(
    r"^\s*A:\s+android:([A-Za-z][A-Za-z0-9]*)"
    r"(?:\([^)]*\))?=(.*)$"
)
QUOTED = re.compile(r'^"([^"]*)"')
TYPED_BOOLEAN = re.compile(r"^\(type 0x12\)0x([0-9a-fA-F]+)")
JAVA_CLASS = re.compile(r"^[A-Za-z_][\w$]*(?:\.[A-Za-z_][\w$]*)+$")
AUTHORITY = re.compile(r"^[A-Za-z0-9_.-]+$")
MAX_XMLTREE_BYTES = 4 * 1024 * 1024
MAX_NODES = 12000


class ProviderError(ValueError):
    pass


def _value(raw: str) -> str:
    found = QUOTED.match(raw)
    return found.group(1) if found else raw.strip()


def _bool(raw: str) -> bool | None:
    text = _value(raw).lower()
    if text in ("true", "false"):
        return text == "true"
    found = TYPED_BOOLEAN.match(text)
    if found:
        return int(found.group(1), 16) != 0
    return None


def parse_providers(xmltree: str) -> list[dict]:
    if len(xmltree) > MAX_XMLTREE_BYTES:
        raise ProviderError("Android manifest XML tree exceeds inspection budget")
    root = {"tag": "__root__", "attrs": {}, "children": []}
    stack: list[tuple[int, dict]] = [(-1, root)]
    count = 0
    for line in xmltree.splitlines():
        node_match = ELEMENT.match(line)
        if node_match:
            depth, tag = len(node_match.group(1)), node_match.group(2)
            while stack[-1][0] >= depth:
                stack.pop()
            parent = stack[-1][1]
            node = {"tag": tag, "attrs": {}, "children": []}
            parent["children"].append(node)
            stack.append((depth, node))
            count += 1
            if count > MAX_NODES:
                raise ProviderError("Android manifest has too many elements")
            continue
        attr = ATTRIBUTE.match(line)
        if attr and stack[-1][1] is not root:
            name, raw = attr.groups()
            attrs = stack[-1][1]["attrs"]
            if name in attrs:
                raise ProviderError("Duplicate Android manifest attribute: " + name)
            attrs[name] = raw
    result = []
    for manifest in root["children"]:
        if manifest["tag"] != "manifest":
            continue
        for app in manifest["children"]:
            if app["tag"] != "application":
                continue
            for node in app["children"]:
                if node["tag"] != "provider":
                    continue
                a = node["attrs"]
                meta = []
                for child in node["children"]:
                    if child["tag"] == "meta-data":
                        ma = child["attrs"]
                        meta.append((_value(ma.get("name", "")),
                                     _value(ma.get("resource", ""))))
                result.append({
                    "class": _value(a.get("name", "")),
                    "authority": _value(a.get("authorities", "")),
                    "exported": _bool(a.get("exported", "")),
                    "grants": _bool(a.get("grantUriPermissions", "")),
                    "paths": meta,
                })
    return result


def check_providers(
    apk: Path, aapt: str, expected: dict[str, str],
    *, command_runner=subprocess.run,
) -> list[dict]:
    if not apk.is_file() or apk.is_symlink() or not aapt:
        raise ProviderError("Expected a real APK and aapt executable path")
    if not isinstance(expected, dict) or not expected:
        raise ProviderError("At least one expected provider is required")
    for cls, authority in expected.items():
        if not JAVA_CLASS.fullmatch(cls) or not AUTHORITY.fullmatch(authority):
            raise ProviderError("Provider class and authority must be fully qualified")
    if len(set(expected.values())) != len(expected):
        raise ProviderError("Expected providers must have independent authorities")

    try:
        cmd = command_runner(
            [aapt, "dump", "xmltree", str(apk), "AndroidManifest.xml"],
            capture_output=True, text=True, check=False, timeout=30,
        )
    except subprocess.TimeoutExpired as exc:
        raise ProviderError("Android manifest inspection timed out") from exc
    if cmd.returncode:
        raise ProviderError("Cannot read final APK manifest: " + cmd.stderr[:300])
    observed = parse_providers(cmd.stdout)
    classes = [item["class"] for item in observed]
    authorities = [item["authority"] for item in observed if item["authority"]]
    if len(classes) != len(set(classes)):
        raise ProviderError("Duplicate provider class in final manifest")
    if len(authorities) != len(set(authorities)):
        raise ProviderError("Provider authorities collide in final manifest")

    for cls, authority in expected.items():
        providers = [x for x in observed if x["class"] == cls]
        if len(providers) != 1:
            raise ProviderError("Required independent FileProvider is missing: " + cls)
        p = providers[0]
        if p["authority"] != authority:
            raise ProviderError("Provider authority mismatched: " + cls)
        if p["exported"] is not False or p["grants"] is not True:
            raise ProviderError("Provider export/grant security flags invalid: " + cls)
        paths = [resource for name, resource in p["paths"]
                 if name == "android.support.FILE_PROVIDER_PATHS"]
        if len(paths) != 1 or not paths[0].startswith("@"):
            raise ProviderError("Provider is missing scoped file-path XML: " + cls)
    return observed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apk", type=Path, required=True)
    parser.add_argument("--aapt", required=True)
    parser.add_argument("--provider", action="append", required=True,
                        help="Exact fully qualified Class=applicationId.suffix")
    args = parser.parse_args(argv)
    expected: dict[str, str] = {}
    for pair in args.provider:
        cls, delim, authority = pair.partition("=")
        if not delim or cls in expected:
            parser.exit(1, "Android FileProviders: malformed or duplicate --provider\n")
        expected[cls] = authority
    try:
        result = check_providers(args.apk, args.aapt, expected)
    except (OSError, ProviderError) as exc:
        parser.exit(1, f"Android FileProviders: FAIL: {exc}\n")
    print(f"Android FileProviders: PASS: {len(expected)} independent scoped providers "
          f"of {len(result)} declared")
    print("Scope: final binary manifest only; not device behavior or recipient ingestion")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
