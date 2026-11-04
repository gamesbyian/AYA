import Foundation
import XCTest
@testable import AYAProtocol

final class AYATemporaryShareRetentionTests: XCTestCase {
    let now = Date(timeIntervalSince1970: 2_000_000_000)
    let ownName = "aya-1725EE26-42AC-4E13-AD5D-75408204837C.txt"

    func testOnlyOwnOldRegularFilesQualify() {
        let stale = now.addingTimeInterval(-AYATemporaryShareRetention.expirationInterval - 1)
        XCTAssertTrue(AYATemporaryShareRetention.canPrune(
            name: ownName, isRegularFile: true, isSymbolicLink: false,
            modifiedAt: stale, now: now
        ))
        for name in ["aya-document.txt", "aya-1725EE26-42AC-4E13-AD5D-75408204837C.json",
                     "important.txt", "../" + ownName] {
            XCTAssertFalse(AYATemporaryShareRetention.canPrune(
                name: name, isRegularFile: true, isSymbolicLink: false,
                modifiedAt: stale, now: now
            ), "Must leave unrelated file \(name) untouched")
        }
    }

    func testFreshFilesAndLinksNeverQualify() {
        let stale = now.addingTimeInterval(-AYATemporaryShareRetention.expirationInterval - 1)
        for change in [now, now.addingTimeInterval(1), now.addingTimeInterval(-60)] {
            XCTAssertFalse(AYATemporaryShareRetention.canPrune(
                name: ownName, isRegularFile: true, isSymbolicLink: false,
                modifiedAt: change, now: now
            ))
        }
        for (regular, link, date) in [
            (false, false, stale), (true, true, stale), (true, false, nil)
        ] {
            XCTAssertFalse(AYATemporaryShareRetention.canPrune(
                name: ownName, isRegularFile: regular, isSymbolicLink: link,
                modifiedAt: date, now: now
            ))
        }
    }
}
