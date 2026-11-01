package dev.aya.android

/** A data-only request for a file the adopting host can actually import. */
data class AyaStructuredTask(
    val artifactRole: String,
    val fileExtension: String,
    val mimeType: String,
    val schemaVersion: String,
    val importInstructions: String
) {
    init {
        require(artifactRole.isNotBlank() && artifactRole.length <= 160 &&
            !artifactRole.contains('\n') && !artifactRole.contains('\r')) {
            "Give the artifact a short, truthful role"
        }
        require(fileExtension.matches(Regex("""\.[a-z0-9][a-z0-9._-]{0,15}"""))) {
            "Use a lower-case file extension such as .json"
        }
        require(mimeType.length <= 100 && mimeType.matches(Regex(
            """[A-Za-z0-9][A-Za-z0-9!#$&^_.+-]*/[A-Za-z0-9][A-Za-z0-9!#$&^_.+-]*"""
        ))) { "Specify the host importer's actual MIME type" }
        require(schemaVersion.isNotBlank() && schemaVersion.length <= 100 &&
            !schemaVersion.contains('\n') && !schemaVersion.contains('\r')) {
            "Specify a short importer/schema version"
        }
        require(importInstructions.isNotBlank() && importInstructions.length <= 2000 &&
            !importInstructions.contains('\u0000')) {
            "Explain the real host-owned manual import process"
        }
    }
}

sealed class AyaStructuredKitCheck {
    object Accepted : AyaStructuredKitCheck()
    data class Rejected(val reason: String) : AyaStructuredKitCheck()
}

/** Reject mismatched or malformed developer-authored context before local review. */
object AyaStructuredKitVerifier {
    private val metadata = Regex("""^([a-z][a-z0-9_]*):\s*(.*?)\s*$""")
    private val headings = listOf(
        "Artifact output contract", "Field semantics and bounds",
        "Interactions and precedence", "State preservation and migration",
        "Worked valid and invalid examples", "Agent clarification and safety",
        "Host import and recovery"
    )

    fun verify(kit: String, packageId: String, version: String, task: AyaStructuredTask): AyaStructuredKitCheck {
        if (kit.toByteArray(Charsets.UTF_8).size > 1024 * 1024)
            return AyaStructuredKitCheck.Rejected("Structured artifact kit exceeds 1 MiB.")
        val lines = kit.removePrefix("\uFEFF").lineSequence().toList()
        if (lines.firstOrNull()?.trim() != "---")
            return AyaStructuredKitCheck.Rejected("Structured kit metadata is missing.")
        val end = (1 until lines.size).firstOrNull { lines[it].trim() == "---" }
            ?: return AyaStructuredKitCheck.Rejected("Structured kit metadata is incomplete.")
        val fields = mutableMapOf<String, String>()
        for (line in lines.subList(1, end)) {
            if (line.isBlank()) continue
            val match = metadata.matchEntire(line)
                ?: return AyaStructuredKitCheck.Rejected("Malformed structured kit metadata.")
            val key = match.groupValues[1]
            if (key in fields)
                return AyaStructuredKitCheck.Rejected("Duplicate structured kit metadata.")
            fields[key] = match.groupValues[2].trim().trim('"', '\'')
        }
        if (fields["schema_version"] != "aya-structured-kit/v1")
            return AyaStructuredKitCheck.Rejected("Unknown structured kit format.")
        if (version.isBlank() || fields["app_id"] != packageId ||
            fields["app_version"] != version)
            return AyaStructuredKitCheck.Rejected("Structured kit does not match installed app.")
        if (listOf("schema_revision", "source_revision", "owner",
                "artifact_extension", "artifact_mime").any { fields[it].isNullOrBlank() })
            return AyaStructuredKitCheck.Rejected("Structured kit provenance is incomplete.")
        if (fields["schema_revision"] != task.schemaVersion ||
            fields["artifact_extension"] != task.fileExtension ||
            fields["artifact_mime"] != task.mimeType)
            return AyaStructuredKitCheck.Rejected("Structured kit output contract differs from task.")
        val body = lines.drop(end + 1)
        val positions = body.indices.filter { body[it].startsWith("## ") }
        val actual = positions.map { body[it].removePrefix("## ").trim() }
        if (actual != headings)
            return AyaStructuredKitCheck.Rejected("Structured kit sections are missing or reordered.")
        if (positions.indices.any { index ->
                val first = positions[index] + 1
                val last = if (index + 1 < positions.size) positions[index + 1] else body.size
                body.subList(first, last).none { it.isNotBlank() }
            })
            return AyaStructuredKitCheck.Rejected("Structured kit has an empty section.")
        if (Regex("""<(?:TODO|REPLACE|APP_ID|APP_VERSION|INSERT)[^>\n]{0,80}>""")
                .containsMatchIn(kit))
            return AyaStructuredKitCheck.Rejected("Structured kit has unresolved placeholders.")
        return AyaStructuredKitCheck.Accepted
    }
}

internal object AyaStructuredDocument {
    fun prompt(task: AyaStructuredTask, direction: String?): String = buildString {
        appendLine("Create a host-importable " + task.artifactRole.trim() + " as a data file.")
        appendLine("The host reports its importer expects " + task.fileExtension +
            " (" + task.mimeType + "), schema/version " + task.schemaVersion.trim() + ".")
        direction?.trim()?.takeIf { it.isNotBlank() }?.let {
            appendLine("My requested design or output:")
            appendLine(it.replace("\u0000", ""))
        } ?: appendLine("Ask what artifact I want to create before generating a file.")
        appendLine("Use only the source-derived attached host schema and documented semantics: " +
            "types, bounds, field dependencies, conditional behavior, overrides and defaults.")
        appendLine("Clarify material ambiguity and contradictory requirements; never invent an " +
            "importer capability, undocumented value or answer to a consequential question.")
        appendLine("Preserve required IDs, existing data and unknown fields as the host contract " +
            "requires. Return the exact importable root format, without adding an AYA wrapper, " +
            "code or explanatory fields unless the importer explicitly accepts them.")
        appendLine("The host must independently validate and preview the resulting file. " +
            "Do not claim the file was installed, activated, tested or successfully imported.")
        append("Make the file available for me to save and manually import using: " +
            task.importInstructions.trim())
    }
}
