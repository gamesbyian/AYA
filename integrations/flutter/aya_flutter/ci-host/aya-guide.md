---
schema_version: aya-reference/v1
app_id: com.example.aya_flutter_ci_host
app_name: AYA Flutter CI Host
app_version_min: 1.0.0
app_version_max: 1.0.0
platform: android
locale: en
guide_revision: 1
source_revision: flutter-ci-host-v1
last_verified_utc: 2026-10-31T19:00:00Z
owner: AYA maintainers
---

# AYA Flutter CI Host: exact-build reference

This reference describes ONLY the synthetic first-party Flutter Android host built by the
AYA repository's Flutter CI workflow. It is not documentation for an unrelated real app.
Its documented code lives at `integrations/flutter/aya_flutter/ci-host/main.dart`,
and its packaging mechanism is `.github/workflows/flutter.yml`. The host is a
test-only app with no private accounts, remote services, or file importer.
This guide does not certify any external assistant's attachment handling.

## Scope and version

- App ID: `com.example.aya_flutter_ci_host`. Android `versionName`: `1.0.0`.
- Android-only debug APK built from a generated Flutter project in CI.
- The host contains one AYA help card and a native Android AYA sharing bridge.
- Flutter desktop, iOS, FlutterFlow and production deployment are outside this fixture.
- Android's real installed package ID and version are checked again by AYA at runtime.

## Quick orientation

The screen displays the heading "AYA Flutter CI Host", a brief note explaining that
this is a test app, and one `AyaHelpCard`. The card displays what reference it offers,
what to do with an answer, a question field and the "Ask Your Agent" button. Its
purpose is to exercise Android APK packaging and the Flutter-to-native SDK linkage.
The card cannot read third-party assistant responses or import their attachments.

## Navigation map

- Host launch > AYA Flutter CI Host: open the single visible screen.
- Host screen > Question for your agent: optionally type a question.
- Host screen > Ask Your Agent: validate the exact-version guide, then open local editable review.
- Review > Cancel: return without sharing.
- Review > Copy: copy the reviewed text for manual paste into an assistant.
- Review > Share: open Android's chooser. A compatible recipient is not guaranteed.

## Task recipes

### TASK-001: Ask for help in this host [AVAILABLE]

- Applies to: CI debug host with matching 1.0.0 package metadata on Android.
- Start: AYA Flutter CI Host screen.
- Prerequisites: an installed version-matched guide and functional Flutter native plugin.
1. Optionally type a question inside the AYA card.
2. Tap "Ask Your Agent". The native AYA SDK validates this guide before showing a review.
3. Read and edit the complete proposed payload; remove any unwanted question details.
4. Choose Cancel to stop, Copy to paste manually, or Share to select a compatible receiver.
- Expect: local editable review, not an assistant answer.
- Verify: Copy/paste should reflect the user-approved text, not an earlier draft.
- Failure: see ERR-001 or ERR-002. No automatic retry or background transmission.
- Side effects: Copy changes clipboard contents; Share can send an approved reference.
- Evidence: `integrations/flutter/aya_flutter/ci-host/main.dart`,
  `integrations/flutter/aya_flutter/lib/aya_flutter.dart`,
  `integrations/flutter/aya_flutter/android/src/main/kotlin/dev/aya/flutter/AyaFlutterPlugin.kt`.
- Validation limit: APK package inspection proves packaging, not UI operation on a physical device.

## Features and settings

### F-001: Host-themed help card [AVAILABLE]

- Location: the single visible screen, under its heading.
- Fields: host description, offered attachment disclosure, answer-use instructions,
  and an optional multiline question.
- Defaults: no account, no automatic assistant choice, no implicit private files.
- Action: only a deliberate tap asks the bridge to open local guarded review.
- Persistence: text state belongs to the host/Flutter widget; no assistant reply is stored.
- Evidence: `integrations/flutter/aya_flutter/ci-host/main.dart`,
  `integrations/flutter/aya_flutter/lib/aya_flutter.dart`.

## Troubleshooting

### ERR-001: AYA reference unavailable [CONDITIONAL]

- Cause: incorrect/missing APK-level `aya-guide.md` or mismatched package/version metadata.
- Check: inspect the host APK and its versioned guide; do not substitute a guide for another app.
- Fix: rebuild with the matching, source-verified fixture. Do not disable the guard.
- Verification: the next local attempt can open review if the native Activity is available.
- Evidence: `aya/src/main/java/dev/aya/android/AyaReferenceVerifier.kt`.

### ERR-002: Receiver cannot process the shared document [CONDITIONAL]

- Cause: receiver not installed, no compatible share target, or receiver declines ingestion.
- Check: inspect the receiving app manually. A chooser launching is inconclusive.
- Fix: return to AYA review, Copy, and paste the visible text manually.
- Verification: only the actual receiver can demonstrate it used the text.
- Evidence: `aya/src/main/java/dev/aya/android/Aya.kt`.

## Limitations and unsupported behavior

- The host has no user account, backend, filesystem importer, image generator, or AI model. [UNSUPPORTED]
- The host does not watch, collect, or automatically apply a reply from an assistant. [UNSUPPORTED]
- AI client attachment ingestion, new-chat creation and answer generation are unverified. [UNKNOWN]
- CI verifies APK shape and a Flutter bridge build, but does not exercise recipient behavior. [UNKNOWN]

## Privacy and data handling

The card holds only a question typed by the user; no source scanning or private file collection
occurs. The compiled app includes a developer-authored guide that describes this synthetic
host. AYA presents an editable full reference before a Share or Copy action. The selected
receiver may retain text after sharing. Copy places the approved text on Android's clipboard.
Avoid inserting credentials or private data in the question. There is no telemetry backend.

## Glossary and synonyms

- AYA: the local user-approved Ask Your Agent handoff interaction.
- Host: this synthetic Flutter app, not an AI provider.
- Reference guide: the packaged `aya-guide.md` matched to installed Android app identity.
- Review: local editable text; opening it does not contact an assistant.
- Sharesheet: Android's recipient chooser for explicit user sharing.

## Evidence and provenance

- Host Flutter UI: `integrations/flutter/aya_flutter/ci-host/main.dart`.
- Native bridge: `integrations/flutter/aya_flutter/android/src/main/kotlin/dev/aya/flutter/AyaFlutterPlugin.kt`.
- APK preparation: `.github/workflows/flutter.yml` and `tools/verify_flutter_host_apk.py`.
- Installed-version reference check: `aya/src/main/java/dev/aya/android/AyaReferenceVerifier.kt`.
- This is build-time/source evidence only. Interactive device behavior and recipient ingestion
  require separate dated acceptance tests.

## Unknowns and escalation

- UNKNOWN: actual third-party assistant behavior on physical Android devices.
- UNKNOWN: whether external FlutterFlow exports can package the same native reference reliably.
- A reproduction can be checked using CI artifact inspection and native Android logs.
- No live support, account recovery, backend diagnostics, or special AI provider access exists.

## Assistant answer policy

- Answer questions about the single-screen synthetic Flutter host using the stated labels.
- Say clearly that its AYA card only opens editable local review before deliberate Copy/Share.
- Never claim the CI host implements an output-file importer, hidden app controls, or automation.
- Treat receiver attachment handling as UNKNOWN unless the user verified the receiver.
- For missing reference or mismatched version, explain how the developer must rebuild the APK.
- Do not request passwords or imply that reading this guide gives control over the host.
