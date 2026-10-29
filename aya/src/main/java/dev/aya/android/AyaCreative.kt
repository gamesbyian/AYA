package dev.aya.android

/**
 * Typed, host-authored requirements for a single image-generation handoff.
 * AYA cannot verify that a recipient creates the image or that the host imports it.
 * Values must describe the current, tested host import workflow.
 */
data class AyaImageRequirements(
    val aspectWidth: Int,
    val aspectHeight: Int,
    val preferredWidthPx: Int? = null,
    val preferredHeightPx: Int? = null,
    val acceptedMimeTypes: List<String> = listOf("image/png", "image/jpeg"),
    val transparentBackground: Boolean? = null,
    val safeMarginPercent: Int? = null
) {
    init {
        require(aspectWidth in 1..100 && aspectHeight in 1..100) {
            "Image aspect ratio must be positive and bounded"
        }
        require((preferredWidthPx == null) == (preferredHeightPx == null)) {
            "Preferred width and height must be specified together"
        }
        if (preferredWidthPx != null && preferredHeightPx != null) {
            require(preferredWidthPx in 1..16384 && preferredHeightPx in 1..16384) {
                "Preferred dimensions must be between 1 and 16384 pixels"
            }
            require(preferredWidthPx.toLong() * aspectHeight ==
                preferredHeightPx.toLong() * aspectWidth) {
                "Preferred dimensions must match the requested aspect ratio"
            }
        }
        require(acceptedMimeTypes.isNotEmpty() && acceptedMimeTypes.distinct().size ==
            acceptedMimeTypes.size &&
            acceptedMimeTypes.all { it in setOf("image/png", "image/jpeg", "image/webp") }) {
            "Accepted formats must be a nonempty, unique list of supported image MIME types"
        }
        require(safeMarginPercent == null || safeMarginPercent in 0..40) {
            "Safe margin must be between 0 and 40 percent"
        }
    }

    internal fun describe(): String = buildString {
        append("Aspect ratio: ${aspectWidth}:${aspectHeight}")
        if (preferredWidthPx != null && preferredHeightPx != null) {
            append("; preferred resolution: ${preferredWidthPx} × ${preferredHeightPx} pixels")
        }
        append("; import-compatible formats: ${acceptedMimeTypes.joinToString(", ")}")
        when (transparentBackground) {
            true -> append("; transparent background required")
            false -> append("; opaque background required")
            null -> Unit
        }
        safeMarginPercent?.let {
            append("; keep essential subjects and lettering at least ${it}% away from every edge")
        }
    }
}

/**
 * Only non-sensitive contextual information deliberately supplied by the host.
 * The user supplies creative direction separately, either in the host's editor
 * or AYA's optional direction composer.
 */
data class AyaCreativeTask(
    val subject: String,
    val assetRole: String,
    val image: AyaImageRequirements,
    val importInstructions: String,
    val hostContext: String? = null
) {
    init {
        require(subject.isNotBlank() && subject.length <= 500 && !subject.contains('\n')) {
            "Use a short, single-line subject"
        }
        require(assetRole.isNotBlank() && assetRole.length <= 200 &&
            !assetRole.contains('\n')) { "Use a short, single-line asset role" }
        require(importInstructions.isNotBlank() && importInstructions.length <= 2000) {
            "Include the current host's manual import steps"
        }
        require(hostContext == null || hostContext.length <= 1000) {
            "Host context is too long"
        }
    }
}

internal object AyaCreativeDocument {
    fun prompt(task: AyaCreativeTask, direction: String?): String = buildString {
        appendLine("Please generate an actual image for me now, rather than merely writing a prompt or explaining how to generate one.")
        appendLine("Subject: ${task.subject.trim()}")
        appendLine("Intended use: ${task.assetRole.trim()}")
        direction?.trim()?.takeIf { it.isNotBlank() }?.let {
            appendLine("My creative direction:")
            appendLine(it.replace("\u0000", ""))
        } ?: appendLine("Creative direction: Choose an appropriate design for this subject and use.")
        appendLine("Image requirements: ${task.image.describe()}.")
        task.hostContext?.trim()?.takeIf { it.isNotBlank() }?.let {
            appendLine("Additional host-supplied context: ${it.replace("\u0000", "")}")
        }
        appendLine("If your image generator cannot meet the exact pixel dimensions or formats, use the closest supported image and tell me what differs. Avoid cropping essential elements.")
        appendLine("Make the generated image available for me to save on my device. Do not claim it has been imported or installed in the host app.")
        appendLine("After saving, I will return to the app and import the artwork manually: ${task.importInstructions.trim().replace("\u0000", "")}")
        append("If you cannot generate an image, say so explicitly. Do not pretend an image was created.")
    }
}
