import Foundation
import XCTest

/// An AYA-SDK-free, installed two-app reproduction of one iOS Files callback.
/// The source app alone writes its private Documents, and this app never
/// receives a path or file contents except from Apple's real picker UI.
final class MinimalFilesConsumerUITests: XCTestCase {
    override func setUpWithError() throws {
        continueAfterFailure = false
    }

    private func selectFromFiles(_ consumer: XCUIApplication) {
        let picker = consumer.buttons["minimal.consumer.choose"]
        XCTAssertTrue(picker.waitForExistence(timeout: 15))
        picker.tap()

        let stage = consumer.staticTexts["minimal.consumer.state"]
        XCTAssertTrue(stage.waitForExistence(timeout: 6))
        XCTAssertEqual(stage.label, "State: picker-opened")

        let file = consumer.cells["aya-layout-invalid.json, json"]
        // Navigate *actual* Files UI. The provider's title is a different
        // element from its folder cell, even when both display the app name.
        for _ in 0..<7 {
            if file.exists && file.isHittable { break }

            let providerFolder = consumer.cells.matching(
                NSPredicate(format: "label BEGINSWITH[c] %@", "Minimal Files Source,")
            ).firstMatch
            let providerTitle = consumer.navigationBars.staticTexts["Minimal Files Source"]
            let localLocation = consumer.descendants(matching: .any)
                .matching(NSPredicate(format: "label ==[c] %@", "On My iPhone"))
                .firstMatch

            if providerFolder.exists && providerFolder.isHittable {
                providerFolder.tap()
                _ = file.waitForExistence(timeout: 5)
            } else if providerTitle.exists {
                // The provider is open. Do not oscillate back to Locations;
                // allow its LocalStorage index to catch up.
                if file.waitForExistence(timeout: 6) { break }
            } else if localLocation.exists && localLocation.isHittable {
                localLocation.tap()
            } else {
                let browse = consumer.buttons.matching(
                    NSPredicate(format: "label == %@", "Browse")
                ).allElementsBoundByIndex
                    .filter { $0.isHittable }
                    .max { $0.frame.midY < $1.frame.midY }
                if let browse {
                    browse.tap()
                } else {
                    _ = file.waitForExistence(timeout: 3)
                }
            }
        }

        guard file.exists && file.isHittable else {
            let screenshot = XCTAttachment(screenshot: consumer.screenshot())
            screenshot.name = "Minimal system Files picker could not find source item"
            screenshot.lifetime = .keepAlways
            add(screenshot)
            XCTFail("The foreign JSON item was never selectable in Files. \(consumer.debugDescription)")
            return
        }

        file.tap() // ONE real Files-selection gesture; no callback injection.
    }

    private func assertSystemDeliversForeignItem(sourceFileCount: Int) {
        let source = XCUIApplication(bundleIdentifier: "org.example.aya.minfiles.source")
        source.launch()
        let prepare = source.buttons[
            sourceFileCount == 1 ? "minimal.source.one" : "minimal.source.seven"
        ]
        XCTAssertTrue(prepare.waitForExistence(timeout: 15))
        prepare.tap()
        let status = source.staticTexts["minimal.source.status"]
        XCTAssertTrue(status.waitForExistence(timeout: 8))
        XCTAssertEqual(
            status.label,
            "Prepared \(sourceFileCount) verified document(s)",
            "The separately installed source must author the exact inventory"
        )

        let consumer = XCUIApplication(bundleIdentifier: "org.example.aya.minfiles.consumer")
        consumer.launch()
        XCTAssertTrue(consumer.staticTexts["Callbacks: 0"].waitForExistence(timeout: 12))
        selectFromFiles(consumer)

        // This is the ONLY product acceptance criterion. No AYA package,
        // reader, JSON parsing or user confirmation exists in the consumer.
        // Fail with real stage and Files hierarchy if a visible item did
        // nothing because Apple's provider could not resolve its item ID.
        let succeeded = consumer.staticTexts[
            "State: callback-success: aya-layout-invalid.json"
        ].waitForExistence(timeout: 16)
        if !succeeded {
            let screenshot = XCTAttachment(screenshot: consumer.screenshot())
            screenshot.name = "Minimal Files selection did not call back"
            screenshot.lifetime = .keepAlways
            add(screenshot)
            let state = consumer.staticTexts["minimal.consumer.state"]
            let count = consumer.staticTexts["minimal.consumer.count"]
            print("MINIMAL FILES CALLBACK FAILURE: \(state.exists ? state.label : "no state"), \(count.exists ? count.label : "no count")")
            print("MINIMAL FILES AX HIERARCHY: \(consumer.debugDescription)")
        }
        XCTAssertTrue(
            succeeded,
            "OS never delivered a successful picker callback for the foreign JSON"
        )
        XCTAssertTrue(consumer.staticTexts["Callbacks: 1"].exists)
    }

    // Run EACH on a separately erased simulator / fresh QA app Documents.
    // Never use one test to stage one file and later add six more.
    func testOneForeignFileReturnsSystemCallback() {
        assertSystemDeliversForeignItem(sourceFileCount: 1)
    }

    func testSevenForeignFilesReturnSystemCallback() {
        assertSystemDeliversForeignItem(sourceFileCount: 7)
    }
}
