# AYA Android host integration readiness

For an artwork-picker integration, additionally apply the [Creative Handoff acceptance contract](CREATIVE_HANDOFF.md) and [creative-specific reference authoring checklist](reference/CREATIVE_AUTHORING.md). A generated image is returned via the host's **normal import control**, never via an AYA callback. Actual third-party image generation remains an independently tested compatibility gate.

This document distinguishes **ready for first host integration** from **ready for public production release**.

## Optional translation readiness

The typed `Aya.launchTranslationBundled()` path requires the ordinary exact-version AYA-RAS guide **and** a second source-derived `aya-translation-kit.md`. See [module contract](translation/README.md) and [host authoring instructions](translation/AUTHORING.md). A host must already have normal language selection, file import, independent schema/ICU/semantic validation and live fallback before offering an AYA "Make a language pack" card. AYA does not supply the host importer or monitor agent output. The fictional ParcelPad schema is example-only. Device/recipient acceptance and a real host translation round trip remain **UNVERIFIED**.

## Current implementation contract

- Stable concept: Android app packages an AYA-RAS guide; user launches an editable privacy preview; Android shares one UTF-8 document with a chosen recipient.
- Preferred Kotlin API: `Aya.launchBundled(activity, guideAsset="aya-guide.md", screenName?, question?, askQuestion=true)`. Question-first mode is the default; when a host already contains a text field, use `question=userText, askQuestion=false` to avoid duplicate entry.
- Version guard: the asset must have an AYA-RAS v1 frontmatter, `app_id` matching the installed Android package, and **both** `app_version_min` and `app_version_max` exactly matching the installed APK `versionName`. Cross-version ranges are deliberately rejected by this API until tested version-selection rules exist.
- Error return: `AyaBundledLaunchResult.Rejected(reason)`; the host decides how to show it. `QuestionOpened` indicates AYA showed its local question editor; `PreviewOpened` only signals local review (`askQuestion=false`). **Neither** establishes recipient ingestion.
- Legacy/manual API: `Aya.launch(activity, AyaRequest(...))` still exists for deliberately constructed guides, but **does not** enforce version identity. Prefer guarded API for integration.
- Delivery: `ACTION_SEND`/FileProvider with read grant, `EXTRA_STREAM` containing the complete reviewed guide/question and `EXTRA_TEXT` derived from the final user-approved question; no provider-specific deep link or automatic chat initiation.

## Adoption checklist

1. **Product reference.** Build real app inventory, AYA-RAS guide and gold question set from shipped code/tests and released APK. Track UNKNOWNs and destructive behavior accurately. Run linter/auditor with strict flags.
2. **Versioned assets.** Bundle exactly one `app/src/main/assets/aya-guide.md` covering the current app ID and exact `versionName`; generate one asset per flavor/version as needed. Do not bundle an incompatible reference or fake a version match.
3. **Dependency.** Embed source module or consume a Maven AAR with its transitive dependencies. Require `android.useAndroidX=true`, JDK 17, supported Gradle/AGP and minSdk 23 or higher. See [integration instructions](INTEGRATION.md).
4. **Host hook.** Add a clear "Ask your agent" entry point to relevant screens. Supply an optional current screen label and neutral question; exclude private details by default.
5. **Failure UX.** Handle `Rejected` gracefully without offering a stale fallback. Do not auto-export a different guide. AYA's Copy action is a fallback for recipient app incompatibility, not for invalid guide identity.
6. **Privacy.** Review consent text, attachment scope, clipboard exposure and host-provided question/context; ensure no credentials, private URLs, full logs or user identifiers are supplied implicitly.
7. **Build smoke.** Compile host against source module **and** independently resolved Maven AAR as applicable; check merged FileProvider authority `${applicationId}.aya.files` and URI subtree.
8. **Device.** Instrumented tests for URI grants, UTF-8 and provider containment; manual TalkBack/font scale/keyboard, navigation and rotation. Then physically test each intended assistant and record versioned outcomes.
9. **Quality.** Measure realistic assistant responses with held-out cases, especially unknown/unsupported features, high-stakes operations and error troubleshooting.
10. **Release.** Choose license/distribution, stable API/versioning/retention policy, and publish only compatibility claims supported by recipient-specific evidence.

## Current gates

| Gate | State |
| --- | --- |
| Reference authoring standard, independent inventory, question quality protocol | Implemented |
| Guarded APK guide selection | Implemented; CI tests required |
| Self-contained sample host | Implemented; CI acceptance required |
| Android module + staging Maven AAR consumption | Configured; CI acceptance required |
| Intent/provider instrumentation source tests | Implemented; emulator/device execution required |
| User-accessible privacy preview | Implemented; manual accessibility/lifecycle acceptance required |
| Android receiver apps (ChatGPT, Claude) | **UNVERIFIED** |
| Stable public distribution and third-party license | **NOT DECIDED** |

## Evidence and limits

Build success validates compilation and packaged integration, not source-guide truth or recipient compatibility. An Android Sharesheet successfully opening also does **not** prove a new conversation was created, the attachment was read, or the question was submitted. A real application can begin integration with this baseline and keep unverified behavior behind an explicit experimental/help label until acceptance.

## Suggested first host selection

Choose one app with a known, reproducible public release and reviewable UI. Produce its reference independently; prove version matching and error handling before adding optional sensitive context. Do not spread AYA to multiple apps until one real app has completed the end-to-end acceptance matrix.
