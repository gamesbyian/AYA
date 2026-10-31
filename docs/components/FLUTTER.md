# Flutter and FlutterFlow AYA integration: source preview

Status: an Android-only Flutter plugin, Dart help card/headless API and Kotlin ActivityAware bridge are under independent CI in the AYA repository. Not on pub.dev or a FlutterFlow marketplace, and not yet proven by a complete Flutter Android APK export.

References:
- Flutter plugin authoring: https://docs.flutter.dev/packages-and-plugins/developing-packages
- Flutter platform channels: https://docs.flutter.dev/platform-integration/platform-channels
- FlutterFlow Custom Widgets and Actions: https://docs.flutterflow.io/concepts/custom-code/

## What is implemented

The source package lives at integrations/flutter/aya_flutter. AyaHelpCard presents host-authored description, attachment disclosure, explicit output-use instructions, optional text input, and a 48px Ask Your Agent control. It uses a local Flutter text draft with optional restoration and Android's existing AYA SDK version-checked privacy review. After review the user still selects Copy or Share. No background network call or AI model is part of AYA.

AyaFlutter.openHelp(guideAsset, screenName, question, askQuestion) is the headless action. Its result reports question_opened, review_opened or rejected as **local** UI states only. No result state means an assistant accepted an attachment, sent a response or produced an importable artifact. Unsupported platforms report a truthful local rejection.

The Kotlin AyaFlutterPlugin implements FlutterPlugin and ActivityAware, retaining activity only while attached, with the engine-scoped platform channel. It delegates to AyaComponentAction.Help, never a weaker manual API or custom share transport.

## Native Android dependency is a release blocker

The Android package currently requests dev.aya:aya-android:0.1.0-SNAPSHOT, which is **not a publicly available Maven dependency**. This repository can stage its AAR and POM using Gradle, but an external Flutter host needs an explicit, compatible repository for that staged publication. Therefore this source preview is NOT directly installable as a working FlutterFlow custom dependency. No build should silently omit the real native SDK or pretend it shipped.

The host must also independently author an exact-installed-version AYA-RAS guide, and bundle it as a raw Android APK asset that Activity.assets.open("aya-guide.md") can read. A file in Flutter pubspec assets or a Godot-like resource package is not proof of native APK asset availability.

## Flutter usage preview

Once the native artifact is properly resolved, import the source package as a path/git dependency, then create AyaHelpCard with truthful host description, attachment disclosure and outputInstructions. It provides an editable question, and launches the actual Android AYA review on explicit tap.

Alternatively call AyaFlutter.openHelp from an existing Flutter button after collecting the user's question. Show rejection locally and never claim success based on the returned review-opened status.

FlutterFlow supports Custom Actions and Custom Widgets with external package dependencies. The editor can host a future AYA widget and visual action node, but public dependency distribution, actual Android export, custom-code import and host-specific asset packaging are release gates, not delivered claims.

## Release gates

1. Flutter analyzer and mocked platform-channel tests pass: user click only, unknown status refusal, invalid guide path, honest local state.
2. Android Kotlin plugin is compiled in a real Flutter APK example with resolved AYA SDK AAR/POM and no manifest conflicts.
3. Exact installed-version guide packaged in the host APK and verified with Android Activity.assets; missing/stale guide refuses.
4. Device testing covers Activity attach/detach/rotation, multiple engines, keyboard, TalkBack, large fonts and narrow phones.
5. FlutterFlow Custom Widget and Custom Action are actually imported/exported with that dependency.
6. Receiving AI-app behavior remains independently unverified until dated device trials. No agent-reply monitoring or automatic file import is introduced.

Dart-only CI success cannot certify the native Android bridge.
