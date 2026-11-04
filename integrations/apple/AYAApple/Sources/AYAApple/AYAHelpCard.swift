#if os(iOS)
import SwiftUI
import UIKit
import AYAProtocol

/// A host-neutral, optional AYA help card. The host supplies its real bundled
/// guide; actual Bundle identity is checked when the user taps Ask.
@available(iOS 16.0, *)
public struct AYAHelpCard: View {
    private let guide: String
    private let title: String
    private let explanation: String
    private let outputInstructions: String
    private let onImportRequested: (() -> Void)?
    @State private var question = ""
    @State private var reviewText = ""
    @State private var showingReview = false
    @State private var errorMessage: String?
    @FocusState private var questionFocused: Bool

    public init(
        guide: String,
        title: String = "Ask Your Agent",
        explanation: String = "Ask your preferred AI assistant about this app.",
        outputInstructions: String,
        onImportRequested: (() -> Void)? = nil
    ) {
        self.guide = guide
        self.title = title
        self.explanation = explanation
        self.outputInstructions = outputInstructions
        self.onImportRequested = onImportRequested
    }

    public var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Label(title, systemImage: "questionmark.circle")
                .font(.headline)
                .accessibilityAddTraits(.isHeader)
            Text(explanation)
                .font(.subheadline)
            Text("Your question and the app's reference are shown for editing before you choose where to share them.")
                .font(.footnote)
                .foregroundStyle(.secondary)
            TextField("Optional question", text: $question, axis: .vertical)
                .lineLimit(2...4)
                .textFieldStyle(.roundedBorder)
                .focused($questionFocused)
                .accessibilityIdentifier("aya.question")

            Button {
                questionFocused = false
                openReview()
            } label: {
                Text("Ask Your Agent")
                    .frame(maxWidth: .infinity, minHeight: 44)
            }
            .buttonStyle(.borderedProminent)
            .accessibilityIdentifier("aya.ask")

            Text(outputInstructions)
                .font(.footnote)
                .foregroundStyle(.secondary)

            if let onImportRequested {
                Button(action: onImportRequested) {
                    Label("Import saved agent output", systemImage: "square.and.arrow.down")
                        .frame(maxWidth: .infinity, minHeight: 44)
                }
                .buttonStyle(.bordered)
                .accessibilityIdentifier("aya.import")
            }
        }
        .padding(16)
        .background {
            RoundedRectangle(cornerRadius: 16)
                .strokeBorder(.secondary.opacity(0.55), lineWidth: 1)
        }
        .sheet(isPresented: $showingReview) {
            AYAReviewSheet(initialText: reviewText, outputInstructions: outputInstructions)
        }
        .alert("Unable to prepare AYA", isPresented: Binding(
            get: { errorMessage != nil },
            set: { if !$0 { errorMessage = nil } }
        )) {
            Button("OK", role: .cancel) { errorMessage = nil }
        } message: {
            Text(errorMessage ?? "Unable to prepare the reference.")
        }
    }

    private func openReview() {
        guard !outputInstructions.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
            errorMessage = "The host has not supplied truthful instructions for using the response."
            return
        }
        guard let appID = Bundle.main.bundleIdentifier,
              let appVersion = Bundle.main.object(forInfoDictionaryKey: "CFBundleShortVersionString") as? String
        else {
            errorMessage = "The installed application's identity or version is unavailable."
            return
        }
        do {
            let reference = try AYAReference(
                guide: guide, installedAppID: appID, installedVersion: appVersion
            )
            let draft = AYAReviewDraft(reference: reference, suggestedQuestion: question)
            reviewText = draft.initialText
            showingReview = true
        } catch {
            errorMessage = "The app's bundled help reference is missing, invalid, or not made for this installed version. Nothing was shared."
        }
    }
}

@available(iOS 16.0, *)
private struct AYAReviewSheet: View {
    @Environment(\.dismiss) private var dismiss
    @State private var editedText: String
    @State private var sharing: AYASharingPresentation?
    @State private var errorMessage: String?
    @State private var copied = false
    let outputInstructions: String

    init(initialText: String, outputInstructions: String) {
        _editedText = State(initialValue: initialText)
        self.outputInstructions = outputInstructions
    }

    var body: some View {
        NavigationStack {
            VStack(alignment: .leading, spacing: 10) {
                Text("Edit everything below before sharing. The selected assistant may store or upload the approved text.")
                    .font(.footnote)
                    .foregroundStyle(.secondary)
                TextEditor(text: $editedText)
                    .font(.body.monospaced())
                    .scrollContentBackground(.hidden)
                    .padding(6)
                    .background {
                        RoundedRectangle(cornerRadius: 8)
                            .strokeBorder(.secondary.opacity(0.4))
                    }
                    .accessibilityLabel("Full editable AYA document")
                    .accessibilityIdentifier("aya.review")
                Text(outputInstructions)
                    .font(.footnote)
                    .foregroundStyle(.secondary)
                    .lineLimit(3)
                if copied {
                    Text("Copied the current approved text. Paste it into an assistant manually.")
                        .font(.caption)
                        .accessibilityAddTraits(.updatesFrequently)
                }
                VStack(spacing: 6) {
                    Button {
                        withApprovedPacket { packet in
                            AYAAppleSharing.copyApprovedText(packet)
                            copied = true
                        }
                    } label: {
                        Label("Copy current text", systemImage: "doc.on.doc")
                            .frame(maxWidth: .infinity, minHeight: 44)
                    }
                    .buttonStyle(.bordered)
                    .accessibilityIdentifier("aya.copy")

                    Button {
                        openShare(.plainText)
                    } label: {
                        Label("Share as text", systemImage: "square.and.arrow.up")
                            .frame(maxWidth: .infinity, minHeight: 44)
                    }
                    .buttonStyle(.borderedProminent)
                    .accessibilityIdentifier("aya.share.text")

                    Button {
                        openShare(.textDocument)
                    } label: {
                        Label("Share full .txt file", systemImage: "doc.text")
                            .frame(maxWidth: .infinity, minHeight: 44)
                    }
                    .buttonStyle(.bordered)
                    .accessibilityIdentifier("aya.share.document")
                }
            }
            .padding(16)
            .navigationTitle("Review AYA handoff")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") { dismiss() }
                        .accessibilityIdentifier("aya.cancel")
                }
            }
            .sheet(item: $sharing) { item in
                AYAActivitySheet(controller: item.controller)
            }
            .alert("Cannot share", isPresented: Binding(
                get: { errorMessage != nil },
                set: { if !$0 { errorMessage = nil } }
            )) {
                Button("OK", role: .cancel) { errorMessage = nil }
            } message: {
                Text(errorMessage ?? "The current text could not be shared.")
            }
        }
        .presentationDetents([.large])
    }

    private func withApprovedPacket(_ action: (AYAApprovedPacket) -> Void) {
        do {
            let packet = try AYAApprovedPacket(editedText: editedText)
            action(packet)
        } catch {
            errorMessage = "The reviewed text is blank or larger than 2 MiB."
        }
    }

    private func openShare(_ representation: AYAShareRepresentation) {
        withApprovedPacket { packet in
            do {
                let controller = try AYAAppleSharing.makeActivityController(
                    packet: packet, representation: representation
                )
                sharing = AYASharingPresentation(controller: controller)
            } catch {
                errorMessage = "The approved document could not be prepared. Copy the text instead."
            }
        }
    }
}

#if os(iOS)
private struct AYASharingPresentation: Identifiable {
    let id = UUID()
    let controller: UIActivityViewController
}

private struct AYAActivitySheet: UIViewControllerRepresentable {
    let controller: UIActivityViewController

    func makeUIViewController(context: Context) -> UIActivityViewController {
        controller
    }
    func updateUIViewController(_ controller: UIActivityViewController, context: Context) {}
}
#endif
#endif
