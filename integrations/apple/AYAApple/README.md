# AYA Apple Swift Package (initial source preview)

Native Apple adapter for the [AYA portable interaction convention](../../../README.md). See [research](../../../docs/apple/RESEARCH.md), [architecture](../../../docs/apple/ARCHITECTURE.md) and [acceptance plan](../../../docs/apple/PLAN.md).

**Status on 2026-11-03:** Portable Swift protocol source and UIKit outgoing Share Sheet/clipboard helper. Local and CI SwiftPM tests passed for the Foundation validator, and [Xcode CI 41600191635](https://github.com/gamesbyian/AYA/actions/runs/41600191635) **compiled the native iOS Simulator SDK slice**. No installed iOS app, Share Sheet interaction or genuine AI receiver test yet. There is no release artifact, native AYA review card or host importer yet. This package does not implement App Intents or observe external responses.

```sh
cd integrations/apple/AYAApple
swift test
```

Two source targets:

- `AYAProtocol` (`Foundation` only): `AYAReference(guide:installedAppID:installedVersion:)` checks `aya-reference/v1` metadata, `platform: ios`, current app identity/version, 12 populated standard sections and obvious unresolved placeholders. `AYAReviewDraft` constructs the initial review text and `approve(editedText:)` produces a bounded `AYAApprovedPacket` containing **only** what the user actually approved. These structural checks do not prove the reference accurately describes the host.
- `AYAApple` (iOS/UIKit conditional): `AYAAppleSharing.present(packet:representation:from:anchoredTo:)` offers a native share sheet with either full plain text or a uniquely named `.txt` document. iPad source-view anchoring is required. `copyApprovedText` is a separate explicit clipboard action. There is no destination targeting, network call or result tracking.

A real host must load a bundled source-verified `aya-guide.md`, pass `Bundle.main.bundleIdentifier` and `CFBundleShortVersionString` to `AYAReference`, show **editable review of the entire exact packet before approval**, and call the native helper only when the user explicitly selects Copy or Share. The package cannot enforce visual review if an integrating developer calls `approve` without showing it; this requires integration and UI testing. For `textDocument` the helper writes a private UTF-8 cache file; do not delete it immediately on activity dismissal, when a receiver may still read it.

The returned generated artifact is never automatically acquired: the host must separately implement a user-owned Files/import path and validation/confirmation. Use Apple security-scoped URLs and coordinated reads, and never treat a filename or AYA marker as authorization. The basic design requires no app group, domain, account, assistant service or AI API key.

**Evidence limit:** SwiftPM Linux compilation excludes `#if os(iOS)`; independent native Xcode iOS Simulator SDK compilation **did** pass, but this does not demonstrate an installed host, interactive Share Sheet, accessible UI, real assistant ingestion or physical-device compatibility.
