#if os(iOS)
import Foundation
import CryptoKit
import SwiftUI
import AYAProtocol

/// A user-mediated text return route for assistant output when a file is not
/// available (or Files' local provider cannot materialize a selection).
///
/// No clipboard read, file access, persistence, network request or execution
/// occurs. The user pastes into an ordinary text editor, explicitly chooses
/// Review, and the host receives immutable *untrusted* bytes. The host still
/// owns content recognition, semantic validation, impact preview and Apply.
@available(iOS 16.0, *)
public struct AYAImportPasteButton: View {
    private let title: String
    private let maximumBytes: Int
    private let onSelected: (AYAImportFile) -> Void

    @State private var showingEditor = false
    @State private var draft = ""
    @State private var errorMessage: String?
    @State private var pendingSnapshot: AYAImportFile?

    public init(
        title: String = "Paste agent output",
        maximumBytes: Int = AYAAppleFileImport.defaultLimit,
        onSelected: @escaping (AYAImportFile) -> Void
    ) {
        self.title = title
        self.maximumBytes = maximumBytes
        self.onSelected = onSelected
    }

    public var body: some View {
        Button {
            draft = ""
            errorMessage = nil
            pendingSnapshot = nil
            showingEditor = true
        } label: {
            Label(title, systemImage: "doc.on.clipboard")
                .frame(maxWidth: .infinity, minHeight: 44)
        }
        .buttonStyle(.bordered)
        .accessibilityIdentifier("aya.import.paste")
        .sheet(isPresented: $showingEditor, onDismiss: {
            // Deliver only after the editor is gone so the adopting host's
            // separate validation/preview sheet or dialog is not suppressed
            // by an overlapping sheet presentation.
            let selected = pendingSnapshot
            pendingSnapshot = nil
            draft = ""
            errorMessage = nil
            if let selected { onSelected(selected) }
        }) {
            NavigationStack {
                VStack(alignment: .leading, spacing: 12) {
                    Text("Paste the assistant's text output below. Review sends it to this app for validation; nothing is applied automatically.")
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                    TextEditor(text: $draft)
                        .font(.system(.body, design: .monospaced))
                        .textInputAutocapitalization(.never)
                        .autocorrectionDisabled(true)
                        .accessibilityLabel("Agent output text")
                        .accessibilityIdentifier("aya.import.paste.editor")
                        .overlay(RoundedRectangle(cornerRadius: 8).stroke(.secondary))
                        .frame(minHeight: 160)
                    if let errorMessage {
                        Text(errorMessage)
                            .foregroundStyle(.red)
                            .accessibilityIdentifier("aya.import.paste.error")
                    }
                }
                .padding(16)
                .navigationTitle("Paste agent output")
                .navigationBarTitleDisplayMode(.inline)
                .toolbar {
                    ToolbarItem(placement: .cancellationAction) {
                        Button("Cancel") {
                            pendingSnapshot = nil
                            showingEditor = false
                        }
                        .accessibilityIdentifier("aya.import.paste.cancel")
                    }
                    ToolbarItem(placement: .confirmationAction) {
                        Button("Review pasted output") { reviewDraft() }
                            .accessibilityIdentifier("aya.import.paste.review")
                    }
                }
            }
        }
        .onDisappear {
            // Disappearing host controls cannot publish a queued import.
            pendingSnapshot = nil
        }
    }

    private func reviewDraft() {
        guard maximumBytes > 0, maximumBytes <= AYAAppleFileImport.absoluteLimit else {
            errorMessage = AYAAppleImportError.invalidLimit.localizedDescription
            return
        }
        // Count the UTF-8 bytes *before* allocating a second buffer.
        let byteCount = draft.utf8.count
        guard byteCount > 0 else {
            errorMessage = "Paste text before reviewing it."
            return
        }
        guard byteCount <= maximumBytes else {
            errorMessage = AYAAppleImportError.tooLarge.localizedDescription
            return
        }
        let bytes = Data(draft.utf8)
        let fingerprint = SHA256.hash(data: bytes)
            .map { String(format: "%02x", $0) }.joined()
        pendingSnapshot = AYAImportFile(
            data: bytes, displayName: "Pasted agent text", sha256Hex: fingerprint
        )
        errorMessage = nil
        showingEditor = false
    }
}
#endif
