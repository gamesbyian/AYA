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

    /// An *external parent* cancels a worker already inside a simulated,
    /// blocking FileHandle/provider chunk read. When the read returns, the
    /// bounded reader must reject partial data and run the worker's cleanup.
    ///
    /// This models the post-accessor cooperative cancellation boundary;
    /// it does not assert that NSFileCoordinator can interrupt a provider's
    /// blocking accessor, or that security-scoped OS resource cleanup was run.
    func testExternalCancellationWhileReadCallbackIsBlocked() async {
        let beganReading = expectation(description: "Reader has entered blocked chunk callback")
        let cleanedUp = expectation(description: "Worker has exited and run cleanup")
        let unblockRead = DispatchSemaphore(value: 0)

        let worker = Task.detached(priority: .userInitiated) { () throws -> Data in
            defer { cleanedUp.fulfill() }
            return try AYAImportBoundedReader.read(maximumBytes: 32, chunkSize: 8) { _ in
                beganReading.fulfill()
                // Emulates one already-executing provider accessor. External
                // cancellation alone cannot interrupt a synchronous read.
                guard unblockRead.wait(timeout: .now() + 8) == .success else {
                    throw CancellationError()
                }
                return Data("valid-looking-prefix".utf8)
            }
        }

        await fulfillment(of: [beganReading], timeout: 10)
        worker.cancel()
        unblockRead.signal()

        do {
            let bytes = try await worker.value
            XCTFail("Externally cancelled reader published \(bytes.count) partial bytes")
        } catch is CancellationError {
            // Expected: cancellation checked after the chunk completes, with
            // no successful immutable artifact returned to the host.
        } catch {
            XCTFail("Unexpected error from externally cancelled worker: \(error)")
        }
        await fulfillment(of: [cleanedUp], timeout: 10)
    }

    func testProviderErrorAfterPartialChunkNeverReturnsIncompleteArtifact() {
        enum SimulatedProviderError: Error { case accessRevoked }
        var requests = 0
        XCTAssertThrowsError(
            try AYAImportBoundedReader.read(maximumBytes: 64, chunkSize: 8) { _ in
                requests += 1
                if requests == 1 { return Data("partial".utf8) }
                throw SimulatedProviderError.accessRevoked
            }
        ) { error in
            guard case SimulatedProviderError.accessRevoked = error else {
                XCTFail("Stream error was swallowed or replaced: \(error)")
                return
            }
        }
        XCTAssertEqual(requests, 2)
    }

}
