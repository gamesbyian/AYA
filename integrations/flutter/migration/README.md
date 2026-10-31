# Flutter built-in Kotlin migration experiment

**Status:** experimental dual-lane migration proof, not a new distributed Flutter
plugin or a claim that the existing legacy package supports AGP 9 built-in Kotlin.
The existing `integrations/flutter/aya_flutter` implementation is unchanged.

## Why a parallel trial instead of immediately bumping the SDK minimum?

The checked-in legacy AYA Flutter adapter advertises Flutter >=3.19, Dart
>=3.3, AGP 8.7.3 and KGP 2.0.21. A current built-in Kotlin migration requires
Flutter >=3.44 and Dart >=3.12; enabling built-in Kotlin in an actual Flutter
host requires Flutter >=3.47 plus AGP >=9.0. This is a **meaningful increase**
in consumer requirements, not a patch update.

The separately tested `modern.android.gradle` and `modern.pubspec.yaml`
provide the proposed 0.2.0-dev.1 configuration without changing that legacy
package. `prepare_host.py` copies the existing source into a disposable
`generated/aya_flutter` folder and uses those candidates only there. A
generated Flutter Android host then receives the exact-version source-authored
CI reference, is pinned to AGP 9.0.1 / Gradle 9.1.0, and explicitly sets
`android.builtInKotlin=true` and `android.newDsl=false`. The app and
plugin must not apply `kotlin-android`. This is tested by an actual
`flutter build apk --debug` and APK identity, guide, manifest and DEX checks.

## Compatibility decision matrix

| Consumer | Support decision | Evidence |
|---|---|---|
| Flutter 3.19+ / Dart 3.3+ with legacy KGP/AGP 8 | Keep **current** source package 0.1.0-dev.1 intact until replacement acceptance; it is not generally published | Existing Flutter CI builds a real generated Android host with the exact guide. Actual physical-device behavior remains unverified |
| Flutter 3.44+ / Dart 3.12+ with AGP 9 but built-in Kotlin disabled | Transitional compatibility exists in Flutter's official guidance; **no AYA host test** in this experiment | Not certified; do not infer support merely from version numbers |
| Flutter 3.47.9 / Dart 3.12+ with AGP 9.0.1, Gradle 9.1.0 and built-in Kotlin enabled | Proposed successor 0.2.0-dev.1 in disposable CI source | Must pass real built APK inspection before this row can be called verified |
| Any Flutter version, any Android recipient | Actual AI recipient ingestion, physical-device accessibility and lifecycle | Independently unverified; requires dated controlled phone tests |

The host's installed package ID and version are checked against
`aya_flutter/ci-host/aya-guide.md`; the original test host is synthetic
and its guide must never be reused by another adopting app.

## Promotion prerequisites

1. Green pinned legacy CI **and** AGP 9 built-in-Kotlin trial for the same
   canonical native SDK and truthful guide (no skipped failing step).
2. Independently verify AGP/KGP host truth after Flutter build; reject hidden
   host migration back to `android.builtInKotlin=false`.
3. Preserve the compiled AYA Flutter bridge class, FileProvider, receiver,
   exact guide bytes and installed identity in final APK.
4. If promoting, release a new source-preview version with an explicit
   Flutter >=3.44/Dart >=3.12 SDK floor and a migration note. Existing
   source consumers needing the earlier baseline must pin the previous Git
   revision; no imaginary dual-compatibility API.
5. Real Android and FlutterFlow editor/recipient acceptance remain separate.

Sources:
- https://docs.flutter.dev/release/breaking-changes/migrate-to-built-in-kotlin/for-plugin-authors
- https://docs.flutter.dev/release/breaking-changes/migrate-to-built-in-kotlin/for-app-developers
- https://developer.android.com/build/releases/agp-9-0-0-release-notes
