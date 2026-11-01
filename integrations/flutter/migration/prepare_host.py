#!/usr/bin/env python3
"""Make a disposable Flutter/AGP9 plugin consumer without modifying legacy source.

The modern plugin is a *candidate* only. This script is intentionally strict
about the generated Flutter host: unexpected templates must fail for review.
"""
from __future__ import annotations
import argparse
import os
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT / "integrations/flutter/aya_flutter"
TRIAL = HERE / "generated/aya_flutter"
HOST = TRIAL / "example"


def replace_exact(text: str, old: str, new: str, reason: str) -> str:
    if text.count(old) != 1:
        raise RuntimeError(f"{reason}: expected one exact anchor, found {text.count(old)}")
    return text.replace(old, new)


def prepare() -> None:
    if TRIAL.exists():
        shutil.rmtree(TRIAL)
    TRIAL.mkdir(parents=True)
    for directory in ("android", "lib", "test"):
        shutil.copytree(SOURCE / directory, TRIAL / directory)
    for file in ("analysis_options.yaml",):
        if (SOURCE / file).is_file():
            shutil.copyfile(SOURCE / file, TRIAL / file)
    shutil.copyfile(HERE / "modern.android.gradle", TRIAL / "android/build.gradle")
    shutil.copyfile(HERE / "modern.pubspec.yaml", TRIAL / "pubspec.yaml")
    print(f"Disposable modern candidate staged in {TRIAL}")


def configure(host: Path | None = None, package: Path | None = None) -> None:
    host = host or HOST
    package = package or SOURCE
    if not (host / "android").is_dir():
        raise RuntimeError("Flutter generated Android host missing; run flutter create first")
    # The package need not be a sibling of the generated Flutter host.
    # Compute a real relative path so this works for out-of-tree source
    # package consumers; do not bake the AYA repository layout into the host.
    host_root = host.resolve()
    package_root = package.resolve()
    if not (package_root / "pubspec.yaml").is_file():
        raise RuntimeError("Flutter AYA source package pubspec missing")
    relative_package = Path(os.path.relpath(package_root, host_root)).as_posix()
    if any(ord(ch) < 32 for ch in relative_package):
        raise RuntimeError("Invalid characters in Flutter package source path")
    # Quote YAML string values (doubling any single quotes) to safely support
    # spaces, colons and punctuation in a developer-owned directory path.
    yaml_path = "'" + relative_package.replace("'", "''") + "'"
    pub = host / "pubspec.yaml"
    value = pub.read_text()
    if not re.search(r"(?m)^version:\s*1\.0\.0\+1\s*$", value):
        raise RuntimeError("Generated app version changed; re-audit CI AYA-RAS guide")
    # Match the top-level YAML key, not the suffix of dev_dependencies.
    value, count = re.subn(
        r"(?m)^dependencies:[ \\t]*$",
        "dependencies:\\n  aya_flutter:\\n    path: " + yaml_path,
        value,
    )
    if count != 1:
        raise RuntimeError("Host pubspec must have one top-level dependencies key")
    pub.write_text(value)

    target = host / "android/app/src/main/assets"
    target.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(package / "ci-host/aya-guide.md", target / "aya-guide.md")
    shutil.copyfile(package / "ci-host/main.dart", host / "lib/main.dart")

    settings = host / "android/settings.gradle.kts"
    if not settings.is_file():
        raise RuntimeError("Unexpected Flutter Gradle settings format")
    source = settings.read_text()
    source, count = re.subn(
        r'(?m)^(\s*id\("com\.android\.application"\)\s+version\s+")[^"]+("\s+apply false\s*)$',
        lambda m: m.group(1) + "9.0.1" + m.group(2), source)
    if count != 1:
        raise RuntimeError("Expected one Flutter Android application AGP version")
    # KGP remains in generated settings as an unused declaration only if the
    # Flutter tooling owns it; no application/plugin project may APPLY KGP.
    source += """
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.PREFER_SETTINGS)
    repositories {
        google()
        mavenCentral()
        maven { url = uri(System.getenv("AYA_STAGING_MAVEN")
            ?: error("AYA_STAGING_MAVEN missing: native AAR must be staged")) }
        maven { url = uri("https://storage.googleapis.com/download.flutter.io") }
    }
}
"""
    settings.write_text(source)

    app = host / "android/app/build.gradle.kts"
    if not app.is_file():
        raise RuntimeError("Unexpected Flutter application Gradle format")
    value = app.read_text()
    value, removed = re.subn(
        r'(?m)^\s*id\("(?:kotlin-android|org\.jetbrains\.kotlin\.android)"\)\s*\n',
        "", value)
    if removed > 1:
        raise RuntimeError("More than one Kotlin plugin in host")
    value, count = re.subn(
        r'(?ms)^\s*kotlinOptions\s*\{.*?^\s*\}\s*\n', "\n", value)
    if count > 1:
        raise RuntimeError("Multiple legacy Kotlin options in host")
    value += """
// Migrated host: compile Kotlin through AGP 9 instead of applying KGP.
kotlin {
    compilerOptions {
        jvmTarget = org.jetbrains.kotlin.gradle.dsl.JvmTarget.JVM_17
    }
}
"""
    app.write_text(value)

    wrapper = host / "android/gradle/wrapper/gradle-wrapper.properties"
    if not wrapper.is_file():
        raise RuntimeError("Flutter generated Gradle wrapper missing")
    value = wrapper.read_text()
    value, count = re.subn(r"gradle-[0-9][^/]*-(?:all|bin)\.zip",
                           "gradle-9.1.0-all.zip", value)
    if count != 1:
        raise RuntimeError("Unexpected Gradle distribution URL")
    wrapper.write_text(value)

    props = host / "android/gradle.properties"
    value = props.read_text()
    # Explicitly override Flutter's temporary old-KGP default; AGP new DSL
    # remains disabled to retain transitional Flutter Gradle compatibility.
    value = re.sub(r"(?m)^android\.builtInKotlin=.*\n?", "", value)
    value = re.sub(r"(?m)^android\.newDsl=.*\n?", "", value)
    props.write_text(value.rstrip() +
                     "\nandroid.builtInKotlin=true\nandroid.newDsl=false\n")
    print("AGP 9.0.1, Gradle 9.1.0, built-in Kotlin true, versioned guide staged")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "configure"))
    parser.add_argument("--host", type=Path, help="Explicit generated host for canonical source")
    parser.add_argument("--source", type=Path, help="Host-owning Flutter package root")
    args = parser.parse_args()
    if args.action == "prepare":
        if args.host or args.source:
            parser.error("--host and --source apply only to configure")
        prepare()
    else:
        configure(args.host, args.source)


if __name__ == "__main__":
    main()
