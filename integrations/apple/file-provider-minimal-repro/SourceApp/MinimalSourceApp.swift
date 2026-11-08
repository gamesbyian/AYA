import Foundation
import SwiftUI

/// Disposable Apple File Provider reproduction. No AYA SDK, network access,
/// App Groups, custom File Provider extensions, or cross-container reads.
@main
struct MinimalSourceApp: App {
    var body: some Scene {
        WindowGroup { SourceView() }
    }
}

private struct SourceView: View {
    @State private var result = "No documents prepared"

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text("Minimal Files Source").font(.title2.bold())
                Text("This app publishes its own Documents folder in Files. Use a fresh simulator or uninstall the app between one-file and seven-file controls.")
                    .font(.subheadline)
                Button("Prepare only malformed JSON") {
                    prepare(includeAll: false)
                }
                .accessibilityIdentifier("minimal.source.one")
                .frame(minHeight: 44)
                Button("Prepare seven documents") {
                    prepare(includeAll: true)
                }
                .accessibilityIdentifier("minimal.source.seven")
                .frame(minHeight: 44)
                Text(result)
                    .accessibilityIdentifier("minimal.source.status")
                Text("Next: launch Minimal Files Consumer, tap Pick document, then browse On My iPhone → Minimal Files Source. Select aya-layout-invalid.json and observe the callback state.")
                    .font(.footnote)
            }
            .padding()
        }
    }

    private func prepare(includeAll: Bool) {
        do {
            let folder = try FileManager.default.url(
                for: .documentDirectory,
                in: .userDomainMask,
                appropriateFor: nil,
                create: true
            )
            let valid = Data("{\"aya_demo_layout\":\"v1\",\"columns\":3,\"accent\":\"cool\"}\n".utf8)
            let invalid = Data("{\"aya_demo_layout\":\"v1\",\"columns\":99,\"accent\":\"invalid\"}\n".utf8)
            var items: [(String, Data)] = [
                ("aya-layout-invalid.json", invalid)
            ]
            if includeAll {
                items += [
                    ("aya-layout-valid.json", valid),
                    ("aya-layout-boolean.json", Data("{\"aya_demo_layout\":\"v1\",\"columns\":true,\"accent\":\"cool\"}\n".utf8)),
                    ("aya-layout-float.json", Data("{\"aya_demo_layout\":\"v1\",\"columns\":1.0,\"accent\":\"cool\"}\n".utf8)),
                    ("aya-layout-aaa-control.json", valid),
                    ("aya-layout-zzz-invalid.json", invalid)
                ]
                let length = 4 * 1_024 * 1_024 + 1
                let prefix = Data("{\"aya_demo_layout\":\"v1\",\"columns\":3,\"accent\":\"cool\"}".utf8)
                var oversized = Data(capacity: length)
                oversized.append(prefix)
                oversized.append(Data(repeating: 0x20, count: length - prefix.count))
                items.append(("aya-layout-oversized.json", oversized))
            }

            // Deterministic, idempotent staging. Existing conflicting files
            // are never replaced. No private or user documents are inspected.
            for (name, bytes) in items {
                let url = folder.appendingPathComponent(name, isDirectory: false)
                if FileManager.default.fileExists(atPath: url.path) {
                    guard try Data(contentsOf: url) == bytes else {
                        throw NSError(
                            domain: "MinimalFilesSource", code: 1,
                            userInfo: [NSLocalizedDescriptionKey: "Existing fixture differs: \(name)"]
                        )
                    }
                } else {
                    try bytes.write(to: url, options: .atomic)
                }
            }
            result = "Prepared \(items.count) verified document(s)"
        } catch {
            result = "Staging failed: \(error.localizedDescription)"
        }
    }
}
