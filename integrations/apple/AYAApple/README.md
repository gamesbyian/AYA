# AYAApple: native iOS and iPadOS source package

Optional Apple transport and SwiftUI component for the [AYA platform-neutral interaction convention](../../../README.md). The package has no AI service, account, network dependency or requirement to adopt AYA's implementation.

**Status as of 2026-11-04:** Native SwiftUI help card, complete editable review, explicit Copy and text/.txt Share Sheet handoff, Files import snapshot and content-based host routing are **implemented in source**. [PR #122 and run 41760530755](https://github.com/gamesbyian/AYA/actions/runs/41760530755) passed Swift unit tests, actual Xcode iOS SDK compilation and built a real first-party example .app with exact guide bytes and installed bundle identity/version. [PR #123 / run 41774435106](https://github.com/gamesbyian/AYA/actions/runs/41774435106) additionally installed the first-party iOS Simulator host and passed 3/3 local review/Cancel/Copy/stale-reference UI checks. [PR #128](https://github.com/gamesbyian/AYA/pull/128) passed shared Swift/Python reference fixtures. [PR #130 / CI 41777217614](https://github.com/gamesbyian/AYA/actions/runs/41777217614) passed 4/4 installed iPhone XCUITests and a separate 1/1 large-text iPad run; [PR #132 / CI 41778363523](https://github.com/gamesbyian/AYA/actions/runs/41778363523) compiled a disposable foreign Share Extension. [PR #133 / CI 41781406186](https://github.com/gamesbyian/AYA/actions/runs/41781406186) passed 2/2 genuine cross-app iPhone Simulator Share Sheet receipts (plain text and .txt), each matching the independent recipient's SHA-256 and byte count; original 4 iPhone and 1 iPad UI tests also passed. Real assistant/provider acceptance, post-review edit variants, Files picker return, physical-device VoiceOver and independent host integration remain outstanding.

Two library products are available via Swift Package Manager:

- AYAProtocol (Foundation only): exact iOS AYA-RAS identity/version/section checks, bounded user-edited approval packet, generic output import registry and conservative private-share cache expiry policy. No UI or assistant backend.
- AYAApple (iOS/UIKit/SwiftUI): AYAHelpCard, system review/Copy/Share text or one .txt file, a native outgoing UIKit helper, user-picked Files snapshot with security-scoped coordinated off-main read and SHA-256, and the optional AYAImportPickerButton. Imported bytes never apply themselves.

**Remote Swift Package discovery:** The repository root now also contains `Package.swift` referencing this package's *same* sources, so Xcode's **Add Package Dependencies** can use `https://github.com/gamesbyian/AYA.git` pinned to a tested **commit revision**. The nested manifest here remains for local development and the first-party example. See [distribution/source-preview boundaries](../../../docs/apple/DISTRIBUTION.md); there is no public SemVer-tagged Apple SDK release yet.

For portable unit tests:

    cd integrations/apple/AYAApple
    swift test

For real native sample compilation, see the [iOS integration guide](../../../docs/apple/INTEGRATION.md) and [fictional XcodeGen sample](../sample). An adopter must author its own source-verified iOS guide with actual Bundle ID/version, truthful instructions, and host-owned output validation, preview and separate confirmation.

Sharing a .txt file writes one private, uniquely named temporary document. It is not removed immediately on Share Sheet dismissal; on a later share the helper performs best-effort cleanup only of regular AYA UUID-named .txt files in its own cache older than seven days. Apple may independently clear cache. This policy does not scan other apps, manage user documents or prove the receiver has read the file.

The portable output registry's ready decision is permission to open the host's own validation/impact preview, **never** permission to execute. Wrong-card detection, ambiguous format choices and malicious output safety remain host responsibilities. Clipboard contents are an explicit disclosure surface; a Share Sheet destination does not establish successful AI ingestion.

**Release boundary:** Source/build evidence and first-party packaging are not physical iPhone/iPad UX, signed public distribution, real recipient compatibility or a certification of the host's reference truth. Consult [Apple research](../../../docs/apple/RESEARCH.md), [architecture](../../../docs/apple/ARCHITECTURE.md), [plan](../../../docs/apple/PLAN.md) and [issue #120](https://github.com/gamesbyian/AYA/issues/120).
