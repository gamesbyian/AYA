package dev.aya.android

import android.app.assist.AssistContent
import org.json.JSONObject

/**
 * Optional host-side Android system-assistant context. This is NOT the AYA
 * handoff, not a new receiver, and not a promise that an assistant uses it.
 *
 * Call only from a host Activity.onProvideAssistContent override when that
 * host explicitly chooses to expose the listed public-facing information.
 * Never put credentials, device identifiers, private library titles or
 * local paths in these fields.
 */
data class AyaPublicAssistContext(
    val applicationName: String,
    val applicationVersion: String,
    val visibleTitle: String,
    val visibleDescription: String? = null
) {
    init {
        require(applicationName.isNotBlank() && applicationName.length <= 120)
        require(applicationVersion.isNotBlank() && applicationVersion.length <= 80)
        require(visibleTitle.isNotBlank() && visibleTitle.length <= 200)
        require(visibleDescription == null || visibleDescription.length <= 500)
        require(listOfNotNull(
            applicationName, applicationVersion, visibleTitle, visibleDescription
        ).all { !it.contains('\u0000') })
    }
}

object AyaAssistContext {
    /** Structured data must be schema.org JSON-LD per Android AssistContent. */
    fun toJsonLd(context: AyaPublicAssistContext): String {
        val data = JSONObject()
            .put("@context", "https://schema.org")
            .put("@type", "SoftwareApplication")
            .put("name", context.applicationName)
            .put("softwareVersion", context.applicationVersion)
            .put("about", JSONObject().apply {
                put("@type", "Thing")
                put("name", context.visibleTitle)
                context.visibleDescription?.takeIf { it.isNotBlank() }?.let {
                    put("description", it)
                }
            })
        val encoded = data.toString()
        require(encoded.toByteArray(Charsets.UTF_8).size <= 2048) {
            "Assist context exceeds 2048 bytes"
        }
        return encoded
    }

    /** No ClipData, Intent extras, URI grants, permissions or file attachments. */
    fun populate(outContent: AssistContent, context: AyaPublicAssistContext) {
        outContent.setStructuredData(toJsonLd(context))
    }
}
