# Native iOS Files return: independent local-provider acceptance

**Status (2026-11-04): implementation and installed-simulator tests in [PR #139](https://github.com/gamesbyian/AYA/pull/139), not yet accepted.** This is a disposable, fictional cross-app test fixture. It is separate from the already verified [outbound iOS QA receiver](RECEIVER_QA.md).

## What the imported file can and cannot authorize

The user saves a generated artifact and later invokes the host's visible **Import saved agent output** action. That is a distinct, independent consent operation. The Files picker returns a **security-scoped URL** to the specific user-selected file, not permission to monitor an AI app, inspect arbitrary directories, recover a conversation or execute arbitrary generated instructions. The host calls `startAccessingSecurityScopedResource`, uses `NSFileCoordinator` to read on a background task, bounds the bytes, hashes them, then releases access. The returned snapshot is immutable local input for **host-authored recognition, semantic validation, preview and final Apply confirmation**.

A chosen filename, extension, `UTType`, adjacent card, app name or producer identity cannot authorize import. The fixture uses distinct synthetic JSON files; the host must independently parse the actual bytes. Importing invalid JSON must leave state unchanged and offer no Apply. Importing valid JSON must not change state until an explicit *subsequent* Apply; Cancel must preserve existing values. On real providers, changes/revocation/races must be handled without partial application.

## Portable synthetic local File Provider fixture

Apple's [File Provider documentation](https://developer.apple.com/documentation/fileprovider) and [Launch Services keys](https://developer.apple.com/library/archive/documentation/General/Reference/InfoPlistKeyReference/Articles/LaunchServicesKeys.html) describe that an iOS app setting both `UIFileSharingEnabled=YES` and `LSSupportsOpeningDocumentsInPlace=YES` exposes its **own Documents** through the system local File Provider. This is enabled **only** in the disposable `integrations/apple/qa-share-receiver` containing app, never the AYA SDK or the importing host.

The macOS workflow builds and installs that app on a disposable iOS Simulator, then places two small synthetic JSON files in **its own QA Documents** via `simctl get_app_container`. This staging supplies only fixture data. The first-party Lantern host remains in its **different sandbox** and **must** open the user-facing `fileImporter` system UI to select either document, receiving a scoped URL and using its real parsing/confirmation path. The test must not pass an arbitrary path or file bytes directly to `AYAImportFile` and call that an installed picker test.

The fixture files are:

- `aya-layout-valid.json`: exact documented fictional host format, 3 columns and cool accent
- `aya-layout-invalid.json`: same nominal format but an out-of-range column count and unsupported accent

The QA app itself makes no network calls, telemetry requests, writes to the host's data, or user-facing production changes. Neither QA fixture is an AI output.

## Acceptance gates

| Scenario | Must prove |
| --- | --- |
| Actual Files picker | Host user action launches the OS picker; a file visible under **On My iPhone → AYA Share QA** can be explicitly chosen |
| Valid foreign snapshot | The host obtains the independently packaged JSON's bytes and recognizes/validates them; visual layout remains unchanged until Apply |
| Cancel | Closing the host preview leaves the old 1-column, warm-accent state |
| Apply | A second explicit selection and positive Apply changes only the fictional host's 3-column/cool-accent state |
| Invalid foreign JSON | No route to Apply is offered; error is visible; prior state persists |
| No Files provider / dismissed picker | Missing recipient or Cancel does not produce a fake imported file or mutation; a test must fail, not silently skip absent fixture |
| Future negative cases | No scope, revoked provider, file mutated during coordination, >4 MiB/16 MiB cap, wrong card and multiple matching host formats all reject or require correct host-directed confirmation |

**Evidence boundary:** a green test here would prove a first-party app reading a user-selected file from a *different local sandbox* via the system provider on a dated iOS Simulator. It would not establish iCloud sync, third-party cloud File Providers, revocation races, physical iPhone/iPad accessibility, arbitrary production importer correctness or compatibility with any model.

## Relevant official Apple references

- [SwiftUI fileImporter](https://developer.apple.com/documentation/swiftui/view/fileimporter%28ispresented%3Aallowedcontenttypes%3Aoncompletion%3A%29): URLs from the picker are security-scoped, Cancel has no success callback
- [Security-scoped URLs](https://developer.apple.com/documentation/foundation/url/startaccessingsecurityscopedresource%28%29): granted access requires balanced start/stop; kernel-resource leaks on missing stop
- [Local File Provider and document browser](https://developer.apple.com/documentation/fileprovider): other apps' exported Documents are system-browsable only with the proper opt-in keys
- [LSSupportsOpeningDocumentsInPlace](https://developer.apple.com/library/archive/documentation/General/Reference/InfoPlistKeyReference/Articles/LaunchServicesKeys.html): reads from other providers can change concurrently and require coordinated access

For the portable content-recognition contract, see [Output Return & Import](../OUTPUT_RETURN_IMPORT.md), [Apple architecture](ARCHITECTURE.md), [Apple rollout plan](PLAN.md) and [module portability](../MODULE_PORTABILITY.md).
