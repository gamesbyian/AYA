# AYA in FlutterFlow: prepared Custom Widget and Custom Action templates

**Status:** prototype / integration instructions, not a certified or published FlutterFlow component. This reference intentionally has no screenshot-based acceptance claim. The underlying Android-only `aya_flutter` plugin source was merged via [AYA PR #29](https://github.com/gamesbyian/AYA/pull/29) and an actual Flutter Android APK was compiled in CI. Its native Maven dependency has **not** been published to a public artifact repository. Do not promise a one-click FlutterFlow install until a full exported Android app and real editor workflow have both been verified.

FlutterFlow provides *Custom Widgets* that developers can place in its visual widget tree, plus *Custom Actions* that run as steps in visual Action Flows. It also supports custom package dependencies, including Git-hosted unpublished packages. See FlutterFlow's [Custom Code](https://docs.flutterflow.io/concepts/custom-code/), [Custom Widgets](https://docs.flutterflow.io/concepts/custom-code/custom-widgets/) and [Custom Actions](https://docs.flutterflow.io/concepts/custom-code/custom-actions/) documentation.

## First: the native distribution blocker

Do **not** add the plugin to an actual FlutterFlow production project yet unless its Android `dev.aya:aya-android` AAR/POM can be resolved in the exported Android build. At present the plugin is source-preview-only. A Git dependency on `aya_flutter` alone does **not** make its unpublished Android AAR available. FlutterFlow's Custom Code editor may successfully compile Dart while the exported Android APK fails.

A future properly versioned public Maven AAR (and a public, pinned Flutter package) or an explicitly tested host-side source setup is required. The host must also bundle the right `aya-guide.md` as an **Android APK asset** matched to its actual application ID/version. Flutter's `pubspec.yaml` asset declaration alone is not a substitute. These are release gates, not buttons in the FlutterFlow editor.

## What the prepared templates accomplish

- [Visual AYA help card](../../integrations/flutter/flutterflow/aya_help_widget.dart): use a Custom Widget named `AyaFlutterFlowHelpWidget`. It accepts `width`, `height`, `description`, `attachmentDisclosure`, `outputInstructions` and optional `screenName`. It wraps `AyaHelpCard`, retaining the user review, output-use guidance and host theme. Its height is a **minimum**, allowing text to expand at large font sizes.
- [Headless AYA action](../../integrations/flutter/flutterflow/aya_open_help_action.dart): use a Custom Action named `ayaFlutterFlowOpenHelp` with `question` and optional `screenName`. It returns a simple status string: `question_opened`, `review_opened` or `rejected`.
- Both invoke the existing Flutter plugin and guarded native Android review, never a separate provider transport. A returned status does **not** prove the user shared the document, that another AI app ingested it, or that an answer was produced.

These are **body templates**. When creating snippets in FlutterFlow, keep its automatically generated imports/boilerplate and add `import 'package:aya_flutter/aya_flutter.dart';` in the editable imports area. Preserve the function/class and parameter names in the right-hand Custom Code configuration. Do not paste these files over the whole generated editor header.

## Developer workflow

1. Complete AYA-AUF host modelling, director clarification, exact-version AYA-RAS reference, independent inventory and held-out question evaluation. Do not infer shipping controls from a design mockup.
2. Once the native package distribution gate is solved, add the compatible `aya_flutter` dependency in FlutterFlow's project dependency settings. Use a pinned version/commit; avoid a mutable branch for production apps.
3. Add the visual card to the Custom Code panel, declare the documented parameters, and bind real host-specific description, reference disclosure and answer-use instructions. Where the host cannot honestly say how answers should be used, AYA should remain disabled.
4. Alternatively add the Custom Action to an existing button's Action Flow. The host must already capture its question, and should visibly explain the guide and output-use process near that trigger. Branch on the local status, displaying a non-success error state for `rejected`.
5. Keep FlutterFlow's automatic snippet imports, compile its Custom Code, inspect the generated Android manifest/build, package the APK-level guide, and test the installed APK. Verify no duplicate question composer, no silent share, and working Copy fallback.
6. Test 320 dp portrait screens, 200% fonts, TalkBack, focus/IME behavior, rotation, missing guide, chooser cancellation, and no compatible AI app. Confirm receiver ingestion only through dated manual tests, not an editor preview.

## What these templates deliberately do not provide

No marketplace item, native Android dependency distribution, real editor compile assertion, account credentials, automatic conversation creation, runtime private state capture, response callbacks, agent-output watcher, file importer or background filesystem operations. The host controls any optional manual import and must independently validate generated files.

Keep AYA's [platform compatibility rules](README.md), [Flutter plugin source-preview notes](FLUTTER.md) and [roadmap](ROADMAP.md) in view. The existence of a widget-shaped Dart file must not be interpreted as proof of working FlutterFlow export.
