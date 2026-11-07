import Foundation
import SwiftUI

/// Independently installed, disposable QA fixture provider. The containing
/// application is never an AYA SDK runtime dependency or a production inbox.
@main
struct AYAShareQAHostApp: App {
    var body: some Scene {
        WindowGroup { QAProviderPreparationView() }
    }
}

private struct QAProviderPreparationView: View {
    @State private var result = "No Files test documents prepared"
    @State private var preparedDirectory: URL?
    @State private var selectedFixture = "aya-layout-valid.json"

    // Only the three synthetic QA samples are exposed as explicit document
    // outgoing actions. Real user content is never read or shared.
    private let shareableFixtures = [
        "aya-layout-valid.json",
        "aya-layout-invalid.json",
        "aya-layout-oversized.json"
    ]

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text("AYA Share QA").font(.title)
                Text("A disposable, separate application for verifying Share Sheet receipts and user-selected Files return into another host.")
                Text("To test Files on an actual iPhone or iPad, prepare seven synthetic JSON documents, then switch to the AYA sample and select them using the system Files picker.")
                    .foregroundStyle(.secondary)
                Button("Prepare seven Files test documents") {
                    do {
                        try QAProviderFixtures.prepare()
                        preparedDirectory = try FileManager.default.url(
                            for: .documentDirectory, in: .userDomainMask,
                            appropriateFor: nil, create: false
                        )
                        result = "Prepared: seven verified JSON files in this QA app's Documents folder"
                    } catch {
                        preparedDirectory = nil
                        result = "Preparation failed: \(error.localizedDescription)"
                    }
                }
                .frame(minHeight: 44)
                .accessibilityIdentifier("qa.prepare.files")
                Text(result)
                    .accessibilityIdentifier("qa.prepare.status")
                    .textSelection(.enabled)
                if let preparedDirectory {
                    Picker("Synthetic document to send", selection: $selectedFixture) {
                        ForEach(shareableFixtures, id: \.self) { filename in
                            Text(filename).tag(filename)
                        }
                    }
                    .accessibilityIdentifier("qa.openin.file")
                    ShareLink(item: preparedDirectory.appendingPathComponent(
                        selectedFixture, isDirectory: false
                    )) {
                        Label("Share selected JSON with another app",
                              systemImage: "square.and.arrow.up")
                            .frame(minHeight: 44)
                    }
                    .accessibilityIdentifier("qa.openin.share")
                    Text("Choose AYA Lantern in iOS's system sharing interface if it is offered. This is an actual cross-app document handoff, not a direct call into AYA.")
                        .font(.footnote)
                }
                Text("No user files are examined. Existing QA documents are verified, never silently overwritten. Delete this disposable app to remove its fixtures.")
                    .font(.footnote)
            }
            .padding()
        }
    }
}

private enum QAProviderFixtures {
    private enum FixtureError: LocalizedError {
        case contentMismatch(String)
        var errorDescription: String? {
            switch self {
            case .contentMismatch(let name):
                return "Existing \(name) differs from the expected QA fixture. Reinstall the disposable QA app before retrying."
            }
        }
    }

    static func prepare() throws {
        let fm = FileManager.default
        let folder = try fm.url(for: .documentDirectory, in: .userDomainMask,
                                appropriateFor: nil, create: true)
        let items: [(String, Data)] = [
            ("aya-layout-valid.json", Data("{\"aya_demo_layout\":\"v1\",\"columns\":3,\"accent\":\"cool\"}\n".utf8)),
            ("aya-layout-invalid.json", Data("{\"aya_demo_layout\":\"v1\",\"columns\":99,\"accent\":\"invalid\"}\n".utf8)),
            ("aya-layout-boolean.json", Data("{\"aya_demo_layout\":\"v1\",\"columns\":true,\"accent\":\"cool\"}\n".utf8)),
            ("aya-layout-float.json", Data("{\"aya_demo_layout\":\"v1\",\"columns\":1.0,\"accent\":\"cool\"}\n".utf8)),
            ("aya-layout-aaa-control.json", Data("{\"aya_demo_layout\":\"v1\",\"columns\":3,\"accent\":\"cool\"}\n".utf8)),
            ("aya-layout-zzz-invalid.json", Data("{\"aya_demo_layout\":\"v1\",\"columns\":99,\"accent\":\"invalid\"}\n".utf8))
        ]
        let prefix = Data("{\"aya_demo_layout\":\"v1\",\"columns\":3,\"accent\":\"cool\"}".utf8)
        let oversizedCount = 4 * 1_024 * 1_024 + 1
        var oversized = Data(capacity: oversizedCount)
        oversized.append(prefix)
        oversized.append(Data(repeating: 0x20, count: oversizedCount - prefix.count))
        var complete = items
        complete.append(("aya-layout-oversized.json", oversized))

        // Write only inside the owning QA application's Documents. The
        // importing sample remains a different sandbox and receives nothing
        // until the person deliberately chooses a file through Files.
        for (name, content) in complete {
            let url = folder.appendingPathComponent(name, isDirectory: false)
            if fm.fileExists(atPath: url.path) {
                guard try Data(contentsOf: url) == content else {
                    throw FixtureError.contentMismatch(name)
                }
            } else {
                try content.write(to: url, options: .atomic)
            }
        }
    }
}
