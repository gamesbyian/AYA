# Minimal two-app iOS LocalStorage File Provider reproduction

This disposable XcodeGen project is **independent of AYA's SDK**. It isolates the system Files picker callback boundary that remains red in [AYA #147](https://github.com/gamesbyian/AYA/pull/147).

**MinimalSource:** one SwiftUI view, FileManager writes either one malformed JSON document or the same seven deterministic fixture names/bytes as the AYA QA app. Its Info.plist sets UIFileSharingEnabled and LSSupportsOpeningDocumentsInPlace, exposing its own Documents in Files. No App Group, extension, cloud account, model, or cross-container read.

**MinimalConsumer:** another SwiftUI app and different sandbox. It presents the real SwiftUI fileImporter for UTType.item only after a user button tap. Its visible state changes to picker-opened, then callback-success or callback-error *only when the actual system completion arrives*. It never imports AYA or attempts to read the selected file.

## Build

Requires macOS with Xcode, iOS Simulator SDK and [XcodeGen](https://github.com/yonaskolb/XcodeGen). From integrations/apple/file-provider-minimal-repro, run XcodeGen generate for project.yml; build the MinimalSource and MinimalConsumer schemes from AYAFileProviderMinimalRepro.xcodeproj with xcodebuild, an iOS Simulator destination and CODE_SIGNING_ALLOWED=NO. CI checks both built app Info.plists rather than trusting source-only declarations. For physical devices, supply valid Apple development signing/provisioning and install both apps. **No physical-device test has been performed.**

## Reproduction with real user selection

1. Create or erase an iOS Simulator and install both apps. Launch MinimalSource, tap **Prepare only malformed JSON**, and verify “Prepared 1 verified document(s)”. Confirm that it appears in Files → On My iPhone → Minimal Files Source.
2. Launch MinimalConsumer and tap **Pick document**. Its state becomes picker-opened. In the genuine system Files UI, navigate to the source folder and tap aya-layout-invalid.json once. Record whether the picker dismisses and the visible Callbacks counter becomes 1. The callback itself is the tested contract: there is no JSON parsing in this consumer.
3. Delete/reinstall the source app (or reset the simulator) before changing the fixture population; do not stage both variants sequentially in the same container when interpreting this as a clean control.
4. On an independent clean simulator, stage **Prepare seven documents** and verify “Prepared 7 verified document(s)”. Select aya-layout-invalid.json, and then aya-layout-valid.json in a new picker invocation, using actual native Files taps.
5. Retain exact iOS and Xcode versions, source and consumer build SHAs, visible Files cells, native picker screenshots, callback state/count, and narrowly scoped File Provider system logs. If a visible item is tapped but the counter remains zero with the picker open, the failure is **before any AYA code or byte reading**. Do not confuse callback-error with no callback.
6. On a signed physical iPhone/iPad, repeat both clean one-file and seven-file variants. If failure reproduces, save a sysdiagnose and use [Apple Feedback Assistant](https://developer.apple.com/feedback-assistant/) with the two-app project, item identifiers and NSFileProviderError.noSuchItem (-1005) evidence.

**Evidence limits:** A passing standalone simulator reproduction of the missing callback would strongly isolate AYA's reader/parser from the failure, but would not independently establish an Apple defect on all iOS devices. Nor would it qualify the original seven-file native acceptance in #147. Never replace AYA's real importer with a direct source-sandbox URL or synthetic test injection.

The reproducer never reads private documents, retries failed system selections automatically, or accesses the other app's storage.
