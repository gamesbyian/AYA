#if os(iOS)
import Foundation
import CryptoKit
import SwiftUI
import UniformTypeIdentifiers
import AYAProtocol

public enum AYAAppleImportError: Error, LocalizedError {
    case invalidLimit
    case permissionDenied
    case tooLarge
    case missingData

    public var errorDescription: String? {
        switch self {
        case .invalidLimit: return "The configured import limit is invalid."
        case .permissionDenied: return "The selected document did not grant read access."
        case .tooLarge: return "The selected file exceeds the host's size limit."
        case .missingData: return "The selected document could not be read."
        }
    }
}

/// Reads only a user-selected URL. The security scope and file coordination
/// run off the main actor and are released once immutable bytes are captured.
public enum AYAAppleFileImport {
    public static let defaultLimit = 4 * 1_024 * 1_024
    public static let absoluteLimit = 16 * 1_024 * 1_024

    public static func snapshot(
        userSelectedURL url: URL,
        maximumBytes: Int = defaultLimit
    ) async throws -> AYAImportFile {
        guard maximumBytes > 0 && maximumBytes <= absoluteLimit else {
            throw AYAAppleImportError.invalidLimit
        }
        return try await Task.detached(priority: .userInitiated) {
            guard url.isFileURL, url.startAccessingSecurityScopedResource() else {
                throw AYAAppleImportError.permissionDenied
            }
            defer { url.stopAccessingSecurityScopedResource() }

            let coordinator = NSFileCoordinator(filePresenter: nil)
            var coordinationError: NSError?
            var readResult: Result<Data, Error>?
            coordinator.coordinate(readingItemAt: url, options: [], error: &coordinationError) { fileURL in
                do {
                    let handle = try FileHandle(forReadingFrom: fileURL)
                    defer { try? handle.close() }
                    // Bound the read even if a File Provider lies about its size.
                    let data = try handle.read(upToCount: maximumBytes + 1) ?? Data()
                    guard data.count <= maximumBytes else { throw AYAAppleImportError.tooLarge }
                    readResult = .success(data)
                } catch {
                    readResult = .failure(error)
                }
            }
            if let error = coordinationError { throw error }
            guard let outcome = readResult else { throw AYAAppleImportError.missingData }
            let bytes = try outcome.get()
            let fingerprint = SHA256.hash(data: bytes).map { String(format: "%02x", $0) }.joined()
            return AYAImportFile(data: bytes, displayName: url.lastPathComponent, sha256Hex: fingerprint)
        }.value
    }
}

/// A standalone optional user-owned import action. This only copies bounded
/// bytes into memory and gives them to the host for *independent* validation,
/// impact preview and explicit apply confirmation. It never applies content.
@available(iOS 16.0, *)
public struct AYAImportPickerButton: View {
    private let title: String
    private let acceptedTypes: [UTType]
    private let maximumBytes: Int
    private let onSelected: (AYAImportFile) -> Void
    @State private var picking = false
    @State private var reading = false
    @State private var errorMessage: String?

    public init(
        title: String = "Import saved agent output",
        acceptedTypes: [UTType],
        maximumBytes: Int = AYAAppleFileImport.defaultLimit,
        onSelected: @escaping (AYAImportFile) -> Void
    ) {
        self.title = title
        self.acceptedTypes = acceptedTypes
        self.maximumBytes = maximumBytes
        self.onSelected = onSelected
    }

    public var body: some View {
        Button {
            picking = true
        } label: {
            Label(title, systemImage: "square.and.arrow.down")
                .frame(maxWidth: .infinity, minHeight: 44)
        }
        .buttonStyle(.bordered)
        .disabled(reading || acceptedTypes.isEmpty)
        .accessibilityIdentifier("aya.import.picker")
        .fileImporter(isPresented: $picking, allowedContentTypes: acceptedTypes) { result in
            switch result {
            case .success(let url):
                reading = true
                Task {
                    defer { reading = false }
                    do {
                        let snapshot = try await AYAAppleFileImport.snapshot(
                            userSelectedURL: url, maximumBytes: maximumBytes
                        )
                        onSelected(snapshot)
                    } catch {
                        errorMessage = error.localizedDescription
                    }
                }
            case .failure:
                errorMessage = "The file picker could not return a document."
            }
        }
        .alert("Cannot import this file", isPresented: Binding(
            get: { errorMessage != nil },
            set: { if !$0 { errorMessage = nil } }
        )) {
            Button("OK", role: .cancel) { errorMessage = nil }
        } message: {
            Text(errorMessage ?? "Select a different document.")
        }
    }
}
#endif
