// swift-tools-version: 5.9
import PackageDescription

// Root discovery manifest for Xcode's "Add Package Dependency" workflow.
// Source stays in the existing, independently testable Apple subpackage.
// The two manifests deliberately expose identical public library products.
// No binary artifacts, assistant APIs, accounts, network or build-time scripts.
let appleSource = "integrations/apple/AYAApple"

let package = Package(
    name: "AYAApple",
    platforms: [.iOS(.v16)],
    products: [
        .library(name: "AYAProtocol", targets: ["AYAProtocol"]),
        .library(name: "AYAApple", targets: ["AYAApple"])
    ],
    targets: [
        .target(
            name: "AYAProtocol",
            path: "\(appleSource)/Sources/AYAProtocol"
        ),
        .target(
            name: "AYAApple",
            dependencies: ["AYAProtocol"],
            path: "\(appleSource)/Sources/AYAApple"
        ),
        .testTarget(
            name: "AYAProtocolTests",
            dependencies: ["AYAProtocol"],
            path: "\(appleSource)/Tests/AYAProtocolTests",
            resources: [.copy("Fixtures")]
        )
    ]
)
