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

        // Strictly separate two *different* OS failures: the activity sheet
        // never opened, or it opened but did not offer the registered viewer.
        // No retries, alternate actions, synthetic callbacks or blind swipes.
        let activity = qa.otherElements["ActivityListView"]
        guard activity.waitForExistence(timeout: 12) else {
            let capture = XCTAttachment(screenshot: qa.screenshot())
            capture.name = "File ShareLink did not present the native activity UI"
            capture.lifetime = .keepAlways
            add(capture)
            XCTFail("iOS did not present a Share Sheet after one explicit user-triggered file share")
            return
        }

        let springboard = XCUIApplication(bundleIdentifier: "com.apple.springboard")
        var target: XCUIElement?
        // Native run 42429726479 passed BOTH actual two-app journeys by
        // tapping a shareCell which accessibility exposes as "AYA Lantern"
        // even though the underlying identifier is just "shareCell".
        for _ in 0..<5 {
            for container in [qa, springboard] {
                let labelledCell = container.cells["AYA Lantern"]
                if labelledCell.exists && labelledCell.isHittable {
                    target = labelledCell
                    break
                }
                // A provider/UI version can instead publish the label on a
                // nested StaticText with identifier "cellTitleLabel".
                for cell in container.cells.matching(identifier: "shareCell")
                    .allElementsBoundByIndex {
                    let label = cell.staticTexts["cellTitleLabel"].firstMatch
                    if label.exists && label.label == "AYA Lantern" && cell.isHittable {
                        target = cell
                        break
                    }
                }
                if target != nil { break }
            }
            if target != nil { break }
        }
        guard let receiver = target else {
            let capture = XCTAttachment(screenshot: qa.screenshot())
            capture.name = "Native Share Sheet lacks registered JSON viewer"
            capture.lifetime = .keepAlways
            add(capture)
            let titles = qa.cells.matching(identifier: "shareCell")
                .allElementsBoundByIndex.compactMap { cell -> String? in
                    let title = cell.staticTexts["cellTitleLabel"].firstMatch
                    return title.exists ? title.label : nil
                }
            print("System Share Sheet app targets: \(titles)")
            print("ActivityListView still visible: \(activity.exists)")
            XCTFail("The genuine activity UI did not offer AYA Lantern as a selectable viewer")
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
