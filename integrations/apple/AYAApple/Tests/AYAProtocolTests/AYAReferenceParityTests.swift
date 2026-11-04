import Foundation
import XCTest
@testable import AYAProtocol

private struct AYAReferenceParityMatrix: Decodable {
    let schema: String
    let installedAppID: String
    let installedVersion: String
    let cases: [Case]

    struct Case: Decodable {
        let id: String
        let find: String?
        let replace: String?
        let offlineAccepts: Bool
        let runtimeAccepts: Bool
    }
}

final class AYAReferenceParityTests: XCTestCase {
    func testSharedLanguageNeutralReferenceCases() throws {
        guard let guideURL = Bundle.module.url(
            forResource: "reference-ios", withExtension: "md", subdirectory: "Fixtures"
        ), let casesURL = Bundle.module.url(
            forResource: "cases", withExtension: "json", subdirectory: "Fixtures"
        ) else {
            XCTFail("The shared reference parity fixtures are missing from the SwiftPM test bundle")
            return
        }
        let source = try String(contentsOf: guideURL, encoding: .utf8)
        let matrix = try JSONDecoder().decode(
            AYAReferenceParityMatrix.self, from: Data(contentsOf: casesURL)
        )
        XCTAssertEqual(matrix.schema, "aya-reference-parity/v1")
        XCTAssertGreaterThanOrEqual(matrix.cases.count, 10)
        var seen = Set<String>()
        for entry in matrix.cases {
            XCTAssertTrue(seen.insert(entry.id).inserted, "Duplicate case: \(entry.id)")
            var guide = source
            if let find = entry.find {
                XCTAssertTrue(guide.contains(find), "Missing replacement token for \(entry.id)")
                XCTAssertEqual(guide.components(separatedBy: find).count, 2,
                               "Replacement token should be unique: \(entry.id)")
                guard let replace = entry.replace else {
                    XCTFail("No replacement provided for \(entry.id)")
                    continue
                }
                guide = guide.replacingOccurrences(of: find, with: replace)
            }
            let accepted = (try? AYAReference(
                guide: guide,
                installedAppID: matrix.installedAppID,
                installedVersion: matrix.installedVersion
            )) != nil
            XCTAssertEqual(accepted, entry.runtimeAccepts, "Parity case: \(entry.id)")
        }
    }
}
