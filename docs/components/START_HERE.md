# Add AYA to an app: developer quickstart

This guide is written for someone who knows what they want their app to do but has **never installed an Android library or a visual-builder plugin**. AYA is an interaction convention: your app gives the user's chosen AI assistant a question and an accurate, version-matched explanation of the host app, with explicit human review. You may use the project's Unlicensed code or build equivalent behavior independently.

## 1. Choose the thing you are building with

| Your development tool | The AYA-shaped thing you can add now | Current limitation |
|---|---|---|
| Android Studio with ordinary XML layouts | An `AyaXmlCardView` element with labels and callbacks | Depends on the AYA Android module; not a one-click marketplace plugin |
| Android Studio with Kotlin Views | An `AyaCardView` card or `AyaComponentAction.Help` call | The host must bundle a real guide and integrate the library |
| Jetpack Compose | `AyaCard()` plus `rememberAyaLauncher()` | Separate `aya-compose` module; no public Maven release yet |
| Godot 4 Android | The AYA addon + a configurable card/node | Godot editor/addon source exists; Android export and app-specific asset packaging need host verification |
| Flutter | `AyaHelpCard` or `AyaFlutter.openHelp` | Source plugin and CI APK compile; unpublished core AAR means manual native dependency setup |
| FlutterFlow | Prepared Custom Widget / Action body templates | Templates are **not** a currently working published FlutterFlow widget |
| React Native / Expo | Android-only Expo Modules source adapter and React Native card | Source/API contract tests pass; unpublished AAR and real Expo APK acceptance pending in PR #42. No Expo Go support. |
| Unity, App Inventor | Design/roadmap only | No implemented or tested drop-in adapter to install |

See the [live snapshot of source and verification evidence](STATUS.md) before trying another toolchain.

## 2. Tell your coding agent what to do

If you're building with an AI coding agent, a reasonable prompt is:

> Add an Ask Your Agent option to my Android app using the AYA interaction convention. Read `AGENTS.md`, `docs/components/README.md` and `docs/components/START_HERE.md` in the AYA repository. Inspect the actual installed-app capabilities and version, create and independently audit the AYA-RAS reference, and integrate the correct guarded card or headless action. Make the copy and output-use instructions true of my app, not the fictional samples. Show me any missing product decisions, maintain privacy review and Copy fallback, and verify the Android build and negative-case tests. Never claim an external AI app received or used the guide without a dated real-device test.

The agent should ask the developer/owner targeted questions only when real product intent, feature truth, disclosure or import behavior is unclear. AYA itself does **not** ask an LLM to model or inspect the app at runtime.

## 3. Android Studio: generate the placement code

The quickest source-only entry point is the [safe component scaffolder](INSTALLER.md). Start with a truthful JSON manifest representing your app's actual help card and a real existing host project. The first command shows a plan without changing files:

```sh
python3 tools/component_scaffold.py \
  --project-dir /path/to/your-android-project \
  --module app \
  --manifest /path/to/your-aya-component.json \
  --mode android-xml
```

After you review the output paths, add `--apply` to write the new XML card. Or choose `--mode kotlin --package your.package.name` for a Kotlin wrapper, or `--mode compose --package your.package.name` for a Compose wrapper. The scaffolder deliberately **does not** guess your app's Gradle configuration, bundle an inaccurate guide, modify existing layouts, overwrite files, or send anything to an assistant.

Your app still needs to include the appropriate AYA module as an Android dependency and ship a UTF-8 **`aya-guide.md` raw Android APK asset** whose metadata matches that app's installed package ID and version. The generated card has to be placed on a real screen; it is not an app-wide overlay or automatic support system. Follow the [Android host guide](../INTEGRATION.md), [AYA-RAS authoring](../reference/INDEX.md) and [independent authoring/audits](../packet/README.md).

## 4. Visual and game engines

For Flutter, use [Flutter source integration](FLUTTER.md), remembering that the native Maven dependency is not publicly distributed yet. For FlutterFlow, the [prepared widget/action templates](FLUTTERFLOW.md) require both a published or otherwise resolved Android dependency and an actual editor/export test. For Godot 4, follow [the staged Android v2 addon instructions](GODOT.md). Do **not** assume putting `aya-guide.md` in a Godot `res://` package or Flutter `pubspec.yaml` makes it visible as an Android `Activity.assets` file.

The goal for visual builders is that an AYA card can become one more reusable component, and a headless AYA operation one more action-flow node. No engine adapter changes what the user must approve or gives the host automatic access to an AI reply.

## 5. What success looks like

The host shows a clearly labelled AYA card or action, explains what information is offered to the assistant, allows the user to type a question, and offers a **full editable local review** before Copy or Share. If the guide is missing or stale, no share opens. If the chosen assistant cannot accept the attachment, Copy/manual paste remains available. The host tells the user how to use any answer or manually import a saved result, if the app actually supports importing that result.

Opening Android's chooser means only that the user initiated Android sharing. It is never evidence that an AI app opened a new chat, read the attachment, answered, or saved a usable output.

See [acceptance testing](../TEST_PLAN.md), [card layout standard](../CARD_UI_STANDARD.md), and [release status](STATUS.md).
