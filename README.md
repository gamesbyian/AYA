# AYA · Ask Your Agent

**A reusable Android bring-your-own-AI help component.** AYA prepares an application-specific, version-aware reference plus the user's question, lets the user review/edit it, and shares a self-contained text document with ChatGPT, Claude, or another compatible Android share target.

AYA has no model API key, inference hosting, developer AI bill, telemetry or account system. Users use their own assistant, subject to that assistant's terms and limits. **The receiving app decides whether to accept the attachment and open a new chat; AYA cannot guarantee either.**

## Where to start

- [Reference-document authoring system](docs/reference/INDEX.md): **mandatory guide for every integrating app**. Includes complete [authoring standard](docs/reference/AUTHORING_STANDARD.md), [template](docs/reference/TEMPLATE.md), [quality rubric](docs/reference/QA_RUBRIC.md), [question bank](docs/reference/QUESTION_BANK.md), [maintenance process](docs/reference/MAINTENANCE.md) and [fictional worked example](docs/reference/EXAMPLE_PARCELPAD.md).
- [Android integration](docs/INTEGRATION.md) and [sample app](sample/): how to invoke and inspect AYA.
- [Product specification](docs/SPEC.md), [privacy/security](docs/SECURITY.md), [test plan](docs/TEST_PLAN.md), [recipient compatibility ledger](docs/PROVIDER_COMPATIBILITY.md).

**A good AYA reference is much more than a manual.** It is a testable, source-backed explanation of screens, settings, version-specific capabilities, exact task steps, errors, recovery, data impact, provider differences and known limits. It must enable a model to say "unknown" instead of hallucinating controls.

## Android usage

Include `:aya` as a library module, bundle a version-matched Markdown reference file as an APK asset, and call from an Activity:

```kotlin
val guide = assets.open("aya-guide.md").bufferedReader(Charsets.UTF_8).use { it.readText() }
Aya.launch(this, AyaRequest(
    appName = "My App",
    appVersion = "1.0.0", // use real installed build version
    guide = guide,
    screenName = "Connections",
    question = "How can I configure this connection?"
))
```

The preview shows the complete text and allows edits before **Share**, **Copy** or **Cancel**. Sharing uses Android `ACTION_SEND` with one UTF-8 text attachment and a temporary read-granted content URI. Copy gives a manual fallback. AYA includes a narrowly scoped AndroidX FileProvider.

AYA never gathers settings, logs, device IDs or credentials automatically. The host is responsible for sanitizing explicit context. The receiver may store/upload the shared content. Clipboard copy is a separate privacy boundary.

## Run the sample

`:sample` is an Android Activity demonstrating the handoff with a **fictional ParcelPad reference**. No ParcelPad functionality is implemented. Build with JDK 17, Android SDK 35, Gradle 8.9:

```sh
gradle :aya:testDebugUnitTest :aya:assembleDebug :sample:assembleDebug
python3 tools/validate_guide.py --strict docs/reference/EXAMPLE_PARCELPAD.md
python3 -m unittest discover -s tools -p 'test_*.py'
```

GitHub Actions runs both suites and publishes the sample debug APK if the Android build passes. Gradle wrapper is not yet checked in.

## Prototype status

Source is implemented, but CI and physical-device verification are still required. Do not claim production readiness or tested ChatGPT/Claude behavior. [Compatibility evidence](docs/PROVIDER_COMPATIBILITY.md) is currently unverified.

Known work: accessibility and lifecycle instrumentation, real-device assistant trials, host guide version selection, automatic redaction, and eventual stable distribution/API.

## License

Undecided. No redistribution license has been granted yet.
