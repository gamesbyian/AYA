# Godot 4.5.1 Android exporter acceptance

**Scope:** first-party synthetic test game under `integrations/godot/`. This gate is intended to exercise a **real Godot-editor-produced Android Gradle APK**, beyond the shared Kotlin/Android sample packaging check. Until CI has succeeded for the exact changeset, no exported APK is claimed.

## Developer workflow

1. Build both native AYA AARs and the Godot Android v2 bridge with `gradle :aya-godot:stageGodotAddon`.
2. Copy the complete staged `aya-godot/build/godot-addon/AYA` directory under the host game's `res://addons/AYA/`, enabling the editor addon. Only one matching debug or release AAR pair must be included in a given export.
3. Install **matching Godot 4.5.1** official Android build templates, including `android_source.zip`, and the Android SDK/NDK required for Godot's Gradle 4.5 template. Use the host's own project-specific `export_presets.cfg`; enable `gradle_build/use_gradle_build=true`.
4. After the Godot Android Gradle build template has created `android/build/build.gradle`, run:

   ```sh
   python3 tools/stage_godot_android_guide.py \
     --project integrations/godot \
     --guide integrations/godot/ci-host/aya-guide.md
   python3 tools/stage_godot_android_guide.py \
     --project integrations/godot \
     --guide integrations/godot/ci-host/aya-guide.md --check
   ```

   This **particular** guide and preset are valid only for `dev.aya.godot.cihost@1.0.0`. A real developer must independently generate an AYA-RAS guide from their own host and installed version, then audit that guide. The helper rejects wrong ID/version, missing Android Gradle templates, unsupported API 23 hosts, symlinked destinations and foreign-file overwrites. The Android 4.5 template's `assets` source set maps `android/build/assets/aya-guide.md` to the actual APK `assets/aya-guide.md`; moving a guide into `res://` or the PCK is insufficient. Godot 4.6 changed its Gradle source layout, so **this specific staging helper is 4.5-only**.
5. Run the pinned Godot editor's `--headless --path integrations/godot --export-debug Android ...apk`, with the Android SDK path and disposable debug signing configured. Inspect the **final** APK via `tools/verify_flutter_host_apk.py` (its generic APK identity/guide/manifest validator), `tools/verify_android_adapter_apk.py`, `tools/verify_android_manifest_metadata.py` and `tools/verify_android_manifest_providers.py`. The last check requires **both** independent `dev.aya.android.AyaFileProvider` (`dev.aya.godot.cihost.aya.files`) and Godot's `androidx.core.content.FileProvider` (`dev.aya.godot.cihost.fileprovider`) to survive with their own non-exported URI-grant flags and scoped path metadata. A build-only success does not establish complete APK integration.

## CI and integrity

`.github/workflows/godot-export.yml` pins Godot 4.5.1 editor and export-template bytes to the SHA-256 digests published by the official `godotengine/godot-builds` 4.5.1 release, and pins compatible Android build dependencies. The official template archive is approximately 1.36 GB, so extraction of only the Android templates is cached under a content-addressed key. The first run must fetch and validate the complete official archive; no unverified mirror or lighter surrogate counts as Godot's exporter.

Godot 4.5's `platform/android/export/export_plugin.cpp` treats missing ETC2/ASTC texture imports as a project configuration failure, **without filling in the diagnostic text**. On Linux headless CI this previously appeared as a blank "Cannot export project ... due to configuration errors" message. The fixture now explicitly enables `textures/vram_compression/import_etc2_astc=true` in `project.godot`, checked by the export-workflow regression test. This is a documented Android exporter prerequisite, not a bypass of application or version validation.

The fixture's own independently authored guide inventory and gold questions are at `integrations/godot/ci-host/` and must pass the same strict AYA-RAS lint and reference audit as any other host. This demonstrates host-specific documentation **for the synthetic CI scene**, not for a real adopting game.

The original actual-engine export exposed an SDK-level manifest collision: Godot and AYA both declared the generic AndroidX FileProvider class. The correct [AYA provider identity fix](../../aya/src/main/java/dev/aya/android/AyaFileProvider.kt) gives AYA its own concrete subclass, preserving the exact `.aya.files` authority, while Android safely retains Godot's own provider. It is forbidden to suppress the collision using `tools:replace` on provider authorities or paths, which would break one provider. The final binary verifier checks both providers independently.

An exported Godot APK, if this exact CI succeeds, establishes **S2 first-party actual-engine packaging** for this setup: guide, merged AYA FileProvider/receiver, native v2 plugin registration and compiled DEX type. It does **not** establish S3 independently authored adopter, S4 physical Android interaction/accessibility, S5 actual assistant receipt, or S6 public installable distribution.

## Independent acceptance still necessary

For an actual Godot host, repeat import/export using a clean project and project-authored guide. Exercise a live Android Activity, desktop/editor/non-Android rejection, long Unicode/multiline questions, repeated taps and multiple card instances, Cancel/Copy/Share, no receiver, stale guide, TalkBack, large fonts, IME and gamepad control. The `aya_local_status` signal means only local UI state and never confirms the recipient read an attachment. All agent-generated outputs remain untrusted and manually handled by the host; no automatic result-return path exists.
