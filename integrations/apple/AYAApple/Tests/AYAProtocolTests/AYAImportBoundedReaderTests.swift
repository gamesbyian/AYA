import Foundation
import XCTest
@testable import AYAProtocol

final class AYAImportBoundedReaderTests: XCTestCase {
    private func streamed(_ input: Data, max limit: Int, chunkSize: Int) throws -> Data {
        var position = 0
        return try AYAImportBoundedReader.read(
            maximumBytes: limit, chunkSize: chunkSize
        ) { request in
            guard position < input.count else { return nil }
            // Deliberately return one byte per request to simulate a File
            // Provider producing numerous short, non-EOF reads.
            let end = min(position + 1, position + request, input.count)
            defer { position = end }
            return input.subdata(in: position..<end)
        }
    }

    func testShortReadsAreCollectedToRealEOF() throws {
        let original = Data("one complete document".utf8)
        XCTAssertEqual(try streamed(original, max: original.count, chunkSize: 7), original)
    }

    func testOversizeBeyondPlausibleValidPrefixIsRejected() throws {
        let prefix = Data(#"{"kind":"valid"}"#.utf8)
        var input = prefix
        input.append(Data(repeating: 0x20, count: 9))
        XCTAssertThrowsError(try streamed(input, max: prefix.count, chunkSize: 4)) {
            XCTAssertEqual($0 as? AYAImportBoundedReadError, .tooLarge)
        }
    }

    func testExactlyAtLimitRequiresAndReachesEOF() throws {
        let input = Data("abcd".utf8)
        var requests: [Int] = []
        var position = 0
        let output = try AYAImportBoundedReader.read(maximumBytes: 4, chunkSize: 3) { count in
            requests.append(count)
            guard position < input.count else { return nil }
            let end = min(position + count, input.count)
            defer { position = end }
            return input.subdata(in: position..<end)
        }
        XCTAssertEqual(output, input)
        XCTAssertEqual(requests.last, 1, "Must probe for EOF at the exact cap")
    }

    func testInvalidLimitAndMisbehavingReaderAreRejected() {
        XCTAssertThrowsError(try AYAImportBoundedReader.read(maximumBytes: 0) { _ in nil }) {
            XCTAssertEqual($0 as? AYAImportBoundedReadError, .invalidLimit)
        }
        XCTAssertThrowsError(try AYAImportBoundedReader.read(maximumBytes: 3, chunkSize: 1) {
            _ in Data("ab".utf8)
        }) {
            XCTAssertEqual($0 as? AYAImportBoundedReadError, .invalidChunk)
        }
    }

    func testCancellationInMiddleOfShortReadsNeverReturnsBytes() async {
        let worker = Task.detached(priority: .userInitiated) {
            try AYAImportBoundedReader.read(maximumBytes: 8, chunkSize: 2) { _ in
                withUnsafeCurrentTask { $0?.cancel() }
                return Data([0x61])
            }
        }
        do {
            _ = try await worker.value
            XCTFail("Cancelled worker must not return a valid-looking prefix")
        } catch is CancellationError {
            // Expected: no success value is published.
        } catch {
            XCTFail("Unexpected error: \(error)")
        }
    }
}
