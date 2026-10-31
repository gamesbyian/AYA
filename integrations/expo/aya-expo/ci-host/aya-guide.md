---
schema_version: aya-reference/v1
app_id: dev.aya.expo.cihost
app_name: AYA Expo CI Host
app_version_min: 1.0.0
app_version_max: 1.0.0
platform: android
locale: en
guide_revision: 1
source_revision: expo-ci-host-v1
last_verified_utc: 2026-10-31T21:00:00Z
owner: AYA maintainers
---

# AYA Expo CI Host: exact-build reference

This reference covers ONLY the synthetic first-party Expo Android CI host whose
single-screen source lives at `integrations/expo/aya-expo/ci-host/App.tsx`.
The guide is build-time documentation, not a receipt for running a device test.
It is neither a general-purpose Expo manual nor documentation for another app.

## Scope and version

- Android application ID: `dev.aya.expo.cihost`; installed `versionName`: `1.0.0`.
- Only the test-only one-screen React Native/Expo host is covered.
- The host uses the optional AYA Expo Modules Android bridge and a packaged exact-version guide.
- It has no account system, file importer, backend or AI inference engine.
- No iOS, web, Expo Go, or production app support is claimed by this test fixture.

## Quick orientation

The only screen has the heading "AYA Expo CI Host", a short note calling it
a test application, and a bordered Ask Your Agent card. The card explains its
reference attachment, how to use any answer, and shows a multiline optional
question field and an "Ask Your Agent" button. The button requests local
AYA question/review UI. A separate receiver is chosen only after the user
explicitly reviews and shares the reference.

## Navigation map

- App launch > AYA Expo CI Host: the single screen.
- Card > Question for your agent, optional: type or edit a question.
- Card > Ask Your Agent: invoke the guarded native Android AYA component.
- Local AYA review > Cancel: stop.
- Local AYA review > Copy: copy the reviewed text for manual pasting.
- Local AYA review > Share: open Android's chooser for an explicit handoff.
- There is no second screen, settings screen or agent-output import workflow.

## Task recipes

### TASK-001: Review and share a help request [AVAILABLE]

- Applies to: this test host and its exact-version guide in a correctly packaged Android APK.
- Start: the single AYA Expo CI Host screen.
- Prerequisites: an active Android Activity, a working AYA native bridge and the matching bundled guide.
1. Optionally type a question in the card.
2. Press "Ask Your Agent" to request local AYA review.
3. Read and edit the proposed material; remove anything you do not want to share.
4. Choose Cancel, Copy, or Share deliberately. For Share, select a compatible recipient in Android's chooser.
- Expect: local review first. No assistant answer is automatically returned to the host.
- Verify: what is copied or shared must reflect the final approved review.
- Failure: see ERR-001 or ERR-002. Do not bypass identity checks or assume an attachment was read.
- Side effects: Copy changes clipboard contents; Share may provide the approved text to a selected app.
- Evidence: `integrations/expo/aya-expo/ci-host/App.tsx`,
  `integrations/expo/aya-expo/src/AyaHelpCard.tsx`,
  `integrations/expo/aya-expo/android/src/main/java/dev/aya/expo/AyaExpoModule.kt`.
- Validation limit: successful source/APK compilation does not prove on-device recipient support.

## Features and settings

### F-001: Optional-question AYA card [AVAILABLE]

- Location: below the heading and explanatory note on the only host screen.
- Shows: host-authored description, truthful attachment disclosure, answer-use instructions,
  optional multiline question and a 48px-minimum review button.
- Default: an empty question; no hidden user data is collected or attached.
- Host appearance: a white page, dark text and a bordered card with theme-aware internal controls.
- No global settings, assistant selection preference, background task, output receiver or auto-apply action.
- Evidence: `integrations/expo/aya-expo/ci-host/App.tsx`,
  `integrations/expo/aya-expo/src/AyaHelpCard.tsx`.

## Troubleshooting

### ERR-001: Local AYA review cannot open [CONDITIONAL]

- Cause: no active Android screen, missing native bridge, missing packaged guide or mismatched installed package/version.
- Check: native installation, package name, version, bundled guide and local error shown below the card.
- Fix: rebuild with the host's exact guide, linked AYA Android AAR and valid native bridge; do not disable validation.
- Verification: a subsequent manual tap can open local review once the installation is correct.
- Evidence: `integrations/expo/aya-expo/src/native.ts`,
  `integrations/expo/aya-expo/android/src/main/java/dev/aya/expo/AyaExpoModule.kt`,
  `aya/src/main/java/dev/aya/android/AyaReferenceVerifier.kt`.

### ERR-002: Assistant target ignores the reference [CONDITIONAL]

- Cause: a third-party app may not appear in Sharesheet or may ignore the offered attachment.
- Check: inspect the selected receiver; opening the chooser does not establish ingestion.
- Fix: use the AYA Copy action and paste the approved text manually if required.
- Verification: only observed behavior in the actual receiving client establishes ingestion.
- Evidence: `aya/src/main/java/dev/aya/android/Aya.kt`.

## Limitations and unsupported behavior

- The test host provides no agent-response monitoring, output importer, command executor or automatic follow-up. [UNSUPPORTED]
- The test host has no external AI credentials or AYA-hosted inference service. [UNSUPPORTED]
- Actual Android recipient document ingestion and new-chat behavior remain unverified. [UNKNOWN]
- CI-built APK checks cannot establish TalkBack quality, physical-device UI operation or receiver results. [UNKNOWN]
- Expo Go, iOS and web do not support this Android native module. [UNSUPPORTED]

## Privacy and data handling

The host contains a static source-authored guide and a question typed by the user.
The AYA Android review is editable before any Copy or Share action. No background
file scans, account identifiers, diagnostics or assistant replies are collected by
this test app. Copy puts approved text on the clipboard; sharing provides approved
content to a user-selected receiver subject to its own data handling. Do not
place secrets in a question. No telemetry or backend is present.

## Glossary and synonyms

- AYA: Ask Your Agent, the local reviewed handoff convention.
- Host: this synthetic Expo app, not an AI assistant.
- Guide/reference: the exact-build `aya-guide.md` bundled inside the APK.
- Review: the editable AYA screen before deliberate Copy or Share.
- Sharesheet/chooser: Android's selection UI, not proof a receiver read the attachment.
- Bridge: the Android-native Expo module invoking AYA's guarded help action.

## Evidence and provenance

- Actual host UI: `integrations/expo/aya-expo/ci-host/App.tsx`.
- Native module: `integrations/expo/aya-expo/android/src/main/java/dev/aya/expo/AyaExpoModule.kt`.
- Card implementation: `integrations/expo/aya-expo/src/AyaHelpCard.tsx`.
- Native guide copier: `integrations/expo/guide-plugin/guide_asset.cjs`.
- Android reference guard: `aya/src/main/java/dev/aya/android/AyaReferenceVerifier.kt`.
- CI packaging and verifier: `.github/workflows/expo-module.yml`, `tools/verify_flutter_host_apk.py`.
- The status is source/build evidence; no physical-device or third-party app trial is implied.

## Unknowns and escalation

- UNKNOWN: recipient app support for file attachments and new conversations.
- UNKNOWN: Android runtime interactions on a physical phone in this CI lane.
- If a build fails, inspect the CI job and app package/version metadata, not a guide from another host.
- No account support channel, backend recovery or remote controls exist in the test host.

## Assistant answer policy

- Describe only the verified one-screen host and visible card; do not invent settings or commands.
- Explain that the button opens local AYA review before an explicit Copy or Share.
- Never claim an agent answer is monitored, imported, executed or automatically applied.
- Treat selected assistant attachment ingestion as UNKNOWN until separately tested.
- For missing or incompatible references, advise a correct build, not a validation bypass.
- Never ask for passwords or imply that possessing the reference grants app control.
