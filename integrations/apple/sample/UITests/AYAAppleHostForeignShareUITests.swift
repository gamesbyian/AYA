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

    private func verifyForeignShare(buttonId: String, expectedKind: String,
                                    editInReview: Bool = false) throws {
        var expected = try expectedApprovedBytes()
        let app = XCUIApplication()
        app.launch()
        let ask = app.buttons["aya.ask"]
        XCTAssertTrue(ask.waitForExistence(timeout: 20), "First-party AYA card missing")
        ask.tap()

        let review = app.textViews["aya.review"]
        XCTAssertTrue(review.waitForExistence(timeout: 15), "Editable consent document missing")
        let approved = try XCTUnwrap(review.value as? String)
        XCTAssertEqual(Data(approved.utf8), expected,
                       "The initial review differs from the source-derived synthetic fixture")

        if editInReview {
            // Actually type into the user-facing TextEditor, rather than
            // injecting a packet or faking a share callback. Verify the edit
            // is exactly one insertion and the original document survived.
            let marker = "AYA_QA_USER_EDIT_20261104"
            review.tap()
            review.typeText(marker)
            let edited = try XCTUnwrap(review.value as? String)
            XCTAssertNotEqual(edited, approved, "User's edit did not take effect")
            XCTAssertTrue(edited.contains(marker), "Editor lost the requested edit")
            XCTAssertEqual(edited.replacingOccurrences(of: marker, with: ""), approved,
                           "Editor unexpectedly modified another part of the reference")
            expected = Data(edited.utf8)

            let done = app.buttons["aya.review.done-editing"]
            XCTAssertTrue(done.waitForExistence(timeout: 10),
                          "No accessible action to close the keyboard before sharing")
            done.tap()
        }
        let digest = receiptSHA(expected)
        let share = app.buttons[buttonId]
        XCTAssertTrue(share.waitForExistence(timeout: 10), "Requested share mode not offered")
        share.tap()

        // The foreign .appex must appear as a genuine, selectable system
        // share target. On current iOS versions the title can derive from
        // either its own CFBundleDisplayName or its containing app. Probe
        // both host and SpringBoard accessibility containers before failing.
        let springboard = XCUIApplication(bundleIdentifier: "com.apple.springboard")
        let labels = ["AYA QA Receiver", "AYA Share QA", "AYA Share QA Extension"]
        var receiver: XCUIElement?
        for attempt in 0..<8 {
            for container in [app, springboard] {
                for label in labels {
                    let candidate = container.descendants(matching: .any)
                        .matching(NSPredicate(format: "label CONTAINS[c] %@", label))
                        .firstMatch
                    if candidate.exists && candidate.isHittable {
                        receiver = candidate
                        break
                    }
                }
                if receiver != nil { break }
            }
            if receiver != nil { break }
            if attempt == 2 {
                // Some iOS share panels hide new extensions behind More.
                let more = app.buttons["More"]
                if more.isHittable { more.tap() }
            }
            app.swipeUp()
        }
        if receiver == nil {
            // Metadata-only diagnostics. Never print the entire accessibility
            // tree, because the AYA review contains the user's approved text.
            let appButtons = app.buttons.allElementsBoundByIndex
                .map(\.label).filter { !$0.contains("\n") && $0.count < 65 }
                .prefix(35)
            let systemButtons = springboard.buttons.allElementsBoundByIndex
                .map(\.label).filter { !$0.contains("\n") && $0.count < 65 }
                .prefix(35)
            print("Foreign Share QA unavailable; host button labels: \(Array(appButtons))")
            print("Foreign Share QA unavailable; system button labels: \(Array(systemButtons))")
            print("ActivityListView present: \(app.otherElements["ActivityListView"].exists)")
        }
        let foreign = try XCTUnwrap(receiver,
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

    func testEditedPlainTextDeliveredWithoutStaleContent() throws {
        try verifyForeignShare(buttonId: "aya.share.text", expectedKind: "text",
                               editInReview: true)
    }

    func testEditedTXTDeliveredWithoutStaleContent() throws {
        try verifyForeignShare(buttonId: "aya.share.document", expectedKind: "file",
                               editInReview: true)
    }
}
