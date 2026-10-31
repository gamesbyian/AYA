#!/usr/bin/env python3
"""Verify staged AYA Maven AAR/POM distribution before previewing a release.

This is a structural release preview, not a cryptographic attestation of source,
installed APK compatibility or external assistant behaviour.
"""
import argparse
import hashlib
import re
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

VERSION = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z][0-9A-Za-z.-]*)?$")
ARTIFACTS = ("aya-android", "aya-compose")
NS = {"m": "http://maven.apache.org/POM/4.0.0"}


def check(root: Path, version: str) -> dict[str, str]:
    if not VERSION.fullmatch(version) or version.endswith("-SNAPSHOT"):
        raise ValueError("Choose an explicit non-SNAPSHOT semantic version")
    manifest = {}
    for artifact in ARTIFACTS:
        folder = root / "dev" / "aya" / artifact / version
        pom = folder / f"{artifact}-{version}.pom"
        aar = folder / f"{artifact}-{version}.aar"
        for path in (pom, aar):
            if not path.is_file() or path.stat().st_size == 0:
                raise ValueError(f"Missing/empty artifact: {path}")
            manifest[path.relative_to(root).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
        tree = ET.parse(pom)
        element = tree.getroot()
        def field(name):
            e = element.find("m:" + name, NS)
            return None if e is None else e.text
        if (field("groupId"), field("artifactId"), field("version")) != ("dev.aya", artifact, version):
            raise ValueError(f"Unexpected coordinates in {pom}")
        if artifact == "aya-compose":
            deps = element.findall(".//m:dependency", NS)
            expected = [d for d in deps
                        if d.findtext("m:groupId", namespaces=NS) == "dev.aya"
                        and d.findtext("m:artifactId", namespaces=NS) == "aya-android"]
            if len(expected) != 1 or expected[0].findtext("m:version", namespaces=NS) != version:
                raise ValueError("Compose dependency must pin matching aya-android version")
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--checksum-output", type=Path)
    args = parser.parse_args(argv)
    try:
        results = check(args.root, args.version)
    except (OSError, ValueError, ET.ParseError) as exc:
        print(f"AYA Maven preview invalid: {exc}", file=sys.stderr)
        return 2
    lines = [f"{digest}  {path}" for path, digest in sorted(results.items())]
    if args.checksum_output:
        args.checksum_output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
