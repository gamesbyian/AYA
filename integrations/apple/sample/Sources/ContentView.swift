import Foundation
import CoreFoundation
import SwiftUI
import UniformTypeIdentifiers
import AYAApple
import AYAProtocol

/// A fictional, first-party demonstration host. Its format and controls must
/// never become defaults of the generic AYA SDK.
private struct LayoutProposal {
    let columns: Int
    let accent: String

    static func recognizes(_ bytes: Data) -> Bool {
        guard let object = (try? JSONSerialization.jsonObject(with: bytes)) as? [String: Any] else {
            return false
        }
        return object["aya_demo_layout"] as? String == "v1"
    }

    static func decode(_ bytes: Data) -> LayoutProposal? {
        guard let object = (try? JSONSerialization.jsonObject(with: bytes)) as? [String: Any],
              Set(object.keys) == Set(["aya_demo_layout", "columns", "accent"]),
              object["aya_demo_layout"] as? String == "v1",
              // JSONSerialization bridges true to NSNumber(1) and even 1.0 to
              // Int(1) under Swift's normal casts. Keep the fictional host's
              // integer schema strict before any user-confirmed Apply.
              let columnNumber = object["columns"] as? NSNumber,
              CFGetTypeID(columnNumber) != CFBooleanGetTypeID(),
              ["c", "C", "s", "S", "i", "I", "l", "L", "q", "Q"]
                  .contains(String(cString: columnNumber.objCType)),
              let columns = columnNumber as? Int, (1...3).contains(columns),
              let accent = object["accent"] as? String, ["warm", "cool"].contains(accent)
        else { return nil }
        return LayoutProposal(columns: columns, accent: accent)
    }
}

struct ContentView: View {
    @State private var showFilePicker = false
    @State private var proposedLayout: LayoutProposal?
    @State private var columns = 1
    @State private var accent = "warm"
    @State private var importError: String?

    private let guide: String = {
        guard let url = Bundle.main.url(forResource: "aya-guide", withExtension: "md"),
              let contents = try? String(contentsOf: url, encoding: .utf8) else {
            return "" // AYAHelpCard rejects, never exports fabricated guidance.
        }
        #if DEBUG
        // Synthetic negative control. A compiled debug fixture with a stale
        // bundled reference must never reach user review or outbound sharing.
        if ProcessInfo.processInfo.arguments.contains("AYA_UI_TEST_STALE_GUIDE") {
            return contents.replacingOccurrences(
                of: "app_version_min: 1.0.0", with: "app_version_min: 0.0.0"
            )
        }
        #endif
        return contents
    }()

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 22) {
                    Text("Lantern Layout Demo")
                        .font(.title2.bold())
                    Text("A fictional, temporary layout editor that demonstrates an AYA handoff and a separate manual JSON import.")
                        .foregroundStyle(.secondary)
                    HStack {
                        Text("Columns: \(columns)")
                        Spacer()
                        Text("Accent: \(accent)")
                    }
                    .font(.headline)
                    .accessibilityIdentifier("host.layout.state")
                    Button("Reset demo layout") {
                        columns = 1
                        accent = "warm"
                    }
                    .frame(minHeight: 44)
                    .accessibilityIdentifier("host.layout.reset")

                    AYAHelpCard(
                        guide: guide,
                        explanation: "Ask an assistant for guidance or a demo-layout JSON proposal.",
                        outputInstructions: "For a demo-layout JSON, save the raw file in Files and use Import saved agent output. This sample validates and previews it before applying.",
                        onImportRequested: {
                            importError = nil
                            showFilePicker = true
                        }
                    )
                    .transformEnvironment(\.dynamicTypeSize) { size in
                        #if DEBUG
                        // Deterministic first-party accessibility fixture.
                        // The override is absent in Release and never reaches
                        // the SDK or an independently adopting host.
                        if ProcessInfo.processInfo.arguments.contains("AYA_UI_TEST_LARGE_TYPE") {
                            size = .accessibility3
                        }
                        #endif
                    }


                }
                .padding(16)
                .frame(maxWidth: 560)
                .frame(maxWidth: .infinity)
            }
            .safeAreaInset(edge: .top, spacing: 0) {
                if let error = importError {
                    // A persistent, immediately readable host-owned error
                    // surface. System alert presentation can conflict with
                    // dismissal of the OS Files picker on older iOS runtimes.
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Cannot use this file")
                            .font(.headline)
                            .accessibilityIdentifier("host.import.error.title")
                        Text(error)
                            .font(.subheadline)
                            .accessibilityIdentifier("host.import.error")
                        Button("Dismiss import error") {
                            importError = nil
                        }
                        .frame(minHeight: 44)
                        .accessibilityIdentifier("host.import.error.dismiss")
                    }
                    .padding(16)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(.regularMaterial)
                    // Only leaf elements carry identifiers: a container-level
                    // identifier can propagate to children in SwiftUI and
                    // make their stable accessibility names unqueryable.
                }
            }
            .navigationTitle("AYA Sample")
            // Include malformed, mislabelled, and oversized candidate files in the\n            // user-visible Files browser. UTType filtering is advisory: the\n            // bounded snapshot and host semantic validator decide acceptance.\n            .fileImporter(isPresented: $showFilePicker, allowedContentTypes: [.item]) { result in
                switch result {
                case .failure:
                    importError = "No readable JSON file was selected."
                case .success(let url):
                    Task {
                        do {
                            let file = try await AYAAppleFileImport.snapshot(userSelectedURL: url)
                            try inspectSelectedFile(file)
                        } catch {
                            importError = error.localizedDescription
                        }
                    }
                }
            }
            .confirmationDialog(
                "Apply imported layout to this demo?",
                isPresented: Binding(
                    get: { proposedLayout != nil },
                    set: { if !$0 { proposedLayout = nil } }
                )
            ) {
                Button("Apply to demo") {
                    if let proposal = proposedLayout {
                        columns = proposal.columns
                        accent = proposal.accent
                    }
                    proposedLayout = nil
                }
                Button("Cancel", role: .cancel) { proposedLayout = nil }
            } message: {
                Text("The proposed layout changes this sample to \(proposedLayout?.columns ?? 1) columns with a \(proposedLayout?.accent ?? "warm") accent. No files are modified.")
            }

        }
    }

    private func inspectSelectedFile(_ file: AYAImportFile) throws {
        let route = AYAImportRoute(
            id: "layout", title: "Demo layout",
            recognizes: LayoutProposal.recognizes,
            validates: { LayoutProposal.decode($0) != nil }
        )
        let registry = try AYAImportRegistry(routes: [route])
        switch registry.inspect(file, cardRouteID: "layout") {
        case .ready:
            // Recheck concrete values before presenting the host's own preview.
            guard let proposal = LayoutProposal.decode(file.data) else {
                importError = "The JSON layout did not pass the host's checks."
                return
            }
            proposedLayout = proposal // only the later Apply action mutates state
        case .unusable, .ambiguous, .unrecognized:
            importError = "This file is not a valid Lantern demo-layout JSON."
        }
    }
}
