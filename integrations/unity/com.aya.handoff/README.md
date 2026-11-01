# AYA for Unity: Android help action (source preview)

This is a **source-only Unity Package Manager package**, intended as an optional
component or visual-workflow action for an existing Unity app. It does **not**
include the AYA native binaries or the app-specific guide. Installing this
package alone does not make its button work on Android.

## Import the C# source package

In Unity Package Manager choose **Add package from git URL** and enter:

```text
https://github.com/gamesbyian/AYA.git?path=/integrations/unity/com.aya.handoff
```

Unity's [Git dependency documentation](https://docs.unity.com/en-us/engine/6000.0/manual/packages-list/upm-git)
supports repository subfolders through `?path=`. Pin the Git revision in
production after testing rather than relying on a moving `main` branch.
**This exact AYA package installation has not yet been tested inside Unity.**

## Native Android requirements (mandatory)

1. Obtain a matching source checkout of AYA. Run
   `gradle :aya-unity:stageUnityPlugin --no-daemon`.
2. From `aya-unity/build/unity-plugin/Plugins/Android/`, choose **one** of
   `debug/` or `release/`. Copy its **two** AARs (`aya` and `aya-unity`)
   into the host Unity project's `Assets/Plugins/Android/`; never copy both
   variants or unrelated versions together.
3. Configure the consuming Android export's AndroidX/Kotlin runtime dependencies
   and preserve AYA's manifest components. Independently inspect the exported
   APK and verify its actual installed package/version.
4. Author and audit the **host application's own** AYA-RAS guide from the
   exact shipping UI and code. Bundle `aya-guide.md` in the Android APK
   **assets/** directory, not merely Unity StreamingAssets or the asset database.
   Rebuild whenever host UI or version changes.
5. Export and test on Android. Missing reference, wrong installed identity,
   missing Activity, unavailable native classes and non-Android platforms must
   reject without bypasses. User-edited AYA review, Copy/Share, accessibility
   and recipient ingestion require separate observation.

## Add an action in the Unity Inspector

Attach `AyaUnityHelpButton` to a GameObject. In the Inspector, provide the
real guide asset name, screen hint, **visible** description, attachment
disclosure, and instructions telling the user how to use any assistant answer.
Place that text visibly in **your own** game's UI. Link a Unity UI Button's
On Click handler to `AyaUnityHelpButton.OpenHelp()`.

For a game-owned question input, link its value-changed event to
`SetQuestionText(string)` and enable the host-question-field toggle.
Otherwise the default action opens AYA's own question composer. The only
result callback is `onLocalStatus(status, reason)`: `question_opened`,
`review_opened`, or `rejected`. It never reports model output or
completion. No automatic result import, AI account integration, backend,
hidden file scan or answer watcher is included.

A Unity Visual Scripting graph can invoke the public `OpenHelp()` method
through its standard Invoke Member capability.

When your Unity project also installs `com.unity.visualscripting` version
1.7 or newer, the **optional** `Aya.Handoff.VisualScripting` assembly adds a
real graph Unit called **AYA/Help > Request Reviewed Help**. Assign the
configured `AyaUnityHelpButton` component to its `card` input and connect
the `enter` trigger. Its `returned` output means only the component action
was invoked synchronously, **not** that the Android review opened, an AI
received the attachment or anything was generated. The host component's
`onLocalStatus` event remains the only local acknowledgement.

The custom Unit has source-level managed C# compilation checks using
**test-only** Unity and Visual Scripting API signatures. Actual Unity Editor
import, graph assembly compatibility and Unity-generated Android exports
remain unverified; pin/test the actual Visual Scripting package version before
using in a released game. The optional assembly is omitted if the Visual
Scripting package is absent and it does not force the package onto adopters.

See the [detailed Unity integration and release gates](https://github.com/gamesbyian/AYA/blob/main/docs/components/UNITY.md).
Native AAR builds and synthetic C# compilation checks are already in CI;
**Unity Editor import, Unity Android export and real device acceptance remain unverified.**
