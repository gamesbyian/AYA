# AYA cross-toolchain adapter status (2026-10-31)

This inventory separates **checked-in source**, CI builds, Android host acceptance, and distribution. Merged code is not equivalent to a marketplace plugin, and opening Android's Sharesheet does not prove assistant ingestion. Keep this ledger current whenever an adapter ships or changes.

| Environment | In repository | Verified so far | Outstanding release gates |
|---|---|---|---|
| Android Views/XML | Canonical AYA AAR, host-themed cards, XML layout control, guarded actions, help-only manifest, non-destructive scaffolder | Module/sample and staged Maven consumer tests, emulator handoff and XML tests | Published versioned distribution; multiple real host apps; physical device, TalkBack and recipient acceptance |
| Jetpack Compose | Optional Compose AAR, saveable card, action launcher and host callbacks | Gradle build and emulator/sample tests | Public artifact, diverse host themes, 200% text and device checks |
| Godot 4 Android | Android v2 Kotlin plugin, GDScript card/editor addon and staged AARs | Godot 4.5.1 headless parser plus Gradle source build; multiline input and missing-output negative smoke under review | Manual editor install, Android APK export and correct guide asset verification |
| Flutter | Android-only Dart card/headless action and Kotlin ActivityAware bridge | Analyzer, mocked widget/channel tests and complete Flutter Android APK build in [CI run 41233862629](https://github.com/gamesbyian/AYA/actions/runs/41233862629); an additional exact-guide and merged-manifest inspection suite is under review | Public native AAR distribution; matching host APK guide; real-device testing; pub.dev |
| FlutterFlow | Custom Widget and Custom Action body templates | Source-contract/docs tests | Actual FlutterFlow editor import/export and publicly resolvable native SDK; not a marketplace component |
| React Native / Expo | Expo guide-asset prebuild helper and Android-only typed Expo Modules bridge with React Native card (source previews) | Guide-plugin filesystem/identity tests and Expo bridge TypeScript/mock contract tests passed | Real Expo CNG/native build with staged AYA AAR, compiled APK guide/manifest verification, Activity/device/recipient tests and npm publication |
| Unity | Specifications | No implemented adapter | UPM, Android plugin, visual nodes, exported APK tests |
| App Inventor / Kodular | Feasibility plan | No shipped extension | Platform extension, APK asset/consent testing |

**All adapters share the same trust boundary:** verified exact-version host guide, user-edited local review, deliberate Copy/Share, truthful output-use instructions, no provider lock-in, and no monitoring of agent answers. A host-owned file importer is separate; generated recipes remain untrusted and must not be executed unattended.

Priorities: run the [non-public versioned Maven preview](DISTRIBUTION.md) and then release reproducible native artifacts; build a real host with matching Android APK guide; verify FlutterFlow editor export and Godot Android export; do TalkBack, keyboard, font-scale and receiver testing; then expand React Native/Expo and Unity. See [architecture](README.md), [roadmap](ROADMAP.md), [Flutter](FLUTTER.md), [FlutterFlow](FLUTTERFLOW.md), [Godot](GODOT.md) and [installation](INSTALLER.md).
