# Apple drop-in distribution: root Swift Package discovery

**Status (2026-11-04): source-preview repository package; root SwiftPM and independent *synthetic* consumer qualified only when [PR #140](https://github.com/gamesbyian/AYA/pull/140) native/portable checks pass.** No semantically versioned public SDK release or independent commercial host has been certified. These instructions are for developers who choose to reuse code. AYA remains an Unlicensed, provider-neutral **interaction convention**; using the concept does not require using this package.

## Why a root manifest matters

Swift Package Manager resolves a remote Git repository as a package when a `Package.swift` is in its **repository root**. The original native iOS package lives in `integrations/apple/AYAApple`, and remains convenient for *local path dependency* and first-party XcodeGen sample builds. That nested layout alone is not an ordinary remote "Add Package Dependency" URL. The new **root `Package.swift`** declares the same `AYAProtocol` and `AYAApple` products and points its targets at their **existing nested source files**, so there is only one code implementation, no copied framework binary, no account, and no network dependency.

The root and nested manifests use the same minimum Swift tools and iOS 16 platform floor. CI compares their public target/product names and compiles root Swift tests, then constructs a **separate test-only SwiftPM consumer outside the repository checkout** and imports `AYAProtocol` to prove the package does not depend on sibling GitHub files or implicit workspace linkage. The native `AYAApple` target still requires the separate Xcode/iOS Simulator acceptance lane; a Linux consumer test only proves pure Swift source import/approval behavior.

## Xcode and SwiftPM adoption

For the source-preview main branch, in Xcode select **File → Add Package Dependencies**, enter:

    https://github.com/gamesbyian/AYA.git

Choose a **specific commit revision** for reproducible source-preview testing, or deliberately select the `main` branch if you accept continuously changing APIs. Select **AYAApple** for the native SwiftUI/UIKit card and transport and **AYAProtocol** for pure Foundation validation and import decisions. Both products have the same public module names when built from the root and nested manifests.

Swift package consumers can also declare:

```swift
dependencies: [
    .package(url: "https://github.com/gamesbyian/AYA.git", revision: "<tested-commit-sha>")
]
```

Then add the relevant product:

```swift
.product(name: "AYAProtocol", package: "AYAApple")
// or .product(name: "AYAApple", package: "AYAApple")
```

The angle-bracket revision above is a developer placeholder, **not** a currently published version. No SemVer release/tag should be claimed until a concrete tagged revision has passed source, native iPhone/iPad, independent consuming host, privacy and artifact integrity checks. A package-version range such as `from: "1.0.0"` must **not** be suggested while no qualifying AYA Apple release has been tagged.

For local development, existing adopters may continue to use:

    integrations/apple/AYAApple

with `.package(path: ".../integrations/apple/AYAApple")`. Host developers must bundle their own exact installed bundle ID/version-matched AYA-RAS guide and truthful output-import instructions; the fictional Lantern fixture is not a real host guide.

## Release/compatibility gates

1. Both SwiftPM manifests agree on public products, targets and available source. One CI run builds/test the *root package*, another compiles the nested package and the actual iOS SwiftUI UIKit app, and one outside-tree Linux client imports the pure Foundation library.
2. A second independently designed **native** host must build and use the public `AYAApple` UI/transport product in a real iOS Simulator, with its own authored guide. Copying the current Lantern first-party app into a different directory is a useful packaging check but does not establish independent implementation quality.
3. Real assistants must be tested by dated app/version/iOS/transport against the actual approved text and attachment. The synthetic foreign extension passed plain text and .txt byte reception ([PR #133 / CI 41781406186](https://github.com/gamesbyian/AYA/actions/runs/41781406186)), but does not prove any third-party AI model consumed the packet.
4. Actual Files return and semantic host apply, physical-device VoiceOver and iPad, lifecycle/background, security review, SemVer API policy, source provenance and public tag policy remain separate release requirements.
5. A release must not introduce tracking, service accounts, a mandatory AI provider, hidden assistant output watchers, cross-app sandbox scanning or automatic artifact application.

**Official documentation:** [Swift PackageDescription](https://developer.apple.com/documentation/packagedescription) (manifest required in package root), [adding dependencies](https://docs.swift.org/swiftpm/documentation/packagemanagerdocs/addingdependencies/), [Apple package publishing](https://developer.apple.com/documentation/xcode/publishing-a-swift-package-with-xcode). See [Apple integration](INTEGRATION.md), [architecture](ARCHITECTURE.md), [plan](PLAN.md), and [module portability](../MODULE_PORTABILITY.md).
