# AYA product/engineering specification (draft 1)

## Goal and operating principle

AYA is a reusable Android **bring-your-own-AI help handoff**. An app provides version-matched, operationally rich documentation and optionally a user question/screen context. AYA previews the exact package and lets the user share it through the Android Sharesheet with a compatible assistant, without running or paying for an AI model.

## Key product component: trustworthy references

**The quality of the app guide determines the help quality.** Every integration must follow [AYA Reference Authoring Standard](reference/AUTHORING_STANDARD.md), with full feature inventory, exact UI paths, task recipes, state and provider variations, troubleshooting, source evidence, unsupported functionality, privacy and upgrade guidance. Guides must match the installed app version. Maintain a quality rubric and held-out question trials. The full static reference is embedded in one plain-text package, not fetched by the recipient.

## Prototype API

`Aya.launch(activity, AyaRequest(appName, appVersion, guide, screenName?, question?))`.

No data is collected by AYA itself. Android library includes a non-exported FileProvider limited to `cacheDir/aya/`. AYA creates a unique text file with the edited payload and sends it using `ACTION_SEND`, `EXTRA_STREAM`, `ClipData`, and `FLAG_GRANT_READ_URI_PERMISSION`.

## User experience

1. Tap "Ask your agent" within a host app.
2. Read and edit the entire context in an expanded, scrollable review dialog.
3. Cancel, Copy to clipboard, or Share using Android Sharesheet.
4. Choose an external assistant; its app decides how to ingest the attachment and whether to start a chat.
5. If recipient does not ingest the file, paste copied text manually.

No guarantee of new-chat creation, auto-send, or assistant adherence. Destination processing is outside AYA's control. Sharing limit: 2 MiB in the prototype. Old unique cache files pruned on a later share after seven days.

## Non-goals

Bundled chatbot, vendor lock-in, inference billing, automatically reading installed accounts, reading assistant responses, screen scraping, silently exporting diagnostics, editing the recipient conversation, unofficial deep links or pretending assistant can operate the host app.

## Acceptance gates and roadmap

**Prototype:** library, documentation/authoring standard, validator, sample build and unit tests.
**Beta:** physical-device and instrumentation verification, accessible preview acceptance, host version-guard, redaction controls, explicit diagnostic opt-in, recipient compatibility ledger.
**Stable:** real integrating app's released guide plus QA rubric, compatibility contract, maintenance ownership, artifact publication, security and accessibility review.

Evidence belongs in [test plan](TEST_PLAN.md) and [compatibility ledger](PROVIDER_COMPATIBILITY.md).
