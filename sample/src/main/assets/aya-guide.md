---
schema_version: aya-reference/v1
app_id: dev.aya.sample
app_name: AYA Sample
app_version_min: 1.0.0
app_version_max: 1.0.0
platform: android
locale: en
guide_revision: 2
source_revision: aya-sample-question-first-v1
last_verified_utc: 2026-10-28T00:00:00Z
owner: AYA maintainers
---

# AYA Sample Android application: integration reference

This is a guide to the real AYA Sample *source implementation*. The Android application can be compiled, but no claim is made that ChatGPT, Claude, or another recipient has been tested on a physical device. This reference concerns this demo only.

## Scope and version

- App identifier: `dev.aya.sample`; APK `versionName` 1.0.0, `versionCode` 1.
- Minimum Android API level 23, target 35. Behavior of individual recipient apps is UNKNOWN.
- Only the published demo's Home screen and AYA preview/share flow are included.
- No remote account, login, subscription or background service is implemented in the sample.
- The library requires the exact app ID and version in this guide's metadata to match the installed application.

## Quick orientation

The sample has a title, explanation, an "Ask your agent" button, and an optional host-owned question field with an "Ask using my question" button. The first button loads this guide, verifies the installed app version, and opens a local question composer. The second uses the host's already typed question to skip the additional question composer. Both paths lead to a local editable privacy review. The user may Cancel, Copy, or Share the help text. Android's chooser offers installed compatible targets; recipients control how they process the file.

The sample is a handoff demonstration, not a functioning helpdesk or AI client. Its external assistant integration is only a standard Android share intent.

## Navigation map

- Home: title "AYA: Ask Your Agent", explanation, "Ask your agent" button, "Or type your question here" field, and "Ask using my question" button.
- Home > Ask your agent: question composer, "What do you need help with?" and multiline input; "Review details" moves to preview.
- Home > Or type your question here > Ask using my question: skips duplicate question entry and opens preview directly.
- Both flows > Review details (when needed): expanded "Ask your agent" review dialog with editable multiline help text.
- Review > Cancel: returns to Home, without sharing.
- Review > Copy: copies the currently edited text into Android's clipboard.
- Review > Share: opens the Android Sharesheet with a temporary text document.
- The receiving application's screens, sign-in state, send controls and attachment processing are beyond this sample's control.

## Task recipes

### TASK-001: Share help with another assistant [CONDITIONAL]

- Applies to: AYA Sample 1.0.0 on Android 23+ with a compatible installed share target.
- Start: Home.
- Prerequisites: a correctly packaged guide; an external application capable of receiving a text attachment.
1. Tap "Ask your agent".
2. Enter your question in the optional multiline prompt, or leave blank for general help.
3. Tap "Review details".
4. Review or edit the complete reference package. Remove private information.
5. Tap "Share" and select a destination in Android's Sharesheet.
6. In the destination, verify that the document content is actually present and start or send the chat as that app requires.
- Expect: the receiving app is offered a UTF-8 text attachment; successful ingestion and chat creation are NOT guaranteed.
- Verification: the Android share chooser opening proves only that a share was initiated, not that the recipient has read the document.
- Side effects/undo: a unique temporary file is written to the sample's cache; the selected app may upload or retain a copy. Once sent, AYA cannot retract it.
- If it fails: see ERR-002; use TASK-002.
- Evidence: `sample/src/main/java/dev/aya/sample/MainActivity.kt`, `aya/src/main/java/dev/aya/android/Aya.kt`; source-inspected, device behavior unverified.

### TASK-002: Copy the help package manually [AVAILABLE]

- Applies to: AYA Sample 1.0.0 and an Android device with clipboard support.
- Start: Home.
- Prerequisites: a valid bundled guide.
1. Tap "Ask your agent".
2. Optionally type your question and tap "Review details".
3. Review or edit text in the review screen.
4. Tap "Copy".
5. Open an assistant manually and paste the text into a conversation.
- Expect: a "Help text copied" message, followed by clipboard data ready for manual paste.
- Verification: verify the pasted content before submitting; copying alone does not contact an AI service.
- Side effects/undo: clipboard contains the complete copied text until replaced/cleared by the OS or user; other applications may have access.
- If it fails: see ERR-001 for the bundled reference or check Android's clipboard behavior.
- Evidence: `aya/src/main/java/dev/aya/android/Aya.kt`; source-inspected, device behavior unverified.

### TASK-003: Ask using the sample's own text field [AVAILABLE]

- Applies to: AYA Sample 1.0.0 on Android 23+.
- Start: Home.
- Prerequisites: valid version-matched reference bundled with app.
1. Type a question in "Or type your question here".
2. Tap "Ask using my question".
3. The full AYA review opens directly, with your typed question already embedded.
4. Edit or remove any text, then use Copy or Share.
- Expect: no duplicate question composer because the host already captured the question.
- Verification: the review's "User's starting question" section reflects what was typed in the host field.
- Side effects/undo: typing and preview are local only; sharing or copying has the disclosure effects described in TASK-001 and TASK-002.
- If it fails: see ERR-001.
- Evidence: `sample/src/main/java/dev/aya/sample/MainActivity.kt` and `aya/src/main/java/dev/aya/android/Aya.kt`; source-inspected, device behavior unverified.

## Features and settings

### F-001: Version-checked bundled reference [AVAILABLE]

- What it does: reads packaged `aya-guide.md`, validates its `app_id`, exact `app_version_min` and `app_version_max`, and required reference sections.
- Location: automatic when "Ask your agent" is tapped.
- Defaults: exact version matching is mandatory in the guarded API; no user preference overrides it.
- Constraints and interactions: invalid or absent guides do not open the review.
- Visibility: the check is automatic and has no configuration UI.
- Persistence: source asset shipped inside the APK.
- Evidence: `aya/src/main/java/dev/aya/android/AyaReferenceVerifier.kt`, `Aya.kt`.

### F-002: Editable review and user-controlled sharing [AVAILABLE]

- What it does: shows a question-first composer or accepts the question already typed in the host; then shows full help text; Cancel, Copy and Share are separate actions.
- Location: Home > Ask your agent, or Home > Ask using my question.
- Defaults: question-first for "Ask your agent"; host-owned question uses `askQuestion=false`; no automatic share. The help package includes the guide, installed version, current screen and user question.
- Constraints and interactions: sharing disallows blank text and packages over 2 MiB; file is plain UTF-8 text. The final user-approved question is also shared as bounded `EXTRA_TEXT`, and can be edited in review.
- Visibility: the dialog appears only after a successfully validated guide.
- Persistence: approved shares are cached temporarily and older AYA cache entries are pruned opportunistically after seven days on subsequent shares.
- Evidence: `aya/src/main/java/dev/aya/android/Aya.kt`.

## Troubleshooting

### ERR-001: "AYA reference unavailable"

- Context: the Home screen shows this prefix when the packaged guide is missing, stale, invalid, or cannot be read.
- Meaning: the guarded API did not open a review or share package.
- Check: use the exact installed build and verify its bundled `aya-guide.md` has the app ID and exact installed version. Do not bypass the check with another app's guide.
- Fix: update the APK with the correct reference asset. End users cannot repair a broken packaged guide in the app.
- Verify: reopen "Ask your agent" and check that the local preview is visible.
- Escalate: report the installed app version and error reason to the app maintainer, without sending credentials.
- Evidence: `sample/src/main/java/dev/aya/sample/MainActivity.kt`; source-inspected.

### ERR-002: "Sharing failed. Use Copy to paste the text into your assistant."

- Context: toast when the AYA share file cannot be written or Android cannot launch the chooser.
- Meaning: no completed recipient handoff has been established.
- Check: retry with a shorter, non-sensitive reference and ensure another share target is available.
- Fix: return to the preview and select "Copy", then paste into the chosen assistant manually.
- Verify: inspect the pasted content in the destination before sending.
- Escalate: report repeatable failures with Android and app versions, without including secrets.
- Evidence: `aya/src/main/java/dev/aya/android/Aya.kt`; source-inspected.

## Limitations and unsupported behavior

- The sample cannot read assistant responses or operate another app. [UNSUPPORTED]
- No question is sent before the user explicitly selects Share and chooses a target. [AVAILABLE]
- AYA cannot force another assistant to create a fresh conversation or ingest the attachment. [UNSUPPORTED]
- ChatGPT and Claude attachment behavior has not been verified on physical devices. [UNKNOWN]
- There is no built-in AI model, API subscription, provider login or device diagnostic collection. [UNSUPPORTED]
- The sample does not edit or manage any real parcel, torrent or other user data. [UNSUPPORTED]

## Privacy and data handling

No app settings, identities, files or logs are automatically gathered. The source-controlled guide, simple screen label and any question the user types are explicitly supplied to AYA. The user can edit this package before sharing. Copy places full text on Android clipboard. Share creates a unique, private cache file and temporarily grants a selected external app read access. It also puts a bounded representation of the **approved** question in `EXTRA_TEXT`; the attached document retains the entire question and guide. That app may upload/store a copy. AYA has no mechanism to withdraw data already shared.

## Glossary and synonyms

- Sharesheet: Android's application picker for sharing files; also called share menu/chooser.
- Help package: self-contained guide, installed app version, question and screen hint.
- Recipient: the separate app the user chooses, such as an AI chat client; not operated by AYA.
- Question composer: local multiline prompt where the user describes the problem.
- Preview: editable local dialog before any share.
- Installed version: the package version declared in the installed APK, not a forecast of future features.

## Evidence and provenance

- Source: `sample/src/main/java/dev/aya/sample/MainActivity.kt`, `sample/build.gradle.kts`, `sample/src/main/AndroidManifest.xml`, `aya/src/main/java/dev/aya/android/Aya.kt`, and `aya/src/main/java/dev/aya/android/AyaReferenceVerifier.kt`.
- Findings above reflect inspected source and build configuration. Real recipient outcomes remain unverified until device testing.
- This is a demo reference, not evidence of production security or accessibility acceptance.

## Unknowns and escalation

- UNKNOWN: Which versions of third-party clients process the document automatically and create a new chat.
- Safe verification: install sample and recipient on an Android device, share, inspect attachment, document target version and exact outcome.
- Support: source repository issues at `https://github.com/gamesbyian/AYA/issues`; no in-app support channel exists.

## Assistant answer policy

- First determine whether the user entered a question in the AYA composer or in the host app field, whether they saw the local review, and whether an external app actually imported the attachment.
- Distinguish local chooser success from downstream ingestion.
- Only suggest the controls explicitly documented above.
- Never claim the assistant can tap buttons inside this sample without a separately authorized tool.
- Never ask the user to disclose private credentials or logs.
