---
schema_version: aya-reference/v1
app_id: org.example.ayalantern
app_name: AYA Lantern Sample
app_version_min: 1.0.0
app_version_max: 1.0.0
platform: ios
locale: en
guide_revision: 1
source_revision: apple-native-sample-20261103
last_verified_utc: 2026-11-03T00:00:00Z
owner: AYA contributors
---

# AYA Lantern Sample: iOS help and layout import reference

## Scope and version

This is the **fictional first-party sample app**, version 1.0.0, with bundle identifier org.example.ayalantern. The iOS 16+ project sources are in integrations/apple/sample. The app has a temporary layout display and a reusable AYA card. It is a development example, not a published consumer service. The following claims describe checked-in source; actual installed device and external assistant behavior require separate QA.

The sample has no account, network API, remote document library, saved preferences, billing or background agent integration. The AYA card checks the actual installed bundle ID and CFBundleShortVersionString before opening review.

## Quick orientation

The home view is a demonstration of a layout editor. It displays Columns and Accent; their starting values are 1 and warm. A Reset demo layout button restores those values. The Ask Your Agent card lets the user ask a third-party assistant a question using a reviewed, version-matched reference. A separate import action reads a user-picked JSON file and offers a confirmation before changing the temporary layout. There is no agent result listener.

## Navigation map

- Main view / AYA card > Optional question > Ask Your Agent: opens local Review AYA handoff after guide checks.
- Review AYA handoff > Full editable AYA document: change or remove any content.
- Review AYA handoff > Copy current text: copies the approved contents without launching an assistant.
- Review AYA handoff > Share as text or Share full .txt file: opens the system share interface using the chosen representation.
- Review AYA handoff > Cancel: leaves without sharing.
- Main view / AYA card > Import saved agent output: launches the iOS Files document picker for JSON.
- After a valid JSON import > Apply to demo or Cancel: the user decides whether to change the temporary display.
- Main view > Reset demo layout: sets Columns to 1 and Accent to warm.

## Task recipes

### TASK-001: Ask for help with the demo [CONDITIONAL]

- Applies to app version 1.0.0 with a matching bundled guide and an available compatible recipient.
1. On the main screen, optionally enter a question in the AYA card.
2. Tap Ask Your Agent. If the local guide fails its version/identity/shape check, sharing is blocked.
3. Read or edit the complete Full editable AYA document. Do not include credentials or private files.
4. Tap Copy current text, Share as text or Share full .txt file.
5. If a compatible third-party assistant appears and accepts the data, review it there and send manually as required by that app.
- Expect: a local copy or a system sharing attempt, not guaranteed assistant ingestion.
- Side effects: clipboard disclosure or explicit sharing to an external app; Cancel avoids both.
- Evidence: Sources/ContentView.swift, AYAHelpCard.swift, AYAAppleSharing.swift. End-to-end external provider acceptance UNKNOWN.

### TASK-002: Import a proposed demo layout [AVAILABLE in source; device QA pending]

- Prerequisites: save a UTF-8 JSON file to a location accessible through the iOS Files picker.
1. Prepare the JSON object as raw file contents, for example {"aya_demo_layout":"v1","columns":2,"accent":"cool"}.
2. Tap Import saved agent output on the main AYA card.
3. Select the JSON file explicitly from Files.
4. The sample checks content, exact keys, version v1, columns 1–3, and accent warm or cool.
5. When asked Apply imported layout to this demo?, inspect the proposed settings, then choose Apply to demo or Cancel.
- Expect: the main view changes columns/accent only after Apply.
- No durable data changes: values exist only in running SwiftUI state. No files are overwritten, removed or executed.
- If invalid: a Cannot use this file error appears; choose a different file. No partial apply.

### TASK-003: Restore default layout [AVAILABLE in source]

1. On the main screen tap Reset demo layout.
2. Check that Columns reads 1 and Accent reads warm.
- There is no persistent configuration and no undo beyond selecting a new JSON file.

## Features and settings

### F-001: Temporary layout display [AVAILABLE in source]

- Main view shows Columns and Accent. Defaults are 1 and warm.
- Importable values: columns integer 1 through 3 inclusive; accent is warm or cool.
- Applying a valid user-confirmed file changes only in-memory demo state. Restarting the app restores defaults.
- The sample does not actually alter a rendering grid; these are illustrative state values.

### F-002: Guarded AYA card [EXPERIMENTAL]

- The card includes Optional question, Ask Your Agent, import action and explanation.
- The exact installed bundle ID and marketing version must match guide metadata, and all twelve AYA-RAS guide sections must contain text.
- Review is editable before any Copy/Share. Sharing sends either one approved plain-text string or one approved .txt file, not both.
- Choosing a system share activity does not prove any AI app has read or understood the document.

### F-003: Manual output import [EXPERIMENTAL]

- Only the system Files picker grants access to a selected JSON document.
- AYA snapshots up to 4 MiB of bytes using a security scope and coordinated read, then passes them to the host.
- The host tests the JSON content rather than trusting its extension or filename, then asks for independent Apply confirmation.
- An AI-generated file is always untrusted. This demo handles only its tiny sample format, not arbitrary JSON recipes.

## Troubleshooting

### ERR-001: Unable to prepare AYA

- Occurs when the guide is absent, for another app/platform/version, malformed or missing required sections.
- Verify that the compiled app bundles aya-guide.md, the installed bundle ID is org.example.ayalantern, and marketing version is 1.0.0.
- Do not bypass guide validation or silently replace the content. An app developer must rebuild with correct documentation.
- This symptom says nothing about any external AI app.

### ERR-002: Cannot use this file

- The file could not be read, exceeded the cap or did not match exact demo-layout JSON semantics.
- Check that it is a JSON file with keys aya_demo_layout, columns and accent, with permitted values; do not include markdown fences.
- Try selecting the file again through Files; permission or File Provider failure may be transient.
- A failed import never applies a layout.

### ERR-003: Cannot share

- The current reviewed text is empty/too large or a temporary document could not be prepared.
- Keep the text within 2 MiB and try Copy current text. The recipient's own capacity and account state are beyond this sample.
- Do not infer that external sharing succeeded solely because the chooser opened.

## Limitations and unsupported behavior

- [UNSUPPORTED] Automated agent conversations, provider selection, reply monitoring and output discovery.
- [UNSUPPORTED] Persistent layout settings, actual document editing, background downloads and any destructive recipe execution.
- [UNKNOWN] Whether any given ChatGPT, Claude, Gemini or other iOS application appears in the Share Sheet or reads a complete AYA file. No recipient is guaranteed.
- [PLANNED] Real-device VoiceOver, iPad multitasking and independent integrating-host acceptance tests.
- The Files picker accepts user-selected JSON; importing cannot locate files saved inside another application's private container.

## Privacy and data handling

The question and reference stay local until an explicit Copy or Share action. Copy puts approved text on the system clipboard, which should be treated as a disclosure surface. Sharing may transfer the entire approved text to a third-party app and potentially its servers. AYA does not know the destination's retention policy, use model APIs, or intercept replies.

An imported file is selected by the user, read into a bounded in-memory snapshot, validated and either dismissed or applied to temporary state. No file is modified. Avoid including passwords, tokens, private paths, personal documents or sensitive logs in questions or artifacts.

## Glossary and synonyms

- AYA card / Ask Your Agent: the host-controlled entry point for a reviewed external-assistant handoff.
- Full editable AYA document / review: local text including the question and app-specific reference.
- Share as text: sends a single string; Share full .txt file: sends a file URL to an identical current approved string.
- Layout JSON / output artifact: a proposed machine-readable file that the host must validate before applying.
- Apply: the sample app's separate user confirmation after a successful content check.

## Evidence and provenance

- App implementation: integrations/apple/sample/Sources/AYAAppleHostApp.swift and ContentView.swift, revision apple-native-sample-20261103.
- Reusable card: integrations/apple/AYAApple/Sources/AYAApple/AYAHelpCard.swift.
- Apple file reading: integrations/apple/AYAApple/Sources/AYAApple/AYAAppleFileImport.swift.
- Identity guard, route semantics: integrations/apple/AYAApple/Sources/AYAProtocol/AYAReference.swift and AYAImportRegistry.swift.
- Read-only source review date 2026-11-03. Real compiled simulator and physical device acceptance are tracked separately; this document does not claim them in advance.
- System API contracts: Apple SwiftUI fileImporter, UIKit UIActivityViewController, Foundation NSFileCoordinator; external app behavior UNKNOWN.

## Unknowns and escalation

There is no customer-support service for this fictional sample. If the document picker does not provide access to a selected file, retest with a local Files document and record the iOS/device version; ask the adopting app developer to inspect its File Provider and scope handling. If the Share Sheet omits a destination or an assistant ignores a text file, try Copy current text and paste manually, then record that specific recipient version/account state for controlled QA. Do not fabricate compatibility or support contacts.

## Assistant answer policy

Only describe actual demo controls named in this guide. If asked to create an importable layout, clarify columns (1–3) and accent (warm/cool) when unclear; return raw JSON matching the exact three-key format, without a Markdown code fence if saved as a file. State that the host must validate and the user must confirm Apply. Distinguish source-verified demo behavior from independently tested device/recipient behavior. Never request secrets or suggest bypassing version, permission or import checks. No direct control of the host app is implied by receiving this reference.
