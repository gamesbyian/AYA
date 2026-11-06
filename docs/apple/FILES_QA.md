# Native iOS Files return: independent local-provider acceptance

**Status (2026-11-06): [Consolidated draft PR #147](https://github.com/gamesbyian/AYA/pull/147) is blocked on genuine native Files-return acceptance.** The latest [Xcode 16.4 / iOS 18.5 rerun 42199158594](https://github.com/gamesbyian/AYA/actions/runs/42199158594) passed **9/17 installed iPhone tests**: eight failed before receiving a selected Files URL, including the new list-view diagnostic. The [Xcode 26.6 / iOS 26.5 comparison 42192636283](https://github.com/gamesbyian/AYA/actions/runs/42192636283) passed 0/2 selected Files tests. All four support workflows passed. QA app-owned document staging, alternate UIKit copy-mode, long-press, double-tap, list view and content/position controls have not resolved this. The original first-party valid import and explicit Apply/Cancel journey still passes on iOS 18.5. **Do not merge or close #139 until exact-head acceptance qualifies its replacement.** The fictional cross-app fixture is separate from [outbound iOS QA receiver](RECEIVER_QA.md).

## Fresh single-document simulator result (2026-11-06)

The [isolation workflow run 42234704265](https://github.com/gamesbyian/AYA/actions/runs/42234704265) created two **separate new iOS 18.5 simulators**. Each independently installed the QA app, let it write **exactly one** synthetic file into its own Documents via FileManager, and used the real Lantern host/system Files importer.

- **Malformed JSON case: passed** its full installed-app rejection test. That test asserts the host-owned visible error, absence of Apply, dismissal, and unchanged state. The bound 4-minute LocalStorage log recorded **zero** unresolved local-storage item IDs, indexing hard timeouts or helper communication failures.
- **Valid JSON case: inconclusive, navigation-harness error.** XCTest threw `Failed to tap "Browse" Button: Find single matching element. Multiple matching elements found` in the common navigator, before reaching document selection. Its provider log likewise had zero LocalStorage errors in the named categories. A test failure caused by ambiguous navigation must never be counted as a valid document rejection or import failure.
- [Commit `27e51b2`](https://github.com/gamesbyian/AYA/commit/27e51b28d6358606f0135c4afa32a1ef47ddc96d) resolves the specific XCTest ambiguity by selecting the lowest visible native Files `Browse` control. A new exact-head isolation run must qualify **both** valid and invalid cases before considering this evidence conclusive.

**Interpretation:** the genuine invalid-file journey can pass end-to-end on a clean, one-file simulator. Multiple provider/item resolution failures observed with the larger seven-file fixture are consistent with bad simulator File Provider state, but a one-to-one causal relationship remains unproven. Continue to require the full seven-document tests, content guards and explicit Apply journey; the isolated success does **not** authorize merging.

## Native Apple File Provider OS evidence (2026-11-06)

[Run 42199158594, attempt 2](https://github.com/gamesbyian/AYA/actions/runs/42199158594) retained `apple-xcodebuild-failure` artifact `aya-fileprovider-events.log`, a **bounded final 9-minute slice** of simulator system logs during real XCUITests. The 9,379 captured lines include:

| Specific signature | Count in bounded log |
| --- | ---: |
| `com.apple.FileProvider.LocalStorage` cannot resolve item ID, `NSFileProviderErrorNonExistentItemIdentifier` / FP -1005 | 9 |
| `com.apple.DocumentManager.Service`: `Failed opening URL: 2` | 120 |
| LocalStorage `indexOneBatchInDomain:completionHandler:` expired/hung | 2 |
| LocalStorage extension launch / helper communication failure | 2 |
| iCloud authentication failure (-1000), **separate provider / likely noise** | 8 |

These are independent **OS-level** errors, not AYA validation messages. The `NSFileProviderErrorNonExistentItemIdentifier` entries mention localstorage IDs such as `did=3`, `did=4`, `did=6`, `did=7`; the Apple local File Provider indexer also exceeded its hard deadline and an extension failed to launch/communicate. In the same run, the native Files UI presented document cells, but failed negative selections left the host's `importProbe` at `picker-opened`. **This strongly implicates local Files provider resolution/indexing or its simulator environment as a contributing factor, but is not proof that each DocumentManager error refers to one of our seven fixtures.** Correlate timestamps and OS messages before declaring causality. Simulator logs are not a substitute for a real iPhone import journey.

CI now includes `scripts/ci/summarize_apple_fileprovider.py` to aggregate these signatures into the GitHub step summary while keeping raw log artifacts and preserving XCTest's original failing exit status. The summary deliberately omits raw OS message contents and document metadata. The concrete next questions are whether a clean fresh simulator or native Files own-provider control can successfully select a document, and whether `LocalStorage` resolution failures correlate exactly with failed selections; avoid further speculative edits to AYA's bounded reader or host validator.



## What the imported file can and cannot authorize

The user saves a generated artifact and later invokes the host's visible **Import saved agent output** action. That is a distinct, independent consent operation. The Files picker returns a **security-scoped URL** to the specific user-selected file, not permission to monitor an AI app, inspect arbitrary directories, recover a conversation or execute arbitrary generated instructions. The host calls `startAccessingSecurityScopedResource`, uses `NSFileCoordinator` to read on a background task, bounds the bytes, hashes them, then releases access. The returned snapshot is immutable local input for **host-authored recognition, semantic validation, preview and final Apply confirmation**.

A chosen filename, extension, `UTType`, adjacent card, app name or producer identity cannot authorize import. The fixture uses distinct synthetic JSON files; the host must independently parse the actual bytes. Importing invalid JSON must leave state unchanged and offer no Apply. Importing valid JSON must not change state until an explicit *subsequent* Apply; Cancel must preserve existing values. On real providers, changes/revocation/races must be handled without partial application.

## Portable synthetic local File Provider fixture

Apple's [File Provider documentation](https://developer.apple.com/documentation/fileprovider) and [Launch Services keys](https://developer.apple.com/library/archive/documentation/General/Reference/InfoPlistKeyReference/Articles/LaunchServicesKeys.html) describe that an iOS app setting both `UIFileSharingEnabled=YES` and `LSSupportsOpeningDocumentsInPlace=YES` exposes its **own Documents** through the system local File Provider. This is enabled **only** in the disposable `integrations/apple/qa-share-receiver` containing app, never the AYA SDK or the importing host.

The macOS workflow builds and installs that app on a disposable iOS Simulator, then places two small synthetic JSON files in **its own QA Documents** via `simctl get_app_container`. This staging supplies only fixture data. The first-party Lantern host remains in its **different sandbox** and **must** open the user-facing `fileImporter` system UI to select either document, receiving a scoped URL and using its real parsing/confirmation path. The test must not pass an arbitrary path or file bytes directly to `AYAImportFile` and call that an installed picker test.

The fixture files are:

- `aya-layout-valid.json`: exact documented fictional host format, 3 columns and cool accent
- `aya-layout-invalid.json`: same nominal format but an out-of-range column count and unsupported accent
- `aya-layout-boolean.json` / `aya-layout-float.json`: otherwise valid demo JSON whose `columns` field is `true` or `1.0`. These values must fail the strict integer field contract even though Swift Foundation's usual `as? Int` casts would accept them as `1`.
- `aya-layout-oversized.json`: otherwise valid three-field JSON with trailing whitespace, exactly **4 MiB + 1 byte**. If the importer silently truncated it or ignored its cap, the host validator would otherwise accept the payload; the test requires the **size-specific** error before any preview or Apply.

The QA app itself makes no network calls, telemetry requests, writes to the host's data, or user-facing production changes. Neither QA fixture is an AI output.

## Acceptance gates

| Scenario | Must prove |
| --- | --- |
| Actual Files picker | Host user action launches the OS picker; a file visible under **On My iPhone → AYA Share QA** can be explicitly chosen |
| Valid foreign snapshot | The host obtains the independently packaged JSON's bytes and recognizes/validates them; visual layout remains unchanged until Apply |
| Cancel | Closing the host preview leaves the old 1-column, warm-accent state |
| Apply | A second explicit selection and positive Apply changes only the fictional host's 3-column/cool-accent state |
| Invalid foreign JSON | No route to Apply is offered; error is visible; prior state persists |
| Invalid JSON numeric types | Files-selected Boolean and floating-point values in integer-only `columns` cannot trigger a preview or Apply, even when bridged numeric casts would coerce them |
| Valid JSON beyond default cap | A real picker-selected 4 MiB + 1 byte document from the independent QA provider raises the explicit file-size error, offers no Apply and preserves prior state |
| No Files provider / dismissed picker | Missing recipient or Cancel does not produce a fake imported file or mutation; a test must fail, not silently skip absent fixture |
| Future negative cases | No scope, revoked provider, file mutated during coordination, custom >16 MiB cap, wrong card and multiple matching host formats all reject or require correct host-directed confirmation |

**Evidence boundary:** a green test here would prove a first-party app reading a user-selected file from a *different local sandbox* via the system provider on a dated iOS Simulator. It would not establish iCloud sync, third-party cloud File Providers, revocation races, physical iPhone/iPad accessibility, arbitrary production importer correctness or compatibility with any model.

## Online incident comparison and next discrimination (2026-11-06)

The observed problem is **before host byte reading**: after tapping a Files document, the host debug marker often remains at `picker-opened`; no picker completion, read, route decision, or visible rejection occurs. A second normal tap does not change that. Valid and invalid payloads both exhibit failures on some runs, so neither the JSON schema nor grid position alone explains them. An independent UIKit `UIDocumentPickerViewController(forOpeningContentTypes: [.item], asCopy: true)` on the same File Provider exhibited the failure as well. On the latest run 9 of 15 iPhone tests passed; the first Boolean negative could pass while the subsequent floating-point negative failed in the same test, further indicating intermittent selection.

Public reports relevant to triage, **not proof of a current OS bug or a production fix**:

- [Stack Overflow: simulator fileImporter selection](https://stackoverflow.com/questions/71806115/how-can-i-select-files-using-file-importer-in-swiftui/71946287): historically a file **long press followed by a second selection** worked when tapping did not. The author reports the issue was fixed for their scenario in Xcode 14.2 by using `allowedContentTypes: [.item]`. Our Xcode **16.4** sample already uses `.item`, so run long press as a **diagnostic** only, not a substitute for the one-tap gate.
- [Stack Overflow: iOS 18 simulator picker freezing](https://stackoverflow.com/questions/79441895/swiftui-fileimporter-inside-uihostingcontroller): reported version-specific simulator regression; compare a second OS runtime before attributing failure to host validation.
- [Stack Overflow: local Files provider visible but not selectable](https://stackoverflow.com/questions/48884248/how-can-i-add-files-to-the-ios-simulator): older simulators displayed files while clicks did nothing; real-device acceptance is a separate requirement.
- [Apple Developer documentation: XCUIElement press(forDuration:)](https://developer.apple.com/documentation/xcuiautomation/xcuielement/press%28forduration%3A%29): supported native automation for the long-press control experiment.
- [Apple Developer documentation: fileImporter](https://developer.apple.com/documentation/swiftui/view/fileimporter%28ispresented%3Aallowedcontenttypes%3Aoncompletion%3A%29): a scoped URL is only available **after** a successful picker completion.
- [Swift Forums: simulator fixture staging](https://forums.swift.org/t/how-do-you-get-files-into-simulator/85026) and [Apple Developer Forums: direct LocalStorage writes](https://developer.apple.com/forums/thread/846994): document staging and File Provider indexing can complicate simulator tests. Test real user selection; never substitute direct host path access as a passing acceptance signal.

**Next decision tree:** run a separately named long-press picker test while preserving all existing strict single-tap cases. If a long press succeeds, compare Files grid/list selection and runtime versions before choosing a production approach. If it fails, test whether a fixture created through the QA app itself or system Files import (rather than direct `simctl` container writes) restores selectable provider items. Keep ordinary host behavior and the bounded semantic validator unchanged until the boundary is demonstrated. Save failing AX snapshots and exact Xcode/runtime details. No hypothetical workaround may be counted as an accepted user journey.

## Relevant official Apple references

- [SwiftUI fileImporter](https://developer.apple.com/documentation/swiftui/view/fileimporter%28ispresented%3Aallowedcontenttypes%3Aoncompletion%3A%29): URLs from the picker are security-scoped, Cancel has no success callback
- [Security-scoped URLs](https://developer.apple.com/documentation/foundation/url/startaccessingsecurityscopedresource%28%29): granted access requires balanced start/stop; kernel-resource leaks on missing stop
- [Local File Provider and document browser](https://developer.apple.com/documentation/fileprovider): other apps' exported Documents are system-browsable only with the proper opt-in keys
- [LSSupportsOpeningDocumentsInPlace](https://developer.apple.com/library/archive/documentation/General/Reference/InfoPlistKeyReference/Articles/LaunchServicesKeys.html): reads from other providers can change concurrently and require coordinated access

For the portable content-recognition contract, see [Output Return & Import](../OUTPUT_RETURN_IMPORT.md), [Apple architecture](ARCHITECTURE.md), [Apple rollout plan](PLAN.md) and [module portability](../MODULE_PORTABILITY.md).
