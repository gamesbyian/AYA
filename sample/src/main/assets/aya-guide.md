---
schema_version: aya-reference/v1
app_id: dev.aya.sample
app_name: AYA Sample
app_version_min: 1.0.0
app_version_max: 1.0.0
platform: android
locale: en
guide_revision: 3
source_revision: aya-sample-creative-handoff-v1
last_verified_utc: 2026-10-29T00:00:00Z
owner: AYA maintainers
---

# AYA Sample Android application: integration reference

This is a guide to the real AYA Sample *source implementation*. The Android application can be compiled, but no claim is made that ChatGPT, Claude, or another recipient has been tested on a physical device. This reference concerns this demo only.

## Scope and version

- App identifier: `dev.aya.sample`; APK `versionName` 1.0.0, `versionCode` 1.
- Minimum Android API level 23, target 35. Behavior of individual recipient apps is UNKNOWN.
- Only the published demo's Home screen, fictional artwork demonstration and AYA preview/share flow are included.
- No remote account, login, subscription or background service is implemented in the sample.
- The library requires the exact app ID and version in this guide's metadata to match the installed application.

## Quick orientation

The sample has a title, explanation, an "Ask your agent" button, and an optional host-owned question field with an "Ask using my question" button. It also has a fictional Aurora Station artwork-generator example with a creative direction editor, a guarded "Generate artwork with my agent" action, an "Import saved image" Android document picker and an on-screen selected-image preview. Import is local to this demo; no media library is modified. The first button loads this guide, verifies the installed app version, and opens a local question composer. The second uses the host's already typed question to skip the additional question composer. Both paths lead to a local editable privacy review. The user may Cancel, Copy, or Share the help text. Android's chooser offers installed compatible targets; recipients control how they process the file.

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

### TASK-004: Ask an external assistant to create fictional cover art [CONDITIONAL]

- Applies to: AYA Sample 1.0.0, when a recipient can accept text and actually generate images. Specific third-party capabilities are UNKNOWN until tested.
- Start: Home > Artwork generation demo.
- Prerequisites: a valid bundled guide and a compatible third-party assistant; no AYA account required.
1. In the "Describe square cover artwork" field, edit or replace the example visual direction.
2. Tap "Generate artwork with my agent". This uses the **host's already typed direction**, so no duplicate AYA composer appears.
3. Review/edit the complete self-contained prompt and installed-version-matched guide. The request asks for actual generation, not merely a prompt.
4. Choose Copy or Share, select your AI app if offered, and send the request there as required.
5. If the assistant generated an image, save it on device using that assistant's own controls; then return to Home and follow TASK-005.
- Expected: the outgoing prompt describes the fictional "Aurora Station (fictional series), Season 4", square season key art, preferred 2000 × 2000 pixels, PNG/JPEG import formats, opaque background and 8% edge margin. Exact generation, file size and format are NOT guaranteed.
- Failure: see ERR-002 for share failure and ERR-003 for an assistant that cannot generate the image; use Copy to paste manually.
- Side effects/undo: creating/reviewing text is local until Copy or Share. A recipient may retain/upload data; image generation and saving occur outside AYA. No response is read by AYA.
- Evidence: `sample/src/main/java/dev/aya/sample/MainActivity.kt`, `aya/src/main/java/dev/aya/android/AyaCreative.kt`, `Aya.kt`; source inspected; provider behavior unverified.

### TASK-005: Import a saved image into the sample preview [AVAILABLE]

- Applies to: AYA Sample 1.0.0 on Android 23+ with an accessible image from the Android document picker.
- Start: Home > Artwork generation demo.
- Prerequisites: an image stored in a location accessible to Android's document picker; the image can come from any source and does not require using AYA.
1. Tap "Import saved image".
2. Choose an image using Android's system `ACTION_OPEN_DOCUMENT` picker.
3. Observe the selected image under "Imported artwork preview for this demo".
- Expected: the sample shows that chosen image on screen. The selected URI is saved through Activity-instance recreation, and persistable read permission is requested where the provider supports it. This sample does **not** save the artwork into a media library or automatically retrieve it from the AI app.
- Failure: if selection is canceled or no read access exists, no image is imported; choose a valid accessible file. The sample has not been device-verified for every documents provider.
- Side effects/undo: local preview only; choose another file to replace it. The picker grants URI access to the host, independently of AYA.
- Evidence: `sample/src/main/java/dev/aya/sample/MainActivity.kt`; source inspected, device acceptance pending.

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

### F-003: Structured creative image generation [AVAILABLE]

- Location: Home > Artwork generation demo > Generate artwork with my agent.
- Runtime input: host-owned creative direction; subject and image requirements supplied explicitly by the sample. The version-checked guide is still mandatory.
- Image specification: 1:1 ratio; preferred 2000 × 2000 pixels (not guaranteed); PNG/JPEG accepted by this demonstration's advertised request; opaque background; 8% margin. The actual Android picker uses `image/*`, and is a demo preview rather than an enforcing media-library importer.
- Interaction: the complete image request and guide can be edited in review. The approved generation request is sent as bounded `EXTRA_TEXT` as well as in the attached text file.
- Persistence: no generation state or third-party output is stored by AYA; the selected image's URI is retained across Activity recreation while saved state exists, not guaranteed across process restart with no saved state.
- Evidence: `AyaCreative.kt`, `Aya.kt`, `MainActivity.kt`.

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

### ERR-003: AI app does not generate artwork [CONDITIONAL]

- Symptom: the destination writes a prompt, ignores the text attachment, requires sign-in, or cannot create an image.
- Interpretation: the recipient's generation capability or handoff behavior differs; AYA cannot command generation or verify success.
- Safe fix: verify that the full request is visible in the destination, paste the reviewed text manually if needed, use an image-capable assistant if available, and save the result yourself.
- Verification: a real generated image saved on the device, then manually chosen using TASK-005. Opening Android's chooser is not proof.
- Evidence: `AyaCreative.kt` specifies requested behavior; actual provider outcomes are UNKNOWN.

## Limitations and unsupported behavior

- The sample cannot read assistant responses or operate another app. [UNSUPPORTED]
- No question is sent before the user explicitly selects Share and chooses a target. [AVAILABLE]
- AYA cannot force another assistant to create a fresh conversation or ingest the attachment. [UNSUPPORTED]
- ChatGPT and Claude attachment behavior has not been verified on physical devices. [UNKNOWN]
- There is no built-in AI model, API subscription, provider login or device diagnostic collection. [UNSUPPORTED]
- The sample does not edit or manage any real parcel, torrent or other user data. It can display a user-selected image locally but cannot persist media-library artwork. [UNSUPPORTED]

- AYA sends no reference image and receives no generated output. The image is saved externally and manually selected by the Android document picker. It is never automatically imported, installed, or monitored. [AVAILABLE]
- The host's 2000 × 2000 preference is not a guarantee about any AI image generator's output. [UNKNOWN]

## Privacy and data handling

No app settings, identities, files or logs are automatically gathered. The source-controlled guide, simple screen label and any question the user types are explicitly supplied to AYA. The user can edit this package before sharing. Copy places full text on Android clipboard. Share creates a unique, private cache file and temporarily grants a selected external app read access. It also puts a bounded representation of the **approved** question in `EXTRA_TEXT`; the attached document retains the entire question and guide. That app may upload/store a copy. AYA has no mechanism to withdraw data already shared.

- Creative handoff: one-way transfer of a user's image-generation request and current app import requirements, followed by user-controlled save/import.
- Artwork direction: editable user-authored description in the demo field.
- Image requirement: verified host-supplied target aspect/format constraints; a preferred size need not match actual output.
- Import saved image: Android document picker for the demo preview, separate from an assistant's save controls.

## Glossary and synonyms

- Sharesheet: Android's application picker for sharing files; also called share menu/chooser.
- Help package: self-contained guide, installed app version, question and screen hint.
- Recipient: the separate app the user chooses, such as an AI chat client; not operated by AYA.
- Question composer: local multiline prompt where the user describes the problem.
- Preview: editable local dialog before any share.
- Installed version: the package version declared in the installed APK, not a forecast of future features.

## Evidence and provenance

- Source: `aya/src/main/java/dev/aya/android/AyaCreative.kt`, `sample/src/main/java/dev/aya/sample/MainActivity.kt`, `sample/build.gradle.kts`, `sample/src/main/AndroidManifest.xml`, `aya/src/main/java/dev/aya/android/Aya.kt`, and `aya/src/main/java/dev/aya/android/AyaReferenceVerifier.kt`.
- Findings above reflect inspected source and build configuration. Real recipient outcomes remain unverified until device testing.
- This is a demo reference, not evidence of production security or accessibility acceptance.

The host supplies fictional artwork metadata and a user-edited direction. The preview contains both plus the app guide; only Copy or Share sends them outside the app. The demo image importer uses Android's document picker with user action; it does not automatically inspect photos or read generated images from the agent. No AYA outcome telemetry, return channel or server exists.

## Unknowns and escalation

- UNKNOWN: Which versions of third-party clients process the document automatically, create a new chat, or generate/save an actual image from the request.
- Safe verification: install sample and recipient on an Android device, share, inspect attachment, document target version and exact outcome.
- Support: source repository issues at `https://github.com/gamesbyian/AYA/issues`; no in-app support channel exists.

- For Creative Handoff, ask the recipient to generate the actual requested image if capable, never imply AYA or this sample already imported it, and direct the person to save the generated image and tap "Import saved image". Respect the fictional example and exact technical preferences without inventing provider support.

## Assistant answer policy

- First determine whether the user entered a question in the AYA composer or in the host app field, whether they saw the local review, and whether an external app actually imported the attachment.
- Distinguish local chooser success from downstream ingestion.
- Only suggest the controls explicitly documented above.
- Never claim the assistant can tap buttons inside this sample without a separately authorized tool.
- Never ask the user to disclose private credentials or logs.
