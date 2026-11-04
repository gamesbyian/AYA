import Foundation

/// Bytes copied from an explicit user selection. Names and hashes are hints,
/// not authorization, provenance, or a reason to execute returned content.
public struct AYAImportFile {
    public let data: Data
    public let displayName: String
    public let sha256Hex: String?

    public init(data: Data, displayName: String, sha256Hex: String? = nil) {
        self.data = data
        self.displayName = displayName
        self.sha256Hex = sha256Hex
    }
}

/// The adopting host supplies truthful content recognition and semantic
/// validation for *its own* artifact formats. AYA never installs a recipe.
public struct AYAImportRoute {
    public let id: String
    public let title: String
    public let recognizes: (Data) -> Bool
    public let validates: (Data) -> Bool

    public init(
        id: String, title: String,
        recognizes: @escaping (Data) -> Bool,
        validates: @escaping (Data) -> Bool
    ) {
        self.id = id
        self.title = title
        self.recognizes = recognizes
        self.validates = validates
    }
}

public enum AYAImportDecision {
    /// Ready to open the host's *additional* impact preview, NOT to apply.
    case ready(route: AYAImportRoute, wrongCard: Bool)
    case ambiguous(routes: [AYAImportRoute])
    case unusable(recognizedRouteIDs: [String])
    case unrecognized
}

/// Routes import files app-wide, not just through the card from which they
/// were picked. Neither the extension, filename nor optional AYA envelope
/// can establish a route without recognition of the actual bytes.
public struct AYAImportRegistry {
    private let routes: [AYAImportRoute]

    public init(routes: [AYAImportRoute]) throws {
        let ids = routes.map(\.id)
        guard ids.allSatisfy({ !$0.isEmpty }),
              Set(ids).count == ids.count else {
            throw AYAImportRegistryError.invalidRoutes
        }
        self.routes = routes
    }

    public func inspect(_ file: AYAImportFile, cardRouteID: String? = nil) -> AYAImportDecision {
        let matched = routes.filter { $0.recognizes(file.data) }
        let valid = matched.filter { $0.validates(file.data) }
        if valid.count == 1 {
            let selected = valid[0]
            return .ready(route: selected, wrongCard: cardRouteID.map { $0 != selected.id } ?? false)
        }
        if valid.count > 1 { return .ambiguous(routes: valid) }
        if !matched.isEmpty { return .unusable(recognizedRouteIDs: matched.map(\.id)) }
        return .unrecognized
    }

    /// Explicit route choice re-runs recognition and validation; it does not
    /// bypass the app's checks when the user selects a different card.
    public func inspectAs(
        _ file: AYAImportFile, routeID: String, cardRouteID: String? = nil
    ) -> AYAImportDecision {
        guard let route = routes.first(where: { $0.id == routeID }) else { return .unrecognized }
        guard route.recognizes(file.data) else { return .unrecognized }
        guard route.validates(file.data) else {
            return .unusable(recognizedRouteIDs: [route.id])
        }
        return .ready(route: route, wrongCard: cardRouteID.map { $0 != route.id } ?? false)
    }
}

public enum AYAImportRegistryError: Error { case invalidRoutes }
