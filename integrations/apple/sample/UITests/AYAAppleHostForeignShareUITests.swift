import CryptoKit
import Foundation
import XCTest

/// Exactly scoped synthetic Share Sheet tests. Both sending host and the
/// receiving .appex must be installed; a chooser alone cannot pass this test.
/// No test dumps the approved reference into logs or test artifacts.
final class AYAAppleHostForeignShareUITests: XCTestCase {
    override func setUpWithError() throws {
        continueAfterFailure = false
    }

    private func expectedApprovedBytes() throws -> Data {
        let bundle = Bundle(for: AYAAppleHostForeignShareUITests.self)
        let url = try XCTUnwrap(
            bundle.url(forResource: "aya-guide", withExtension: "md"),
            "The test must use the independently packaged source guide fixture"
        )
        let guide = try String(contentsOf: url, encoding: .utf8)
        // This is the current AYAReviewDraft default question format.
        let packet = "# Ask Your Agent\n\nQuestion: Help me use this app.\n\n---\n\n" + guide
        return Data(packet.utf8)
    }

    private func receiptSHA(_ bytes: Data) -> String {
        SHA256.hash(data: bytes).map { String(format: "%02x", $0) }.joined()
    }

    private func verifyForeignShare(buttonId: String, expectedKind: String) throws {
        let expected = try expectedApprovedBytes()
        let digest = receiptSHA(expected)
        let app = XCUIApplication()
        app.launch()
        let ask = app.buttons["aya.ask"]
        XCTAssertTrue(ask.waitForExistence(timeout: 20), "First-party AYA card missing")
        ask.tap()

        let review = app.textViews["aya.review"]
        XCTAssertTrue(review.waitForExistence(timeout: 15), "Editable consent document missing")
        let approved = try XCTUnwrap(review.value as? String)
        XCTAssertEqual(receiptSHA(Data(approved.utf8)), digest,
                       "The actual reviewed document differs from the source fixture")

        let share = app.buttons[buttonId]
        XCTAssertTrue(share.waitForExistence(timeout: 10), "Requested share mode not offered")
        share.tap()

        // The other APK's Share Extension must be available in the actual
        // operating-system activity chooser. No recipient substitution or
        // simulation is permitted if its item is absent.
        let foreign = app.descendants(matching: .any)
            .matching(NSPredicate(format: "label CONTAINS[c] %@", "AYA QA Receiver"))
            .firstMatch
        _ = foreign.waitForExistence(timeout: 12)
        for _ in 0..<8 {
            if foreign.isHittable { break }
            app.swipeUp()
        }
        XCTAssertTrue(foreign.isHittable,
                      "Foreign QA Share Extension was not offered/reachable in the real system chooser")
        foreign.tap()

        let extensionApp = XCUIApplication(bundleIdentifier: "org.example.aya.shareqa.extension")
        // On some OS builds the extension UI is part of the host accessibility
        // tree; on others it is reached through the extension process.
        let localStatus = app.staticTexts["qa.receiver.status"]
        let extensionStatus = extensionApp.staticTexts["qa.receiver.status"]
        let insideHost = localStatus.waitForExistence(timeout: 5)
        let status = insideHost ? localStatus : extensionStatus
        XCTAssertTrue(status.waitForExistence(timeout: 20),
                      "Independent extension did not display a received-byte receipt")
        let scope = insideHost ? app : extensionApp
        XCTAssertEqual(status.label, "Status: received", "Foreign extension did not read complete bytes")
        XCTAssertEqual(scope.staticTexts["qa.receiver.kind"].label, "Type: \(expectedKind)")
        XCTAssertEqual(scope.staticTexts["qa.receiver.bytes"].label, "Bytes: \(expected.count)")
        XCTAssertEqual(scope.staticTexts["qa.receiver.sha256"].label, "SHA-256: \(digest)",
                       "Foreign extension digest does not match independently expected approved bytes")
    }

    func testApprovedPlainTextReceivedBySeparateExtension() throws {
        try verifyForeignShare(buttonId: "aya.share.text", expectedKind: "text")
    }

    func testApprovedTXTFileReceivedBySeparateExtension() throws {
        try verifyForeignShare(buttonId: "aya.share.document", expectedKind: "file")
    }
}
