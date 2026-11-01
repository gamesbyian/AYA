# Adapter release evidence and claim boundaries

This is a common acceptance checklist for **every** optional AYA host adapter. A module's build, a first-party sample APK, an independent consuming application, and a recipient's use of an attachment prove different things. Keep evidence attached to the exact source and binary revision; never silently upgrade a claim.

| Evidence level | What must have been observed | Safe claim |
| --- | --- | --- |
| S0 | Source and dependency declarations checked into the repository | Source preview |
| S1 | Compiler, unit tests and public native entry-point verification | Source/build validated |
| S2 | An actual first-party host APK, installed identity/version, exact guide bytes, merged manifest and native DEX definitions | First-party Android packaging validated |
| S2+ | Adapter installed from an npm/UPM/Maven package in an out-of-tree synthetic host, with a real compiled APK | Package installation smoke validated, synthetic host only |
| S3 | Independently authored consuming host, clean editor/prebuild/export and no undisclosed source-tree dependencies | Independent host integration validated |
| S4 | Physical device interaction, lifecycle, accessibility, Copy/Share/cancellation and negative cases | Device interaction validated for listed setup |
| S5 | Controlled complete text/attachment receipt in dated individual AI recipient app versions | Specific recipient ingestion validated |
| S6 | Reproducible, versioned publicly resolvable artifacts, verified checksums/provenance, install and rollback instructions | Public distribution supported |

Never infer S3 from a relocated copy of a first-party fixture or S5 from Android chooser launch. S6 distribution does not imply S4 accessibility or S5 receiver ingestion. An AYA project-specific developer packet must be authored from the actual host, not AYA's fictional examples.

## Required acceptance record

For each run capture: host repository/revision or explicitly synthetic fixture identity; AYA revision; tool versions; Android API and device/emulator; build commands; artifact digest; reference guide digest; positive and negative cases; known workarounds; and the precise untested boundary. Evidence links should point to immutable jobs/artifacts when possible.

A test must fail closed when the guide is absent, stale or inconsistent with installed Android package/version; the native adapter is unavailable; an Activity is detached; the selected receiver is missing; or an unknown status returns from the native bridge. No hidden scanning, automatic imported agent replies, or bypass of editable review.

## Clean consumer procedure

1. Install the relevant AYA distribution format outside the monorepo, using pinned package versions and **no** undocumented `../AYA` source paths.
2. Author a source-derived AYA-RAS guide for that consuming host, audit it independently, then package it in actual APK assets.
3. Inspect the **final APK** for exact guide bytes, installed package/version identity, FileProvider and receiver declarations, and defined native adapter classes.
4. Test visible help UI, optional question composition, editable review, Cancel, Copy, explicit Share, duplicate actions, disabled/no-recipient states, Activity recreation and font/input accessibility on supported devices.
5. Test receiving assistant app versions independently: whether the actual complete reviewed text and intended file are visible. A chooser opening only demonstrates a local Android dispatch.
6. Review provenance, version compatibility, stable installation and uninstallation, rollback and source-package license conditions before any public release claim.

## Current independent gates

- Expo has S2+ evidence: a genuine npm-tarball consumer created outside the checkout, with complete real Android APK, identity/guide/manifest/DEX inspection ([CI 41259561589](https://github.com/gamesbyian/AYA/actions/runs/41259561589)) and separately exported Metro JavaScript ([CI 41259561573](https://github.com/gamesbyian/AYA/actions/runs/41259561573)). The test host is still authored by AYA maintainers; independent adopting developers, physical devices and AI recipients are unverified.
- Flutter's AGP 9 built-in Kotlin promoted source passed a first-party real-host APK test ([CI 41249286150](https://github.com/gamesbyian/AYA/actions/runs/41249286150)) and out-of-tree synthetic source-package APK inspection ([CI 41250574535](https://github.com/gamesbyian/AYA/actions/runs/41250574535)), qualifying only for S2+. Legacy KGP remains a **separately pinned source version**. External Flutter/FlutterFlow editors, independent adopter authorship, actual devices and recipients remain unverified.
- Godot has **S2 actual-engine packaging**, followed by a limited **emulator runtime smoke**: Godot 4.5.1 produced its own Gradle APK and verified guide/receivers/providers/native registration ([CI 41264756578](https://github.com/gamesbyian/AYA/actions/runs/41264756578)); the same exported APK then started on Android 35 x86_64, with a live Godot process, enabled card and registered native singleton in 412×892 and 320×700/200% font configurations ([CI 41266974910](https://github.com/gamesbyian/AYA/actions/runs/41266974910)). **This is not full S4**: it has not shown a person can tap, read, navigate via TalkBack, Copy/Share or complete assistant ingestion; independently authored game adoption remains S3-unverified.
- MIT App Inventor v206 has an unpublished, genuine Rush 2.1.2 **S1 AIX source-extension build** ([CI 41267356990](https://github.com/gamesbyian/AYA/actions/runs/41267356990)). A consuming App Inventor-built APK, exact native AYA-RAS guide, bundled AndroidX compatibility, provider/receiver merge, editor UX, physical device and assistant ingestion are **not verified**; Kodular is a separate compatibility target.
- Unity has native AAR and stand-in C# compilation evidence. Actual Unity Editor import, exported Android APK, Mono/IL2CPP and device lifecycle are unverified.

Use [the adapter status ledger](STATUS.md) for the latest evidence and issues [#21](https://github.com/gamesbyian/AYA/issues/21), [#14](https://github.com/gamesbyian/AYA/issues/14), [#4](https://github.com/gamesbyian/AYA/issues/4), and [#5](https://github.com/gamesbyian/AYA/issues/5) for unresolved release gates.
