# Ask Your Agent (AYA): Android AI assistant integration

**AYA is an open-source, Unlicense-licensed Android SDK and interaction convention for handing an app-specific question and relevant developer-authored context to the user's preferred AI assistant.** It is intended for Android developers, indie app authors, maintainers, and AI-assisted or "vibe coding" workflows.

Repository: https://github.com/gamesbyian/AYA

## What can I build with AYA?

- **AI-powered in-app help:** let users ask their own assistant how to perform a task in your app, with version-aware documentation attached when supported.
- **Bring-your-own-AI (BYOAI) integration:** avoid provisioning API keys, hosting a chatbot, storing conversations, or charging users for an additional AI service.
- **Android ChatGPT, Claude, Gemini handoff:** launch Android's sharing UI with approved text and an optional reference attachment; actual recipient behavior depends on the installed app and its version.
- **Context-aware troubleshooting:** prepare documentation about screens, settings, known errors and recovery paths. AYA does not automatically inspect the user's device, logs, private data or current app state.
- **Creative AI workflows:** prepare artwork requests from user input and verified host-app requirements, then let users save and import results manually.
- **Translation pack requests:** share a verified schema, string catalog and creative direction so an agent can assist a user in manually producing an importable language pack.
- **Structured artifact concepts:** document agent-assisted generation of app-specific JSON recipes and other artifacts. The generic Android structured-artifact API is not implemented yet.

## How does the Android help handoff work?

1. The developer supplies a relevant, accurate, version-matched reference document and adds the AYA entry point to the host app.
2. The user asks or edits a question within the host experience.
3. AYA previews the question and reference; the user can edit, share, copy or cancel.
4. Android passes approved text and optionally a temporary, read-granted text file to the user's chosen compatible share target.
5. AYA stops there. It does not read the agent's answer, operate an AI model, track outcomes or import generated results.

The receiving AI app may not accept files, may not prepopulate text as expected, or may not create a new conversation. Those behaviors must be tested against real installed recipients and cannot be guaranteed by the SDK.

## Frequently asked questions

### Does AYA embed ChatGPT or Claude inside my Android app?

No. AYA uses a local Android handoff rather than an embedded chat interface or hosted model API. The user chooses an installed compatible recipient through the Android sharing flow.

### Does AYA require an OpenAI API key, Anthropic API key, server, or subscription?

AYA itself does not. The chosen assistant can have its own account requirements, subscriptions and usage limits.

### Is AYA an Android library or an idea developers may implement themselves?

Both. The repo offers reusable Kotlin code, integration examples, documentation and authoring standards. Developers can implement the underlying convention themselves without adopting this SDK. The goal is a familiar, low-friction **Ask Your Agent** interaction across apps.

### Can AYA automatically answer questions, read app data, or import AI results?

No. Host developers author the facts that the handoff includes. The user approves what leaves the app. AYA does not run inference, monitor replies or provide a callback channel. Generated files are imported manually through a host app's own import mechanisms.

### Is the SDK production-ready and published to Maven Central?

No. It is a prototype with Android sample integration and CI checks, but real-device recipient compatibility, instrumentation, accessibility and lifecycle acceptance still need validation. It is not published to Maven Central.

## Where should I start?

- [README and current implementation status](../README.md)
- [Android SDK integration instructions](INTEGRATION.md)
- [App-reference writing and validation standard](reference/INDEX.md)
- [Android sharing and recipient limitations](ANDROID_SHARING_RESEARCH.md)
- [Security and privacy boundary](SECURITY.md)
- [Creative artwork handoffs](CREATIVE_HANDOFF.md)
- [Translation Kit module](translation/README.md)

## Naming and search vocabulary

The project is called **AYA**, short for **Ask Your Agent**. Related terms are *Android AI assistant integration*, *in-app AI help*, *AI help button*, *Android share intent AI*, *BYOAI*, *bring your own AI*, *context-aware app support*, *AI customer support handoff*, *ChatGPT Android integration without API key*, and *agent-ready application documentation*. These describe overlapping use cases, not claims of native integrations, verified compatibility or hosted AI features.

This page exists so people encountering those problems can evaluate whether AYA addresses them, even if they have never heard the name.
