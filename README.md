<p align="center">
  <img src="assets/ask-your-agent-icon.svg" alt="Ask Your Agent icon" width="220">
</p>

# AYA · Ask Your Agent

**Open-source Android AI assistant integration without an API key.** Add an **Ask Your Agent** help button to an Android app so people can ask ChatGPT, Claude, Gemini, or another compatible assistant for help with that app. AYA packages the user's question with developer-authored, version-matched app documentation, offers review and edit controls, and hands the approved context to Android's share system. Assistant attachment support varies, and the user remains in control.

**For Android developers:** AYA is a reusable Kotlin/Android SDK and a documented design pattern for bringing your own AI (BYOAI) to in-app help, AI-powered customer support handoffs, app-aware troubleshooting, creative requests, and optional user-generated translation packs. It requires **no AI API key, backend, paid model integration, or reply tracking**.

[**Android integration guide**](docs/INTEGRATION.md) · [**Quick explanation and use cases**](docs/DISCOVERABILITY.md) · [**Reference packet authoring**](docs/reference/INDEX.md) · [**Privacy and security**](docs/SECURITY.md)

**Help Handoff + Creative Handoff + optional Translation Kit Handoff.** Image requests now let users choose between text-only sharing and an optional full reference attachment. AYA also supports an image-generation request prepared from the host's verified artwork requirements and the user's creative direction. See [Creative Handoff specification](docs/CREATIVE_HANDOFF.md). The user generates/saves artwork in their chosen AI app and imports it via the host's existing picker. AYA never observes the result.

**A reusable Android bring-your-own-AI handoff component.** AYA prepares an application-specific, version-aware reference plus the user's question, lets the user review/edit it, and shares a self-contained text document with ChatGPT, Claude, or another compatible Android share target.

AYA has no model API key, inference hosting, developer AI bill, telemetry or account system. Users use their own assistant, subject to that assistant's terms and limits. **The receiving app decides whether to accept the attachment and open a new chat; AYA cannot guarantee either.**

## Translation Kit: optional language and personality packs

Apps can offer ordinary **Language** settings (device language, installed languages, Import pack) with a small optional **"Make a language pack with your AI"** AYA card. AYA now provides `Aya.launchTranslationBundled()`: an exact-version-guarded, one-way handoff carrying a host-authored translation schema, catalog, Rosetta/glossary, style and safety constraints, examples, and import instructions. Users can request French, Pirate, Cajun-flavoured, space-sage, technical terminology, or other creative voices. The recipient may produce a JSON pack; the user saves it and imports it through the **host's existing language importer**. AYA never sees the response or applies a pack.

**Start here:** [Translation module and Kotlin usage](docs/translation/README.md), [app-specific kit authoring standard](docs/translation/AUTHORING.md), [fictional complete kit](docs/translation/examples/parcelpad-translation-kit.md), [output schema](docs/translation/examples/parcelpad-output.schema.json), and [Pirate pack example](docs/translation/examples/parcelpad-pirate.pack.json).

**Implementation status:** the typed task/verifier and guarded Android handoff are implemented in the SDK; no host language-pack runtime, generator, gallery or real-recipient acceptance is implemented or verified. This module is optional and does not require an AI account for normal language settings.

## Structured artifact handoffs

AYA's one-way concept also applies when a host asks an agent to generate a **structured data file**, such as a ROYGBIV wallpaper recipe in JSON. A version-matched schema and effect guide can accompany an editable natural-language brief and optional user-approved current artifact. The person manually saves and imports the agent's file into the original app. No callback, agent-response monitoring or automatic import is needed.

The [structured artifact handoff profile](docs/STRUCTURED_ARTIFACT_HANDOFF.md) documents the browser/PWA reference integration under ROYGBIV's More menu and a future generic Android SDK extension. **The Android structured-artifact API is not implemented yet**, and receiving assistants have different attachment capabilities.

## Why use AYA instead of opening an AI app yourself?

You absolutely can open ChatGPT, Claude, or another assistant and type a question yourself. AYA is meant to make that familiar process **a little smoother**, especially when the question comes up while you are already using an app.

Instead of leaving the app, switching to an assistant, explaining which app and screen you are using, and finding the relevant instructions, you can start with **Ask Your Agent** where the question arises. The host can offer a suggested question or let you write your own, then AYA lets you review a relevant, version-aware app reference and pass the approved question and context to your chosen assistant through Android sharing. Whether the receiving app accepts the attachment or opens a new conversation depends on that app.

The benefit is deliberately modest: **one less point of inertia between wanting to do something and getting help to do it**. AYA keeps the user moving toward the experience they wanted in the first place, without replacing their assistant, operating an AI service, or tracking what happens after the handoff.

## Understanding the host before producing packets

The [AYA Application Understanding Framework](docs/understanding/README.md) teaches a developer's agent to reconstruct the host application's purpose, domain concepts, user goals, interaction philosophy, misconceptions and evidence boundaries **before** building any AYA informational packet. Its [adaptive Director Consultation Protocol](docs/understanding/CONSULTATION.md) encourages focused questions to authorized project directors when intent is unclear, with a [reusable question bank](docs/understanding/QUESTIONS.md), [decision records](docs/understanding/SCHEMA.md) and offline validation. Director answers express design intent; they do not prove functionality ships. Consultation happens during development, not through AYA's runtime handoff.

## Packet authoring across modules

AYA has a [common Packet Authoring Standard](docs/packet/AUTHORING_STANDARD.md) and [four module profiles](docs/packet/PROFILES.md) covering Help, Creative, Structured Artifact and Translation Kit. Developers define source-backed atomic host facts, an independent inventory, module-specific output contracts and negative examples. The offline [packet compiler](tools/packet_compiler.py) deterministically creates scoped, provenance-marked, dependency-complete context packets and explicitly reports omitted facts; it refuses stale external claims and oversized exports. See [quickstart and fictional fixtures](docs/packet/README.md).

**Scope:** this is **build-time authoring infrastructure**, not a new on-device model, dynamic host-state reader, assistant integration, or automatic reply/import mechanism. The verified packet must be deliberately packaged into the existing version-matched AYA handoff. AYA still ends at the user-controlled Share/Copy boundary.

## Standard host-app AYA card

The [AYA Card UI Standard v1](docs/CARD_UI_STANDARD.md) defines the thin-outline, host-themed card with the monochrome AYA mark, contextual explanation, honest file-sharing disclosure, optional question field, and **Ask Your Agent** action. The Android SDK now includes `AyaCardView`, a reusable View implementation demonstrated in the sample. Blank questions are welcome; pressing the button opens the existing version-checked **local review**, not automatic sharing. The host controls corner radius and contextual copy. Both Standard and Compact densities are implemented through `AyaCardDensity`, sharing the same safe handoff and full-width controls.

## Where to start
**Interoperability additions (October 2026):** [recipient capability evidence model](docs/RECIPIENT_CAPABILITIES.md), [portable handoff manifest schema](docs/protocol/README.md), optional [AssistContent adapter](docs/ASSIST_CONTEXT.md), and a [separate AppFunctions decision record](docs/APPFUNCTIONS_DECISION.md). The capability model holds only developer-supplied QA facts; it neither monitors user conversations nor learns from outcomes. The JSON manifest is a documented *host-side interchange format*, not a new wire format for AI recipients.


- [Reference-document authoring system](docs/reference/INDEX.md): **mandatory guide for every integrating app**. Includes the [base authoring standard](docs/reference/AUTHORING_STANDARD.md), [advanced authoring techniques](docs/reference/ADVANCED_AUTHORING.md), [agent production workflow](docs/reference/AGENT_WORKFLOW.md), [independent inventory and traceability](docs/reference/TRACEABILITY.md), [assistant evaluation protocol](docs/reference/EVALUATION_PROTOCOL.md), [template](docs/reference/TEMPLATE.md), [quality rubric](docs/reference/QA_RUBRIC.md), [question bank](docs/reference/QUESTION_BANK.md), [maintenance process](docs/reference/MAINTENANCE.md), [modular guide builder](docs/reference/MODULAR_BUILDS.md) and [fictional worked example](docs/reference/EXAMPLE_PARCELPAD.md).
- [Android integration](docs/INTEGRATION.md), [question-first UX contract](docs/QUESTION_COMPOSER.md), [Android sharing research](docs/ANDROID_SHARING_RESEARCH.md), [readiness checklist](docs/INTEGRATION_READINESS.md), and [real sample host](sample/): version-guarded invocation, standalone AAR consumption, and release gates.
- [Product specification](docs/SPEC.md), [privacy/security](docs/SECURITY.md), [test plan](docs/TEST_PLAN.md), [recipient compatibility ledger](docs/PROVIDER_COMPATIBILITY.md).

**A good AYA reference is much more than a manual.** It is a testable, source-backed explanation of screens, settings, version-specific capabilities, exact task steps, errors, recovery, data impact, provider differences and known limits. It must enable a model to say "unknown" instead of hallucinating controls.

## Android usage
**Creative UX:** users now see a concise editable generation prompt first. **Share request** sends only that text, **Copy request** copies it, and **Full guide** opens the full editable app-reference package with optional attachment. This version guard is enforced before either route. See the [artwork host-acceptance contract](docs/CREATIVE_HOST_ACCEPTANCE.md) before integrating into an existing picker.


### Creative artwork generation

`Aya.launchCreativeBundled(activity, task, direction, askDirection=false)` is the version-guarded creative API; `AyaCreativeTask` supplies subject, artwork role, required manual import path and an `AyaImageRequirements` object (aspect ratio, optional preferred dimensions, verified accepted formats and optional composition limits). The user supplies editable creative direction in the host or AYA composer. The complete generation request can be shared as plain text with no attachment, or alongside the full reference. The compact review offers text-only Share and Copy by default; Full guide exposes the full reference and its separate text-only/attachment choices. Text-only requests over 4000 characters are rejected rather than truncated. The sample provides a working Android file picker to import a saved image afterward. See [API example](docs/CREATIVE_HANDOFF.md#host-api-and-required-data) and [integration guide](docs/INTEGRATION.md).


The recommended integration method **automatically checks the bundled reference against the installed app's package and exact version**, instead of trusting hardcoded strings:

```kotlin
when (val result = Aya.launchBundled(
    activity = this,
    guideAsset = "aya-guide.md",
    screenName = "Connections",
    question = "How can I configure this connection?" // optional editable suggestion
)) {
    is AyaBundledLaunchResult.Rejected ->
        Toast.makeText(this, "AYA help unavailable: ${result.reason}", Toast.LENGTH_LONG).show()
    AyaBundledLaunchResult.QuestionOpened -> Unit // question field is shown
    AyaBundledLaunchResult.PreviewOpened -> Unit // full review is shown
}
```

**By default, AYA first asks the user to type or edit a question inside the host app**, then opens the complete privacy preview. If your host already has its own question field, pass `question = userTypedQuestion, askQuestion = false` to go straight to review and avoid asking twice. The question is included inside the attachment and is also passed as `Intent.EXTRA_TEXT` when sharing, derived from the final approved payload so edits cannot leak an earlier question. Recipient support varies; see [sharing research](docs/ANDROID_SHARING_RESEARCH.md).

Ship `app/src/main/assets/aya-guide.md` following the [AYA-RAS standard](docs/reference/INDEX.md), with `app_id` and `app_version_min/max` matching the APK. There is no fallback to a stale guide. `PreviewOpened` means the local review started, not that a recipient accepted the file. The original `Aya.launch(AyaRequest(...))` API remains available for advanced/manual cases but does not validate the bundled guide.

The preview shows the complete text and allows edits before **Share**, **Copy** or **Cancel**. Sharing uses Android `ACTION_SEND` with one UTF-8 text attachment, the user-approved question in `EXTRA_TEXT`, and a temporary read-granted content URI. Copy gives a manual fallback. AYA includes a narrowly scoped AndroidX FileProvider.

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

Creative Handoff is a **prototype** with typed Kotlin implementation and sample image chooser; real AI-recipient generation, saving and manual-return behavior remain unverified. AYA does not generate images, monitor output, or automatically apply the result in the host. No Chunks, Plex or other real-world app integration is implied.


Android builds and reference checks have passed CI; real-device recipient verification is still required. Do not claim production readiness or tested ChatGPT/Claude behavior. [Compatibility evidence](docs/PROVIDER_COMPATIBILITY.md) is currently unverified.

Known work: actually executing instrumentation tests on emulator/device, accessibility and lifecycle acceptance, real-device assistant trials, comprehensive privacy review, and stable distribution/API policy. The guarded API supports **exact** version-matched guides; multi-version guide resolution is deliberately unsupported.

## License

AYA is released under [the Unlicense](UNLICENSE), a public-domain dedication with a permissive fallback where applicable. The project maintainer contributes concepts and direction; the implementation code is generated with AI assistance. The maintainer does not claim personal authorship or exclusive ownership of that generated code, and dedicates any copyright interest they may hold in the repository's original material to the public domain.

Anyone may use, copy, change, distribute, or sell the material without attribution or permission, subject to any independently applicable third-party rights. The Unlicense cannot waive rights belonging to others; third-party dependencies retain their own licenses.
