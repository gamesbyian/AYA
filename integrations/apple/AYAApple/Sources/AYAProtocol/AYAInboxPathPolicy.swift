import Foundation

/// Restricts the *unscoped* form of an OS Open In handoff to a file copied
/// into this app's own Documents/Inbox. This is an authorized host-owned copy,
/// not access to a provider or another app's directory.
///
/// The caller is responsible for proving this URL came from a user-controlled
/// document-opening callback and for coordinating, bounding and validating
/// the bytes. This policy grants no filesystem rights itself.
public enum AYAInboxPathPolicy {
    public static func permitsCopiedDocument(
        _ fileURL: URL, documentsDirectory: URL
    ) -> Bool {
        guard fileURL.isFileURL, documentsDirectory.isFileURL else {
            return false
        }
        let inbox = documentsDirectory
            .appendingPathComponent("Inbox", isDirectory: true)
            .resolvingSymlinksInPath()
            .standardizedFileURL
            .path
        let selected = fileURL
            .resolvingSymlinksInPath()
            .standardizedFileURL
            .path
        // Require the path separator. Inbox2 and Inbox/../Other must not
        // become implicitly authorized merely by sharing a string prefix.
        return selected.hasPrefix(inbox + "/")
    }
}
