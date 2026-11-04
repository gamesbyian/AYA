import SwiftUI

/// Disposable installation container for the separately packaged Share Extension.
/// The host app itself never reads AYA data and is not an AYA runtime dependency.
@main
struct AYAShareQAHostApp: App {
    var body: some Scene {
        WindowGroup {
            VStack(spacing: 12) {
                Text("AYA Share QA")
                    .font(.title)
                Text("This disposable test app installs a separate Share Extension for verifying bytes received through the iOS Share Sheet.")
                    .multilineTextAlignment(.center)
                Text("There is no account, backend, inbox, saved document or automatic import.")
                    .font(.footnote)
                    .foregroundStyle(.secondary)
            }
            .padding()
        }
    }
}
