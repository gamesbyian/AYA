# Flutter built-in Kotlin migration: source preview and evidence

**Status:** the Flutter AGP 9 built-in Kotlin **trial passed**, and the
primary source-preview plugin has been promoted from `0.1.0-dev.1` to
`0.2.0-dev.1`. This does **not** publish a package, grant receiving
assistant compatibility, or establish all external host toolchains.

## Tested migration and compatibility matrix

| Consumer | Source path / compatibility | Verification |
|---|---|---|
| Flutter >=3.19 / Dart >=3.3, legacy KGP/AGP 8 | Frozen `aya_flutter@0.1.0-dev.1` source at Git SHA `fb5e004eea766261ed50194e8013b11fd9ade583`; do not silently install the modern package | Real host and exact-version guide passed legacy [CI 41248634751](https://github.com/gamesbyian/AYA/actions/runs/41248634751) |
| Flutter >=3.44 / Dart >=3.12 / AGP9 with built-in Kotlin **false** | Flutter supports this transition upstream. AYA's new source-preview declared minimum is 3.44/3.12, but this *specific host configuration is not verified* | Unverified |
| Flutter 3.47.9 / Dart >=3.12 / AGP9.0.1 / Gradle9.1.0 / built-in Kotlin **true** | Merged `aya_flutter@0.2.0-dev.1` source preview, with host-owned exact-version guide and staged AYA AAR | Migrated disposable source-copy APK passed [CI 41248634708](https://github.com/gamesbyian/AYA/actions/runs/41248634708). The primary source checkout's real host APK/guide/DEX gate also passed [CI 41249286150](https://github.com/gamesbyian/AYA/actions/runs/41249286150) |
| FlutterFlow editor, external consuming app, real Android recipient | Source adapter import, native setup and on-device assistant attachment handling | Not independently verified |

This is an explicit minimum-support decision. Flutter's official
[plugin-author migration guide](https://docs.flutter.dev/release/breaking-changes/migrate-to-built-in-kotlin/for-plugin-authors)
requires a Flutter 3.44 / Dart 3.12 floor for the migrated compiler options.
Flutter 3.47 adds built-in Kotlin true host support. The version
`0.2.0-dev.1` is a **separate preview series**, not a backward-compatible
patch to an already-published stable release.

## Test architecture

`modern.android.gradle` and `modern.pubspec.yaml` preserve the green
migration trial's reviewed compiler and dependency configuration.
`prepare_host.py prepare` copies the AYA Flutter Dart/Kotlin source to
a disposable trial and uses those manifests. `prepare_host.py configure`
accepts an explicit `--host` and `--source` to configure the **actual**
root Flutter host, with exact-version guide verification, AGP 9.0.1,
Gradle 9.1.0, built-in Kotlin enabled and transitional AGP DSL disabled.

Both `.github/workflows/flutter-builtin-kotlin.yml` (experimental mirror)
and `.github/workflows/flutter.yml` (real source package) require the
canonical staged AYA core AAR, independent guide inventory and held-out
question audit, Android compilation, installed app package/version, exact
guide bytes, merged FileProvider/receiver and DEX class definitions.
They must reject a post-build downgrade to legacy `kotlin-android` and
must never substitute a dummy guide.

## Migration checklist for a consuming host

1. Confirm your Flutter SDK/Dart version. If below 3.44/3.12, pin the
   historical legacy AYA source checkout, or update the host deliberately.
2. Upgrade the Flutter host to a version compatible with AGP 9. For
   built-in Kotlin true, use Flutter 3.47+ and AGP 9+, with the minimum
   compatible Gradle wrapper. Remove applied Kotlin Gradle Plugin from
   host Android modules, move `android.kotlinOptions` to
   `kotlin.compilerOptions`, and test the host's **other** plugins.
3. Supply the unpublished canonical AYA native Android AAR and exact version
   from a controlled Maven staging repository. Do not silently omit
   dependencies or copy unrelated AAR variants.
4. Author a source-verified exact-installed-package/version AYA-RAS guide
   for **your** app and package it into raw Android APK `assets/`.
   Sample CI reference files must never be reused as real app guides.
5. Build your actual APK and inspect installed ID/version, guide bytes,
   merged manifest and compiled plugin classes. Test lifecycle, locale,
   accessibility, Copy fallback and receiving assistant separately.

Upstream docs:
- https://docs.flutter.dev/release/breaking-changes/migrate-to-built-in-kotlin/for-plugin-authors
- https://docs.flutter.dev/release/breaking-changes/migrate-to-built-in-kotlin/for-app-developers
- https://developer.android.com/build/releases/agp-9-0-0-release-notes
