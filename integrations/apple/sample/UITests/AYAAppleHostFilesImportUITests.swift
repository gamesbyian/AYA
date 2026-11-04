import Foundation
import XCTest

/// Real, user-triggered Files picker acceptance. The fixture JSON lives in
/// the Documents directory of an *independently installed* disposable QA app
/// exposed through iOS's local File Provider. We never bypass the picker.
final class AYAAppleHostFilesImportUITests: XCTestCase {
    override func setUpWithError() throws {
        continueAfterFailure = false
    }

    private func openImport(_ app: XCUIApplication) {
        let button = app.buttons["aya.import"]
        XCTAssertTrue(button.waitForExistence(timeout: 15), "Host import action was not rendered")
        for _ in 0..<8 {
            if button.isHittable { break }
            app.swipeUp()
        }
        XCTAssertTrue(button.isHittable, "Host import action cannot be reached")
        button.tap()
    }

    private func selectForeignDocument(_ app: XCUIApplication, stem: String) {
        openImport(app)
        let file = app.descendants(matching: .any)
            .matching(NSPredicate(format: "label CONTAINS[c] %@", stem))
            .firstMatch
        // Navigate the actual Files browser instead of granting synthetic
        // test-only filesystem access. UI labels may vary by device version;
        // retain a fail-closed diagnostic with only fixed fixture names.
        var visited = Set<String>()
        for _ in 0..<12 {
            if file.exists && file.isHittable { break }
            var advanced = false
            for destination in ["AYA Share QA", "On My iPhone", "Browse"] {
                let node = app.descendants(matching: .any)
                    .matching(NSPredicate(format: "label ==[c] %@", destination))
                    .firstMatch
                if node.exists && node.isHittable && !visited.contains(destination) {
                    visited.insert(destination)
                    node.tap()
                    advanced = true
                    break
                }
            }
            if !advanced { app.swipeUp() }
        }
        XCTAssertTrue(file.isHittable,
                      "QA fixture document never became available through the real Files browser")
        file.tap()
    }

    func testUserPickedForeignJSONRequiresExplicitApply() throws {
        let app = XCUIApplication()
        app.launch()
        XCTAssertTrue(app.staticTexts["Columns: 1"].waitForExistence(timeout: 15))
        XCTAssertTrue(app.staticTexts["Accent: warm"].exists)

        selectForeignDocument(app, stem: "aya-layout-valid")

        let apply = app.buttons["Apply to demo"]
        XCTAssertTrue(apply.waitForExistence(timeout: 20),
                      "User-selected foreign document did not reach host semantic preview")
        // Reading + validating the content must not silently mutate state.
        XCTAssertTrue(app.staticTexts["Columns: 1"].exists,
                      "The imported recipe applied before explicit consent")
        XCTAssertTrue(app.staticTexts["Accent: warm"].exists)
        app.buttons["Cancel"].tap()
        XCTAssertTrue(app.staticTexts["Columns: 1"].exists,
                      "Cancelled import unexpectedly applied the proposal")

        selectForeignDocument(app, stem: "aya-layout-valid")
        let again = app.buttons["Apply to demo"]
        XCTAssertTrue(again.waitForExistence(timeout: 20))
        again.tap()
        XCTAssertTrue(app.staticTexts["Columns: 3"].waitForExistence(timeout: 12),
                      "Explicit Apply failed to use the inspected snapshot")
        XCTAssertTrue(app.staticTexts["Accent: cool"].exists)
    }

    func testMalformedForeignJSONNeverAuthorizesApply() throws {
        let app = XCUIApplication()
        app.launch()
        XCTAssertTrue(app.staticTexts["Columns: 1"].waitForExistence(timeout: 15))
        selectForeignDocument(app, stem: "aya-layout-invalid")
        let rejected = app.staticTexts["host.import.error"]
        XCTAssertTrue(rejected.waitForExistence(timeout: 20),
                      "Invalid foreign JSON produced no visible host-owned rejection")
        XCTAssertEqual(rejected.label, "This file is not a valid Lantern demo-layout JSON.")
        XCTAssertFalse(app.buttons["Apply to demo"].exists,
                       "Invalid JSON offered Apply")
        app.buttons["host.import.error.dismiss"].tap()
        XCTAssertTrue(app.staticTexts["Columns: 1"].exists)
        XCTAssertTrue(app.staticTexts["Accent: warm"].exists)
    }
}
