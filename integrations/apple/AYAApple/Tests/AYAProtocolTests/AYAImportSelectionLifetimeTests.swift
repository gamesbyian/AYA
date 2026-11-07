import Foundation
import XCTest
@testable import AYAProtocol

final class AYAImportSelectionLifetimeTests: XCTestCase {
    func testNewSelectionInvalidatesPreviousCallbackAndStaleFinish() {
        var lifetime = AYAImportSelectionLifetime()
        let first = lifetime.begin()
        XCTAssertTrue(lifetime.isCurrent(first))

        let second = lifetime.begin()
        XCTAssertFalse(lifetime.isCurrent(first))
        XCTAssertTrue(lifetime.isCurrent(second))
        XCTAssertFalse(lifetime.finish(first), "Stale completion cannot clear a newer selection")
        XCTAssertTrue(lifetime.isCurrent(second))
        XCTAssertTrue(lifetime.finish(second))
        XCTAssertFalse(lifetime.isCurrent(second))
    }

    func testCancelPreventsLateSelectionFromPublishing() {
        var lifetime = AYAImportSelectionLifetime()
        let pending = lifetime.begin()
        lifetime.cancel()
        XCTAssertFalse(lifetime.isCurrent(pending))
        XCTAssertFalse(lifetime.finish(pending))
        let replacement = lifetime.begin()
        XCTAssertTrue(lifetime.isCurrent(replacement))
        XCTAssertFalse(lifetime.isCurrent(pending))
    }

    func testFinishCannotBeReplayed() {
        var lifetime = AYAImportSelectionLifetime()
        let id = lifetime.begin()
        XCTAssertTrue(lifetime.finish(id))
        XCTAssertFalse(lifetime.finish(id))
        XCTAssertFalse(lifetime.isCurrent(id))
    }

    func testFreshValueStartsWithoutAuthorizedSelection() {
        let lifetime = AYAImportSelectionLifetime()
        XCTAssertFalse(lifetime.isCurrent(UUID()))
    }
}
