# iOS and iPadOS rollout plan / acceptance ledger (2026-11-04)

**Goal:** developer-drop-in, zero-backend AYA for real native Apple hosts, without splitting the convention or diluting established Android security and evidence standards. [Research](RESEARCH.md) · [Architecture](ARCHITECTURE.md).

## Scope and priority

### P0: contracts and source foundation

- [x] Research documented Apple APIs, provider-specific prior art and fundamental unknowns, with source links and applicability limits.
- [x] Define platform-neutral semantics and Apple-specific identity/transport/input boundaries.
- [x] Add a SwiftPM first-party source preview with guarded iOS reference, editable draft representation, approved-text data contract and UIKit plain-text/.txt sharing entry points.
- [x] Run portable Swift unit tests on Linux for reference identity, version, section completeness, duplicates, unresolved placeholders, user-edited approval, empty/oversized cases. **Local Linux test only.**
- [x] Qualify actual iOS `UIKit` compilation with Xcode on macOS runner: [run 41600191635](https://github.com/gamesbyian/AYA/actions/runs/41600191635) passed both Linux Swift unit tests and a genuine Xcode iOS Simulator SDK compile at merged PR #119 head `987eeee8`. **No installed iOS app or synthetic recipient was run.**
- [x] Shared [Python/iOS Swift reference fixtures](REFERENCE_PARITY.md), 13 structural and installed-version cases, merged in [PR #128](https://github.com/gamesbyian/AYA/pull/128) with docs, Linux Swift and Xcode checks green. **The Android JVM verifier now runs the same fixture matrix in its own platform profile**, with exact-package/version and 2 MiB UTF-8 guards; [parity test documentation](REFERENCE_PARITY.md). This is structural acceptance, not installed-host or recipient evidence.
- [x] Path-scoped Apple CI for Swift source/tests/package and native sample; cheap always-on Python reference checks remain independent. Package README/docs-only edits do not trigger the macOS lane; native runner cost is still monitored.

### P1: fully accessible native host UI and real sample

- [x] First-party native XcodeGen iOS sample with its own source-derived fictional guide and verified packaged bundle/version bytes: [PR #122, CI 41760530755](https://github.com/gamesbyian/AYA/actions/runs/41760530755). [PR #140](https://github.com/gamesbyian/AYA/pull/140) subsequently verified the root SwiftPM manifest from an out-of-tree synthetic consumer; [PR #141 / CI 41830294217](https://github.com/gamesbyian/AYA/actions/runs/41830294217) installed and UI-tested a second separately authored **fictional** host. Genuine production adopter integration remains open.
- [ ] SwiftUI AYA card/source compiled in PR #122: disclosure, task and host-owned output instructions, question, 44pt actions and no fake import action. [PR #130, CI 41777217614](https://github.com/gamesbyian/AYA/actions/runs/41777217614) additionally passed **4/4 installed iPhone and 1/1 separate iPad XCUITests**, including bounded scrolling and tappable controls at accessibility Dynamic Type size. **Custom scalable AYA logo and actual VoiceOver, high contrast, hardware keyboard, rotation, multitasking and physical-device acceptance remain.**
- [x] Full editable SwiftUI review and explicit Cancel, Copy, Share text, Share .txt sources compile in [PR #122](https://github.com/gamesbyian/AYA/pull/122); [PR #123 / run 41774435106](https://github.com/gamesbyian/AYA/actions/runs/41774435106) installed a real first-party iOS Simulator host and passed **3/3 XCUITests** for opened review/Cancel, populated review/Copy and stale-guide denial. **Actual text and .txt file Share Sheet delivery to a synthetic independent extension is now verified by [PR #133 / run 41781406186](https://github.com/gamesbyian/AYA/actions/runs/41781406186); real assistant ingestion is not.**
- [ ] iPad popover anchoring, repeated share, cancellation, unavailable target fallback, dismissal/background, scene restoration and version mismatch.
- [x] An independent, disposable *foreign receiver* Share Extension compiled and packaged ([PR #132](https://github.com/gamesbyian/AYA/pull/132)); then [PR #133 / run 41781406186](https://github.com/gamesbyian/AYA/actions/runs/41781406186) passed **2/2 installed iPhone Simulator Share Sheet tests** delivering approved plain text and a complete .txt to that foreign extension, verifying its received byte counts and independent SHA-256 against the approved fixture. Original 4/4 iPhone and 1/1 separate iPad large-text UI tests also passed. [PR #138 / CI 41825989062](https://github.com/gamesbyian/AYA/actions/runs/41825989062) subsequently verified user-edited text and .txt foreign-receiver bytes; [PR #142 / CI 41831599513](https://github.com/gamesbyian/AYA/actions/runs/41831599513) tested both modes on iPad. **No real LLM compatibility, physical-device evidence or accepted Files return is established here.** See [receiver QA](RECEIVER_QA.md).
- [x] Confirm exact app resources packaged ([CI 41760530755](https://github.com/gamesbyian/AYA/actions/runs/41760530755)) and installed stale-version guide fails closed before review ([CI 41774435106](https://github.com/gamesbyian/AYA/actions/runs/41774435106)); cross-app identity rejection covered by Swift unit tests, not a second installed host.
- [ ] Host-owned Files picker source, scoped coordinated off-main snapshot with cap and SHA-256, content-based multi-route registry with wrong-card/ambiguity decisions, and separate sample Apply confirmation compile; portable negative routing tests pass. [PR #139 / run 41890208508](https://github.com/gamesbyian/AYA/actions/runs/41890208508) proved valid user-selected Files import with Cancel and explicit Apply, but **failed** the malformed-file visible-error test (9/10 iPhone tests passed). [Replacement PR #147](https://github.com/gamesbyian/AYA/pull/147) includes a persistent accessible rejection panel, strict Boolean/float field validation, and a real File Provider 4 MiB + 1 byte negative. **Full exact-head simulator acceptance is pending**; provider revocation, wrong-card UI and independent production importer integration remain.
- [ ] Reuse Android version/identity/test fixture decisions but reject any Android-only platform path assumptions.

### P2: genuine compatibility and distribution

- [ ] On real iPhone and iPad, test large type, VoiceOver, keyboard, offline and background/foreground conditions. Simulators alone don't qualify as physical devices.
- [ ] Maintain dated *per app/version/iOS/account/transport* acceptance rows for ChatGPT, Claude, Gemini and any other actually exercised receiver. Never infer attachment consumption from an advertised Share Sheet destination.
- [ ] Independently authored native host with genuine source-derived guide, host importer, clean SwiftPM resolution and complete manual output round trip.
- [ ] Signed reproducible app integration / source release, package provenance, install/uninstall and upgrade path, check no entitlement/domain/payment is required for basic function.
- [ ] Add App Intents only for justified read-only / prepare operations after host acceptance. Validate Shortcuts discoverability and execute refusal for destructive requests; evaluate `AppIntentsTesting` on supported Xcode.
- [ ] Consider SwiftUI `ShareLink` / `Transferable` alternate instead of default UIKit only after an observed receiver-compatibility benefit and equal review semantics.
- [ ] Consider an inbound Share Extension only if a specific receiving workflow cannot reasonably be served by the host's own file picker.

## Test strategy and economics

| Boundary | Fast evidence | Higher-level gate | Not proved |
| --- | --- | --- | --- |
| Portable packet and reference | SwiftPM Linux `swift test`; existing Python/schema/portability checks | Cross-language fixture comparisons | Truth of content or real host UI |
| Native outgoing share | macOS Xcode iOS Simulator build; XCTest + synthetic receiver on changed iOS native code | Actual device testing with file/text targets | External agent understanding |
| Import file provider | Unit tests for registry, caps and bytes | System Files/iCloud simulated/physical File Provider revocation and concurrent mutation | Semantic safety without independent host validation |
| Accessibility | Snapshot/AX tree and UI tests | Actual VoiceOver, large type, keyboard and iPad multitasking | Human usability from screenshot alone |
| App Intents optional | Targeted intent/parameter unit tests | Real out-of-process App Intents Testing and Shortcuts discovery | AI agent's arbitrary invocation privilege |
| Recipient compatibility | Published capabilities are research leads only | Exact dated physical/device app tests | Transfer to other app versions/account states |

Use source/OS version pinning, bounded execution and failure artifacts. macOS runner minutes are costlier; do **not** launch Xcode/simulator on every unrelated Android/docs-only commit. At PR review explicitly distinguish local Linux Swift tests, Xcode compile, iOS simulator, physical-device and receiver evidence.

## Work board handoff

**Immediate next engineering session:** qualify [consolidated PR #147](https://github.com/gamesbyian/AYA/pull/147) on its exact head after [#139's malformed-file visible-alert failure](https://github.com/gamesbyian/AYA/actions/runs/41890208508). #147 contains the entire real Files-provider picker/Cancel/Apply path plus persistent host-owned error feedback, a genuine **4 MiB + 1 byte** foreign-file size negative, and strict JSON numeric-type tests. **Keep it draft and do not merge without green native checks.** On accepted evidence, close superseded #139 with a precise comment. Then address ambiguous/wrong-card UX, revoked provider and mutation/cancellation races. User-edited outbound receiver bytes and a second *fictional* consuming host are qualified (#138, #141); further gates include iPad multitasking/popover, physical VoiceOver/keyboard/high contrast, independent production adoption and dated real assistant ingestion.

**Operational unknowns:** target iOS minimum deployment version, stable Xcode runner availability/cost, eligible physical test devices, and actual compatibility of individual assistant targets. iOS 16 is the provisional SwiftPM minimum for baseline accessibility and document workflows; reconsider if measured adoption benefits warrant older support. No Apple Developer account is necessary for source research/SwiftPM unit tests, but shipping/signed physical distribution may need one.

**Do not equate:** source preview ≠ Xcode build ≠ simulator app ≠ physical-device UX ≠ AI recipient successful ingestion ≠ publicly distributed SDK.
