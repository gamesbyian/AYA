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

- Expo has first-party APK/guide/manifest/DEX evidence. A clean npm tarball consumer is tracked separately and remains a synthetic host until an independently developed app is tested.
- Flutter's AGP 9 built-in Kotlin promoted source passed a first-party real-host APK test ([CI 41249286150](https://github.com/gamesbyian/AYA/actions/runs/41249286150)). Legacy KGP remains a **separately pinned source version**. External Flutter/FlutterFlow editors, actual devices and recipients remain unverified.
- Godot has native AAR and headless editor evidence. Actual Android export with the host's raw APK guide and real editor integration are independent requirements.
- Unity has native AAR and stand-in C# compilation evidence. Actual Unity Editor import, exported Android APK, Mono/IL2CPP and device lifecycle are unverified.

Use [the adapter status ledger](STATUS.md) for the latest evidence and issues [#21](https://github.com/gamesbyian/AYA/issues/21), [#14](https://github.com/gamesbyian/AYA/issues/14), [#4](https://github.com/gamesbyian/AYA/issues/4), and [#5](https://github.com/gamesbyian/AYA/issues/5) for unresolved release gates.
