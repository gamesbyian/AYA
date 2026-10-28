package dev.aya.android

/**
 * The bundled reference is treated as versioned release data, not blindly trusted text.
 * AYA-RAS currently supports an *exact* app version for the guarded integration API.
 * This is deliberately stricter than a loose version range: cross-version equivalence
 * cannot be established from two strings alone.
 */
data class AyaVerifiedReference(val appName: String, val guide: String)

sealed class AyaReferenceCheck {
    data class Accepted(val reference: AyaVerifiedReference) : AyaReferenceCheck()
    data class Rejected(val reason: String) : AyaReferenceCheck()
}

object AyaReferenceVerifier {
    private val metadataLine = Regex("^([a-z][a-z0-9_]*):\\s*(.*?)\\s*$")
    private val requiredSections = listOf(
        "Scope and version", "Quick orientation", "Navigation map",
        "Task recipes", "Features and settings", "Troubleshooting",
        "Limitations and unsupported behavior", "Privacy and data handling",
        "Glossary and synonyms", "Evidence and provenance",
        "Unknowns and escalation", "Assistant answer policy"
    )

    fun verify(guide: String, installedPackageId: String, installedVersion: String): AyaReferenceCheck {
        val lines = guide.removePrefix("\uFEFF").lineSequence().toList()
        if (lines.firstOrNull()?.trim() != "---") {
            return AyaReferenceCheck.Rejected("Reference metadata is missing.")
        }
        val end = lines.indexOfFirstAfter(1) { it.trim() == "---" }
        if (end < 0) return AyaReferenceCheck.Rejected("Reference metadata is incomplete.")
        val values = mutableMapOf<String, String>()
        for (line in lines.subList(1, end)) {
            if (line.isBlank()) continue
            val match = metadataLine.matchEntire(line)
                ?: return AyaReferenceCheck.Rejected("Reference metadata has an invalid entry.")
            val key = match.groupValues[1]
            if (values.containsKey(key)) return AyaReferenceCheck.Rejected("Reference metadata repeats a field.")
            values[key] = match.groupValues[2].trim().trim('"', '\'')
        }
        if (values["schema_version"] != "aya-reference/v1" || values["platform"] != "android") {
            return AyaReferenceCheck.Rejected("Reference format or platform is unsupported.")
        }
        if (values["app_id"] != installedPackageId) {
            return AyaReferenceCheck.Rejected("Reference was built for another application.")
        }
        val min = values["app_version_min"]
        val max = values["app_version_max"]
        if (min != installedVersion || max != installedVersion || installedVersion.isBlank()) {
            return AyaReferenceCheck.Rejected("Reference version does not match the installed application.")
        }
        val name = values["app_name"]?.takeIf { it.isNotBlank() }
            ?: return AyaReferenceCheck.Rejected("Reference application name is missing.")
        val required = listOf("guide_revision", "source_revision", "last_verified_utc", "owner", "locale")
        if (required.any { values[it].isNullOrBlank() }) {
            return AyaReferenceCheck.Rejected("Reference provenance is incomplete.")
        }
        val body = lines.drop(end + 1).joinToString("\n")
        if (body.isBlank()) return AyaReferenceCheck.Rejected("Reference document is empty.")
        val headings = body.lineSequence().filter { it.startsWith("## ") }.map { it.removePrefix("## ").trim() }.toList()
        if (requiredSections.any { section -> headings.count { it == section } != 1 }) {
            return AyaReferenceCheck.Rejected("Reference document is missing required sections.")
        }
        if (Regex("<[A-Za-z][^>\\n]{2,80}>").containsMatchIn(guide)) {
            return AyaReferenceCheck.Rejected("Reference contains unresolved authoring placeholders.")
        }
        return AyaReferenceCheck.Accepted(AyaVerifiedReference(name, guide))
    }

    private inline fun <T> List<T>.indexOfFirstAfter(start: Int, predicate: (T) -> Boolean): Int {
        for (index in start until size) if (predicate(this[index])) return index
        return -1
    }
}
