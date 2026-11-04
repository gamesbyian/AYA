// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "AYAApple",
    platforms: [.iOS(.v16)],
    products: [
        .library(name: "AYAProtocol", targets: ["AYAProtocol"]),
        .library(name: "AYAApple", targets: ["AYAApple"])
    ],
    targets: [
        .target(name: "AYAProtocol"),
        .target(name: "AYAApple", dependencies: ["AYAProtocol"]),
        .testTarget(
            name: "AYAProtocolTests",
            dependencies: ["AYAProtocol"],
            resources: [.copy("Fixtures")]
        )
    ]
)
