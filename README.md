# AYA: Ask Your Agent

**Bring-your-own-AI help for Android apps.** AYA lets an Android app create a version-aware help package and offer it to ChatGPT, Claude, or any other compatible share target, using the assistant the user already has.

## Status

Early reusable Kotlin Android library prototype. **Not yet built or tested on a device.** The recipient app controls whether it accepts the attachment and starts a new conversation. AYA cannot guarantee either behavior.

## Integration

Add the `:aya` module to your Android project, then:

```kotlin
Aya.launch(this, AyaRequest(
    appName = "Chunks",
    appVersion = "1.0.0",
    guide = assets.open("aya-guide.txt").bufferedReader().use { it.readText() },
    screenName = "Connections",
    question = "How do I configure this connection?"
))
```

The user sees the full content before deciding to Cancel, Copy, or Share. Share sends one UTF-8 text attachment through Android Sharesheet. Copy permits manual pasting into a chat. The library includes a non-exported, narrowly scoped FileProvider.

AYA does **not** require a hosted model, vendor API keys, developer inference bills, subscriptions, analytics, or any network access. The selected assistant may have its own limits and privacy terms.

## Design

- Host supplies the app guide and optional context. AYA collects no settings, logs, passwords, or device data.
- Installed version and current screen appear in the package.
- Use public Android share intents, not undocumented provider deep links.
- No guarantee of automatic file ingestion, chat creation, or zero-tap sending.
- Assistant must distinguish documented features from planned functionality.

See [specification](docs/SPEC.md), [privacy and security](docs/SECURITY.md), and [verification plan](docs/TEST_PLAN.md).

## Build

Requires Android SDK, JDK 17, and Gradle compatible with AGP 8.7.3. No wrapper included yet. Try `gradle :aya:testDebugUnitTest`; build execution remains unverified.

## Roadmap

1. Prototype library, docs, sharing UX and tests.
2. Demo app, accessibility and instrumentation acceptance, dated ChatGPT/Claude testing.
3. Editable privacy preview, cache expiration, provider compatibility matrix and stable API.

## License

Not yet selected. Do not assume a redistribution license.
