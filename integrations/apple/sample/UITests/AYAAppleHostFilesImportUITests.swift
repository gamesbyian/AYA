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
        // Use Files' cell identifier, not a broad 'any' query that can
        // resolve to a stale, offscreen label or a non-tappable subview.
        let file = app.cells["\(stem).json, json"]
        // Files sometimes restores Recents, a provider root, or an existing
        // folder between test launches. Explore each level explicitly and
        // never scroll the host app behind the system document picker.
        for _ in 0..<5 {
            if file.exists && file.isHittable { break }

            let qaFolder = app.descendants(matching: .any)
                .matching(NSPredicate(format: "label ==[c] %@", "AYA Share QA"))
                .firstMatch
            let local = app.descendants(matching: .any)
                .matching(NSPredicate(format: "label ==[c] %@", "On My iPhone"))
                .firstMatch
            let browse = app.buttons["Browse"]
            if qaFolder.exists && qaFolder.isHittable {
                qaFolder.tap()
            } else if local.exists && local.isHittable {
                local.tap()
            } else if browse.exists && browse.isHittable {
                browse.tap()
            } else {
                // Wait for document-provider enumeration instead of swiping
                // the host behind the sheet.
                _ = file.waitForExistence(timeout: 3)
            }
        }
        if !file.exists || !file.isHittable {
            let screenshot = XCTAttachment(screenshot: app.screenshot())
            screenshot.name = "Files navigation failed: \(stem)"
            screenshot.lifetime = .keepAlways
            add(screenshot)
            XCTFail("QA fixture not visible in Files for \(stem). AX hierarchy: \(app.debugDescription)")
            return
        }
        file.tap()

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

    /// Separate transport experiment: use a real UIKit Files picker in
    /// as-copy mode while retaining the identical foreign provider,
    /// rejection requirements, and host validation.
    /// Differential provider controls. Same valid payload as the proven
    /// fixture, but sorted earlier in Files' grid; the invalid control is
    /// deliberately sorted after the proven valid fixture.
    func testEarlyGridValidForeignJSONStillReachesPreview() throws {
        let app = XCUIApplication()
        app.launch()
        XCTAssertTrue(app.staticTexts["Columns: 1"].waitForExistence(timeout: 15))
        selectForeignDocument(app, stem: "aya-layout-aaa-control")
        let apply = app.buttons["Apply to demo"]
        XCTAssertTrue(apply.waitForExistence(timeout: 12),
                      "An early-grid valid JSON fixture should reach preview")
        app.buttons["Cancel"].tap()
        XCTAssertTrue(app.staticTexts["Columns: 1"].exists)
    }

    func testLateGridInvalidForeignJSONStillRejected() throws {
        let app = XCUIApplication()
        app.launch()
        XCTAssertTrue(app.staticTexts["Columns: 1"].waitForExistence(timeout: 15))
        selectForeignDocument(app, stem: "aya-layout-zzz-invalid")
        assertRejectedWithoutApply(
            app,
            message: "This file is not a valid Lantern demo-layout JSON.",
            why: "An invalid JSON fixture in a late grid slot must be rejected",
            stem: "aya-layout-zzz-invalid"
        )
    }

    func testCopyPickerProbeRejectsMalformedForeignJSON() throws {
        let app = XCUIApplication()
        app.launchArguments.append("AYA_UI_TEST_COPY_PICKER")
        app.launch()
        XCTAssertTrue(app.staticTexts["Columns: 1"].waitForExistence(timeout: 15))
        selectForeignDocument(app, stem: "aya-layout-invalid")
        assertRejectedWithoutApply(
            app,
            message: "This file is not a valid Lantern demo-layout JSON.",
            why: "UIKit copy-mode Files selection must reject invalid foreign JSON",
            stem: "aya-layout-invalid"
        )
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
