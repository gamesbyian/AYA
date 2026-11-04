#if os(iOS)
import Foundation
import UIKit
import AYAProtocol

public enum AYAShareRepresentation: Equatable {
    case plainText
    case textDocument
}

/// Outgoing-only iOS share transport. It never guesses a receiving application,
/// records recipient selection or interprets Share Sheet completion as ingestion.
@MainActor public enum AYAAppleSharing {
    public static func makeActivityController(
        packet: AYAApprovedPacket,
        representation: AYAShareRepresentation
    ) throws -> UIActivityViewController {
        let item: Any
        switch representation {
        case .plainText:
            item = packet.text
        case .textDocument:
            item = try writeTemporaryDocument(packet.text)
        }
        return UIActivityViewController(activityItems: [item], applicationActivities: nil)
    }

    /// For UIKit integrations. Host calls this only after the user approved
    /// the exact text and explicitly tapped Share. iPad needs a popover anchor.
    public static func present(
        packet: AYAApprovedPacket,
        representation: AYAShareRepresentation,
        from host: UIViewController,
        anchoredTo sourceView: UIView
    ) throws {
        let controller = try makeActivityController(packet: packet, representation: representation)
        if let popover = controller.popoverPresentationController {
            popover.sourceView = sourceView
            popover.sourceRect = sourceView.bounds
        }
        host.present(controller, animated: true)
    }

    /// Clipboard disclosure is a separate user-selected action. The host
    /// must label it and never use it to replace or follow a failed share.
    public static func copyApprovedText(_ packet: AYAApprovedPacket) {
        UIPasteboard.general.string = packet.text
    }

    /// Best-effort cleanup only when making another share. Restricts removal
    /// to our own private cache directory, genuine UUID-named regular files
    /// older than seven days; never follows symlinks or deletes user documents.
    private static func pruneExpiredPrivateShares(in directory: URL, using manager: FileManager) {
        let keys: Set<URLResourceKey> = [
            .isRegularFileKey, .isSymbolicLinkKey, .contentModificationDateKey
        ]
        guard let urls = try? manager.contentsOfDirectory(
            at: directory,
            includingPropertiesForKeys: Array(keys),
            options: [.skipsHiddenFiles]
        ) else { return }
        let now = Date()
        for url in urls {
            guard let attributes = try? url.resourceValues(forKeys: keys),
                  AYATemporaryShareRetention.canPrune(
                    name: url.lastPathComponent,
                    isRegularFile: attributes.isRegularFile == true,
                    isSymbolicLink: attributes.isSymbolicLink == true,
                    modifiedAt: attributes.contentModificationDate,
                    now: now
                  ) else { continue }
            try? manager.removeItem(at: url)
        }
    }

    private static func writeTemporaryDocument(_ text: String) throws -> URL {
        let fileManager = FileManager.default
        guard let cache = fileManager.urls(for: .cachesDirectory, in: .userDomainMask).first else {
            throw AYAAppleShareError.cacheUnavailable
        }
        let directory = cache.appendingPathComponent("AYA", isDirectory: true)
        try fileManager.createDirectory(at: directory, withIntermediateDirectories: true)
        pruneExpiredPrivateShares(in: directory, using: fileManager)
        let name = "aya-\(UUID().uuidString).txt"
        let destination = directory.appendingPathComponent(name)
        try Data(text.utf8).write(to: destination, options: [.atomic])
        // Do not unlink immediately on activity dismissal: an extension might
        // still consume the exported URL. The host may prune only its own
        // expired AYA cache files in a later lifecycle, after testing.
        return destination
    }
}

public enum AYAAppleShareError: Error { case cacheUnavailable }
#endif
