# AYA Expo Modules Android bridge (source preview)

**Status:** Android-only typed Expo Modules API/Kotlin bridge and React Native card merged as source previews in PR #41. An actual generated Expo Android host APK is being verified separately in PR #42; do not claim successful packaging until those checks pass. TypeScript compiler and mocked local-status checks are CI gates. This is not yet a published npm module, tested Expo Android APK, validated Expo editor export, or physical-device acceptance.

## API and visible card

The host can call `openAyaHelp({question, screenName, guideAsset, askQuestion})`. A headless call with no `question` argument defaults to the native AYA question composer; when the host supplies `question` (even an intentionally empty host-owned field), it defaults to direct editable review to avoid duplicate question boxes. `askQuestion` explicitly overrides the default. The action returns only `question_opened`, `review_opened` or `rejected`. These are **local** results and do not indicate that an AI recipient accepted any content. The native Kotlin `AyaExpoModule` invokes the existing exact-version guarded `AyaComponentAction.Help` on the foreground Android Activity. No alternative share transport, AI provider, reply callback, hidden data collection or importer exists.

```tsx
import { AyaHelpCard, openAyaHelp } from 'aya-expo';

// Existing button: host already captured the question.
const result = await openAyaHelp({question: userTypedQuestion, screenName: 'Support'});
if (result.status === 'rejected') showLocalError(result.reason);

// Visible React Native card with verified host-specific copy:
<AyaHelpCard
  description="Ask about this version's actual settings."
  attachmentDisclosure="The app guide is offered as a text file; your AI app may ignore it."
  outputInstructions="Read the answer and apply useful advice manually in Settings."
  screenName="Settings"
/>
```

The card requires all three host-authored messages, supports a multiline question, and uses accessible, 48px-minimum action controls. It leaves vertical scrolling to the host. The text draft is local to the mounted card, and navigation/process recreation requires separate host testing. A host's own file importer must remain separately validated and explicitly user-controlled.

## Native Android and asset packaging

The module registers `Name("AyaExpo")` through `expo-module.config.json`. Its `AsyncFunction("openHelp")` dispatches to Android's main thread only with an active Activity, and returns local failure for detached/invalid host state. The Android Gradle module has an explicit native dependency `dev.aya:aya-android`, by default an unpublished `0.1.0-SNAPSHOT`. A real host must provide a pinned matching Maven repository and the actual merged FileProvider/receiver; this preview does not silently download a native binary.

Pair the native module with the independent [Expo guide prebuild helper](EXPO.md). Every adopting app must author an audited AYA-RAS guide from its exact installed version and put it in native `android/app/src/main/assets/aya-guide.md`. The host's `android.package` and installed `versionName` must match its guide. Never reuse a sample guide across apps.

The package is intentionally private/unpublished. Follow Expo's [native module setup](https://docs.expo.dev/modules/get-started/) and [Modules API](https://docs.expo.dev/modules/module-api/). AYA cannot run in ordinary Expo Go, on iOS or on web. Use a custom Android development build or actual APK.

## Release gates

1. Pass TypeScript compiler and mocked status/validation tests against a pinned Expo SDK/React Native baseline.
2. Build a real Expo Android APK with a matching staged version of the AYA core SDK and exact host guide; verify merged native manifest and APK bytes.
3. Test Activity detach/reattach, rotation, backgrounding, no recipient, Copy fallback, 200% font scaling, TalkBack and narrow phones on real devices.
4. Test dated selected AI receivers separately. Opening local review is never evidence of ingestion, answer generation or import.
