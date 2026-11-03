import XCTest
@testable import AYAProtocol

final class AYAReferenceTests: XCTestCase {
    let headings = [
        "Scope and version", "Quick orientation", "Navigation map", "Task recipes",
        "Features and settings", "Troubleshooting", "Limitations and unsupported behavior",
        "Privacy and data handling", "Glossary and synonyms", "Evidence and provenance",
        "Unknowns and escalation", "Assistant answer policy"
    ]

    func guide(platform: String = "ios", appID: String = "org.example.lantern", version: String = "1.2", emptyHeading: Int? = nil) -> String {
        let metadata = """
        ---
        schema_version: aya-reference/v1
        app_id: \(appID)
        app_name: Lantern
        app_version_min: \(version)
        app_version_max: \(version)
        platform: \(platform)
        locale: en
        guide_revision: 1
        source_revision: fixture
        last_verified_utc: 2026-11-03T00:00:00Z
        owner: Test fixture
        ---

        """
        return metadata + headings.enumerated().map { index, title in
            "## \(title)\n\(emptyHeading == index ? "" : "Verified example content")\n"
        }.joined(separator: "\n")
    }

    func testExactIOSGuideAndEditedApproval() throws {
        let reference = try AYAReference(guide: guide(), installedAppID: "org.example.lantern", installedVersion: "1.2")
        let draft = AYAReviewDraft(reference: reference, suggestedQuestion: "Explain this feature")
        XCTAssertTrue(draft.initialText.contains("Explain this feature"))
        let approved = try draft.approve(editedText: "Only this edited text")
        XCTAssertEqual(approved.text, "Only this edited text")
        XCTAssertFalse(approved.text.contains("Explain this feature"))
    }

    func testFailClosedWrongPlatformIdentityAndVersion() throws {
        XCTAssertThrowsError(try AYAReference(guide: guide(platform: "android"), installedAppID: "org.example.lantern", installedVersion: "1.2"))
        XCTAssertThrowsError(try AYAReference(guide: guide(appID: "org.example.other"), installedAppID: "org.example.lantern", installedVersion: "1.2"))
        XCTAssertThrowsError(try AYAReference(guide: guide(version: "1.0"), installedAppID: "org.example.lantern", installedVersion: "1.2"))
    }

    func testRejectsEmptySectionAndDuplicatedMetadata() throws {
        XCTAssertThrowsError(try AYAReference(guide: guide(emptyHeading: 2), installedAppID: "org.example.lantern", installedVersion: "1.2"))
        let duplicated = guide().replacingOccurrences(of: "app_name: Lantern", with: "app_name: Lantern\napp_name: Lantern")
        XCTAssertThrowsError(try AYAReference(guide: duplicated, installedAppID: "org.example.lantern", installedVersion: "1.2"))
    }

    func testRejectsUnresolvedPlaceholdersAndOversize() throws {
        let placeholder = guide().replacingOccurrences(of: "Verified example content", with: "<replace me now>")
        XCTAssertThrowsError(try AYAReference(guide: placeholder, installedAppID: "org.example.lantern", installedVersion: "1.2"))
        XCTAssertThrowsError(try AYAApprovedPacket(editedText: " "))
        XCTAssertThrowsError(try AYAApprovedPacket(editedText: String(repeating: "x", count: 2 * 1_024 * 1_024 + 1)))
    }
}
