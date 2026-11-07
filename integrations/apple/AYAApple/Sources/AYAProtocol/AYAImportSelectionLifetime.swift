import Foundation

/// Tracks one explicitly user-authorized import selection at a time.
/// A callback from an earlier selection must never publish a proposal into
/// the host after the user cancels, navigates away or chooses another file.
///
/// This has no filesystem, provider or automatic-retry capabilities.
public struct AYAImportSelectionLifetime {
    private var currentID: UUID?

    public init() {}

    /// Starts a new selection and invalidates all previously issued tokens.
    @discardableResult
    public mutating func begin() -> UUID {
        let id = UUID()
        currentID = id
        return id
    }

    /// True only for the currently active selection.
    public func isCurrent(_ id: UUID) -> Bool {
        currentID == id
    }

    /// Finishes only the current selection. Stale callbacks cannot clear it.
    @discardableResult
    public mutating func finish(_ id: UUID) -> Bool {
        guard isCurrent(id) else { return false }
        currentID = nil
        return true
    }

    /// Explicit dismissal invalidates every outstanding callback token.
    public mutating func cancel() {
        currentID = nil
    }
}
