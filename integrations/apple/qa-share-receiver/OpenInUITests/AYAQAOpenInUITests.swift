import Foundation
import XCTest

/// Separate, installed-app handoff. The QA source app owns every test file,
/// the user opens iOS's real Share Sheet, and the system must offer the
/// separately installed AYA Lantern document viewer. Never simulate the
/// destination scene callback or import bytes directly into Lantern.
final class AYAQAOpenInUITests: XCTestCase {
    override func setUpWithError() throws {
        continueAfterFailure = false
    }

    private func prepareQA(_ qa: XCUIApplication, filename: String) {
        qa.launch()
        let prepare = qa.buttons["qa.prepare.files"]
        XCTAssertTrue(prepare.waitForExistence(timeout: 20))
        prepare.tap()
        let status = qa.staticTexts["qa.prepare.status"]
        XCTAssertTrue(status.waitForExistence(timeout: 10))
        XCTAssertEqual(status.label,
            "Prepared: seven verified JSON files in this QA app's Documents folder")
        if filename != "aya-layout-valid.json" {
            let picker = qa.buttons["qa.openin.file"]
            XCTAssertTrue(picker.waitForExistence(timeout: 10))
            picker.tap()
            let option = qa.buttons[filename]
            XCTAssertTrue(option.waitForExistence(timeout: 10),
                          "Requested QA file was not offered in the source app")
            option.tap()
        }
    }

    private func shareToInstalledLantern(_ qa: XCUIApplication) throws {
        let share = qa.buttons["qa.openin.share"]
        XCTAssertTrue(share.waitForExistence(timeout: 10))
        XCTAssertTrue(share.isHittable)
        share.tap()

        // A receiving application must be a real *action* in Apple's UI.
        // DO NOT search all accessibility element types: the QA app's own
        // instructions can contain the destination name as static text, and
        // tapping that text will produce a false-positive handoff.
        let springboard = XCUIApplication(bundleIdentifier: "com.apple.springboard")
        var target: XCUIElement?
        for attempt in 0..<6 {
            for container in [qa, springboard] {
                // Apple's actual activity accessibility hierarchy uses an
                // *unlabelled* cell identifier "shareCell" with a nested
                // StaticText "AYA Lantern" (seen in native run 42427447880).
                // Tap the selectable cell, never the nested label or a source
                // guidance sentence that merely mentions the app name.
                let nativeCells = container.cells
                    .matching(identifier: "shareCell").allElementsBoundByIndex
                for cell in nativeCells {
                    // The cell has identifier "shareCell" while the *child*
                    // static text has identifier "cellTitleLabel" and a
                    // VARIABLE label (AYA Lantern, More, QA Receiver). The
                    // previous query accidentally compared "AYA Lantern"
                    // against the static text's identifier, not its label.
                    let title = cell.staticTexts["cellTitleLabel"].firstMatch
                    if title.exists && title.label == "AYA Lantern" && cell.isHittable {
                        target = cell
                        break
                    }
                }
                if target != nil { break }
                for candidate in [
                    container.buttons["AYA Lantern"],
                    container.buttons["Open in AYA Lantern"],
                    container.buttons["Open with AYA Lantern"],
                    container.cells["AYA Lantern"],
                    container.cells["Open in AYA Lantern"]
                ] where candidate.exists && candidate.isHittable {
                    target = candidate
                    break
                }
                if target != nil { break }
            }
            if target != nil { break }
            if attempt == 1 {
                // "More" is also a shareCell with child title "More" on this
                // runtime, rather than necessarily a UIButton.
                for cell in qa.cells.matching(identifier: "shareCell")
                    .allElementsBoundByIndex {
                    let title = cell.staticTexts["cellTitleLabel"].firstMatch
                    if title.exists && title.label == "More" && cell.isHittable {
                        cell.tap()
                        break
                    }
                }
            }
            // Do not swipe the entire source app here: previous AX traces
            // show this can scroll a visible app recipient out of the row.
        }
        guard let receiver = target else {
            let screenshot = XCTAttachment(screenshot: qa.screenshot())
            screenshot.name = "System Share Sheet without an AYA Lantern action"
            screenshot.lifetime = .keepAlways
            add(screenshot)
            print("Open In diagnostic: activity UI exists = \(qa.otherElements["ActivityListView"].exists)")
            print("Open In diagnostic: QA hierarchy = \(qa.debugDescription)")
            print("Open In diagnostic: SpringBoard hierarchy = \(springboard.debugDescription)")
            XCTFail("OS did not offer a selectable AYA Lantern application target. Do not infer a handoff from source-app text.")
            return
        }
        receiver.tap()
    }

    func testForeignDocumentRequiresPreviewCancelAndApply() throws {
        let qa = XCUIApplication(bundleIdentifier: "org.example.aya.shareqa")
        let lantern = XCUIApplication(bundleIdentifier: "org.example.ayalantern")
        // Each test must start with a clean fictional host layout. The prior
        // test may have completed an explicit Apply and left Lantern running.
        if lantern.state != .notRunning { lantern.terminate() }
        prepareQA(qa, filename: "aya-layout-valid.json")
        try shareToInstalledLantern(qa)

        XCTAssertTrue(lantern.staticTexts["Columns: 1"].waitForExistence(timeout: 25),
                      "The destination app was not launched")
        let apply = lantern.buttons["Apply to demo"]
        XCTAssertTrue(apply.waitForExistence(timeout: 25),
                      "Foreign JSON did not reach an actual review")
        XCTAssertTrue(lantern.staticTexts["Accent: warm"].exists)
        lantern.buttons["Cancel"].tap()
        XCTAssertTrue(lantern.staticTexts["Columns: 1"].exists)

        qa.activate()
        try shareToInstalledLantern(qa)
        XCTAssertTrue(lantern.buttons["Apply to demo"].waitForExistence(timeout: 25))
        XCTAssertTrue(lantern.staticTexts["Columns: 1"].exists)
        lantern.buttons["Apply to demo"].tap()
        XCTAssertTrue(lantern.staticTexts["Columns: 3"].waitForExistence(timeout: 12))
        XCTAssertTrue(lantern.staticTexts["Accent: cool"].exists)
    }

    func testForeignInvalidDocumentNeverOffersApply() throws {
        let qa = XCUIApplication(bundleIdentifier: "org.example.aya.shareqa")
        let lantern = XCUIApplication(bundleIdentifier: "org.example.ayalantern")
        // Each test must start with a clean fictional host layout. The prior
        // test may have completed an explicit Apply and left Lantern running.
        if lantern.state != .notRunning { lantern.terminate() }
        prepareQA(qa, filename: "aya-layout-invalid.json")
        try shareToInstalledLantern(qa)

        XCTAssertTrue(lantern.staticTexts["Columns: 1"].waitForExistence(timeout: 25))
        XCTAssertTrue(lantern.alerts["Cannot use this file"].waitForExistence(timeout: 25),
                      "A real foreign malformed JSON should show visible rejection")
        XCTAssertFalse(lantern.buttons["Apply to demo"].exists)
        XCTAssertTrue(lantern.staticTexts["Accent: warm"].exists)
    }
}
