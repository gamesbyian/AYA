import Foundation

/// Source-verified, installed-build-matched AYA-RAS text. This validates the
/// packet shape and identity; it cannot independently prove factual accuracy.
public struct AYAReference: Equatable {
    public let appName: String
    public let text: String

    public init(guide: String, installedAppID: String, installedVersion: String) throws {
        guard !installedAppID.isEmpty, !installedVersion.isEmpty else {
            throw AYAReferenceError.invalidHostIdentity
        }
        guard guide.utf8.count <= 2 * 1_024 * 1_024 else {
            throw AYAReferenceError.tooLarge
        }
        let cleaned = guide.hasPrefix("\u{FEFF}") ? String(guide.dropFirst()) : guide
        let lines = cleaned.components(separatedBy: .newlines)
        guard lines.first?.trimmingCharacters(in: .whitespaces) == "---",
              let close = lines.dropFirst().firstIndex(where: { $0.trimmingCharacters(in: .whitespaces) == "---" })
        else { throw AYAReferenceError.invalidMetadata }

        var metadata: [String: String] = [:]
        for line in lines[1..<close] where !line.trimmingCharacters(in: .whitespaces).isEmpty {
            guard let colon = line.firstIndex(of: ":") else { throw AYAReferenceError.invalidMetadata }
            let key = String(line[..<colon])
            guard let first = key.first, first.isLowercase && first.isASCII,
                  key.allSatisfy({ $0.isASCII && ($0.isLowercase || $0.isNumber || $0 == "_") }),
                  metadata[key] == nil
            else { throw AYAReferenceError.invalidMetadata }
            let value = String(line[line.index(after: colon)...]).trimmingCharacters(in: .whitespaces)
            metadata[key] = value.trimmingCharacters(in: CharacterSet(charactersIn: "\"'"))
        }
        guard metadata["schema_version"] == "aya-reference/v1", metadata["platform"] == "ios" else {
            throw AYAReferenceError.unsupportedReference
        }
        guard metadata["app_id"] == installedAppID else { throw AYAReferenceError.wrongHost }
        guard metadata["app_version_min"] == installedVersion,
              metadata["app_version_max"] == installedVersion else {
            throw AYAReferenceError.staleReference
        }
        for field in ["app_name", "guide_revision", "source_revision", "last_verified_utc", "owner", "locale"] {
            guard let value = metadata[field], !value.isEmpty else {
                throw AYAReferenceError.invalidMetadata
            }
        }
        let requiredHeadings = [
            "Scope and version", "Quick orientation", "Navigation map",
            "Task recipes", "Features and settings", "Troubleshooting",
            "Limitations and unsupported behavior", "Privacy and data handling",
            "Glossary and synonyms", "Evidence and provenance",
            "Unknowns and escalation", "Assistant answer policy"
        ]
        let body = Array(lines.dropFirst(close + 1))
        let locations = body.indices.filter { body[$0].hasPrefix("## ") }
        let headings = locations.map { String(body[$0].dropFirst(3)).trimmingCharacters(in: .whitespaces) }
        guard headings == requiredHeadings else { throw AYAReferenceError.invalidSections }
        for index in locations.indices {
            let start = locations[index] + 1
            let end = index + 1 < locations.count ? locations[index + 1] : body.count
            guard body[start..<end].contains(where: {
                let trimmed = $0.trimmingCharacters(in: .whitespacesAndNewlines)
                return !trimmed.isEmpty && !trimmed.hasPrefix("#")
            }) else { throw AYAReferenceError.invalidSections }
        }
        if cleaned.range(of: "<[A-Za-z][^>\\n]{2,80}>", options: .regularExpression) != nil {
            throw AYAReferenceError.unresolvedPlaceholder
        }
        self.appName = metadata["app_name"]!
        self.text = cleaned
    }
}

public enum AYAReferenceError: Error, Equatable {
    case invalidHostIdentity, tooLarge, invalidMetadata, unsupportedReference
    case wrongHost, staleReference, invalidSections, unresolvedPlaceholder
}

/// Represents a reviewed AYA packet. Calling approve is an explicit UI event
/// from the integrating host; merely constructing a draft never shares data.
public struct AYAReviewDraft {
    public let reference: AYAReference
    public let suggestedQuestion: String

    public init(reference: AYAReference, suggestedQuestion: String = "") {
        self.reference = reference
        self.suggestedQuestion = suggestedQuestion
    }

    public var initialText: String {
        let question = suggestedQuestion.trimmingCharacters(in: .whitespacesAndNewlines)
        return "# Ask Your Agent\n\nQuestion: \(question.isEmpty ? "Help me use this app." : question)\n\n---\n\n" + reference.text
    }

    public func approve(editedText: String) throws -> AYAApprovedPacket {
        try AYAApprovedPacket(editedText: editedText)
    }
}

public struct AYAApprovedPacket: Equatable {
    public let text: String

    public init(editedText: String) throws {
        guard !editedText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
            throw AYAApprovalError.emptyText
        }
        guard editedText.utf8.count <= 2 * 1_024 * 1_024 else {
            throw AYAApprovalError.tooLarge
        }
        self.text = editedText
    }
}

public enum AYAApprovalError: Error, Equatable { case emptyText, tooLarge }
