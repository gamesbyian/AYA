# Godot Android v2 AYA drop-in (prototype)

Status: prototype Kotlin bridge and Godot editor addon under independent CI, including a pinned 4.5.1 headless editor parse and no-Android smoke check. This is NOT a tested Godot APK export, verified recipient handoff, published Asset Library plugin or generally installable addon yet. No binary AARs are committed.

The design follows the official Godot Android v2 plugin documentation (https://docs.godotengine.org/en/stable/tutorials/platform/android/android_plugin.html) and the Godot Android Plugin Template (https://github.com/m4gr3d/Godot-Android-Plugin-Template). It targets Godot 4.2+ v2 architecture and compiles against Godot Android library 4.5.1.stable.

## Implementation

The optional aya-godot Gradle Android library supplies a GodotPlugin whose exposed openHelp(...) method calls the canonical, installed-version-checked AyaComponentAction.Help on Android's UI thread. Nothing is sent before the user's editable local privacy review and deliberate Copy/Share.

The source addon in integrations/godot/addons/AYA contains an EditorExportPlugin and a tool-mode scene component. The AYACard script can be attached to a VBoxContainer; inspector fields expose app-specific guide path, screen hint, task description, attachment disclosure, output-use instructions and optional multiline, Unicode-preserving question in a host-scroll-owned TextEdit. The field grows with its contents instead of adding an internal scrollbar. The button is disabled in the editor or when the Android singleton is absent. No mock-success state is shown.

The sole emitted signal aya_local_status has three strings: request ID, local state (question_opened, review_opened, rejected) and local reason. Each card filters by request ID. This signal does NOT indicate assistant receipt, processing, output generation or import. No model API, external app detection, filesystem watch or network service is introduced.

## Build

From the AYA repository root:

    gradle :aya-godot:stageGodotAddon --no-daemon

The Gradle task builds both the plugin and the core SDK AARs for debug/release, then stages the addon at aya-godot/build/godot-addon/AYA. The editor export script declares both AARs and the core AndroidX/Kotlin dependencies. Keep the SDK binary and adapter versions together; do not replace one AAR independently.

## Godot host installation (requires actual verification)

1. Copy the complete staged AYA directory to the game project under res://addons/AYA, enable the addon under Godot Project Settings > Plugins.
2. Install a matching Godot Android Gradle build template and enable Gradle Build for the Android export preset.
3. Create a VBoxContainer node and attach res://addons/AYA/aya_card.gd, then replace every example label with the game's actual release-backed behaviour and instructions. Alternatively wire a user button directly to the Android AYA singleton.
4. Build and independently audit a real AYA-RAS guide for that game's actual installed Android application ID and versionName. This guide must be packaged into the Android APK assets so Activity.assets.open("aya-guide.md") can read it. A file merely living in Godot res:// or the PCK is NOT proven to work.
5. Inspect the generated APK for the AYA guide asset, both AARs' merged manifests and the scoped FileProvider. Then validate an exact-version guide opens local review and a missing/stale one refuses. Test Copy fallback and actual recipient behaviour separately.

This prototype does not silently edit an unknown Godot build template or invent a universal way to put game-specific documents into Android assets. If the host uses a different asset path, the host developer must confirm and document it. Failing that gate blocks release.

## Binary bridge packaging check

The shared game-engine Android packaging workflow (`.github/workflows/unity-apk.yml`) injects both optional Unity and Godot Gradle library dependencies into an existing **first-party synthetic Android sample** and compiles one actual debug APK. It inspects the installed package/version, raw exact-version guide bytes, scoped AYA FileProvider and receiver, defined DEX classes for both bridges, and the exact `<application><meta-data>` Godot v2 registration pair `org.godotengine.plugin.v2.AYA = dev.aya.godot.AyaGodotPlugin`. The generic `tools/verify_android_manifest_metadata.py` parser rejects unrelated attributes, duplicate metadata registration and missing/mismatched values.

This is **native Android library merge evidence**, not proof that Godot's `EditorExportPlugin` installed AARs, that Godot generated an APK, or that the Godot singleton runs on an actual Android device. Those acceptance gates remain open, including proper host-specific guide installation in the Android Gradle export.

## Acceptance before release

- Android Gradle module compiles and staged addon contains all four debug/release AARs and editor scripts.
- Headless Godot 4.5.1 parser and scene smoke must verify multiline question input, Unicode/newline draft preservation, missing output-use instructions, and non-Android rejection (new checks pending CI).
- Manual GUI editor import is still required for Godot 4.5 and 4.6: preview and inspector should render, scripts should parse, editor should not initiate a handoff, and Android export registration should load.
- Exported APK has the correct AYA-RAS guide as a raw APK asset and matches installed app version. A missing/incorrect guide is rejected without fallback.
- Multi-card request ID isolation, dismissal, rotation, unavailable engine singleton and no share-target behaviour are tested without claiming AI ingestion.
- Large fonts, gamepad focus, screen readers, narrow phones, and IME behaviour satisfy the host's UX/accessibility requirements.
- No automatic output retrieval or remote execution. File imports remain host-owned and independently validated.

Current Godot adapter is intentionally help-only; creative, translation, filesystem and output-return handoffs require separately verified host-specific contracts before exposure.
