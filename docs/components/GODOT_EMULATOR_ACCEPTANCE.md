# Godot Android runtime acceptance: synthetic emulator smoke

**Scope:** a disposable first-party Godot 4.5.1 Android debug APK built and independently inspected by the real [Godot exporter workflow](../../.github/workflows/godot-export.yml). This lane is a **separate runtime test** of the *same* APK, not a second expensive Gradle build or a receiving-assistant test.

## Exactly what is exercised

The CI exporter enables Android **x86-64** in the synthetic game's export preset, alongside its existing arm64 option. It bundles the test-only subclass `ci-host/runtime_probe_card.gd` as the scene root. That script delegates all UI construction to the reusable `AYACard` and, **on Android only**, waits for Godot's first completed render frame before checking the real AYA singleton, enabled Ask button, multiline input, and nonzero/intersecting viewport geometry. It prints synthetic-only, non-sensitive geometry dimensions/render driver and then a fixed `AYA_CI_GODOT_RUNTIME_READY` marker if those checks pass. This verifies **submitted-frame and layout geometry**, still not actual visible compositor pixels. Failures print `AYA_CI_GODOT_RUNTIME_FAIL` and raise a Godot error. No question content, private device state or attachment bytes are logged.

The downstream emulator job downloads the exact upstream APK artifact and runs on Android API 35 x86-64 using a lean AOSP/default image, a smaller Nexus 4 profile (instead of a Pixel 6-sized software framebuffer), four virtual CPU cores, and supported SwiftShader software graphics instead of the runner's deprecated `swiftshader_indirect` default. Earlier headless Vulkan/GLES captures logged `bad color buffer handle` and produced all-black frames, so this is an empirical CI renderer stabilization, not an AYA app requirement. It starts the actual exported package `dev.aya.godot.cihost` twice on a disposable emulator:

1. 412×892 pixels at 160 dpi and Android font scale 1.0.
2. 320×700 pixels at 160 dpi and Android font scale 2.0.

For each launch the script clears previous logcat content, starts the package through Android's public launcher, checks for a live process, and demands the **new** runtime marker. It refuses absent markers, a missing process, a test failure marker, or an app-specific Android fatal exception. It resets emulator settings after the test, even on error.

The script `tools/verify_godot_emulator_runtime.py` emits a bounded `aya-godot-emulator-smoke/v1` JSON artifact with the actual APK SHA-256 and observed test scenarios. Its negative-control unit tests cover missing APKs, failed installation, missing process, unrelated crashes, missing/failing markers and command failures.

## Visual evidence for layout review

The synthetic fixture reads its own **Godot ViewportTexture** after `frame_post_draw`, samples a 64×64 image and prints only fixed-format dark/light counts. These are cross-checked against Android's independent `screencap`. If the Godot viewport contains contrasting UI pixels while Android's capture is black, the diagnostic implicates Android composition/capture; if both are blank, investigate Godot rendering first. Missing or contradictory viewport diagnostics fail visual acceptance. Nothing logs image bytes or user content, and pixel counts alone do not certify accessibility.

The **synthetic CI host** anchors its AYA card to the full viewport and requests Godot's GL Compatibility renderer on Android to reduce Vulkan/software-GPU black-frame failures in headless emulation. These are disposable test-fixture settings, not requirements of the reusable AYA addon or adopting hosts. Developers must validate the renderer and layout of their own Godot project.


After the synthetic host reports an enabled native AYA card and a live Godot process, CI captures **two raw Android PNG screenshots** using `adb exec-out screencap -p`: the 412×892/100%-font scenario and the 320×700/200%-font scenario. Before launching, the disposable emulator's Android immersive-mode first-use confirmation is set to `confirmed` and read back; the prior value is restored afterward. This prevents the **"Viewing full screen"** system overlay, which was observed obscuring the entire AYA card in an earlier nominally successful capture. The verifier checks PNG chunk framing and CRC, dimensions (accepting orientation changes), size and SHA-256 before saving the files. The script also requires Android's **currently focused window** to belong to the synthetic Godot package before capture. An ANR, launcher, or system dialog fails the visual-evidence gate even when the native ready marker and live process are present. A second previously green run produced PNGs reading **"Pixel Launcher isn't responding"** instead of showing the AYA card. On screenshot failure, the job includes only bounded **synthetic fixture geometry/render-driver diagnostics** from the test log, without question content or private data. The fixture-specific decoder also checks for meaningful dark and bright pixel regions in bounded RGBA/RGB8 screenshots, retries for a first frame not yet presented by Vulkan, and fails after four black/blank captures. This was added after the foreground check passed and a third green native-startup run still produced **uniform black frames** (every pixel 0,0,0). The same limited runtime JSON records each screenshot's actual width, height, orientation, capture attempts and digest. The artifact `aya-godot-emulator-runtime-evidence` contains the JSON and both PNGs.

Screenshots are restricted to the disposable **first-party CI host**, which has no real user data or credentials, and are produced without selecting an AI target, opening an assistant, or sharing any attachment. They offer reproducible visual evidence for independent human/agent review of text clipping, button visibility, card density, keyboard affordances and scaling. The screenshot validator **does not assert those properties are good**, and screenshot dimensions and presence cannot certify TalkBack, tap targets, IME operation, contrast, accessibility, or usability. Record those verdicts only after inspecting the actual captures and testing interactions.

## Important boundaries

This demonstrates **first-party Android emulator boot, Godot scene construction, native plugin availability and local Ask-card readiness** only when the actual CI run succeeds. It cannot establish real screen-reader accessibility, actual on-screen button geometry and tapability, opening editable Android review, Copy/Share semantics, Android lifecycle across real rotation, compatibility with a physical device, actual receipt by ChatGPT/Claude/Gemini, or third-party project integration.

The 200% system font setting tests startup under that configuration. It does not prove text remains unclipped or readable. Real accessibility testing requires snapshots and interaction on actual UI surfaces, and separate physical-device validation.

The reusable Android and Godot modules remain unchanged by the fixture. The scene's test marker is not a production telemetry feature or an agent-response tracker.

## Reproducing

After a successful Godot exporter workflow, download the `aya-godot-4-5-real-export-debug` artifact and install it on a clean Android API 35 x86-64 emulator. From the repository root:

```sh
python3 -m unittest discover -s tools -p 'test_verify_godot_emulator_runtime.py'
python3 tools/verify_godot_emulator_runtime.py \
  --apk /path/to/aya-godot-host-debug.apk \
  --report /tmp/aya-godot-emulator-evidence.json \
  --screenshots-dir /tmp/aya-godot-screenshots
```

The helper uses `adb`, so the emulator must already be running and report `sys.boot_completed=1`. Inspect JSON outcomes and Godot logcat when failures occur. A valid file alone is insufficient: look for a successful emulator CI run for the exact source SHA.

The existing Godot/AYA UI, provider-compatibility, and public distribution release gates remain open until their own evidence is recorded.
