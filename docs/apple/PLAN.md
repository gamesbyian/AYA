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

- [x] First-party native XcodeGen iOS sample with its own source-derived fictional guide and verified packaged bundle/version bytes: [PR #122, CI 41760530755](https://github.com/gamesbyian/AYA/actions/runs/41760530755). **Out-of-tree independently authored consumer is still outstanding.**
- [ ] SwiftUI AYA card/source compiled in PR #122: disclosure, task and host-owned output instructions, question, 44pt actions and no fake import action. [PR #130, CI 41777217614](https://github.com/gamesbyian/AYA/actions/runs/41777217614) additionally passed **4/4 installed iPhone and 1/1 separate iPad XCUITests**, including bounded scrolling and tappable controls at accessibility Dynamic Type size. **Custom scalable AYA logo and actual VoiceOver, high contrast, hardware keyboard, rotation, multitasking and physical-device acceptance remain.**
- [x] Full editable SwiftUI review and explicit Cancel, Copy, Share text, Share .txt sources compile in [PR #122](https://github.com/gamesbyian/AYA/pull/122); [PR #123 / run 41774435106](https://github.com/gamesbyian/AYA/actions/runs/41774435106) installed a real first-party iOS Simulator host and passed **3/3 XCUITests** for opened review/Cancel, populated review/Copy and stale-guide denial. **Actual text and .txt file Share Sheet delivery to a synthetic independent extension is now verified by [PR #133 / run 41781406186](https://github.com/gamesbyian/AYA/actions/runs/41781406186); real assistant ingestion is not.**
- [x] Independent first-party **iPadOS Simulator Share Sheet acceptance**: [PR #142 / CI 41831599513](https://github.com/gamesbyian/AYA/actions/runs/41831599513) passed a distinct iPad run with **3/3** tests: large-Dynamic-Type review controls and both real plain-text/.txt Share Sheet handoffs to the separate QA extension with recipient-side matching SHA-256/length. **Physical iPad VoiceOver, rotation/multitasking, repeated sharing, cancellation, unavailable-target fallback, dismissal/background and scene restoration remain separate gates.**
- [x] An independent, disposable *foreign receiver* Share Extension compiled and packaged ([PR #132](https://github.com/gamesbyian/AYA/pull/132)); then [PR #133 / run 41781406186](https://github.com/gamesbyian/AYA/actions/runs/41781406186) passed **2/2 installed iPhone Simulator Share Sheet tests** delivering approved plain text and a complete .txt to that foreign extension, verifying its received byte counts and independent SHA-256 against the approved fixture. Original 4/4 iPhone and 1/1 separate iPad large-text UI tests also passed. [PR #138 / CI 41825989062](https://github.com/gamesbyian/AYA/actions/runs/41825989062) separately passed both **user-edited** plain-text and .txt external receipt tests, comparing the foreign extension's exact hash and byte count to the edited on-screen text. **No real LLM compatibility, physical-device evidence or completed Files return is established.** See [receiver QA](RECEIVER_QA.md).
- [x] Confirm exact app resources packaged ([CI 41760530755](https://github.com/gamesbyian/AYA/actions/runs/41760530755)) and installed stale-version guide fails closed before review ([CI 41774435106](https://github.com/gamesbyian/AYA/actions/runs/41774435106)); cross-app identity rejection covered by Swift unit tests, not a second installed host.
- [ ] Host-owned Files picker source, scoped coordinated off-main snapshot with cap and SHA-256, content-based multi-route registry with wrong-card/ambiguity decisions, and separate sample Apply confirmation compile; portable negative routing tests pass. **Full wrong-card UX, provider revocation/oversize installed tests and independent importer integration remain.**
- [ ] Reuse Android version/identity/test fixture decisions but reject any Android-only platform path assumptions.

### P2: genuine compatibility and distribution

- [ ] On real iPhone and iPad, test large type, VoiceOver, keyboard, offline and background/foreground conditions. Simulators alone don't qualify as physical devices.
- [ ] Maintain dated *per app/version/iOS/account/transport* acceptance rows for ChatGPT, Claude, Gemini and any other actually exercised receiver. Never infer attachment consumption from an advertised Share Sheet destination.
- [x] [PR #141 / CI 41830294217](https://github.com/gamesbyian/AYA/actions/runs/41830294217) built and ran a **second separately authored fictional native iOS host** that imports the `AYAApple` product through the root SwiftPM manifest with its own source-matched guide. A genuinely external adopting developer, production host importer and complete manual output round trip remain unverified.
- [x] [Root SwiftPM Git URL discovery and an outside-checkout pure-Swift consuming project](DISTRIBUTION.md) passed [PR #140 / CI 41828745641](https://github.com/gamesbyian/AYA/actions/runs/41828745641). This is **source preview only**; signed reproducible app integration, SemVer tagged public release, provenance, install/uninstall and upgrade path remain open. Check that basic operation requires no service entitlement, domain or payment.
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

**Immediate next engineering session:** finish the **real foreign Files return** through [PR #139](https://github.com/gamesbyian/AYA/pull/139). Initial iPhone CI proved valid cross-app Files selection, semantic preview, Cancel, and explicit Apply; invalid JSON rejection initially lacked a visible error, and its follow-up now uses a host-owned alert. The same coordinated PR carries complete bounded EOF reads and conservative ambiguous-route selection, pending its exact-head checks. Edited foreign sharing (#138), iPadOS foreign sharing (#142), root SwiftPM (#140) and a second fictional native host (#141) are already green and merged. Next: real File Provider revocation/oversize, wrong-card UI, physical VoiceOver, repeated-share lifecycle, real assistant target compatibility and adoption by an independent developer. First-party iOS SDK and .app packaging are proven in PR #122; PR #123 adds only the observed local interaction flows, not external assistant receipt or safe manual import. Use one coherent batch of UI modifications before the first full simulator suite; correct only meaningful failures, preserve actionable build logs, and avoid redundant job fan-out.

**Operational unknowns:** target iOS minimum deployment version, stable Xcode runner availability/cost, eligible physical test devices, and actual compatibility of individual assistant targets. iOS 16 is the provisional SwiftPM minimum for baseline accessibility and document workflows; reconsider if measured adoption benefits warrant older support. No Apple Developer account is necessary for source research/SwiftPM unit tests, but shipping/signed physical distribution may need one.

**Do not equate:** source preview ≠ Xcode build ≠ simulator app ≠ physical-device UX ≠ AI recipient successful ingestion ≠ publicly distributed SDK.
