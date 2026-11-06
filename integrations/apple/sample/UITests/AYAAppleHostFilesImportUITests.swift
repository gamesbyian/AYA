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
        // iOS Files may display documents in a large grid cell whose centre
        // falls on a preview region. Prefer the visible filename itself,
        // which is the deterministic single-tap activation target in the
        // native browser. Retain cell fallback only when Files omits text.
        let filename = app.staticTexts["\(stem).json"]
        if filename.exists && filename.isHittable {
            filename.tap()
        } else {
            file.tap()
        }

        // First-use local Files providers may present a separate system
        // confirmation after a user selects the document. Only confirm the
        // already chosen test document; do not bypass the real fileImporter.
        for title in ["Open", "Select", "Allow Access", "Allow", "Continue"] {
            let confirmation = app.buttons[title]
            if confirmation.exists && confirmation.isHittable {
                confirmation.tap()
                break
            }
        }
    }

    private func assertRejectedWithoutApply(
        _ app: XCUIApplication, message: String, why: String,
        stem: String, timeout: TimeInterval = 8
    ) {
        // Validate user-visible accessible text, not merely an implementation
        // detail. On a failure retain the *actual* hierarchy: it distinguishes
        // a still-open Files picker, missing state and overwritten child IDs.
        let title = app.staticTexts["Cannot use this file"]
        if !title.waitForExistence(timeout: timeout) {
            // Diagnose the distinction between a still-present Files browser
            // and a callback that completed but left feedback obscured.
            // This remains a failed acceptance test, never a fallback pass.
            let before = app.debugDescription
            let capture = XCTAttachment(screenshot: app.screenshot())
            capture.name = "Picker after first selection: \(stem)"
            capture.lifetime = .keepAlways
            add(capture)

            // Diagnostic only: does a second tap cause a picker callback?
            // The assertion still FAILS, because normal one-tap acceptance
            // requires immediately visible rejection.
            let candidate = app.cells
                .matching(NSPredicate(format: "label CONTAINS[c] %@", stem))
                .firstMatch
            let secondTapAvailable = candidate.exists && candidate.isHittable
            if secondTapAvailable {
                candidate.tap()
            }
            let visibleErrorAfterSecondTap = app.staticTexts["Cannot use this file"]
                .waitForExistence(timeout: 4)

            let cancel = app.buttons["Cancel"]
            if cancel.exists && cancel.isHittable {
                cancel.tap()
            }
            let probe = app.staticTexts["host.import.probe"].firstMatch
            let stage = probe.waitForExistence(timeout: 5) ? probe.label : "no host probe visible"
            XCTFail("\(why). Second tap available: \(secondTapAvailable); error after second tap: \(visibleErrorAfterSecondTap); stage after dismissal: \(stage). Before: \(before)")
            return
        }
        XCTAssertEqual(title.identifier, "host.import.error.title")
        let explanation = app.staticTexts[message]
        XCTAssertTrue(explanation.exists, "Wrong or inaccessible file rejection: \(app.debugDescription)")
        XCTAssertEqual(explanation.identifier, "host.import.error")
        XCTAssertFalse(app.buttons["Apply to demo"].exists, "Invalid import exposed Apply")
        let dismiss = app.buttons["Dismiss import error"]
        XCTAssertTrue(dismiss.isHittable)
        XCTAssertEqual(dismiss.identifier, "host.import.error.dismiss")
        dismiss.tap()
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
        assertRejectedWithoutApply(
            app,
            message: "This file is not a valid Lantern demo-layout JSON.",
            why: "Invalid foreign JSON must produce immediately visible host-owned feedback",
            stem: "aya-layout-invalid"
        )
        XCTAssertTrue(app.staticTexts["Columns: 1"].exists)
        XCTAssertTrue(app.staticTexts["Accent: warm"].exists)
    }

    func testOversizedForeignJSONCannotBypassByteCap() throws {
        let app = XCUIApplication()
        app.launch()
        XCTAssertTrue(app.staticTexts["Columns: 1"].waitForExistence(timeout: 15))
        selectForeignDocument(app, stem: "aya-layout-oversized")

        assertRejectedWithoutApply(
            app,
            message: "The selected file exceeds the host's size limit.",
            why: "A valid but oversized JSON must fail the capped read",
            stem: "aya-layout-oversized", timeout: 10
        )
        XCTAssertTrue(app.staticTexts["Columns: 1"].exists)
        XCTAssertTrue(app.staticTexts["Accent: warm"].exists)
    }

    func testBooleanAndFloatingColumnsNeverPassIntegerSchema() throws {
        let app = XCUIApplication()
        app.launch()
        XCTAssertTrue(app.staticTexts["Columns: 1"].waitForExistence(timeout: 15))
        for filename in ["aya-layout-boolean", "aya-layout-float"] {
            selectForeignDocument(app, stem: filename)

            assertRejectedWithoutApply(
                app,
                message: "This file is not a valid Lantern demo-layout JSON.",
                why: "\(filename) must fail the integer-only host schema",
                stem: filename
            )
            XCTAssertTrue(app.staticTexts["Columns: 1"].exists)
            XCTAssertTrue(app.staticTexts["Accent: warm"].exists)
        }
    }
}
