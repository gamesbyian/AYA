import Foundation

/// A host-neutral bounded reader for one already-authorized byte stream.
///
/// Some providers return fewer bytes than requested before EOF. Treating a
/// short read as a complete file can accept a valid-looking truncated prefix.
/// This helper requires an actual EOF and probes one byte past the limit.
/// The caller owns document authorization, coordination and handle cleanup.
public enum AYAImportBoundedReadError: Error, Equatable {
    case invalidLimit
    case tooLarge
    case invalidChunk
}

public enum AYAImportBoundedReader {
    public static func read(
        maximumBytes: Int,
        chunkSize: Int = 64 * 1_024,
        nextChunk: (Int) throws -> Data?
    ) throws -> Data {
        guard maximumBytes > 0, maximumBytes < Int.max, chunkSize > 0 else {
            throw AYAImportBoundedReadError.invalidLimit
        }
        var bytes = Data()
        while true {
            try Task<Never, Never>.checkCancellation()
            // At the exact cap, the next read asks for one byte to distinguish
            // actual EOF from a file that must be rejected as oversized.
            let request = min(chunkSize, maximumBytes - bytes.count + 1)
            guard let chunk = try nextChunk(request), !chunk.isEmpty else { break }
            guard chunk.count <= request else { throw AYAImportBoundedReadError.invalidChunk }
            guard chunk.count <= maximumBytes - bytes.count else {
                throw AYAImportBoundedReadError.tooLarge
            }
            bytes.append(chunk)
        }
        try Task<Never, Never>.checkCancellation()
        return bytes
    }
}
