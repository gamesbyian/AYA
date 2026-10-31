# Unity Android AYA Help Bridge (source preview)

**Status:** An optional Android Kotlin AAR, an unpublished source-only Unity Package Manager folder, a host-configurable `MonoBehaviour` button/action and a custom Inspector. A native Gradle build and managed C# compilation against *explicit test-only Unity API stubs* are CI gates. No Unity Editor import, Unity game APK export, accessibility/device testing, or third-party assistant ingestion is yet verified. This is **not** a marketplace release.

## What a Unity developer can add

Use `integrations/unity/com.aya.handoff/` as an embedded *source* package. Attach `AyaUnityHelpButton` to a GameObject, configure its `guideAsset`, public screen name, user-visible description, attachment disclosure and manual answer-use instructions in the Inspector, and bind its `OpenHelp()` method to an existing UI Button. If your UI has a question field, connect the field's value-changed event to `SetQuestionText(string)` and enable `hostHasQuestionField`; otherwise AYA uses its own question composer.

This `MonoBehaviour` is an action, **not an automatically created card**. The host must render the description, disclosure, output-use guidance, and a visible, accessible button. The host owns fonts, gamepad, TalkBack, safe areas, viewport scaling, layout and input. On desktop/editor and unsupported platforms the action returns a local `rejected` event. The `onLocalStatus(status, reason)` UnityEvent is *local state only*, never a callback for the user's AI answer.

A developer can also call `AyaAndroidHelp.OpenHelp(questionOrNull, guideAsset, screenName, onLocalResult, askQuestion)` from C#, an existing button, or a Unity Visual Scripting **Invoke Member** node targeting the public `AyaUnityHelpButton.OpenHelp()` method. A custom Unity Visual Scripting Unit is **not implemented**; do not represent this public method as a certified custom graph node.

## Native dependency and APK identity

From this repository root:

```sh
gradle :aya-unity:stageUnityPlugin --no-daemon
```

The task stages canonical `aya` and `aya-unity` AARs in **separate** `aya-unity/build/unity-plugin/Plugins/Android/debug/` and `release/` folders. Copy **only the matched pair** for your chosen build variant into the consuming Unity project's `Assets/Plugins/Android/`; never copy both variants together (duplicate class definitions). This source-preview does not configure Unity's Android platform import selectors automatically. Unity host developers must supply required AndroidX/Kotlin runtime dependencies in their actual Android Gradle export, and verify that AYA's FileProvider/receiver manifest entries merge correctly. Unity's native Android build must package the source-derived, independently audited AYA-RAS `aya-guide.md` under the actual APK `assets/`, matching its *installed Android application ID and versionName*. Merely placing a Markdown file in Unity `Assets/` or StreamingAssets is **not** proof `Activity.assets.open()` can read the expected file. Never use another game's sample guide or bypass the version guard.

On Android, the C# wrapper obtains UnityPlayer's current Activity, dispatches the Kotlin call onto the Android UI thread, and posts the resulting local status to the captured Unity synchronization context. The native bridge calls only `AyaComponentAction.Help`, which invokes the existing guarded AYA SDK and never opens Android's recipient chooser before editable review. Android errors, missing Activity, invalid guide paths, non-Android exports, and unrecognized statuses fail closed; no backend, AI API token or automatic output retrieval is involved.

Unity's official [C# to Java plug-in documentation](https://docs.unity.cn/Manual/android-plugins-java-code-from-c-sharp.html) describes the AndroidJavaClass/currentActivity pattern. Unity [Visual Scripting](https://docs.unity.com/en-us/engine/6000.5/manual/packages-list/packages-all/pack-safe/com-unity-visualscripting) can invoke public C# APIs, but a source method's existence alone does not certify a version-specific graph editor interaction.

## Release acceptance still required

1. First-party Kotlin/Gradle AAR build; inspect staged artifacts and Java-visible `AyaUnityBridge.openHelp` method. C# source builds in two conditional-compilation lanes against tiny stand-in Unity API signatures as a syntax/contract smoke. This **does not** establish actual Unity Editor assembly compatibility or exported-player behavior.
2. Test an actual Unity 2022.3+ project with this UPM source folder and the exact matched AARs, AndroidX dependencies and host guide. Check both Mono and IL2CPP; Unity Player/Activity APIs may differ by Unity engine version.
3. Export and inspect the APK's exact guide bytes, Android installed identity/version, scoped FileProvider/receiver, and compiled bridge class; reject stale guide builds before opening local review.
4. Exercise real Android Activity lifecycle, cancellation, Copy fallback, multiple instances, duplicate taps, Unity main-thread callback, no recipient, IME, gamepad, 200% text, TalkBack and narrow portrait layouts.
5. Test dated assistant recipient versions separately, without inferring ingestion from Sharesheet launch. Generated files, if any, require a completely separate user-initiated host-owned importer.

**Design boundary:** AYA defines a reusable reviewed handoff; each Unity project supplies its own real guide and visible UI. No adopter-specific game features, paths or built-in ontology belong in the generic AYA Unity module.
