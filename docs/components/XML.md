# Android Studio XML layout-editor drop-in

**Status:** initial XML-inflatable View adapter under test in a dependent branch. This is an Android View XML component, not a published Android Studio IDE plugin or a standalone AI service.

`dev.aya.android.AyaXmlCardView` can be inserted in an Android XML screen. At runtime it delegates to the canonical `AyaCardView`, using the same installed-version-guarded AYA preview and user-chosen Android Sharesheet. No receiver detection, model credentials or result monitoring is added. Android Studio's layout editor shows an **inert preview** when no real Activity exists.

## Generate the XML layout element

```sh
python3 tools/component_codegen.py docs/components/examples/sample-help-card.json --format android-xml
```

The help-only component manifest now generates a real Android XML custom-view element with stable collision-resistant card/question IDs and escaped XML attributes. The output can be pasted into a layout file. Multi-line/backslash-containing text and ambiguous `@`/`?`-prefixed values fail instead of silently changing wording; those should be authored as verified Android string resources by the host. Action-only manifests must instead use a native button and the Kotlin action API.

## Paste into a host layout

```xml
<dev.aya.android.AyaXmlCardView
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:id="@+id/support_aya_card"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    app:ayaGuideAsset="aya-guide.md"
    app:ayaScreenName="Settings"
    app:ayaTitle="Ask Your Agent"
    app:ayaDescription="Ask about this screen and its actual controls."
    app:ayaAttachmentDisclosure="The app guide is offered as a text file; your AI may not accept it."
    app:ayaOutputInstructions="Read the answer and make changes in Settings yourself."
    app:ayaQuestionInputId="@+id/support_aya_question"
    app:ayaDensity="compact"
    app:ayaCornerRadius="12dp" />
```

The actual host must package `aya-guide.md` under `app/src/main/assets/`, with AYA-RAS frontmatter matching its *installed* Android app ID and version. Source-derived guide authoring and independent evaluation remain required. Do not copy the example's Settings instructions into an app without verifying its actual controls.

Available attributes: `ayaGuideAsset`, `ayaScreenName`, `ayaTitle`, `ayaDescription`, `ayaAttachmentDisclosure`, **required** `ayaOutputInstructions`, `ayaQuestionInputId` (strongly recommended for draft restoration), `ayaDensity` (`standard`/`compact`) and `ayaCornerRadius`.

The wrapper locates its parent Activity through ContextWrapper traversal. Without one, or when output-use instructions are missing, it displays an explanatory, non-actionable state and cannot share. The layout preview is never wired to a fake Activity. The host may install `onLocalRejected` to show local AYA guide errors; this does not observe assistant acceptance.

For apps using Compose instead of XML layouts, use [the separate Compose adapter](COMPOSE.md). For visual logic, pair your own host control with `AyaComponentAction.Help`. Neither path creates a reply callback.

## Testing

The first-party sample includes XML demo resources and Android instrumentation tests to verify successful inflation, stable question IDs and fail-closed missing instructions. These test-only resources are not a shipping sample screen. Additional layout-editor, TalkBack, font scaling, IME and real-recipient acceptance remain explicit manual gates.
