# AYAApple: native iOS and iPadOS source package

Optional Apple transport and SwiftUI component for the [AYA platform-neutral interaction convention](../../../README.md). The package has no AI service, account, network dependency or requirement to adopt AYA's implementation.

**Status as of 2026-11-03/04:** Native SwiftUI help card, complete editable review, explicit Copy and text/.txt Share Sheet handoff, Files import snapshot and content-based host routing are **implemented in source**. [PR #122 and run 41760530755](https://github.com/gamesbyian/AYA/actions/runs/41760530755) passed Swift unit tests, actual Xcode iOS SDK compilation and built a real first-party example .app with exact guide bytes and installed bundle identity/version. Installed iPhone Simulator interaction is qualified separately by [PR #123](https://github.com/gamesbyian/AYA/pull/123), with genuine assistant/provider acceptance, physical-device VoiceOver and independent host integration still outstanding.

Two library products are available via Swift Package Manager:

- AYAProtocol (Foundation only): exact iOS AYA-RAS identity/version/section checks, bounded user-edited approval packet, generic output import registry and conservative private-share cache expiry policy. No UI or assistant backend.
- AYAApple (iOS/UIKit/SwiftUI): AYAHelpCard, system review/Copy/Share text or one .txt file, a native outgoing UIKit helper, user-picked Files snapshot with security-scoped coordinated off-main read and SHA-256, and the optional AYAImportPickerButton. Imported bytes never apply themselves.

For portable unit tests:

    cd integrations/apple/AYAApple
    swift test

For real native sample compilation, see the [iOS integration guide](../../../docs/apple/INTEGRATION.md) and [fictional XcodeGen sample](../sample). An adopter must author its own source-verified iOS guide with actual Bundle ID/version, truthful instructions, and host-owned output validation, preview and separate confirmation.

Sharing a .txt file writes one private, uniquely named temporary document. It is not removed immediately on Share Sheet dismissal; on a later share the helper performs best-effort cleanup only of regular AYA UUID-named .txt files in its own cache older than seven days. Apple may independently clear cache. This policy does not scan other apps, manage user documents or prove the receiver has read the file.

The portable output registry's ready decision is permission to open the host's own validation/impact preview, **never** permission to execute. Wrong-card detection, ambiguous format choices and malicious output safety remain host responsibilities. Clipboard contents are an explicit disclosure surface; a Share Sheet destination does not establish successful AI ingestion.

**Release boundary:** Source/build evidence and first-party packaging are not physical iPhone/iPad UX, signed public distribution, real recipient compatibility or a certification of the host's reference truth. Consult [Apple research](../../../docs/apple/RESEARCH.md), [architecture](../../../docs/apple/ARCHITECTURE.md), [plan](../../../docs/apple/PLAN.md) and [issue #120](https://github.com/gamesbyian/AYA/issues/120).
