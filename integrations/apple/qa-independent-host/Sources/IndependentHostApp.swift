import Foundation
import SwiftUI
import AYAApple

/// Independent fictional help-only host: no Lantern layout types, import
/// callback, or dependency on another source checkout. Demonstrates using the
/// ROOT SwiftPM AYAApple product via the normal public package identity.
@main
struct IndependentHostApp: App {
    var body: some Scene {
        WindowGroup {
            ReadingListHome()
        }
    }
}

private struct ReadingListHome: View {
    @State private var saved = 0
    private let guide: String = {
        guard let url = Bundle.main.url(forResource: "aya-guide", withExtension: "md"),
              let content = try? String(contentsOf: url, encoding: .utf8) else {
            return "" // AYAHelpCard must reject a missing source guide.
        }
        return content
    }()

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 18) {
                    Text("Reading Queue QA")
                        .font(.title.bold())
                    Text("Disposable, entirely local reading-list example.")
                        .foregroundStyle(.secondary)
                    Text("Saved titles: \(saved)")
                        .accessibilityIdentifier("reader.saved.count")
                    Button("Add sample title") {
                        saved += 1
                    }
                    .frame(minHeight: 44)
                    .accessibilityIdentifier("reader.add")
                    AYAHelpCard(
                        guide: guide,
                        explanation: "Ask your assistant about this fictional reading list.",
                        outputInstructions: "This sample has no file importer. Apply any suggestions manually using its visible controls."
                    )
                }
                .padding(18)
            }
            .navigationTitle("Reading QA")
        }
    }
}
