import Foundation
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
              let columns = object["columns"] as? Int, (1...3).contains(columns),
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
    @State private var importTask: Task<Void, Never>?
    @State private var importLifetime = AYAImportSelectionLifetime()
    #if DEBUG
    @State private var cancellationProbe: String?
    #endif

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
                    #if DEBUG
                    if let cancellationProbe {
                        Text("Cancelled read: \(cancellationProbe)")
                            .accessibilityIdentifier("host.import.cancel.probe")
                    }
                    #endif
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
                            // Opening a new picker supersedes any outstanding
                            // read and makes stale import completions inert.
                            importTask?.cancel()
                            importTask = nil
                            importLifetime.cancel()
                            proposedLayout = nil
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

                    // Explicit text-only alternative when a saved file cannot
                    // be selected. This is a reusable AYA transport, while
                    // recognizing a Lantern JSON remains host-owned.
                    AYAImportPasteButton(title: "Paste JSON output") { file in
                        importTask?.cancel()
                        importTask = nil
                        importLifetime.cancel()
                        proposedLayout = nil
                        importError = nil
                        do {
                            try inspectSelectedFile(file)
                        } catch {
                            importError = error.localizedDescription
                        }
                    }
                }
                .padding(16)
                .frame(maxWidth: 560)
                .frame(maxWidth: .infinity)
            }
            .navigationTitle("AYA Sample")
            #if DEBUG
            .task {
                // Deterministic, synthetic cancellation control. No Files UI,
                // private-app access or claimed provider-revocation coverage.
                // An already cancelled caller must fail *before* scope access.
                guard ProcessInfo.processInfo.arguments.contains(
                    "AYA_UI_TEST_PRE_CANCELLED_IMPORT"
                ) else { return }
                cancellationProbe = await Task.detached {
                    () -> String in
                    withUnsafeCurrentTask { $0?.cancel() }
                    do {
                        _ = try await AYAAppleFileImport.snapshot(
                            userSelectedURL: URL(fileURLWithPath: "/aya-absent-cancel-probe.json")
                        )
                        return "unexpected-success"
                    } catch is CancellationError {
                        return "cancelled"
                    } catch {
                        return "unexpected-error"
                    }
                }.value
            }
            #endif
            .fileImporter(isPresented: $showFilePicker, allowedContentTypes: [.json]) { result in
                switch result {
                case .failure:
                    importError = "No readable JSON file was selected."
                case .success(let url):
                    receiveUserOpenedDocument(url)
                }
            }
            // Files > Share/Open In > AYA Lantern: Launch Services delivers a
            // user-chosen JSON document. This route uses the same scoped
            // bounded snapshot, semantic validation and explicit Apply as the
            // native fileImporter. It cannot browse another app's files.
            .onOpenURL { url in
                guard url.isFileURL else { return }
                receiveUserOpenedDocument(url)
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
            .onDisappear {
                importTask?.cancel()
                importTask = nil
                importLifetime.cancel()
                proposedLayout = nil
            }
            .alert("Cannot use this file", isPresented: Binding(
                get: { importError != nil },
                set: { if !$0 { importError = nil } }
            )) {
                Button("OK", role: .cancel) { importError = nil }
            } message: {
                Text(importError ?? "The import could not be completed.")
            }
        }
    }

    private func receiveUserOpenedDocument(_ url: URL) {
        // A new explicit user choice invalidates any pending document read,
        // preview, and completion. The URL may originate from either
        // fileImporter or the system's Open In entry point.
        guard url.isFileURL else { return }
        importTask?.cancel()
        importTask = nil
        proposedLayout = nil
        importError = nil
        let token = importLifetime.begin()
        importTask = Task { @MainActor in
            do {
                let file = try await AYAAppleFileImport.snapshot(userSelectedURL: url)
                try Task.checkCancellation()
                guard importLifetime.isCurrent(token) else { return }
                try inspectSelectedFile(file)
            } catch is CancellationError {
                // A superseded user selection cannot be published.
            } catch {
                if importLifetime.isCurrent(token) && !Task.isCancelled {
                    importError = error.localizedDescription
                }
            }
            if importLifetime.finish(token) { importTask = nil }
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
