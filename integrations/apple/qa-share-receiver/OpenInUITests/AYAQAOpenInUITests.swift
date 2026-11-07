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

        // This is a real iOS system activity UI, not a test-injected URL.
        // Discover the *installed application target*, not just any Share
        // Sheet button or the visible contents of the document.
        let springboard = XCUIApplication(bundleIdentifier: "com.apple.springboard")
        var target: XCUIElement?
        for attempt in 0..<8 {
            for container in [qa, springboard] {
                let candidate = container.descendants(matching: .any)
                    .matching(NSPredicate(
                        format: "label CONTAINS[c] %@", "AYA Lantern"
                    )).firstMatch
                if candidate.exists && candidate.isHittable {
                    target = candidate
                    break
                }
            }
            if target != nil { break }
            if attempt == 2 {
                let more = qa.buttons["More"]
                if more.exists && more.isHittable { more.tap() }
            }
            qa.swipeUp()
        }
        guard let receiver = target else {
            let labels = qa.buttons.allElementsBoundByIndex
                .map(\.label).filter { !$0.contains("\n") && $0.count < 65 }
                .prefix(30)
            XCTFail("OS did not offer independently installed Lantern for the QA JSON document. Share buttons: \(Array(labels))")
            return
        }
        receiver.tap()
    }

    func testForeignDocumentRequiresPreviewCancelAndApply() throws {
        let qa = XCUIApplication(bundleIdentifier: "org.example.aya.shareqa")
        let lantern = XCUIApplication(bundleIdentifier: "org.example.ayalantern")
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
        prepareQA(qa, filename: "aya-layout-invalid.json")
        try shareToInstalledLantern(qa)

        XCTAssertTrue(lantern.staticTexts["Columns: 1"].waitForExistence(timeout: 25))
        XCTAssertTrue(lantern.alerts["Cannot use this file"].waitForExistence(timeout: 25),
                      "A real foreign malformed JSON should show visible rejection")
        XCTAssertFalse(lantern.buttons["Apply to demo"].exists)
        XCTAssertTrue(lantern.staticTexts["Accent: warm"].exists)
    }
}
