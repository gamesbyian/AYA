import Foundation
import XCTest

/// Installed native UI proof for the user's explicit text-return route.
/// No fabricated file-picker callback, automatic clipboard scraping, or
/// direct access to another application's sandbox is involved.
final class AYAAppleHostPasteImportUITests: XCTestCase {
    override func setUpWithError() throws {
        continueAfterFailure = false
    }

    private func openEditor(_ app: XCUIApplication) {
        let open = app.buttons["aya.import.paste"]
        XCTAssertTrue(open.waitForExistence(timeout: 15))
        for _ in 0..<10 {
            if open.isHittable { break }
            app.swipeUp()
        }
        XCTAssertTrue(open.isHittable, "Paste return action must be reachable")
        open.tap()
        XCTAssertTrue(app.textViews["aya.import.paste.editor"].waitForExistence(timeout: 10))
    }

    private func submit(_ app: XCUIApplication, text: String) {
        openEditor(app)
        let editor = app.textViews["aya.import.paste.editor"]
        XCTAssertTrue(editor.isHittable)
        editor.tap()
        editor.typeText(text)
        let review = app.buttons["aya.import.paste.review"]
        XCTAssertTrue(review.isHittable)
        review.tap()
    }

    func testPasteRequiresExplicitSecondApply() {
        let app = XCUIApplication()
        app.launch()
        XCTAssertTrue(app.staticTexts["Columns: 1"].waitForExistence(timeout: 12))
        submit(app, text: "{\"aya_demo_layout\":\"v1\",\"columns\":3,\"accent\":\"cool\"}")
        let apply = app.buttons["Apply to demo"]
        XCTAssertTrue(apply.waitForExistence(timeout: 12),
                      "User-submitted text did not reach host review")
        XCTAssertTrue(app.staticTexts["Columns: 1"].exists,
                      "Review must not mutate the host")
        app.buttons["Cancel"].tap()
        XCTAssertTrue(app.staticTexts["Columns: 1"].exists,
                      "Cancelling a valid pasted proposal must preserve state")

        submit(app, text: "{\"aya_demo_layout\":\"v1\",\"columns\":3,\"accent\":\"cool\"}")
        XCTAssertTrue(app.buttons["Apply to demo"].waitForExistence(timeout: 12))
        app.buttons["Apply to demo"].tap()
        XCTAssertTrue(app.staticTexts["Columns: 3"].waitForExistence(timeout: 12))
        XCTAssertTrue(app.staticTexts["Accent: cool"].exists)
    }

    func testPastedInvalidPayloadNeverExposesApply() {
        let app = XCUIApplication()
        app.launch()
        XCTAssertTrue(app.staticTexts["Columns: 1"].waitForExistence(timeout: 12))
        submit(app, text: "{\"aya_demo_layout\":\"v1\",\"columns\":99,\"accent\":\"cool\"}")
        XCTAssertTrue(app.alerts["Cannot use this file"].waitForExistence(timeout: 12),
                      "Host must visibly reject invalid pasted data")
        XCTAssertFalse(app.buttons["Apply to demo"].exists)
        XCTAssertTrue(app.staticTexts["Columns: 1"].exists)
        app.alerts.buttons["OK"].tap()
    }

    func testPasteCancelNeverSubmitsOrMutates() {
        let app = XCUIApplication()
        app.launch()
        XCTAssertTrue(app.staticTexts["Columns: 1"].waitForExistence(timeout: 12))
        openEditor(app)
        let editor = app.textViews["aya.import.paste.editor"]
        editor.tap()
        editor.typeText("{\"aya_demo_layout\":\"v1\",\"columns\":3,\"accent\":\"cool\"}")
        app.buttons["aya.import.paste.cancel"].tap()
        XCTAssertFalse(app.buttons["Apply to demo"].exists)
        XCTAssertTrue(app.staticTexts["Columns: 1"].exists)
        XCTAssertTrue(app.staticTexts["Accent: warm"].exists)
    }
}
