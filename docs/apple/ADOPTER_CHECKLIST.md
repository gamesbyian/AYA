# iOS adopter checklist (source-preview integration)

This is an adoption procedure for an **existing iOS 16+ host application**. AYA is a host-neutral, user-initiated help/handoff convention. The Apple source package uses native public APIs, has no model backend or account requirement and does **not** observe assistant responses.

**Qualification boundary (2026-11-07):** Outbound share, text-paste return and **system Open In of a synthetic foreign JSON document** have genuine installed-simulator evidence. [Merged #162 / run 42431460633](https://github.com/gamesbyian/AYA/actions/runs/42431460633) passed both real two-app Open In native tests with host review/Cancel/Apply or visible invalid rejection. The separate populated-provider native Files picker remains red in [draft #147](https://github.com/gamesbyian/AYA/pull/147). Do not advertise general Files provider reliability, real assistant ingestion, signed-device or physical accessibility as established. See [delivery gates](DELIVERY_GATES.md).

## Integration procedure

1. **Pin and inspect the source.** In Xcode add this GitHub repository as a Swift Package dependency from its **root** `Package.swift`, choosing a specific reviewed commit or release. Add `AYAApple` for native card/share interfaces and `AYAProtocol` for reference/approval/import routing. The subpackage under `integrations/apple/AYAApple` is a development convenience; do not import both manifests into one host as separate copies.
2. **Source-author the host reference.** Inventory the running host's actual UI, states, warnings, permissions, output formats and version. Package its own UTF-8 AYA-RAS reference, with `platform: ios`, the real bundle ID and installed marketing version. Follow the [authoring standard](../reference/AUTHORING_STANDARD.md). The fictional Lantern guide is **never** a production reference.
3. **Validate the reference before build.** From the repository root run `python3 tools/validate_guide.py --platform ios --strict path/to/your-guide.md`. Match the actual installed `Bundle.main.bundleIdentifier` and `CFBundleShortVersionString`; stale or incomplete references must block sharing instead of being silently repaired.
4. **Wire the user-facing AYA card.** Use `AYAHelpCard` with the bundled reference, host-supplied explanation and output instructions. Let the person review the complete generated handoff text, edit it, and explicitly select Copy or Share. Do not trigger a share from background state or infer that a selected assistant consumed the packet. A UIKit host can use the corresponding native sharing helper instead of adopting SwiftUI.
5. **Only if the host accepts agent-produced output:** provide a user-visible, supported return route. Native `fileImporter` / `AYAImportPickerButton` allows an explicitly selected Files document, while `AYAImportPasteButton` accepts explicit pasted text; hosts that actually register a narrow supported document UTType can optionally handle system Open In via `.onOpenURL` and `AYAAppleFileImport.snapshot(userOpenedURL:)`. The sample registers JSON as an **alternate Viewer**; generic AYA never registers a host's document types automatically. Both snapshot APIs only deliver bounded untrusted bytes, not host format validation or Apply. Maintain the distinction between scoped picker URLs and a system-copied file in the host's own canonical Inbox.
6. **Validate independently.** Register the host's real recognizable formats and strict validators in `AYAImportRegistry`. Handle unrecognized, invalid, ambiguous and ready routes. The host shows the exact proposed changes, their effects and affected destination, and requires explicit Apply. Cancel, picker cancellation and validation errors must preserve prior state. Never trust filename, selected card, UTType, AI-generated metadata or a hash alone as authorization.
7. **Define lifecycle behavior.** Stop import work when the user leaves or supersedes it; do not allow a late completion to expose Apply. Handle revoked security scope, file read error, oversized file, malformed content and uncertain provider state separately. Do not silently retry a failed write, discover other apps' private folders or watch for downloaded files. The cancellation hardening is still tracked in [#148](https://github.com/gamesbyian/AYA/issues/148).
8. **Qualify in an unrelated host.** Build a clean SwiftPM consumer, install a real iOS simulator host, verify review/Cancel/Copy and independent outbound synthetic receipt. If the host supports Open In, require a real system-mediated document from a separately installed app with preview, Cancel, Apply and invalid rejection (as in [#162](https://github.com/gamesbyian/AYA/pull/162)); do not substitute a synthetic `.onOpenURL` call. Separately run genuine Files picker selection with provider-owned documents and preserve the original failing seven-file negatives in #147. Request physical-device acceptance before broad compatibility claims.

## Developer verification commands

Run these at a reviewed source SHA, not against an unpinned moving branch:

```bash
# From the AYA repository root
python3 tools/validate_guide.py --platform ios --strict path/to/your-guide.md

# Root Swift Package protocols and fixture contracts
swift test

# Subpackage contract tests
cd integrations/apple/AYAApple
swift test
```

The Swift tests are **not** a substitute for an iOS SDK build or installed user interaction. To exercise the fictional sample, use a Mac with Xcode and XcodeGen:

```bash
cd integrations/apple/sample
xcodegen generate
xcodebuild -project AYAAppleHost.xcodeproj -scheme AYAAppleHost \
  -sdk iphonesimulator -destination 'generic/platform=iOS Simulator' \
  CODE_SIGNING_ALLOWED=NO build
```

For real installed tests, choose an available simulator destination and run the sample's `AYAAppleHostUITests` suite. Do not infer green native import from a successful compile. Run the separate share-receiver and sample builds against the same exact source revision and record simulator runtime, app identity and test outputs.

## Host readiness checklist

- [ ] Pinned reviewed AYA commit/release; no conflicting copies of the package
- [ ] Host-authored, installed-version-matched AYA-RAS reference with strict validation
- [ ] User controls every handoff: exact preview, Copy, Share, Cancel
- [ ] Files return (if enabled) uses OS selection, scoped capped read, strict host validator and separate preview/Apply
- [ ] Wrong-card/ambiguous imports and rejected bytes never apply automatically
- [ ] Dismissal/supersession prevents late import completion or stale Apply
- [ ] Genuine native receipt is distinguished from Share Sheet display or assistant ingestion
- [ ] Device/accessibility and supported Files providers are tested and recorded separately
- [ ] Release description accurately names remaining unqualified gates, including #147

For architectural rationale and component names, consult [native integration](INTEGRATION.md), [Apple plan](PLAN.md) and [import return safety](../OUTPUT_RETURN_IMPORT.md). 
