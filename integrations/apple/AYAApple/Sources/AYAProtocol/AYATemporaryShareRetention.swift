import Foundation

/// Conservative selection policy for AYA's *own* expired temporary shares.
/// The transport supplies verified regular-file/symlink metadata and owns the
/// actual filesystem deletion. This never searches another app's sandbox.
public enum AYATemporaryShareRetention {
    public static let expirationInterval: TimeInterval = 7 * 24 * 60 * 60

    public static func canPrune(
        name: String,
        isRegularFile: Bool,
        isSymbolicLink: Bool,
        modifiedAt: Date?,
        now: Date
    ) -> Bool {
        guard isRegularFile && !isSymbolicLink,
              name.hasPrefix("aya-") && name.hasSuffix(".txt"),
              let changed = modifiedAt,
              let parsed = UUID(uuidString: String(name.dropFirst(4).dropLast(4))),
              parsed.uuidString.count == 36
        else { return false }
        let age = now.timeIntervalSince(changed)
        return age > expirationInterval
    }
}
