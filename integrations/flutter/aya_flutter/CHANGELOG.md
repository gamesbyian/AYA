# Changelog

## 0.2.0-dev.1 (source preview, not published)

- Raise declared minimum to Flutter 3.44.0 and Dart 3.12.0.
- Remove the legacy Kotlin Gradle Plugin application and plugin-local pinned
  KGP/AGP classpaths in favor of host-owned Android Gradle Plugin and the
  built-in Kotlin `kotlin.compilerOptions` DSL.
- Validate real Flutter 3.47.9 / AGP 9.0.1 / Gradle 9.1.0 Android host builds
  with built-in Kotlin enabled, exact source-authored AYA guide and native APK
  manifest/class verification. Physical-device and assistant ingestion tests
  remain separate.
- Preserve the one-way exact-version-guarded AYA Android handoff API and local
  result semantics. No model service, telemetry or output watcher added.
- **Compatibility break:** older Flutter/Dart consumers must pin the
  `0.1.0-dev.1` source at Git revision
  `fb5e004eea766261ed50194e8013b11fd9ade583`.

## 0.1.0-dev.1 (historical source preview)

- Initial Android-only Dart help card, platform channel and ActivityAware
  Kotlin bridge with Flutter >=3.19 / Dart >=3.3 and legacy Kotlin Gradle
  Plugin. Not published on pub.dev.
