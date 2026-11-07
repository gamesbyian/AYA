# Apple delivery and investigation budget

> **Working status, 2026-11-06:** iOS AYA is a functional **source preview**, not a fully qualified import integration. Outbound Share Sheet and independent synthetic receiver journeys are supported by native XCUITest evidence; return through the system Files picker has intermittent failures with Apple's local provider. [Open acceptance PR #147](https://github.com/gamesbyian/AYA/pull/147) stays draft. Its failing tests remain failures. This plan separates **forward product development** from **diagnosis of simulator behavior**.

## Delivery lanes and gates

| Lane | Deliverable and owner-neutral contract | Evidence needed | Status |
| --- | --- | --- | --- |
| A. Portable packet core | Exact installed-version identity, readable reference, immutable approved snapshot, Copy/Share | SwiftPM tests, native SDK compile, second independent host | Established in previous native checks; recheck at release head |
| B. Outbound user handoff | User selects a share target; receiver gets approved text or complete attachment bytes | Installed iPhone/iPad Share Sheet and independent receiver with byte count/hash | Synthetic receiver accepted; **real assistant ingestion unverified** |
| C. Import preview | User explicitly chooses file, bounded security-scoped snapshot, host validates and previews, Cancel leaves state unchanged, Apply only with consent | Unit/integration tests plus installed native real Files journey | **Partial**: positive and malformed journeys passed on fresh 1-file devices; 7-file negative and full installed suite remain red |
| D. Import lifecycle | Cancel pending/in-flight read, revoked access, concurrent mutation, error visibility and no stale Apply | Deterministic injected test, native lifecycle test | **Open [#148](https://github.com/gamesbyian/AYA/issues/148)**; do not imply complete |
| E. Device and accessibility | Real supported iPhone/iPad; VoiceOver, Dynamic Type, focus, cancellation, foreground/background | Signed build and reproducible human/device record | **Not yet established** |
| F. Developer adoption | SwiftPM pinning, host-neutral sample/reference, failure checklist, no app-specific customization | Fresh unrelated host builds and source/version audit | Second native host evidence exists; final installation guide/release packaging still needs sign-off |

Do **not** redefine an unresolved red gate as green. But a red *simulator-specific* gate should not indefinitely block work in independent lanes A, B, D and F. Record each lane's evidence grade and remain explicit about the preview's limitations.

## Next two implementation increments

1. **Finish source-preview integration**: review the public SwiftPM API, sample SwiftUI AYA card, accepted UTTypes, user-visible file-return errors, host-owned validation and explicit Apply. Produce a concise consumer checklist with build instructions and source references. Ensure the examples are host-feature neutral. Run reference/portable Swift tests and a genuine native sample/second-host build.
2. **Harden return lifecycle independently of picker enumeration**: implement [#148](https://github.com/gamesbyian/AYA/issues/148) on a separately scoped branch or small PR. Propagate cancellation from host to any detached read worker; preserve security-scope/file-handle cleanup; never expose incomplete bytes or Apply after cancellation. Add deterministic tests that don't depend on a live Files indexer. Native coordination/cancellation remains a separate gate.
3. **Actual iPhone acceptance** once a physical Apple device and signing are available: install both sample host and independent QA provider, let that provider stage the seven files, select through Files exactly as a user does, and capture app version, iOS version, observed preview/error and Apply/Cancel behavior. Do not use direct sandbox URLs as a pass substitute. Use a second provider (iCloud Drive or another authorized document provider) only with consent and disposable fixtures.

## Bounded investigation protocol

The current evidence is substantial: [six-case native run 42307760222](https://github.com/gamesbyian/AYA/actions/runs/42307760222) passed the single-file valid and malformed tests, and seven-file valid test; all three seven-file malformed variants failed with LocalStorage missing-item-ID errors. Neither an oversized neighbor nor atomic versus direct creation explained the failure. [Independent slot comparison 42318353889](https://github.com/gamesbyian/AYA/actions/runs/42318353889) failed both early-valid and late-invalid despite real cell taps. The normal [full suite 42307760296](https://github.com/gamesbyian/AYA/actions/runs/42307760296) remained 9/17. Keep all those original results and artifact links.

**One question, one manipulated variable, one predefined interpretation, and a stop condition.** For the current File Provider investigation, the remaining affordable control is the creation-order comparison already in [PR #147](https://github.com/gamesbyian/AYA/pull/147). After its result, **stop adding speculative simulator variants** unless a new observation gives a materially different, actionable hypothesis. A maximum of two independent attempts per hypothesis is the default, with exceptions requiring written justification.

- Preserve ordinary native XCTest assertions and failure exit status. A failed Files return is still failed.
- Run narrow File Provider experiments via **manual workflow dispatch only**, with the exact branch/SHA recorded and bounded seven-day artifacts. These tests are diagnostics rather than new automatically required CI fan-outs.
- Prefer deterministic model, parser, consent, cancellation and reference tests for fast feedback. Preserve true installed-app build and outward handoff journeys as separate evidence.
- If native OS selection remains red after bounded tests, classify it **unresolved provider/simulator behavior**. Capture a minimal reproducible sample, OS logs and Xcode/iOS version; seek a physical-device check or upstream report. Do not modify the AYA read API merely to satisfy a broken system selection.
- Avoid automatic retries, polling user documents, enumerating foreign app sandboxes, replacing the Files picker with a hidden local-path shortcut, or downgrading the byte/semantic/Apply gates.

## CI and ownership boundaries

**Automatic checks:** portable Swift/reference contracts, independent receiver build/tests, native package/host compilation, and normal installed acceptance when relevant. Any genuinely failing native acceptance stays red and discoverable. A release claim requires a qualified exact-head run. On the experimental #147 branch, diagnostic workflows are set to manual dispatch only; mainline release checks are not silently downgraded.

**Manual diagnostics (when available on the experimental #147 branch):** Apple Files iOS 26 comparison, one/seven inventory/publication comparison, document-slot control, and creation-order control. Trigger these only for a stated hypothesis. Do not continually add a new workflow after an inconclusive run.

**Governance:** [Apple plan](PLAN.md) is the main rollout ledger, [Files QA](FILES_QA.md) retains detailed OS/Files traces, [integration guide](INTEGRATION.md) is for adopting developers, and [#120](https://github.com/gamesbyian/AYA/issues/120) tracks the Apple feature. Keep host-neutral package contracts separate from the synthetic Lantern and QA app fixtures. 