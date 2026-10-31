#!/usr/bin/env python3
"""Make a disposable Flutter/AGP9 plugin consumer without modifying legacy source.

The modern plugin is a *candidate* only. This script is intentionally strict
about the generated Flutter host: unexpected templates must fail for review.
"""
from __future__ import annotations
import argparse
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


def configure() -> None:
    if not (HOST / "android").is_dir():
        raise RuntimeError("Flutter generated Android host missing; run flutter create first")
    pub = HOST / "pubspec.yaml"
    value = pub.read_text()
    if not re.search(r"(?m)^version:\s*1\.0\.0\+1\s*$", value):
        raise RuntimeError("Generated app version changed; re-audit CI AYA-RAS guide")
    value = replace_exact(value, "dependencies:\n",
                          "dependencies:\n  aya_flutter:\n    path: ..\n",
                          "Host pubspec dependencies")
    pub.write_text(value)

    target = HOST / "android/app/src/main/assets"
    target.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SOURCE / "ci-host/aya-guide.md", target / "aya-guide.md")
    shutil.copyfile(SOURCE / "ci-host/main.dart", HOST / "lib/main.dart")

    settings = HOST / "android/settings.gradle.kts"
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

    app = HOST / "android/app/build.gradle.kts"
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

    wrapper = HOST / "android/gradle/wrapper/gradle-wrapper.properties"
    if not wrapper.is_file():
        raise RuntimeError("Flutter generated Gradle wrapper missing")
    value = wrapper.read_text()
    value, count = re.subn(r"gradle-[0-9][^/]*-(?:all|bin)\.zip",
                           "gradle-9.1.0-all.zip", value)
    if count != 1:
        raise RuntimeError("Unexpected Gradle distribution URL")
    wrapper.write_text(value)

    props = HOST / "android/gradle.properties"
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
    args = parser.parse_args()
    (prepare if args.action == "prepare" else configure)()


if __name__ == "__main__":
    main()
