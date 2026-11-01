---
schema_version: aya-reference/v1
app_id: dev.aya.godot.cihost
app_name: AYA Godot CI Host
app_version_min: 1.0.0
app_version_max: 1.0.0
platform: android
locale: en
guide_revision: 1
source_revision: godot-ci-host-v1
last_verified_utc: 2026-10-31T21:00:00Z
owner: AYA maintainers
---

# AYA Godot CI Host: version-specific Android help reference

This reference documents only the first-party synthetic AYA Godot scene and Android plugin source at `integrations/godot/`. The editor smoke and compiled APK are developer evidence, not proof that a third-party assistant read the attachment. A separate project's host guide must be generated from that project's own implementation and installed Android version.

## Scope and version

- Application ID `dev.aya.godot.cihost`, versionName `1.0.0`, versionCode 1; see `integrations/godot/export_presets.cfg`.
- Platform: Android using Godot 4.5.1 Gradle export and the optional AYA Android v2 plugin, minimum Android API 24.
- The test fixture exposes a single `AYAEditorSmoke` root node with the `AYACard` script. Its card appears on the one scene, not in a multi-screen production game.
- The fixture demonstrates provider-neutral help handoff. There is no login, paid AYA account, network API key, agent API, importer, game save system, or automatic answer processing.
- Native APK packaging and Godot headless tests cannot establish real device accessibility, assistant ingestion, or a working recipient connection.

## Quick orientation

The scene renders a heading `Ask Your Agent`, a short description of the test screen, an attachment disclosure, after-answer instructions, an optional multiline text field, and a button labeled `Ask Your Agent`. The output instructions say to read and apply advice manually; the host does not apply any answers. On a correctly built Android export, the Godot AYA singleton calls the guarded native Android AYA component. It verifies this exact guide against the installed package and version and opens editable local review. Nothing is automatically transmitted when the button is tapped.

The button is intentionally disabled inside the Godot editor, on desktop/non-Android platforms, if the Android singleton is absent, or when required host output-use instructions are missing. In those cases, a disabled button does not prove assistant contact.

## Navigation map

- App launch > `AYAEditorSmoke`: the only scene with the AYA card.
- Card > multiline optional question: enter ordinary text, including newlines; the control grows with its content.
- Card > `Ask Your Agent`: request guarded Android review, if the plugin is present and enabled.
- Local AYA review > Cancel: stop without sharing.
- Local AYA review > Copy: place approved text in the Android clipboard for manual pasting.
- Local AYA review > Share: deliberately open Android's Sharesheet. Whether the selected target ingests the text/document is not established by the chooser alone.
- This synthetic scene has no in-game settings, account configuration, generated-answer import, chat-history screen or automated agent task execution.

## Task recipes

### TASK-001: Ask about the test scene [CONDITIONAL]

- Applies to: the exact Android 1.0.0 synthetic host when its AYA v2 plugin, AYA Android SDK and matching raw APK guide have been packaged correctly.
- Start: the single AYA card in the synthetic scene.
- Prerequisites: a live Android Activity, valid installed-version-matched guide, complete host-facing instructions and a working Android AYA singleton.
1. Optionally type a question using the multiline field. Blank questions are permitted for general help.
2. Tap `Ask Your Agent`. The host calls the Android native bridge with a per-card request identifier and the raw guide path.
3. If local review opens, read and edit the exact content. Remove any private information.
4. Choose Cancel to stop, Copy for manual pasting, or Share to offer the approved text/attachment to a chosen installed Android app.
5. In the receiving app, verify whether the attachment/text arrived and follow that app's own Send action if appropriate.
- Expect: local review and user-controlled Copy/Share on a compatible device. Successful assistant ingestion is UNKNOWN until tested separately.
- Failures: see ERR-001 for unavailable native plugin/guide; ERR-002 for absent or incompatible recipient.
- Side effects: Copy modifies the clipboard; Share may expose approved content to a recipient; no model output is captured or executed by the host.
- Evidence: `integrations/godot/addons/AYA/aya_card.gd`, `aya-godot/src/main/java/dev/aya/godot/AyaGodotPlugin.kt` and `aya/src/main/java/dev/aya/android/AyaComponentAction.kt`.

### TASK-002: Interpret advice without a return channel [AVAILABLE]

- Start: after an external assistant answers a shared request, or after manually pasting a copied request.
1. Read the advice in that external application.
2. Return manually to the synthetic Godot scene.
3. Apply any useful knowledge yourself. There is no button to import an answer or run a generated command.
- Expect: a manual user decision. The scene has no writable game state or agent-output handler.
- Limitations: AYA cannot know whether you received or acted on an answer.
- Evidence: `integrations/godot/aya_smoke.tscn` and `integrations/godot/addons/AYA/aya_card.gd`.

## Features and settings

### F-001: Guarded help card [CONDITIONAL]

- Location: the only `AYAEditorSmoke` scene, under the `Ask Your Agent` title.
- Defaults: empty optional question, raw native guide name `aya-guide.md`, title `Ask Your Agent`, generic test-scene description, clear attachment disclosure and manual answer-use instructions.
- UI: VBoxContainer with host-owned vertical layout, multiline `AYAQuestion` TextEdit and a minimum-height 48-unit `AYAButton`.
- Dependencies: Android OS, native v2 Godot addon and AYA Android core; installation requires exact asset and app-version match.
- Security: user can review and edit content before deliberate Copy or Share; no background sharing, provider selection, file watcher or assistant reply hook.
- State: draft text is local to the scene instance; persistence through process death is not verified. The emitted `aya_local_status` only describes local question/review/rejection and is filtered by request ID.
- Evidence: `aya_card.gd` and `AyaGodotPlugin.kt`.

### F-002: Editor safety and missing-output rejection [AVAILABLE]

- Location: editor/non-Android run of the same card.
- Default: the Ask button is disabled, and the tooltip explains Android-only behavior. A card without required result-use instructions is disabled.
- This is source and headless Godot parser behavior, not a receiver compatibility guarantee.
- Evidence: `integrations/godot/aya_smoke.gd`, `aya_card.gd`.

## Troubleshooting

### ERR-001: Ask button unavailable or review rejected [CONDITIONAL]

- Symptoms: `Ask Your Agent` is disabled, or the native bridge reports `rejected` via its local signal.
- Possible causes: running in the editor/desktop, missing Android AYA singleton, missing required output-use copy, stale or absent raw guide, detached Android Activity or version mismatch.
- Check: confirm Android Gradle export includes both matching AARs; verify installed APK ID/version, raw `assets/aya-guide.md`, native FileProvider/receiver and Godot v2 metadata using the APK verification scripts.
- Recovery: rebuild with the host's correct guide and bridge, not a foreign app's reference. Never turn off guide verification or pretend a disabled editor preview contacted an assistant.
- Evidence: `aya_card.gd`, `AyaGodotPlugin.kt`, `AyaReferenceVerifier.kt`.

### ERR-002: Chosen assistant ignores the attachment [CONDITIONAL]

- Symptom: Android's chooser opened, but the selected assistant has no guide or question visible.
- Cause: the receiver may handle Android text and file URIs differently, be uninstalled, require authentication or not support the offered attachment.
- Recovery: use Copy, open the agent manually and paste the approved text; confirm it is complete before sending.
- Limits: opening the chooser never proves a message was sent or read. No silent retry or external-account inspection occurs.
- Evidence: `aya/src/main/java/dev/aya/android/Aya.kt`.

## Limitations and unsupported behavior

- [UNSUPPORTED] No autonomous agent, AI model, API calls, transcript monitoring, generated command execution, file importer, automatic handoff return, or provider-specific routing.
- [UNSUPPORTED] No desktop/iOS/web Android Sharesheet integration via this Godot addon.
- [UNKNOWN] Real external ChatGPT, Claude, Gemini and other recipients' current attachment ingestion on a given Android device.
- [UNKNOWN] Physical-device screen-reader/navigation and large-font acceptance for the synthetic scene; automated headless parsing does not prove this.
- [UNKNOWN] Whether the built APK works with every Android version or Godot game template; verify the exact exporting version and manifest.
- [PLANNED] Broader independent host/editor QA and public versioned distribution depend on separate release gates.

## Privacy and data handling

The Godot card holds the optional question in local scene state. The native AYA bridge requests local review before any deliberate Copy or Share. Clipboard content is available through Android according to the OS policy; selected recipients may upload or retain the approved information. AYA has no account, telemetry collector, backend, model subscription or answer monitor. Avoid putting passwords, private documents or unrelated host data into questions or guides. Cancel does not invoke an external assistant.

## Glossary and synonyms

- AYA: Ask Your Agent, a provider-neutral handoff convention and optional Android library.
- Godot singleton: the Android native plugin object exposed to a Godot game.
- AAR: Android archive containing compiled native bridge/core code and manifest declarations.
- Raw APK asset: an uncompressed or compressed entry at `assets/aya-guide.md` reachable from `Activity.assets.open()`, not just a PCK resource.
- Review: local user-editable text screen before Copy or Share.
- Recipient/agent: the independently chosen external AI application. Its response is never monitored.

## Evidence and provenance

- Source of the single screen: `integrations/godot/aya_smoke.tscn`, `integrations/godot/addons/AYA/aya_card.gd`.
- Source of native guarded action and local-status signal: `aya-godot/src/main/java/dev/aya/godot/AyaGodotPlugin.kt`, `aya/src/main/java/dev/aya/android/AyaComponentAction.kt`.
- Build identity and Android Gradle export choice: `integrations/godot/export_presets.cfg`.
- Packaging preparation and binary tests are in AYA CI. Any successful source or APK test is conditional on its exact workflow run; this guide does not assert a successful physical-device or recipient test.
- Guide last source review: 2026-10-31 UTC. The fixture only, no real user project.

## Unknowns and escalation

If a user asks about a different Godot project, app version or proprietary feature, inspect that host's own source-derived reference rather than repurposing this CI guide. If an export fails, capture the exact version, Android Gradle output and native manifest error without credentials; report it to the developing project's own maintainer or issue tracker. No fictional support URL or AYA-operated service is provided.

## Assistant answer policy

Describe only the synthetic host's observable controls and their documented limits. If the user's question refers to a different app, obtain that app's real source-specific instructions. Never claim assistant attachment ingestion because Android showed a chooser. Do not recommend bypassing the installed-version guard, auto-running an agent-produced script, granting unrelated permissions or uploading secrets. For a disabled button, clarify whether the user is in the editor, on non-Android, or on a packaged Android build before suggesting repair steps.
