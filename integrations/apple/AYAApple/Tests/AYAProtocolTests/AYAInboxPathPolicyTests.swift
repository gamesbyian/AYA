import Foundation
import XCTest
@testable import AYAProtocol

final class AYAInboxPathPolicyTests: XCTestCase {
    func testOnlyCanonicalInboxDescendantsAreAccepted() throws {
        let documents = FileManager.default.temporaryDirectory
            .appendingPathComponent("AYA-Demo-Documents", isDirectory: true)
        let inbox = documents.appendingPathComponent("Inbox", isDirectory: true)
        XCTAssertTrue(AYAInboxPathPolicy.permitsCopiedDocument(
            inbox.appendingPathComponent("proposal.json"), documentsDirectory: documents
        ))
        XCTAssertTrue(AYAInboxPathPolicy.permitsCopiedDocument(
            inbox.appendingPathComponent("subfolder/proposal.json"),
            documentsDirectory: documents
        ))
        XCTAssertFalse(AYAInboxPathPolicy.permitsCopiedDocument(
            documents.appendingPathComponent("InboxAdjacent/proposal.json"),
            documentsDirectory: documents
        ))
        XCTAssertFalse(AYAInboxPathPolicy.permitsCopiedDocument(
            documents.appendingPathComponent("proposal.json"),
            documentsDirectory: documents
        ))
        XCTAssertFalse(AYAInboxPathPolicy.permitsCopiedDocument(
            inbox.appendingPathComponent("../unrelated.json"),
            documentsDirectory: documents
        ))
        XCTAssertFalse(AYAInboxPathPolicy.permitsCopiedDocument(
            URL(string: "https://example.invalid/proposal.json")!,
            documentsDirectory: documents
        ))
        XCTAssertFalse(AYAInboxPathPolicy.permitsCopiedDocument(
            inbox, documentsDirectory: documents
        ))
    }

    func testSymlinkEscapingInboxIsRejected() throws {
        let fm = FileManager.default
        let sandbox = fm.temporaryDirectory
            .appendingPathComponent("AYAInboxPolicy-" + UUID().uuidString, isDirectory: true)
        defer { try? fm.removeItem(at: sandbox) }
        let documents = sandbox.appendingPathComponent("Documents", isDirectory: true)
        let inbox = documents.appendingPathComponent("Inbox", isDirectory: true)
        try fm.createDirectory(at: inbox, withIntermediateDirectories: true)
        let outside = sandbox.appendingPathComponent("outside.json")
        try Data("{}".utf8).write(to: outside)
        let link = inbox.appendingPathComponent("escape.json")
        try fm.createSymbolicLink(at: link, withDestinationURL: outside)
        XCTAssertFalse(AYAInboxPathPolicy.permitsCopiedDocument(
            link, documentsDirectory: documents
        ))
        let owned = inbox.appendingPathComponent("owned.json")
        try Data("{}".utf8).write(to: owned)
        XCTAssertTrue(AYAInboxPathPolicy.permitsCopiedDocument(
            owned, documentsDirectory: documents
        ))
    }
}
