# Apple implementation architecture and trust contracts

**Status: engineering decision record, 2026-11-03.** See [research](RESEARCH.md), [work plan](PLAN.md), the [cross-host module standard](../MODULE_PORTABILITY.md), [shared packet authoring](../packet/AUTHORING_STANDARD.md) and [output return/import](../OUTPUT_RETURN_IMPORT.md).

## Core concept and layering

AYA is a convention; adapters are optional. Source-derived **host capabilities, question, task-specific kit/schema, privacy disclosure, artifact instructions and version truth** remain identical in meaning across Android and iOS. Platform adapters implement only identity lookup, UI review, transport and user-picked output selection.

| Layer | Contract / decision |
| --- | --- |
| Common semantic contract | AYA-RAS v1 exact-built reference, same 12 sections; reusable help / creative / structured / translation / filesystem capability classes; same human approval and output-import boundaries |
| Portable manifest | `aya-handoff/v1` is an optional developer interchange preview. Its `host.packageId` key reflects Android heritage; interpret as platform application identifier **only in documented cross-platform uses** until a backward-compatible v2 schema is designed. Do not rename v1 and break established consumers. |
| iOS domain model | Swift Package `AYAProtocol`: validation and render/approved-text data only; platform-independent Foundation code with deterministic tests |
| iOS transport | `AYAApple`: system Share Sheet presentation of one approved String **or** a uniquely named UTF-8 .txt file; system clipboard on a distinct explicit user action |
| iOS host integration | Build a source-supplied SwiftUI/UIViewController card: Compose question, verify bundled `aya-guide.md` against actual `Bundle.main.bundleIdentifier` + `CFBundleShortVersionString`, show editable exact payload, Cancel/Copy/Share; no auto-share on creating the draft |
| Return/import | Host's `fileImporter` / `UIDocumentPickerViewController`, scoped access plus coordinated off-main read, bounded private snapshot and independent registered host format checks; route by content rather than chosen card or filename |
| Optional system features | App Intents/App Shortcuts for declared non-destructive capability preparation, deferred until independent host implementation and explicit confirmation designs exist |
| Distribution | Unlicense SwiftPM source package, no mandatory service/entitlement/API key/domain or SDK dependency on any AI provider |

## Lifecycles

**Outbound:** host verified app version + guide → local question → compose packet → **editable review** → explicit Copy or Share → system UI. A successful return from `UIActivityViewController` proves at most local activity completion. AYA records no destination and learns nothing from assistant conversations.

**Inbound:** user saves file in destination → user invokes host's Import action → system picker grants access → background bounded coordinated read into private snapshot → host registry probes *actual bytes* → wrong-card/multiple matches/foreign hints treated as guidance, not proof → host semantic validation → impact preview → explicit separate apply confirmation → atomic host transaction when supported. No automatic import, execution or background watching.

**Privacy:** file is user-approved and may go to a third-party service; edited text is the only content placed on the clipboard or exported. Temporaries belong in a private app-controlled cache directory with unpredictable names. No immediate deletion on share-dismissal and no export of other document contents. No claim of automatic redaction.

## iOS-specific guards

- Use genuine **iOS Bundle ID** and installed version, not a hard-coded Android package name, build number, or marketing app version guessed from source metadata.
- `platform: ios` applies to both iPhone and iPad adaptations; separate `platform: android` guides remain invalid for the Apple guarded API.
- Preserve exact guide provenance metadata and enforce nonempty 12 sections. Android's AYA-RAS current verifier is a useful precedent, but not a formal proof that two independently coded verifiers have identical behavior. Add common language-neutral fixture coverage.
- Keep plain text and document sharing **separate**. Apple receivers advertise different accepted types; don't silently attach a file when a user chose text-only or claim both were sent together.
- Share popovers on iPad need a real view/source-rect anchor; SwiftUI share sheets must also be tested under iPad multitasking, rotation and large Dynamic Type.
- On import, treat imported path, claimed MIME/UTType, optional AYA envelope, `request_id` and deep-link parameters as **untrusted hints**. Never apply without validating bytes and host policy.
- App Intents and deep links must not become shortcuts around exact-version checks or destructive import confirmation.
- Avoid provider-specific URL schemes, private APIs, class-name probing, jailbreak-dependent access, third-party container scans and background output polling.

## First SwiftPM foundation release boundary

The initial `integrations/apple/AYAApple` source preview intentionally implements only exact-version reference shape checks, an editable draft data model, explicit `AYAApprovedPacket`, and a user-invoked outgoing UIKit share/clipboard helper. **It does not yet implement:** native card and review UI, a complete file importer, share-extension receiver, App Intents, third-party AI ingress testing, physical-device acceptance or a published package.

A Linux SwiftPM test can verify `AYAProtocol` only. A macOS job can compile general Swift targets, but must not be misreported as an iOS simulator build of `UIKit` code. An actual Xcode iOS Simulator SDK compile passed at [run 41600191635](https://github.com/gamesbyian/AYA/actions/runs/41600191635), establishing S1 native compiler evidence. Installed iOS Simulator app and interaction/receiver integration tests remain the next gate.
