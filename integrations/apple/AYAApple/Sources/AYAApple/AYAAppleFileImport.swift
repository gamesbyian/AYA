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

/// Narrow sendability boundary for Foundation's coordinated-read cancellation.
/// Apple permits cancelling a pending NSFileCoordinator operation from another
/// thread; `cancel()` is explicitly designed to race with a blocking
/// `coordinate(...)` call. The underlying coordinator never escapes
/// this private per-import lifetime. This wrapper exposes no shared mutable file
/// data or arbitrary coordinator access to callers.
private final class AYACancelableFileCoordinator: @unchecked Sendable {
    let value = NSFileCoordinator(filePresenter: nil)

    func cancel() {
        value.cancel()
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
        // A caller already cancelled must never start provider access or
        // allocate an unstructured worker that races the cancellation handler.
        try Task.checkCancellation()
        // Detached work keeps the coordinated file read off the UI actor.
        // Explicitly bind its lifetime to the caller: awaiting a detached
        // task alone does not propagate cancellation.
        let cancellableCoordinator = AYACancelableFileCoordinator()
        let worker = Task.detached(priority: .userInitiated) {
            try Task.checkCancellation()
            guard url.isFileURL, url.startAccessingSecurityScopedResource() else {
                throw AYAAppleImportError.permissionDenied
            }
            defer { url.stopAccessingSecurityScopedResource() }

            try Task.checkCancellation()
            var coordinationError: NSError?
            var readResult: Result<Data, Error>?
            cancellableCoordinator.value.coordinate(readingItemAt: url, options: [], error: &coordinationError) { fileURL in
                do {
                    try Task.checkCancellation()
                    let handle = try FileHandle(forReadingFrom: fileURL)
                    defer { try? handle.close() }
                    // FileHandle may return a short chunk before EOF. Never
                    // accept a valid-looking prefix as a complete artifact.
                    // Preserve the one-extra-byte cap and per-chunk cancellation.
                    let data: Data
                    do {
                        data = try AYAImportBoundedReader.read(maximumBytes: maximumBytes) {
                            try handle.read(upToCount: $0)
                        }
                    } catch AYAImportBoundedReadError.tooLarge {
                        throw AYAAppleImportError.tooLarge
                    } catch AYAImportBoundedReadError.invalidChunk {
                        throw AYAAppleImportError.missingData
                    }
                    try Task.checkCancellation()
                    readResult = .success(data)
                } catch {
                    readResult = .failure(error)
                }
            }
            try Task.checkCancellation()
            if let error = coordinationError { throw error }
            guard let outcome = readResult else { throw AYAAppleImportError.missingData }
            let bytes = try outcome.get()
            let fingerprint = SHA256.hash(data: bytes).map { String(format: "%02x", $0) }.joined()
            try Task.checkCancellation()
            return AYAImportFile(data: bytes, displayName: url.lastPathComponent, sha256Hex: fingerprint)
        }
        return try await withTaskCancellationHandler {
            let result = try await worker.value
            try Task.checkCancellation()
            return result
        } onCancel: {
            // NSFileCoordinator.cancel() can terminate pending coordination,
            // but cannot interrupt an already running accessor. The worker's
            // own cancellation checks fence publication in either case.
            worker.cancel()
            cancellableCoordinator.cancel()
        }
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
    @State private var importTask: Task<Void, Never>?
    @State private var selectionLifetime = AYAImportSelectionLifetime()

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
                // A second selection supersedes any read still in flight.
                // Only its own live task may publish validated snapshot bytes.
                importTask?.cancel()
                let id = selectionLifetime.begin()
                errorMessage = nil
                reading = true
                importTask = Task { @MainActor in
                    do {
                        let snapshot = try await AYAAppleFileImport.snapshot(
                            userSelectedURL: url, maximumBytes: maximumBytes
                        )
                        try Task.checkCancellation()
                        guard selectionLifetime.isCurrent(id) else { return }
                        onSelected(snapshot)
                    } catch is CancellationError {
                        // User dismissed the host or superseded this import.
                        // Cancellation is not an invalid-file error.
                    } catch {
                        if selectionLifetime.isCurrent(id) && !Task.isCancelled {
                            errorMessage = error.localizedDescription
                        }
                    }
                    if selectionLifetime.finish(id) {
                        reading = false
                        importTask = nil
                    }
                }
            case .failure:
                errorMessage = "The file picker could not return a document."
            }
        }
        .onDisappear {
            // A host navigation/dismissal must not leave a read alive that
            // subsequently exposes Apply in a no-longer-active context.
            importTask?.cancel()
            importTask = nil
            selectionLifetime.cancel()
            reading = false
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
