import XCTest

/// UI tests exercise a real installed first-party iOS host. They do not
/// assert third-party assistant ingestion or physical-device accessibility.
final class AYAAppleHostUITests: XCTestCase {
    override func setUpWithError() throws {
        continueAfterFailure = false
    }

    func testReviewOpensAndCancelReturnsWithoutSharing() throws {
        let app = XCUIApplication()
        app.launch()

        let ask = app.buttons["aya.ask"]
        XCTAssertTrue(ask.waitForExistence(timeout: 20), "Native AYA card did not appear")
        ask.tap()

        let review = app.textViews["aya.review"]
        XCTAssertTrue(review.waitForExistence(timeout: 15), "Editable complete document missing")
        XCTAssertTrue(app.buttons["aya.share.text"].exists)
        XCTAssertTrue(app.buttons["aya.share.document"].exists)
        XCTAssertTrue(app.buttons["aya.copy"].exists)
        app.buttons["aya.cancel"].tap()

        XCTAssertTrue(ask.waitForExistence(timeout: 10), "Cancel did not return to host")
    }

    func testUserCanChooseCopyInsideReviewedDocument() throws {
        let app = XCUIApplication()
        app.launch()
        let ask = app.buttons["aya.ask"]
        XCTAssertTrue(ask.waitForExistence(timeout: 20))
        ask.tap()

        let copy = app.buttons["aya.copy"]
        XCTAssertTrue(copy.waitForExistence(timeout: 15))
        copy.tap()
        let confirmation = app.staticTexts[
            "Copied the current approved text. Paste it into an assistant manually."
        ]
        XCTAssertTrue(confirmation.waitForExistence(timeout: 10))
        app.buttons["aya.cancel"].tap()
    }

    func testStaleBundledGuideFailsBeforeReview() throws {
        let app = XCUIApplication()
        app.launchArguments = ["AYA_UI_TEST_STALE_GUIDE"]
        app.launch()

        let ask = app.buttons["aya.ask"]
        XCTAssertTrue(ask.waitForExistence(timeout: 20))
        ask.tap()

        XCTAssertTrue(app.alerts["Unable to prepare AYA"].waitForExistence(timeout: 10))
        XCTAssertFalse(app.textViews["aya.review"].exists, "Stale guide opened review")
        app.alerts.buttons["OK"].tap()
    }
}
