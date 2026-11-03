# iOS and iPadOS rollout plan / acceptance ledger (2026-11-03)

**Goal:** developer-drop-in, zero-backend AYA for real native Apple hosts, without splitting the convention or diluting established Android security and evidence standards. [Research](RESEARCH.md) · [Architecture](ARCHITECTURE.md).

## Scope and priority

### P0: contracts and source foundation

- [x] Research documented Apple APIs, provider-specific prior art and fundamental unknowns, with source links and applicability limits.
- [x] Define platform-neutral semantics and Apple-specific identity/transport/input boundaries.
- [x] Add a SwiftPM first-party source preview with guarded iOS reference, editable draft representation, approved-text data contract and UIKit plain-text/.txt sharing entry points.
- [x] Run portable Swift unit tests on Linux for reference identity, version, section completeness, duplicates, unresolved placeholders, user-edited approval, empty/oversized cases. **Local Linux test only.**
- [ ] Qualify actual iOS `UIKit` compilation with Xcode on macOS runner. `#if os(iOS)` is excluded from Linux tests. Do not merge an iOS API claim without Xcode evidence.
- [ ] Shared language-neutral JSON fixtures comparing Android and iOS guide acceptance and key handoff semantics.
- [ ] Add CI selectivity: cheap portable tests on relevant changes, costly simulator/native tests only when Apple native source/manifest changes; keep always-on repository `docs` check.

### P1: fully accessible native host UI and real sample

- [ ] Source-package-based out-of-tree native iOS sample with its own fictional guide derived from actual sample source and matching bundle/version.
- [ ] SwiftUI AYA card: logo drawn with host tint, visible task and attachment disclosure, host-authored output-use instructions, optional question field, one Ask action, min 44pt targets, VoiceOver labels, high contrast, Dynamic Type, Reduce Motion, keyboard focus and iPad split-screen layouts.
- [ ] Full editable review, Cancel, distinct Copy / Share text / Share .txt. No duplicate composer, no unsolicited share and no post-approval resurrection of earlier question.
- [ ] iPad popover anchoring, repeated share, cancellation, unavailable target fallback, dismissal/background, scene restoration and version mismatch.
- [ ] iOS Simulator installed-host tests using a synthetic *foreign receiver* extension/app to inspect exactly what text and file bytes are passed, without claiming any real LLM compatibility.
- [ ] Confirm exact app resources are packaged and stale/cross-app guide fails closed.
- [ ] Host-owned importer: Files picker, security-scope lifecycle, coordinated off-main snapshots with byte cap and hash, content-based multi-route registry, wrong-card UX, ambiguous/oversized/invalid file tests, separate apply boundary.
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

**Immediate next engineering session:** implement the native review card and a real first-party iOS sample, then qualify Xcode iOS Simulator compilation and behavior. The UIKit source-preview helper in the foundation is **unverified on Apple** until then. Use one coherent batch of UI modifications before the first full simulator suite; correct only meaningful failures, preserve actionable build logs, and avoid redundant job fan-out.

**Operational unknowns:** target iOS minimum deployment version, stable Xcode runner availability/cost, eligible physical test devices, and actual compatibility of individual assistant targets. iOS 16 is the provisional SwiftPM minimum for baseline accessibility and document workflows; reconsider if measured adoption benefits warrant older support. No Apple Developer account is necessary for source research/SwiftPM unit tests, but shipping/signed physical distribution may need one.

**Do not equate:** source preview ≠ Xcode build ≠ simulator app ≠ physical-device UX ≠ AI recipient successful ingestion ≠ publicly distributed SDK.
