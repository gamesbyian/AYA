#!/usr/bin/env python3
"""Verify staged AYA Maven AAR/POM distribution before previewing a release.

This is a structural release preview, not a cryptographic attestation of source,
installed APK compatibility or external assistant behaviour.
"""
import argparse
import hashlib
import re
import sys
import io
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

VERSION = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z][0-9A-Za-z.-]*)?$")
ARTIFACTS = ("aya-android", "aya-compose")
NS = {"m": "http://maven.apache.org/POM/4.0.0"}
MAX_AAR_BYTES = 128 * 1024 * 1024
MAX_CLASSES_JAR_BYTES = 64 * 1024 * 1024
REQUIRED_CLASSES = {
    "aya-android": (
        "dev/aya/android/Aya.class",
        "dev/aya/android/AyaReferenceVerifier.class",
        "dev/aya/android/AyaComponentAction.class",
        "dev/aya/android/AyaShareSelectionReceiver.class",
    ),
    "aya-compose": ("dev/aya/compose/AyaComposeKt.class",),
}


def validate_aar(aar: Path, artifact: str) -> None:
    """Inspect the actual published AAR, not just its name and byte count.

    This proves that expected compiled types are packaged. It does not prove
    source provenance, binary API compatibility, or a consuming APK's behavior.
    """
    if aar.stat().st_size > MAX_AAR_BYTES:
        raise ValueError(f"AYA AAR exceeds inspection budget: {aar}")
    try:
        with zipfile.ZipFile(aar) as archive:
            names = [entry.filename for entry in archive.infolist()]
            if len(names) != len(set(names)):
                raise ValueError(f"Duplicate AAR entries: {aar}")
            if any(
                name.startswith("/") or chr(92) in name or
                ".." in name.split("/") or "" in name.split("/")[:-1]
                for name in names
            ):
                raise ValueError(f"Unsafe AAR entry path: {aar}")
            if archive.testzip() is not None:
                raise ValueError(f"AAR has damaged archive member: {aar}")
            for entry in ("AndroidManifest.xml", "classes.jar"):
                if entry not in names:
                    raise ValueError(f"Missing required AAR member {entry}: {aar}")
            if archive.getinfo("AndroidManifest.xml").file_size == 0:
                raise ValueError(f"Empty AAR Android manifest: {aar}")
            classes_info = archive.getinfo("classes.jar")
            if not (0 < classes_info.file_size <= MAX_CLASSES_JAR_BYTES):
                raise ValueError(f"Invalid AAR classes.jar length: {aar}")
            with zipfile.ZipFile(io.BytesIO(archive.read("classes.jar"))) as classes:
                class_names = [member.filename for member in classes.infolist()]
                if len(class_names) != len(set(class_names)):
                    raise ValueError(f"Duplicate compiled class entry: {aar}")
                if classes.testzip() is not None:
                    raise ValueError(f"Damaged compiled class entry: {aar}")
                for expected in REQUIRED_CLASSES[artifact]:
                    if expected not in class_names:
                        raise ValueError(f"Missing compiled {expected} in {aar}")
    except (zipfile.BadZipFile, zipfile.LargeZipFile) as exc:
        raise ValueError(f"Corrupt published AAR/classes.jar: {aar}") from exc


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
        validate_aar(aar, artifact)
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
