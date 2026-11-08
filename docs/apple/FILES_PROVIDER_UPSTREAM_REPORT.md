# Reproducible iOS LocalStorage File Provider selection failure

**Report status:** Candidate for Apple Feedback Assistant, 2026-11-07. Not submitted to Apple. iOS AYA's independent seven-file native picker gate remains **red** in [draft PR #147](https://github.com/gamesbyian/AYA/pull/147). This document is the minimal reproducible technical account, not an assertion that Apple's OS is proven uniquely at fault.

## Environment and user-visible failure

- **Environment:** GitHub-hosted `macos-15` runners, Xcode 16.4, iOS 18.5 simulator; distinct independently installed `org.example.aya.shareqa` source and `org.example.ayalantern` importing applications, no App Group.
- Source application declares `UIFileSharingEnabled = YES` and `LSSupportsOpeningDocumentsInPlace = YES`; it stages seven `.json` documents in its own `Documents` via `FileManager`. The failing seven-file branch presents SwiftUI `.fileImporter(isPresented:allowedContentTypes:)` allowing the broad `UTType.item` (the separate minimal reproducer also uses `.item`). This is an intentionally broader picker than the sample's production JSON-only choice; the failure occurs before any host content validation.
- Using the **real native Files interface**, an XCTest driver navigates `On My iPhone → AYA Share QA`, finds the complete visible document cell and taps it. No direct sandbox read, fake callback or test-injected `AYAImportFile` occurs.
- Expected: the system supplies a security-scoped file URL to `.fileImporter` or a user-visible system error. Actual for certain document identities in seven-file inventory: native Files remains open; the importer callback has not fired, the host still reports `Import stage: picker-opened`, and even a second diagnostic tap does not complete selection. The consuming app's byte-limit reader and semantic validation have **not run**.
- Bounded simulator system logs contain `NSFileProviderErrorNonExistentItemIdentifier` / LocalStorage `-1005` and `DocumentManager failed opening URL (code 2)`. The latter signature also occurs in passing cases, so **do not use it alone to declare a failure**.

## Minimal A/B that separates filename identity from JSON contents

[Exact native differential run 42419092457](https://github.com/gamesbyian/AYA/actions/runs/42419092457) used **two fresh iOS 18.5 simulators**. Before tests, each verified all seven exact filenames and the expected bytes. It exchanged only the valid and malformed JSON payloads under these two filenames, leaving all other five file payloads, names, file sizes, published format and ordering unchanged.

| Real user selection of document | Contents after exchange | Installed native result | LocalStorage -1005 |
| --- | --- | --- | --- |
| `aya-layout-valid.json` | **Invalid** JSON layout (out-of-range columns) | **PASS:** real selection reaches host-owned visible rejection, no Apply | 0 |
| `aya-layout-invalid.json` | **Valid** JSON layout | **FAIL:** expected preview never appears | 1 |

The failure follows the second selected **filename/provider item**, even when its JSON bytes are valid. This disproves a deterministic explanation based solely on the consuming JSON schema. It does **not** isolate whether an item ID, filename, native grid interaction, provider record or simulator state is the specific cause.

## Source-process lifetime A/B

[Exact native differential run 42420270808](https://github.com/gamesbyian/AYA/actions/runs/42420270808) used two **fresh** simulators and identical seven-file inventory, asserting the exact bytes before selection. The sole changed condition was leaving the external fixture app alive/backgrounded or explicitly terminating it before the imported host opened Files.

| Source-app lifetime | Native invalid selection | LocalStorage -1005 | Post-diagnostic host stage |
| --- | --- | --- | --- |
| Backgrounded, not explicitly terminated | FAIL | 2 | `picker-opened` |
| Explicitly terminated | FAIL | 2 | `picker-opened` |

Source-app termination alone is therefore **not sufficient** to explain or fix the problem.

Earlier [six-case differential 42307760222](https://github.com/gamesbyian/AYA/actions/runs/42307760222) passed one-file valid and invalid, and seven-file valid journeys, but failed seven-file invalid variants with the same OS missing-ID signature. Other controls changed neighbour size, initial write mode, creation order, grid position, native List layout, double tap, long press, and a second iOS version; none has established a reliable seven-file negative acceptance. Historical results and screenshots are in [FILES_QA.md](FILES_QA.md).

## Steps for Apple / minimal reproduction

1. Build two **separate** iOS applications. App A exposes `Documents` through `UIFileSharingEnabled` and `LSSupportsOpeningDocumentsInPlace` and writes seven JSON files, including `aya-layout-valid.json` and `aya-layout-invalid.json`; app B declares a document picker for `UTType.item`, matching the actual failing seven-file host. This is intentionally distinct from a narrowly restricted JSON-only picker.
2. On a fresh iOS 18.5 simulator, install app A and write documents using its own process, confirm they appear in Files under `On My iPhone → App A`. Install app B.
3. In app B, invoke the native picker and select `aya-layout-valid.json`: inspect callback delivery.
4. Restart from fresh simulator with original inventory and select `aya-layout-invalid.json`: record whether the picker returns a URL, closes, or surfaces an error. Repeat after exchanging only the two payloads.
5. Collect a bounded File Provider / DocumentManager OS log, system picker screenshots, UI accessibility hierarchy, and the exact Xcode/iOS build. If the native callback fires, record that separately; the above bug applies only to failures **before callback delivery**.

**Expected system contract:** user selection of a visible, app-owned JSON document results in a delivered URL or an actionable error, independent of the document's semantic JSON contents.

**Actual symptom:** visible selectable cell can correspond to a stale/unresolvable LocalStorage provider identity and leave the document picker open without return/error.

The [draft PR's automated QA fixtures](https://github.com/gamesbyian/AYA/pull/147) retain the isolated reproduction scripts and system logs. An [AYA-free two-application minimal reproduction](../../integrations/apple/file-provider-minimal-repro/README.md), merged as [#166](https://github.com/gamesbyian/AYA/pull/166), also compiles on the native iOS Simulator SDK. It has **not yet demonstrated the picker failure**; its consumer merely displays real picker callback state and allows a clean single-file/seven-file manual or future physical-device comparison. CI artifacts expire after seven days; export relevant evidence for any Apple Feedback Assistant submission while available. Do not attach arbitrary personal documents, model prompts or private user data. These examples are fully synthetic.


## Relevant public prior art (not proof of the same root cause)

- An [Apple Developer Technical Support engineer](https://developer.apple.com/forums/thread/713814) has warned that the iOS Simulator does not reproduce all physical-device sandbox behavior. That supports **testing a real device next**, not treating every simulator failure as automatically harmless.
- [React Native Document Picker issue #246](https://github.com/react-native-documents/document-picker/issues/246) describes a visible file in the **iOS 13 Simulator** whose selection does nothing, while the reporter says an iOS 12 physical device worked. This is an analogous historic user-visible symptom, not direct evidence about iOS 18.5.
- [Nextcloud iOS issue #3261](https://github.com/nextcloud/ios/issues/3261) contains a File Provider log with error **FP -1005** during an iOS 18.5 Simulator investigation. That provider and operation differ, so the matching error code alone does not establish the same bug. It does show that the symptom family exists outside AYA's reader code.
- [Apple's document-picker documentation](https://developer.apple.com/documentation/uikit/uidocumentpickerviewcontroller) explicitly describes OS-provided security-scoped URLs and coordinated document access for external files. AYA's reader follows those post-selection responsibilities; the red case never receives a URL to process.

These sources motivate escalation and physical-device comparisons but do **not** replace the controlled local evidence or authorize relaxing the acceptance assertions.

## Severity, limitations and next decision

- **Release effect:** AYA's Files-return full seven-document native acceptance is not qualified. Do not mark the underlying importer production-proven or bypass the system to force green tests.
- **Not proven:** all physical devices fail; all File Providers fail; any specific Apple defect or AYA OS-version compatibility issue; true cancellation of an already executing accessor.
- **Next decisive evidence:** signed physical iPhone/iPad, independently installed source and importing host, same seven-file user-selected flow. If a physical device reproduces the failure, include its diagnostic logs in an Apple Feedback Assistant report. If a physical device passes, preserve simulator CI as an unresolved OS/harness reliability issue rather than relabeling it green.
- **Parallel validated functionality:** the text-paste fallback and alternate registered Open In pathway are merged. Genuine foreign-app-to-host **Open In succeeded in 2/2 installed iOS Simulator cases** at [run 42431460633](https://github.com/gamesbyian/AYA/actions/runs/42431460633), including explicit Apply and invalid rejection; signed real-device and real AI-app compatibility remain unqualified. Neither substitutes for the red `.fileImporter` gate.
