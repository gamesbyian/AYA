import Foundation
import SwiftUI
import UniformTypeIdentifiers

/// Deliberately minimal unrelated consumer. It does NOT import AYA, access
/// the source sandbox, read selected bytes or perform file coordination. Its
/// sole purpose is to establish whether Apple's system picker produces any
/// completion callback for an item visible in Files.
@main
struct MinimalConsumerApp: App {
    var body: some Scene {
        WindowGroup { ConsumerView() }
    }
}

private struct ConsumerView: View {
    @State private var choosing = false
    @State private var result = "No picker opened"
    @State private var callbackCount = 0

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Minimal Files Consumer")
                .font(.title2.bold())
            Text("Pick a JSON document from Minimal Files Source using Apple's real Files interface. This app only reports whether the system delivered a callback.")
                .font(.subheadline)
            Button("Pick document") {
                result = "picker-opened"
                choosing = true
            }
            .accessibilityIdentifier("minimal.consumer.choose")
            .frame(minHeight: 44)
            Text("State: \(result)")
                .accessibilityIdentifier("minimal.consumer.state")
                .textSelection(.enabled)
            Text("Callbacks: \(callbackCount)")
                .accessibilityIdentifier("minimal.consumer.count")
            Text("Closing Files with Cancel is a deliberate no-op; it is not a successful file selection.")
                .font(.footnote)
            Spacer(minLength: 0)
        }
        .padding()
        // Match the broad UTType.item probe from AYA's seven-file tests.
        // Do not add a snapshot reader: the original failure is pre-callback.
        .fileImporter(isPresented: $choosing, allowedContentTypes: [.item]) { pick in
            callbackCount += 1
            switch pick {
            case .success(let url):
                result = "callback-success: \(url.lastPathComponent)"
            case .failure(let error):
                result = "callback-error: \(error.localizedDescription)"
            }
        }
    }
}
