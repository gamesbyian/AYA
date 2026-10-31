# Drop-in AYA for Jetpack Compose (Android only)

**Implementation status:** optional `aya-compose` Android library and first-party sample implementation in the feature branch. This is **not yet a published Maven Central package** and does not verify how any AI app handles shared attachments.

The core `aya` module retains the version-guarded help, image generation, translation and Android Sharesheet logic; the optional Compose library only wraps the real host-themed `AyaCardView` with `AndroidView` and exposes a headless `rememberAyaLauncher` function. There is **no second handoff engine**.

## Installation

For a source-level Android Studio multi-module project:

```kotlin
// settings.gradle.kts
include(":aya", ":aya-compose")

// Android app build.gradle.kts
dependencies {
    implementation(project(":aya-compose"))
}
```

Add the Kotlin 2.0+ Compose Compiler Gradle plugin matching your Kotlin version in the host as required by Android's Compose setup. In this repository it is `2.0.21`, with Android Gradle Plugin `8.7.3`, `compileSdk 35`, and a pinned Compose BOM `2024.12.01`. This is a compatibility baseline, **not** a recommendation to downgrade a modern host. The `aya-compose` module can be published to a staged local Maven repo as `dev.aya:aya-compose:0.1.0-SNAPSHOT`, together with core `dev.aya:aya-android:0.1.0-SNAPSHOT`. No public artifact is promised.

Bundle a developer-authored, audited, installed-version-matched `app/src/main/assets/aya-guide.md` in the **host APK**, not just the library. Follow [AYA-AUF](../understanding/README.md), [AYA-RAS](../reference/INDEX.md) and the [Packet Authoring Standard](../packet/README.md). Version-guard failure means no review/share.

## Generate a drop-in Compose component from a manifest

```sh
python3 tools/component_codegen.py docs/components/examples/sample-help-card.json --format kotlin-compose
python3 tools/component_codegen.py docs/components/examples/sample-help-action.json --format kotlin-compose
```

This emits a compilable `@Composable` wrapper for a card or an `@Composable` function returning a headless action. Generated function names include the stable component ID and a short collision-resistant suffix, so separate cards can coexist. The output is **source to integrate into the host project**, not an installed FlutterFlow or Compose marketplace plugin. The CI compiles both generated forms inside the first-party sample.

## Visible card

```kotlin
@Composable
fun SupportScreen(activity: Activity) {
    AyaCard(
        activity = activity,
        componentId = "settings.support", // unique, stable within this screen
        outputInstructions = "Read the answer and make changes in Settings yourself.",
        description = "Ask how to use the current Settings screen.",
        screenName = "Settings",
        modifier = Modifier.fillMaxWidth()
    )
}
```

The card includes its own editable question, explicit attachment disclosure, output-use instruction and full-width action. The host remains the source of truth for the description and output use. `componentId` identifies the saveable state location, not an externally transmitted tracking token. For repeated entries in a lazy list, key the enclosing Compose item by stable host item ID; avoid changing component IDs between recompositions. `initialQuestion` seeds only a fresh draft; edits survive Compose saveable-state restoration while the host can restore that screen. `onQuestionChanged` can observe locally typed draft values for host UI, **not** agent replies. `onRejected` is a local guide-error callback; absent a handler the View presents a local toast.

This wrapper intentionally inherits the host **Android View theme** (the same as `AyaCardView`), which may differ from a Material 3-only Compose theme. Real apps should validate both host theme layers, screen readers, IME and large font layouts.

## Existing Compose button or visual action

```kotlin
@Composable
fun HelpMenu(activity: Activity, question: String) {
    val launch = rememberAyaLauncher(
        activity = activity,
        action = remember {
            AyaComponentAction.Help(
                guideAsset = "aya-guide.md",
                screenName = "Settings",
                askQuestion = false // host already captured the question
            )
        }
    )
    Button(onClick = {
        when (val result = launch(question)) {
            is AyaBundledLaunchResult.Rejected -> {
                // Show an accessible host-owned local error, never silently bypass review.
            }
            else -> Unit // QuestionOpened or PreviewOpened: LOCAL UI, not external success.
        }
    }) { Text("Ask Your Agent") }
}
```

The same launcher can wrap `GenerateImage` or `Translation` action instances with genuine host-supported schemas/import paths. Do not claim `aya-component/v1` supports those tasks; its **declarative** manifest remains help-only. The host must not send private app state without meaningful review.

## Optional return-file import

AYA never listens for an AI response, reads an output directory, or automatically imports files. If the host supports the separate [Output Return & Import contract](../OUTPUT_RETURN_IMPORT.md), it must explicitly expose its own picker/validation action. The first Compose wrapper only demonstrates the help card. Future Compose parameters may surface the core card's optional import button once the independently developed output-return implementation is reconciled and tested; do not render a fake import action.

## Build and acceptance

```sh
gradle :aya-compose:assembleDebug :sample:assembleDebug
gradle :aya:publishReleasePublicationToStagingRepository :aya-compose:publishReleasePublicationToStagingRepository
gradle :sample:assembleDebug -Paya.consumePublished=true
```

The sample exposes **Home > Open Compose component demo** with a compact embedded card and a separately configured headless action. `sample/src/androidTest/java/dev/aya/sample/ComposeDemoTest.kt` exercises the real Card->review path in an Android emulator. Tested emulator runs must still be distinguished from manual TalkBack, small-screen, font scale and external recipient verification. The library has no inference backend or recipient credentials.
