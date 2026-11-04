# iOS reference authoring ↔ runtime parity

**Status:** deterministic shared fixtures and tests; evidence is limited to structural reference acceptance and must never be interpreted as accuracy of developer-authored statements, installed-app UI behavior or AI recipient ingestion.

## Purpose

AYA's authoring linter (`tools/validate_guide.py --platform ios`) and native `AYAReference` check overlapping but distinct properties. A guide may pass structural authoring and still fail an installed app's **exact app ID/version** guard, for example when a guide from an older build is accidentally packaged. Failing such a guide at runtime is essential; the offline linter cannot know which app is installed.

The shared reference case matrix is `integrations/apple/AYAApple/Tests/AYAProtocolTests/Fixtures/cases.json`, applied to its fictional `reference-ios.md` fixture. Every case specifies two explicit expectations:

- `offlineAccepts`: whether the Python validator reports structural `ok` for the iOS profile. Python warnings are separate; the existing release guide check may require `--strict`.
- `runtimeAccepts`: whether Swift `AYAReference(guide:installedAppID:installedVersion:)` accepts the mutated guide for the matrix's *actual installed* identity.

`wrong-installed-app` and `wrong-installed-version` are expected to pass offline structure but fail Swift's exact identity/installed version check. Other cases test shared rejections for metadata, platform, section count/contents and placeholders. No rule should be loosened solely to force identical expectations.

## How to exercise

- Portable Python: `python3 -m unittest tools.test_apple_reference_parity`
- Portable SwiftPM from `integrations/apple/AYAApple`: `swift test`
- iOS Simulator SDK and first-party host still require the targeted `apple-swift.yml` Xcode build; the reference matrix is not a UI or Share Sheet test.

Each mutation must target exactly one substring in the fixture. Both languages reject stale cases where an intended substring silently disappears. Add a case here when evolving the AYA-RAS reference schema. Changes to required major sections, metadata validation or exact-version semantics need coordinated authoring/runtime tests and a review of Android's separate reference verifier; do not accidentally accept an Android guide for an iOS host.

This is a reusable contract test across at least two plausible host classes. All examples are fictional. Nothing in the fixture grants access to another app, a user's private files, a model or an importer.
