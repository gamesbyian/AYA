# AYA for MIT App Inventor: experimental Rush 2 extension

This folder holds a **help-only, non-visible block extension source preview**. The target is MIT App Inventor v206's **built Android APK**, not its live AI Companion and not a Google Play or extension-gallery release. It demonstrates the *concept* of Ask Your Agent; using this code is optional.

The adapter delegates to the canonical Android `AyaComponentAction.Help` and returns only `LocalStatus(status, reason)`: `question_opened`, `review_opened` or `rejected`. It neither sends a question automatically to an AI nor monitors the answer.

## Build

From AYA's repository root, with Android SDK 35, Java 17, Gradle 8.9 and Rush CLI 2.1.2 installed:

```sh
gradle :aya:assembleDebug --no-daemon
mkdir -p integrations/app-inventor/aya-rush/deps
cp aya/build/outputs/aar/aya-debug.aar integrations/app-inventor/aya-rush/deps/
cd integrations/app-inventor/aya-rush
rush build
```

The [CI workflow](../../../.github/workflows/app-inventor.yml) builds from canonical AYA source and creates a disposable `.aix` artifact if the Rush v206 compiler succeeds. **Do not commit the locally generated AAR or AIX**, or claim an actual App Inventor consumer APK has passed unless it independently does. The binary depends on the current App Inventor runtime, Kotlin stdlib and AndroidX library behavior.

## Host developer instructions

1. In App Inventor, import the built AYA `.aix` under Extensions. The extension appears as a **non-visible component**; a builder cannot drag the extension itself into the screen.
2. Build a normal visible card yourself using a `VerticalArrangement`, explanatory `Label`s, a multiline `TextBox` (if questions should be prefilled) and an accessible `Button`. Render what the AYA card does, that the agent might ignore the guide attachment, and **how to use the agent's response manually**. Do not invent automatic imports, a reply callback or provider guarantees.
3. Generate the host's actual AYA-RAS guide **from the exact host project**, not a generic AYA example. It must have the installed Android package/version identity. App Inventor's app ID may depend on its creator/project identifiers: use the extension's `HostIdentity` block in a preliminary built APK or inspect the final APK. A wildcard or another app's reference is forbidden.
4. Add the exact guide Markdown to the project's media/assets using an actual filename that the built APK makes available to `Activity.assets.open()`. The `OpenHelp(guideAsset, screenName, question)` block checks a safe relative `.md` path, then the **native AYA library** checks actual contents, ID and version. An App Inventor media dropdown is not proof that the binary asset path is identical; inspect the actual APK.
5. Bind the visible Button's Click block to `AyaHelp.OpenHelp(...)`; optionally consume `LocalStatus` as **local** UI/rejection feedback only. Users must edit AYA's review and deliberately choose Copy/Share to contact a recipient.

This source preview intentionally excludes creative, translation, filesystem execution, other-project customization, hidden provider selection and agent-response watching.

## Critical unverified compatibility

- **AAR source/manifest integration:** Rush 2.1.2 supports Android AARs and merging their manifests, but a generated `.aix` alone does not prove the *App Inventor-generated APK* retains AYA's scoped `AyaFileProvider`, `.aya.files` authority, chooser receiver, metadata, raw app guide and compiled Kotlin classes.
- **AndroidX versions:** App Inventor bundles AndroidX Core 1.9.0, which takes precedence over newer dependencies. This adapter names the canonical core dependency for source compilation but marks AndroidX Core as `provided`. Independently verify every AYA call on a built APK, especially at runtime; do not assume newer classes are available. No Compose dependency is used.
- **Rush private-library relocation:** Kotlin/AYA native classes are repacked by Rush. Verify the actual class names referenced in the merged Android manifest and that provider URI handling and share intents still work. Do not mask a missing class with `-dontwarn`.
- **AI Companion:** AAR-based extensions are not loadable there according to Rush 2 documentation; build/install an Android APK for real tests.
- **Accessibility/recipient acceptance:** TalkBack, 200% text, 320×700, 412×892, keyboard/IME, cancellation, file URI grants, actual recipient app ingestion and output-use instructions need independent device evaluation.
- **No public release:** A GitHub Actions artifact is not a stable versioned App Inventor marketplace item or an independently installable production service.

Do not use the extension in a live app until a real App Inventor-built host passes the canonical native AYA APK checks and the device/recipient acceptance matrix.

## Upstream toolchain

Official [Rush 2 source](https://github.com/shreyashsaitwal/rush-cli), [configuration](https://github.com/shreyashsaitwal/rush-cli/blob/v2.1.2/docs/configuration.md), [dependency placement](https://github.com/shreyashsaitwal/rush-cli/blob/v2.1.2/docs/dependencies.md), [manifest rules](https://github.com/shreyashsaitwal/rush-cli/blob/v2.1.2/docs/manifest.md) and [writing extension blocks](https://github.com/shreyashsaitwal/rush-cli/blob/v2.1.2/docs/writing-extensions.md). The source and pinned toolchain are MIT App Inventor-specific. The architecture remains host-neutral.
