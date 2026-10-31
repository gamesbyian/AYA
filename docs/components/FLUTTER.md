# Flutter and FlutterFlow AYA integration: source preview

Status (2026-10-31): the Android-only Flutter plugin, Dart card/action and Kotlin ActivityAware bridge have merged. Flutter analyze, widget/channel tests, and complete Flutter Android APK compilation with a staged native AAR passed [CI run 41233862629](https://github.com/gamesbyian/AYA/actions/runs/41233862629). Still not distributed through pub.dev or a public Maven repository; host guide/device/editor acceptance remains outstanding.

References:
- Flutter plugin authoring: https://docs.flutter.dev/packages-and-plugins/developing-packages
- Flutter platform channels: https://docs.flutter.dev/platform-integration/platform-channels
- FlutterFlow Custom Widgets and Actions: https://docs.flutterflow.io/concepts/custom-code/

## What is implemented

The source package lives at integrations/flutter/aya_flutter. AyaHelpCard presents host-authored description, attachment disclosure, explicit output-use instructions, optional text input, and a 48px Ask Your Agent control. It uses a local Flutter text draft with optional restoration and Android's existing AYA SDK version-checked privacy review. After review the user still selects Copy or Share. No background network call or AI model is part of AYA.

AyaFlutter.openHelp(guideAsset, screenName, question, askQuestion) is the headless action. Its result reports question_opened, review_opened or rejected as **local** UI states only. No result state means an assistant accepted an attachment, sent a response or produced an importable artifact. Unsupported platforms report a truthful local rejection.

The Kotlin AyaFlutterPlugin implements FlutterPlugin and ActivityAware, retaining activity only while attached, with the engine-scoped platform channel. It delegates to AyaComponentAction.Help, never a weaker manual API or custom share transport.

## Flutter 3.47 / Android Gradle 9 migration experiment

An independent, **non-shipping** [AGP 9 built-in Kotlin migration trial](../../integrations/flutter/migration/README.md) exists alongside this legacy source package. It copies the same Dart/Kotlin bridge into a disposable CI consumer, substitutes a candidate plugin Gradle script without applying KGP, and configures a real Flutter 3.47.9 Android host for AGP 9.0.1, Gradle 9.1.0 and `android.builtInKotlin=true`. The host still uses its independently verified exact-version AYA-RAS guide, staged SDK and APK checks.

The legacy `aya_flutter` package has **not** been retargeted or version-bumped. Flutter's official migration minimum (3.44/Dart 3.12) would exclude some previously declared consumers; only a separately reviewed new source-preview version should make that compatibility change. Until the trial and baseline both pass, do not advertise AGP 9 built-in Kotlin compatibility. See [Flutter plugin-author guidance](https://docs.flutter.dev/release/breaking-changes/migrate-to-built-in-kotlin/for-plugin-authors).

## Native Android dependency is a release blocker

The Android package currently requests dev.aya:aya-android:0.1.0-SNAPSHOT, which is **not a publicly available Maven dependency**. This repository can stage its AAR and POM using Gradle, but an external Flutter host needs an explicit, compatible repository for that staged publication. Therefore this source preview is NOT directly installable as a working FlutterFlow custom dependency. No build should silently omit the real native SDK or pretend it shipped.

The host must also independently author an exact-installed-version AYA-RAS guide, and bundle it as a raw Android APK asset that Activity.assets.open("aya-guide.md") can read. A file in Flutter pubspec assets or a Godot-like resource package is not proof of native APK asset availability.

## Flutter usage preview

Once the native artifact is properly resolved, import the source package as a path/git dependency, then create AyaHelpCard with truthful host description, attachment disclosure and outputInstructions. It provides an editable question, and launches the actual Android AYA review on explicit tap.

Alternatively call AyaFlutter.openHelp from an existing Flutter button after collecting the user's question. Show rejection locally and never claim success based on the returned review-opened status.

FlutterFlow supports Custom Actions and Custom Widgets with external package dependencies. The editor can host a future AYA widget and visual action node, but public dependency distribution, actual Android export, custom-code import and host-specific asset packaging are release gates, not delivered claims.

## Synthetic host APK packaging acceptance

The repository's Flutter CI now compiles a generated Android host with a **real `AyaHelpCard` on its screen** and an independent source-derived, exact-version `aya-guide.md` packed in native `android/app/src/main/assets/`. The guide's ID/version are pinned to the *generated host* (`com.example.aya_flutter_ci_host`, `1.0.0`), never copied blindly into an unrelated app.

The offline APK verifier checks that the final APK includes the exact reference bytes, that Android's compiled package identity/version match the reference metadata, and that the AYA FileProvider and share-selection receiver survive Android manifest merging. Negative tests reject missing/altered/duplicate guides, mismatched package/version and absent native components. This is packaging evidence, **not** proof of on-device dialog success, Android Sharesheet target compatibility, or any recipient reading the guide.

The fixture exists only at `integrations/flutter/aya_flutter/ci-host/` and should not be reused as a reference for third-party apps. Real hosts must build their own vetted guides.

## Independent host-reference evidence

The CI host includes a source-derived [inventory](../../integrations/flutter/aya_flutter/ci-host/inventory.json) and independent [held-out questions](../../integrations/flutter/aya_flutter/ci-host/questions.json) for its own demo screen. `tools/audit_reference.py --strict` checks structural coverage, guide statuses and source claims against that inventory. This remains a static consistency audit and is **not proof** that a receiving assistant answers the questions or that the UI is usable on every Android device.

## Release gates

1. Flutter analyzer and mocked platform-channel tests pass: user click only, unknown status refusal, invalid guide path, honest local state.
2. Android Kotlin plugin is compiled in a real Flutter APK example with resolved AYA SDK AAR/POM and no manifest conflicts.
3. Exact installed-version guide packaged in the host APK and verified with Android Activity.assets; missing/stale guide refuses.
4. Device testing covers Activity attach/detach/rotation, multiple engines, keyboard, TalkBack, large fonts and narrow phones.
5. FlutterFlow Custom Widget and Custom Action are actually imported/exported with that dependency.
6. Receiving AI-app behavior remains independently unverified until dated device trials. No agent-reply monitoring or automatic file import is introduced.

Dart-only CI success cannot certify the native Android bridge.
