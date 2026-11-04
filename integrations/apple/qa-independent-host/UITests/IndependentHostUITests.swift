import XCTest

final class IndependentHostUITests: XCTestCase {
    override func setUpWithError() throws {
        continueAfterFailure = false
    }

    func testRealInstalledAppUsesRootPackageCardAndSourceGuide() throws {
        let app = XCUIApplication()
        app.launch()
        XCTAssertTrue(app.staticTexts["Reading Queue QA"].waitForExistence(timeout: 20))
        let add = app.buttons["reader.add"]
        XCTAssertTrue(add.exists)
        add.tap()
        XCTAssertTrue(app.staticTexts["Saved titles: 1"].waitForExistence(timeout: 10))

        let ask = app.buttons["aya.ask"]
        XCTAssertTrue(ask.waitForExistence(timeout: 15),
                      "Root-package AYA card not integrated in the host")
        for _ in 0..<8 {
            if ask.isHittable { break }
            app.swipeUp()
        }
        XCTAssertTrue(ask.isHittable)
        ask.tap()

        let review = app.textViews["aya.review"]
        XCTAssertTrue(review.waitForExistence(timeout: 15))
        let value = try XCTUnwrap(review.value as? String)
        XCTAssertTrue(value.contains("Reading Queue QA"), "Host-specific guide not in review")
        XCTAssertTrue(value.contains("Add sample title"), "Actual host feature missing")
        XCTAssertTrue(value.contains("Scope and version"), "AYA-RAS sections not packaged")
        XCTAssertFalse(app.buttons["aya.import"].exists,
                       "Help-only second host must not show an invented import action")
        app.buttons["aya.cancel"].tap()
        XCTAssertTrue(ask.waitForExistence(timeout: 10))
        XCTAssertTrue(app.staticTexts["Saved titles: 1"].exists,
                      "Cancelled AYA handoff changed independent host state")
    }
}
