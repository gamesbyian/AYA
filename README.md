# AYA · Ask Your Agent

**A reusable Android bring-your-own-AI help component.** AYA prepares an application-specific, version-aware reference plus the user's question, lets the user review/edit it, and shares a self-contained text document with ChatGPT, Claude, or another compatible Android share target.

AYA has no model API key, inference hosting, developer AI bill, telemetry or account system. Users use their own assistant, subject to that assistant's terms and limits. **The receiving app decides whether to accept the attachment and open a new chat; AYA cannot guarantee either.**

## Where to start

- [Reference-document authoring system](docs/reference/INDEX.md): **mandatory guide for every integrating app**. Includes the [base authoring standard](docs/reference/AUTHORING_STANDARD.md), [advanced authoring techniques](docs/reference/ADVANCED_AUTHORING.md), [agent production workflow](docs/reference/AGENT_WORKFLOW.md), [independent inventory and traceability](docs/reference/TRACEABILITY.md), [assistant evaluation protocol](docs/reference/EVALUATION_PROTOCOL.md), [template](docs/reference/TEMPLATE.md), [quality rubric](docs/reference/QA_RUBRIC.md), [question bank](docs/reference/QUESTION_BANK.md), [maintenance process](docs/reference/MAINTENANCE.md), [modular guide builder](docs/reference/MODULAR_BUILDS.md) and [fictional worked example](docs/reference/EXAMPLE_PARCELPAD.md).
- [Android integration](docs/INTEGRATION.md), [readiness checklist](docs/INTEGRATION_READINESS.md), and [real sample host](sample/): version-guarded invocation, standalone AAR consumption, and release gates.
- [Product specification](docs/SPEC.md), [privacy/security](docs/SECURITY.md), [test plan](docs/TEST_PLAN.md), [recipient compatibility ledger](docs/PROVIDER_COMPATIBILITY.md).

**A good AYA reference is much more than a manual.** It is a testable, source-backed explanation of screens, settings, version-specific capabilities, exact task steps, errors, recovery, data impact, provider differences and known limits. It must enable a model to say "unknown" instead of hallucinating controls.

## Android usage

The recommended integration method **automatically checks the bundled reference against the installed app's package and exact version**, instead of trusting hardcoded strings:

```kotlin
when (val result = Aya.launchBundled(
    activity = this,
    guideAsset = "aya-guide.md",
    screenName = "Connections",
    question = "How can I configure this connection?"
)) {
    is AyaBundledLaunchResult.Rejected ->
        Toast.makeText(this, "AYA help unavailable: ${result.reason}", Toast.LENGTH_LONG).show()
    AyaBundledLaunchResult.PreviewOpened -> Unit
}
```

Ship `app/src/main/assets/aya-guide.md` following the [AYA-RAS standard](docs/reference/INDEX.md), with `app_id` and `app_version_min/max` matching the APK. There is no fallback to a stale guide. `PreviewOpened` means the local review started, not that a recipient accepted the file. The original `Aya.launch(AyaRequest(...))` API remains available for advanced/manual cases but does not validate the bundled guide.

The preview shows the complete text and allows edits before **Share**, **Copy** or **Cancel**. Sharing uses Android `ACTION_SEND` with one UTF-8 text attachment and a temporary read-granted content URI. Copy gives a manual fallback. AYA includes a narrowly scoped AndroidX FileProvider.

AYA never gathers settings, logs, device IDs or credentials automatically. The host is responsible for sanitizing explicit context. The receiver may store/upload the shared content. Clipboard copy is a separate privacy boundary.

## Run the sample

`:sample` is a **real Android consuming application**, with a reference describing the actual sample app, validated against its independent feature inventory and support question cases. The separate ParcelPad guide remains fictional and is used only as an authoring example. Build with JDK 17, Android SDK 35, Gradle 8.9:

```sh
gradle :aya:testDebugUnitTest :aya:assembleDebug :sample:assembleDebug
python3 tools/validate_guide.py --strict docs/reference/EXAMPLE_PARCELPAD.md
python3 tools/audit_reference.py docs/reference/EXAMPLE_PARCELPAD.md --inventory docs/reference/examples/parcelpad_inventory.json --questions docs/reference/examples/parcelpad_questions.json --strict
python3 -m unittest discover -s tools -p 'test_*.py'
```

GitHub Actions runs reference checks, Kotlin unit tests and the sample build, compiles Android instrumentation tests, publishes a staging AAR/POM repository, and rebuilds the sample against the staged artifact. To build the Maven repository locally, use `gradle :aya:publishReleasePublicationToStagingRepository`. Its coordinates are `dev.aya:aya-android:0.1.0-SNAPSHOT`; **no Maven Central publication exists yet**. Gradle wrapper is not yet checked in.

## Prototype status

Android builds and reference checks have passed CI; real-device recipient verification is still required. Do not claim production readiness or tested ChatGPT/Claude behavior. [Compatibility evidence](docs/PROVIDER_COMPATIBILITY.md) is currently unverified.

Known work: actually executing instrumentation tests on emulator/device, accessibility and lifecycle acceptance, real-device assistant trials, comprehensive privacy review, and stable license/distribution/API policy. The guarded API supports **exact** version-matched guides; multi-version guide resolution is deliberately unsupported.

## License

Undecided. No redistribution license has been granted yet.
