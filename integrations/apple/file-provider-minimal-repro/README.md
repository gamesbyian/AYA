# Minimal two-app iOS LocalStorage File Provider reproduction

This disposable XcodeGen project is **independent of AYA's SDK**. It isolates the system Files picker callback boundary that remains red in [AYA #147](https://github.com/gamesbyian/AYA/pull/147).

**MinimalSource:** one SwiftUI view, FileManager writes either one malformed JSON document or the same seven deterministic fixture names/bytes as the AYA QA app. Its Info.plist sets UIFileSharingEnabled and LSSupportsOpeningDocumentsInPlace, exposing its own Documents in Files. No App Group, extension, cloud account, model, or cross-container read.

**MinimalConsumer:** another SwiftUI app and different sandbox. It presents the real SwiftUI fileImporter for UTType.item only after a user button tap. Its visible state changes to picker-opened, then callback-success or callback-error *only when the actual system completion arrives*. It never imports AYA or attempts to read the selected file.

## Build

Requires macOS with Xcode, iOS Simulator SDK and [XcodeGen](https://github.com/yonaskolb/XcodeGen). From integrations/apple/file-provider-minimal-repro, run XcodeGen generate for project.yml; build the MinimalSource and MinimalConsumer schemes from AYAFileProviderMinimalRepro.xcodeproj with xcodebuild, an iOS Simulator destination and CODE_SIGNING_ALLOWED=NO. CI checks both built app Info.plists rather than trusting source-only declarations. For physical devices, supply valid Apple development signing/provisioning and install both apps. **No physical-device test has been performed.**

## Actual installed iOS Simulator A/B, 2026-11-08 UTC

[GitHub Actions native run 42433068046](https://github.com/gamesbyian/AYA/actions/runs/42433068046) built these **two independent apps** on two separately erased iPhone simulators with **Xcode 16.4 (16F6)** and used XCUITest to tap the **real system Files cell** `aya-layout-invalid.json`. No AYA SDK, JSON parsing, security-scoped snapshot reader, injected callback or direct cross-sandbox access is present in this receiver.

| Actual source inventory | Native selection result | Test duration |
| --- | --- | --- |
| Exactly 1 file (`aya-layout-invalid.json`) | **PASS**: actual Files picker returned the selected file through its callback | 29.438 s |
| Exactly 7 files (same target name and bytes, plus 6 neighbours) | **FAIL**: native selection left the receiving app at `State: picker-opened`, `Callbacks: 0` | 46.022 s |

Both jobs selected source-owned documents using the same explicit user action and test code, differing in the number of files the source had authored. The seven-file test reached and tapped an existing, hittable native Files cell before failing the subsequent callback assertion. The seven-file failure is **before any consumer file reading**. This reproduces the original #147 failure boundary without AYA code and removes its reader and host-schema parser from the possible immediate causes. The specific Apple component responsible remains unproven, and no physical-device result is implied.

**Independent OS log confirmation:** the passing one-file simulator contained **0 LocalStorage `FP -1005` errors**. The failing seven-file simulator logged **one `FP -1005`** from `com.apple.FileProvider.LocalStorage` approximately **0.756 seconds after** the Files item tap, reporting unresolved item `did=6`. This repeats the error family seen in AYA's original test under a receiving app that does not import AYA at all. The exact provider ID of the tapped document is still unproven; the timing alone is a strong association, not definitive mapping. The [small evidence record](../../../docs/apple/evidence/minimal-files-localstorage-20261108.json) preserves the timestamps and experiment versions.

The exact run retains native `.xcresult`, screenshots/accessibility diagnostics, test logs, and bounded File Provider OS logs for each matrix case as expiring GitHub Actions artifacts. The **seven-file XCTest remains intentionally red**; do not count the whole differential as a successful green workflow. The native differential workflow is **manual-only** after this bounded experiment to control macOS runner cost. The installed apps are available for physical-device reproduction when signed hardware can be tested.

## Reproduction with real user selection

1. Create or erase an iOS Simulator and install both apps. Launch MinimalSource, tap **Prepare only malformed JSON**, and verify “Prepared 1 verified document(s)”. Confirm that it appears in Files → On My iPhone → Minimal Files Source.
2. Launch MinimalConsumer and tap **Pick document**. Its state becomes picker-opened. In the genuine system Files UI, navigate to the source folder and tap aya-layout-invalid.json once. Record whether the picker dismisses and the visible Callbacks counter becomes 1. The callback itself is the tested contract: there is no JSON parsing in this consumer.
3. Delete/reinstall the source app (or reset the simulator) before changing the fixture population; do not stage both variants sequentially in the same container when interpreting this as a clean control.
4. On an independent clean simulator, stage **Prepare seven documents** and verify “Prepared 7 verified document(s)”. Select aya-layout-invalid.json, and then aya-layout-valid.json in a new picker invocation, using actual native Files taps.
5. Retain exact iOS and Xcode versions, source and consumer build SHAs, visible Files cells, native picker screenshots, callback state/count, and narrowly scoped File Provider system logs. If a visible item is tapped but the counter remains zero with the picker open, the failure is **before any AYA code or byte reading**. Do not confuse callback-error with no callback.
6. On a signed physical iPhone/iPad, repeat both clean one-file and seven-file variants. If failure reproduces, save a sysdiagnose and use [Apple Feedback Assistant](https://developer.apple.com/feedback-assistant/) with the two-app project, item identifiers and NSFileProviderError.noSuchItem (-1005) evidence.

**Evidence limits:** A passing standalone simulator reproduction of the missing callback would strongly isolate AYA's reader/parser from the failure, but would not independently establish an Apple defect on all iOS devices. Nor would it qualify the original seven-file native acceptance in #147. Never replace AYA's real importer with a direct source-sandbox URL or synthetic test injection.

The reproducer never reads private documents, retries failed system selections automatically, or accesses the other app's storage.
