package dev.aya.android

/** Optional translation/personality-pack handoff, not a localization engine. */
enum class AyaTranslationKind { LANGUAGE, PERSONALITY, TERMINOLOGY, COMBINED }

data class AyaTranslationTask(
    val kind: AyaTranslationKind,
    val target: String,
    val importInstructions: String
) {
    init {
        require(target.isNotBlank() && target.length <= 160 && !target.contains('\n')) {
            "Specify a short target language, personality or terminology goal"
        }
        require(importInstructions.isNotBlank() && importInstructions.length <= 2000) {
            "Document the host's real manual pack-import workflow"
        }
    }
}

sealed class AyaTranslationKitCheck {
    object Accepted : AyaTranslationKitCheck()
    data class Rejected(val reason: String) : AyaTranslationKitCheck()
}

/**
 * Structural and identity guard for a host-authored kit bundled in the installed
 * APK. The host must separately test catalog accuracy and validate imported packs.
 */
object AyaTranslationKitVerifier {
    private val metadataLine = Regex("""^([a-z][a-z0-9_]*):\s*(.*?)\s*$""")
    private val requiredSections = listOf(
        "Output schema", "Source catalog", "Rosetta and glossary",
        "Style and meaning constraints", "Worked examples",
        "Agent instructions", "Host import instructions"
    )

    fun verify(kit: String, installedPackageId: String, installedVersion: String): AyaTranslationKitCheck {
        if (kit.toByteArray(Charsets.UTF_8).size > 1024 * 1024) {
            return AyaTranslationKitCheck.Rejected("Translation kit exceeds 1 MiB.")
        }
        val lines = kit.removePrefix("\uFEFF").lineSequence().toList()
        if (lines.firstOrNull()?.trim() != "---") {
            return AyaTranslationKitCheck.Rejected("Translation kit metadata is missing.")
        }
        val end = (1 until lines.size).firstOrNull { lines[it].trim() == "---" }
            ?: return AyaTranslationKitCheck.Rejected("Translation kit metadata is incomplete.")
        val values = mutableMapOf<String, String>()
        for (line in lines.subList(1, end)) {
            if (line.isBlank()) continue
            val match = metadataLine.matchEntire(line)
                ?: return AyaTranslationKitCheck.Rejected("Invalid translation kit metadata.")
            val key = match.groupValues[1]
            if (key in values) return AyaTranslationKitCheck.Rejected("Duplicate translation kit metadata.")
            values[key] = match.groupValues[2].trim().trim('"', '\'')
        }
        if (values["schema_version"] != "aya-translation-kit/v1") {
            return AyaTranslationKitCheck.Rejected("Unsupported translation kit format.")
        }
        if (values["app_id"] != installedPackageId ||
            values["app_version"] != installedVersion || installedVersion.isBlank()) {
            return AyaTranslationKitCheck.Rejected("Translation kit does not match this installed app.")
        }
        if (listOf("catalog_revision", "source_revision", "source_locale", "owner")
                .any { values[it].isNullOrBlank() }) {
            return AyaTranslationKitCheck.Rejected("Translation kit provenance is incomplete.")
        }
        val headings = lines.drop(end + 1).filter { it.startsWith("## ") }
            .map { it.removePrefix("## ").trim() }
        if (requiredSections.any { section -> headings.count { it == section } != 1 }) {
            return AyaTranslationKitCheck.Rejected("Translation kit is missing a required section.")
        }
        if (Regex("""<[A-Za-z][^>\n]{2,80}>""").containsMatchIn(kit)) {
            return AyaTranslationKitCheck.Rejected("Translation kit contains unresolved placeholders.")
        }
        return AyaTranslationKitCheck.Accepted
    }
}

internal object AyaTranslationDocument {
    fun prompt(task: AyaTranslationTask, direction: String?): String = buildString {
        appendLine("Create an importable language or personality pack for this application.")
        appendLine("Pack type: ${task.kind.name.lowercase()}")
        appendLine("Requested language or style: ${task.target.trim()}")
        direction?.trim()?.takeIf { it.isNotBlank() }?.let {
            appendLine("My additional direction:")
            appendLine(it.replace("\u0000", ""))
        }
        appendLine("Use the attached application's Output schema, Source catalog, Rosetta and glossary, " +
            "meaning constraints, worked examples and agent instructions. Preserve stable keys, " +
            "parameters, plurals, accessibility meaning and exact data-loss distinctions.")
        appendLine("A playful voice may change expressions but must never obscure destructive actions, " +
            "permission choices, safety warnings or technical facts.")
        appendLine("Produce a valid complete or explicitly partial pack in the specified output format. " +
            "Do not change application code, invent features or claim to install the result.")
        appendLine("Make the resulting pack available for me to save. " +
            "I will import it myself using the host's normal controls: " +
            task.importInstructions.trim().replace("\u0000", ""))
        append("If you cannot create a compatible file, explain the limitation instead of pretending it is ready.")
    }
}
