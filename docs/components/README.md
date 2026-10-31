# AYA Drop-in Components and Visual Builder Integration

**Status (2026-10-31):** Android Views/XML, Compose, Flutter source plugin and Godot Android v2 source addon are integrated with different levels of CI evidence. FlutterFlow body templates are available, while React Native/Expo, Unity and no-code extensions remain planned. See [current adapter status and release blockers](STATUS.md). The portable component manifest **v1 remains help-only**; passing structural checks does not prove correct host instructions or assistant ingestion.

## Purpose

A developer should be able to add an **Ask Your Agent** entry point from a visual editor, IDE, node/logic graph or coding agent, without reimplementing Android sharing, reviewing private data or understanding every AYA internal detail. AYA is also an **interaction convention**: developers may implement the compatible interaction themselves without installing any AYA library. The repository is Unlicensed.

The drop-in component is a user-facing control or action, not an assistant. The host is responsible for evidence-backed context and file import. The user decides whether and what to share; a selected receiving app decides what it accepts.

### Non-negotiable product boundary

1. The installed app owns and bundles an **exact-version AYA-RAS v1 guide**. A declared path alone cannot make a reference accurate. Author it via [AYA-AUF](../understanding/README.md), [Director Consultation](../understanding/CONSULTATION.md), [AYA-RAS](../reference/INDEX.md), and [Packet Authoring](../packet/README.md).
2. An AYA action launches the existing **question/review + Copy/Share** sequence. Only the final approved payload is eligible for Android sharing. Do not skip either consent or version checks to simplify a plugin.
3. It uses Android public sharing, not recipient-specific undocumented deep links. No vendor API keys, inference, account, network service, reply tracking, conversation monitoring or automatic result collection.
4. Exposing a UI event means **local** UI opening, rejection, or a known Android dispatch attempt only. It never means an assistant read, answered or acted on the request.
5. The host alone imports/validates outputs. An optional output-import control is an **independent host operation**; it cannot be framed as an AYA return callback. See [Card UI Standard](../CARD_UI_STANDARD.md) and [Structured Artifact Handoff](../STRUCTURED_ARTIFACT_HANDOFF.md).
6. No automatic scraping of app source, files, screens, logs, installed AI apps or sensitive state at runtime. Source analysis is an explicit, build-time developer-agent workflow with approval and traceability.
7. All graphical controls must be accessible and usable offline, without an AI app installed, using documented Copy/manual alternatives.

## Layered architecture

```text
Developer and director
  -> AYA-AUF conceptual model and evidence / consultation
  -> AYA-RAS + independent inventory + held-out question tests
  -> optional Packet Compiler module profile
  -> version-matched assets packaged into host APK
  -> aya-component/v1 (declarative, build-time help wiring)
       | Android Studio/Views    -> AyaCardView or AyaComponentAction.Help
       | Compose                -> merged optional aya-compose source adapter
       | Flutter/FlutterFlow    -> source Flutter plugin + unverified editor templates
       | React Native/Expo      -> future native module + JS component/action
       | Godot                  -> Android v2 addon + card (export/device unverified)
       | Unity                  -> future Android plugin + Visual Scripting unit
       | App Inventor/Kodular   -> future compatible .aix extension
  -> canonical installed-version-checked Android SDK
  -> user question and editable review
  -> user Copy / Android ACTION_SEND Sharesheet
  -> selected recipient (behaviour unknown until separately tested)

Independent path: host's own picker/importer validates files returned by agent.
```

There are **three complementary surfaces**: a visible card/button; an invisible action for existing controls or graph nodes; and the canonical Android runtime. Adapters share the same contract and never fork packet semantics. Platform-facing wrappers may show an optional manual "Import generated file" action **only when the host supplies a real importer**.

## Component manifest v1

See [JSON Schema](aya-component-v1.schema.json) and [sample fixture](examples/sample-help-card.json). The manifest is a **build-time configuration**, not a runtime app-state reader, a transport file, or the existing `aya-handoff/v1` protocol. Unknown keys and unknown operations fail closed. It supports:

| Property | Meaning |
|---|---|
| `component` | Exactly `aya-component/v1` |
| `id` | Stable, developer-chosen identifier for this integration point |
| `operation` | Exactly `help` in v1; do not pretend unsupported operations are installed |
| `guideAsset` | Relative APK asset path of the exact-version, host-authored AYA-RAS guide |
| `screenName` | Optional fixed public label, **not** collected dynamically |
| `presentation.kind` | `card` or `action` |
| `presentation.title/description/attachmentDisclosure/outputInstructions` | Mandatory for a card, source-verified host copy with accurate manual output path |
| `presentation.density` | `standard` or `compact`, matching `AyaCardView` |
| `presentation.askQuestion` | For action only: show AYA question composer when true |

A `card` includes its own optional editable question and launches local review. An `action` is headless: its host may supply `question` at invocation time. Neither offers a runtime field that bypasses review, bypasses guide validation, forces a recipient, or automatically attaches additional user files.

Example generator:

```sh
python3 tools/component_codegen.py docs/components/examples/sample-help-card.json --check
python3 tools/component_codegen.py docs/components/examples/sample-help-card.json --format kotlin
python3 -m unittest discover -s tools -p 'test_*.py'
```

The generated card/action function name incorporates the component's stable ID and a short hash so multiple drop-ins can coexist without duplicate Kotlin functions. **State restoration remains host-owned:** when installing a card, assign both the returned card and its `questionInput` stable resource IDs (for example `R.id.aya_help_card` and `R.id.aya_help_question`) and retain the same IDs across Activity recreation. The sample app demonstrates this requirement. The generator cannot safely invent resources in an unrelated host project.

The generated Kotlin is an **integration snippet** to paste or adapt, not an automatically modified project. The sample fixture is bound to the first-party sample's real guide; other hosts must source their own documentation and output instructions. Do not copy sample wording into unrelated apps. `--check` validates static configuration only. It cannot establish binary/guide equivalence, source truth, installed recipient behavior, accessibility or runtime success.

### Runtime action API (first slice)

`AyaComponentAction.Help`, `AyaComponentAction.GenerateImage`, and `AyaComponentAction.Translation` are typed Kotlin action configurations. Their `launch(activity, text)` methods delegate directly to the existing guarded `Aya.launch*Bundled()` entry points; they report only `AyaBundledLaunchResult` (local UI opened or rejected). The image and translation **Kotlin actions** are available independently of the help-only manifest v1; a future manifest revision must specify their complete verified task contracts before enabling automatic generation.

```kotlin
val action = AyaComponentAction.Help(
    guideAsset = "aya-guide.md",
    screenName = "Transfers",
    askQuestion = false // host already has a question field
)
val result = action.launch(activity, text = userTypedQuestion)
if (result is AyaBundledLaunchResult.Rejected) {
    showError(result.reason) // host-owned, accessible feedback
}
// No result from any assistant is available here.
```

For a simple embedded card, use `AyaCardView(context, activity, outputInstructions = "...")` as documented in [Card UI Standard](../CARD_UI_STANDARD.md). Compose hosts can use the optional [AyaCard and rememberAyaLauncher adapter](COMPOSE.md), which wraps the established Android card without adding Compose as a dependency of the core runtime. The same help-only manifest can generate Compose snippets with `--format compose`.

## Adapter compatibility contract

Every adapter MUST:

- map manifest fields to the guarded SDK without dropping, changing or inventing source context; fail closed on unsupported modes, asset paths or API versions;
- keep question state controlled by the host, preserving final user edits and respecting lifecycle and process-recreation boundaries;
- preserve recipient choice, honest attachment disclosures, Copy/manual fallback and lack of agent-return events;
- expose local failure outcomes without fabricating handoff completion, assistant capabilities or import success;
- avoid capturing screenshots, UI trees, clipboard, private documents, credentials and app state without specific, separate user consent;
- preserve current host theme, font scaling, 48 dp action target (at least 44 dp), TalkBack semantics, focus/IME behavior and a single sensible scroll owner;
- handle unavailable Android Activity, unsuitable platform/OS, no share targets, large guides, invalid/expired assets and repeated launches gracefully;
- provide reproducible version compatibility, sample host project, offline tests, license information and a dated real-device acceptance matrix.

Do not synthesize a common "onAgentAnswered" callback. Cross-platform interface events should be `onLocalReviewOpened`, `onLocalActionRejected`, and (only if implemented with verifiable Android signals) `onAndroidDispatchAttempted`. Android chooser-component selection is not evidence the recipient processed the payload.

## Host-owned output/import extension (separate standard)

Optional future integration: `AYA Import Result` is a distinct host picker/action that carries a declared output contract (artifact type, MIME/extension, producer schema revision, host feature/slot ID, size and validation limits, migration policy, human confirmation, undo/rollback when applicable). An origin token may help route manually selected files; it is **not** proof of authorship, permission or trust. A mismatched card/feature must explain the mismatch, allow an explicit correct destination where safe, or fall back to a harmless manual file selection. Unknown or damaged files must never be applied by default. No filesystem watcher, automatic AI-result search, agent callback or unattended execution. File automation recipes require dry run, precise plan review and transaction safety in the host.

This import standard is **design work only**; it does not imply AYA has a general result receiver or that the host has an importer.

## Platform adapter shape

| Toolchain | User experience | Implementation target | Status |
|---|---|---|---|
| Android Studio / Kotlin Views | Gradle dependency + card/action | Existing AAR plus typed action/config generator | First slice underway |
| Jetpack Compose | Reusable composable + action | Separate optional Compose artifact, no core dependency | Planned |
| Flutter | Dart widget and callable action | Android platform channel/native plugin | Planned |
| FlutterFlow | Reusable custom widget/action | Flutter plugin + editor distribution; test custom-code restrictions | Planned |
| React Native / Expo | npm component and function | Kotlin-backed native module; config plugin for required Android setup | Planned |
| Godot | AYA node with inspector inputs/signals | Godot 4 Android v2 plugin + GDScript addon | Planned |
| Unity | Inspector component + Visual Scripting unit | Android Java/Kotlin plugin + UPM wrapper | Planned |
| App Inventor / Kodular | Designer block with properties | Compatible .aix extension, build target constraints tested | Research/planned |

CI and samples must make installation/removal, minSdk/AndroidX compatibility, runtime packaging and Android manifest merges visible. Generic node metadata is insufficient: actual editor UI integration must be tested in that specific tool.

## Developer-agent quickstart

A developer can ask their coding agent: "Read `docs/components/README.md`, AGENTS.md and the AYA authoring standards. Identify the Android host toolchain and released build. Build a source-derived AYA-AUF model, consult me only for consequential unresolved product intent, write and independently validate a version-matched AYA guide, choose a supported card/action and integrate it using the guarded SDK. Show the exact review, missing recipient fallback and honest return/import guidance. Do not invent shipping features or assistant behaviour. Run the checks and report what remains unverified."

Coding-agent skills/templates should be offered as an optional convenience. No agent may silently scan private repositories, export secrets or deploy an unreviewed generated guide. The installer should declare what files it changes and be idempotent; uninstallation must leave no orphaned manifest/provider definitions or data.

## Compatibility and conformance

A project may describe its **behaviour** as AYA-compatible without importing AYA code, provided an independent compatibility suite verifies the essentials: informed one-way user-controlled transfer, source-verified installed-version reference, review/edit and Copy fallback, safe URI grants, no response monitoring, truthful output-use instructions, accessibility, explicit exclusions and provider-neutral semantics. Use "AYA-compatible (self-implemented)" separately from "AYA SDK integrated"; neither label implies assistant ingestion. Never award a certification solely from manifest validation.

See [implementation roadmap and acceptance matrix](ROADMAP.md).
