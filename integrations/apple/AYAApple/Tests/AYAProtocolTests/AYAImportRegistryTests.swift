import Foundation
import XCTest
@testable import AYAProtocol

final class AYAImportRegistryTests: XCTestCase {
    private let good = AYAImportFile(
        data: Data(#"{"kind":"palette","value":"blue"}"#.utf8),
        displayName: "wrong-card.txt"
    )

    private func paletteRoute(id: String = "palette") -> AYAImportRoute {
        AYAImportRoute(
            id: id, title: "Palette",
            recognizes: { String(data: $0, encoding: .utf8)?.contains(#""kind":"palette""#) ?? false },
            validates: { String(data: $0, encoding: .utf8)?.contains(#""value":"blue""#) ?? false }
        )
    }

    func testSingleRecognizedRouteAndWrongCardAreHintsOnly() throws {
        let registry = try AYAImportRegistry(routes: [paletteRoute()])
        switch registry.inspect(good, cardRouteID: "translation") {
        case .ready(let route, let wrongCard):
            XCTAssertEqual(route.id, "palette")
            XCTAssertTrue(wrongCard)
        default:
            XCTFail("Expected validated route and wrong-card hint")
        }
    }

    func testMultipleMatchesMustNotPickAutomatically() throws {
        let registry = try AYAImportRegistry(routes: [paletteRoute(), paletteRoute(id: "alternate")])
        switch registry.inspect(good) {
        case .ambiguous(let routes): XCTAssertEqual(routes.count, 2)
        default: XCTFail("Expected explicit route choice")
        }
        switch registry.inspectAs(good, routeID: "alternate") {
        case .ready(let route, _): XCTAssertEqual(route.id, "alternate")
        default: XCTFail("Requested route must revalidate")
        }
    }

    func testUnrecognizedAndInvalidInputsDoNotAuthorizeApply() throws {
        let registry = try AYAImportRegistry(routes: [paletteRoute()])
        let alien = AYAImportFile(data: Data("unrelated".utf8), displayName: "palette.json")
        if case .unrecognized = registry.inspect(alien) {} else { XCTFail("Unrecognized must stay unrecognized") }
        let wrong = AYAImportFile(data: Data(#"{"kind":"palette","value":"red"}"#.utf8), displayName: "palette.json")
        if case .unusable = registry.inspect(wrong) {} else { XCTFail("Recognized invalid content must be unusable") }
        if case .unrecognized = registry.inspectAs(good, routeID: "missing") {} else { XCTFail("Unknown route cannot be forced") }
    }

    func testDuplicateAndEmptyRouteIdentifiersAreRejected() throws {
        XCTAssertThrowsError(try AYAImportRegistry(routes: [paletteRoute(), paletteRoute()]))
        XCTAssertThrowsError(try AYAImportRegistry(routes: [paletteRoute(id: "")]))
    }
}
