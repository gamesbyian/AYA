import XCTest

/// UI tests exercise a real installed first-party iOS host. They do not
/// assert third-party assistant ingestion or physical-device accessibility.
final class AYAAppleHostUITests: XCTestCase {
    override func setUpWithError() throws {
        continueAfterFailure = false
    }

    private func reveal(_ target: XCUIElement, scrollingIn scroll: XCUIElement) {
        for _ in 0..<10 {
            if target.isHittable { return }
            scroll.swipeUp()
        }
        XCTAssertTrue(target.isHittable, "Control remains unreachable after bounded scrolling")
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

        let review = app.textViews["aya.review"]
        XCTAssertTrue(review.waitForExistence(timeout: 15), "Review editor never appeared")
        // Check the actual editable state before Copy. A presented sheet with
        // an empty/stale State value must never count as usable review.
        let editorValue = try XCTUnwrap(review.value as? String, "Review editor has no text value")
        XCTAssertTrue(editorValue.contains("Ask Your Agent"), "The review has no AYA request header")
        XCTAssertTrue(editorValue.contains("Scope and version"), "The bundled guide was not in review")

        let copy = app.buttons["aya.copy"]
        XCTAssertTrue(copy.waitForExistence(timeout: 15))
        copy.tap()
        let confirmation = app.alerts["Copied to clipboard"]
        if !confirmation.waitForExistence(timeout: 10) {
            // Retain bounded synthetic diagnostics, without logging full
            // question/reference contents or changing the acceptance gate.
            let titles = app.alerts.allElementsBoundByIndex.map(\.label)
            let visibleButtons = app.buttons.allElementsBoundByIndex
                .map(\.label).filter { !$0.isEmpty }.prefix(20)
            print("AYA Copy: expected success alert missing; visible alerts: \(titles)")
            print("AYA Copy: visible button labels: \(Array(visibleButtons))")
        }
        XCTAssertTrue(confirmation.exists, "Explicit Copy needs visible confirmation")
        XCTAssertTrue(confirmation.staticTexts[
            "The current approved text is on the clipboard. Paste it into your chosen assistant."
        ].exists)
        confirmation.buttons["OK"].tap()
        app.buttons["aya.cancel"].tap()
    }

    func testLargeTypeReviewActionsRemainReachable() throws {
        let app = XCUIApplication()
        app.launchArguments = ["AYA_UI_TEST_LARGE_TYPE"]
        app.launch()

        let ask = app.buttons["aya.ask"]
        XCTAssertTrue(ask.waitForExistence(timeout: 20), "Large-type AYA card missing")
        // The host deliberately scrolls at large Dynamic Type. Offscreen
        // controls are acceptable if the user can reveal and tap them.
        let hostScroll = app.scrollViews.firstMatch
        XCTAssertTrue(hostScroll.exists, "Host has no scrollable large-text layout")
        reveal(ask, scrollingIn: hostScroll)
        XCTAssertGreaterThanOrEqual(ask.frame.height, 44, "Ask target is too small")
        ask.tap()

        let review = app.textViews["aya.review"]
        XCTAssertTrue(review.waitForExistence(timeout: 15), "Full reviewed reference missing")
        let text = try XCTUnwrap(review.value as? String)
        XCTAssertTrue(text.contains("Scope and version"), "Large-type review lost reference content")

        for identifier in ["aya.copy", "aya.share.text", "aya.share.document"] {
            let action = app.buttons[identifier]
            XCTAssertTrue(action.waitForExistence(timeout: 10), "\(identifier) missing")
            XCTAssertGreaterThanOrEqual(action.frame.height, 44, "\(identifier) tap target too small")
            let reviewScroll = app.scrollViews["aya.review.scroller"]
            XCTAssertTrue(reviewScroll.exists, "Full review lacks an accessible scrolling surface")
            reveal(action, scrollingIn: reviewScroll)
        }
        app.buttons["aya.cancel"].tap()
        XCTAssertTrue(ask.waitForExistence(timeout: 10))
    }

    func testAlreadyCancelledImportNeverRequestsProviderAccess() throws {
        let app = XCUIApplication()
        app.launchArguments = ["AYA_UI_TEST_PRE_CANCELLED_IMPORT"]
        app.launch()

        let outcome = app.staticTexts["host.import.cancel.probe"]
        XCTAssertTrue(outcome.waitForExistence(timeout: 20),
                      "Synthetic pre-cancelled snapshot did not finish")
        XCTAssertEqual(outcome.label, "Cancelled read: cancelled",
                       "A cancelled call must fail before any file scope access")
        XCTAssertTrue(app.staticTexts["Columns: 1"].exists)
        XCTAssertTrue(app.staticTexts["Accent: warm"].exists)
        XCTAssertFalse(app.buttons["Apply to demo"].exists)
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
