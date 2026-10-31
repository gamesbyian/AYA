# AYA Compose drop-in (initial optional Android adapter)

**Status:** optional source/CI-tested Android Compose adapter in AYA; not a published Maven Central package or a visual editor marketplace extension. Source module `:aya-compose` adds an optional Compose UI adapter and depends on the existing Android `:aya` SDK. Minimum Android API 23. Version 0.1.0-SNAPSHOT is for CI staging; no external release is claimed.

## Why an optional module?

`aya` remains usable from Java/Kotlin Views, fragments and non-Compose hosts. Compose users opt into `aya-compose` and its Compose dependencies; neither translation nor creative handoff needs to be rewritten. The Android `AyaCardView` provides the same thin outline, optional question, required manual-output instructions, theme-derived mark, 48dp actions and reviewed AYA handoff.

## Source-module installation

Add `include(":aya", ":aya-compose")` to Gradle settings, and `implementation(project(":aya-compose"))` in the host app. Enable Compose in the app module using the Kotlin version-matched Compose Compiler plugin. The repo pins Kotlin 2.0.21, Compose UI/runtime 1.7.8, and a Compose-compatible test sample; external projects should reconcile dependency versions with their own build and verify binary compatibility.

The host still bundles `src/main/assets/aya-guide.md` with app ID and min/max version equal to its **installed Android versionName**, and validates against its shipped UI. See [AYA-RAS](../reference/INDEX.md), [component standard](README.md) and [Card UI Standard](../CARD_UI_STANDARD.md).

```kotlin
@Composable
fun HelpPanel(activity: Activity) {
    AyaCard(
        activity = activity,
        outputInstructions = "Return here and apply the advice manually.",
        screenName = "Settings",
        modifier = Modifier.fillMaxWidth()
    )
}

@Composable
fun HelpMenu(activity: Activity) {
    val launcher = rememberAyaLauncher(
        activity,
        AyaComponentAction.Help(screenName = "Settings", askQuestion = false)
    )
    Button(onClick = { launcher.launch("How do I configure this setting?") }) {
        Text("Ask Your Agent")
    }
}
```

Import `dev.aya.compose.AyaCard`, `dev.aya.compose.rememberAyaLauncher`, `dev.aya.android.AyaComponentAction` and the usual Compose libraries. `AyaCard` owns a saveable draft; **host must supply a stable Compose key for dynamic lists**, one outer scroll owner, and a valid Activity. A MaterialTheme changes Compose widgets, whereas the embedded Android View card derives its colors from the Activity's Android theme. Test matching schemes/high contrast rather than assuming the palettes synchronize automatically.

`rememberAyaLauncher` is only a headless click-handler façade. Its `launch()` returns `AyaBundledLaunchResult.QuestionOpened`, `PreviewOpened` or `Rejected` for **local UI**, never Share completion, receiving-app ingestion, generated output or import completion. Do not call `launch()` from `LaunchedEffect`, `SideEffect` or app startup.

For output import, the host must use its own verified import pipeline. The first Compose adapter deliberately keeps a simple Help card; use the existing `AyaCardView` optional import callback in a tailored `AndroidView` if the host really supports import. Future adapter releases may offer an explicit import hook after it has its own tests.

## Generate Compose wrappers from a component manifest

The same help-only component configuration works for traditional Android and Compose. Run `python3 tools/component_codegen.py docs/components/examples/sample-help-card.json --format compose` to emit an annotated, uniquely named Kotlin composable; use the action example to emit a `rememberAyaLauncher` wrapper. Add the generated source to an app package, pass its actual Activity and place it in the desired UI. Code generation is static and never reads host runtime state. CI compiles both generated Compose examples into the consuming sample.

## Validation

- `gradle :aya-compose:assembleDebug :sample:assembleDebug`
- `gradle :aya-compose:publishReleasePublicationToStagingRepository`, then build the sample against its staged AAR/POM rather than only project source.
- Emulator: enter text in Compose-embedded card; verify local review contains exact question and cancel returns without share; exercise headless action and missing guide refusal.
- Manual Android device: 320x700 and 412x892; 200% font, TalkBack, keyboard IME, rotation, multiple cards, light/dark host theme, chooser canceled/no target, Copy fallback.
- Re-evaluate imported outputs separately in the host. None of these tests can confirm that a third-party AI provider ingested an attachment.

## Extended host-facing card contract

The Compose card also accepts an optional stable `componentId` for multi-card screens, an `initialQuestion` seed, `questionHint`, `cornerRadiusDp`, and `onQuestionChanged` for **locally typed** draft text. No callback receives model responses. A generated Compose card automatically uses the manifest's stable component ID. A host changing component identity or guide/screen scope must not carry stale private drafts into another context.

Optional `onAskRequested = { question -> ... }` allows a real host implementation to invoke a **guarded module-specific SDK action** instead of default Help; the host must keep source-verified packet contracts, user review and local error handling. Optional `onImportRequested = { ... }` exposes the existing native card's secondary import control only when a real host-controlled SAF picker and validator are supplied. These are independent user-initiated actions, **not** agent-return listeners. A help-only host should omit both callbacks. The wrapped Android View remains the visible source of the attachment and output-use disclosures.
