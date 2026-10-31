package dev.aya.android

import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Build
import android.provider.DocumentsContract
import java.io.ByteArrayOutputStream
import java.io.IOException
import java.security.MessageDigest
import org.json.JSONObject

/** Human-selected document; bytes are snapshotted once and never changed by a route. */
class AyaImportFile private constructor(
    bytes: ByteArray,
    val displayName: String?,
    val mimeType: String?
) {
    private val snapshot = bytes.copyOf()
    val sizeBytes: Int get() = snapshot.size
    val sha256: String by lazy {
        MessageDigest.getInstance("SHA-256").digest(snapshot).joinToString("") {
            "%02x".format(it.toInt() and 0xff)
        }
    }

    fun bytes(): ByteArray = snapshot.copyOf()
    fun utf8Text(): String? = try {
        Charsets.UTF_8.newDecoder()
            .onMalformedInput(java.nio.charset.CodingErrorAction.REPORT)
            .onUnmappableCharacter(java.nio.charset.CodingErrorAction.REPORT)
            .decode(java.nio.ByteBuffer.wrap(snapshot)).toString()
    } catch (_: Exception) { null }

    /** Metadata is an untrusted routing hint, not proof of provenance or validity. */
    fun hints(): AyaArtifactHints? = try {
        val obj = JSONObject(utf8Text() ?: return null)
        val raw = obj.optString("aya_artifact", "")
        if (raw != "v1") return null
        AyaArtifactHints(
            targetApp = obj.optString("target_app", "").takeIf { it.isNotBlank() },
            artifactType = obj.optString("artifact_type", "").takeIf { it.isNotBlank() },
            schemaVersion = obj.optString("schema_version", "").takeIf { it.isNotBlank() },
            requestId = obj.optString("request_id", "").takeIf { it.isNotBlank() }
        )
    } catch (_: Exception) { null }

    companion object {
        fun fromBytes(bytes: ByteArray, displayName: String? = null, mimeType: String? = null): AyaImportFile =
            AyaImportFile(bytes, displayName, mimeType)
    }
}

data class AyaArtifactHints(
    val targetApp: String?,
    val artifactType: String?,
    val schemaVersion: String?,
    val requestId: String?
)

/** Host validators must inspect the *content*, not merely the suffix or AYA hint. */
interface AyaImportRoute {
    val id: String
    val title: String
    /** Must be read-only and cheap. Return true only when content resembles this format. */
    fun recognizes(file: AyaImportFile): Boolean
    /** Host-specific schema/version/semantic safety checks; never mutate here. */
    fun validate(file: AyaImportFile): AyaImportValidation
}

sealed class AyaImportValidation {
    data class Valid(val preview: String, val warnings: List<String> = emptyList()) : AyaImportValidation()
    data class Invalid(val explanation: String) : AyaImportValidation()
}

/**
 * Analyze only. A host must show a preview and seek deliberate confirmation before
 * calling its *own* importer. For destructive recipes it must dry-run and require
 * operation-specific approvals. Nothing here executes recipes or modifies files.
 */
sealed class AyaImportDecision {
    data class Ready(
        val route: AyaImportRoute,
        val validation: AyaImportValidation.Valid,
        val wrongCard: Boolean,
        val declaredTargetAppMismatch: Boolean,
        val artifact: AyaImportFile
    ) : AyaImportDecision()
    data class Unusable(val route: AyaImportRoute, val explanation: String) : AyaImportDecision()
    data class Ambiguous(val routes: List<AyaImportRoute>) : AyaImportDecision()
    data object Unrecognized : AyaImportDecision()
}

class AyaImportRegistry(
    private val installedAppId: String,
    routes: List<AyaImportRoute>
) {
    private val routes = routes.toList()
    init {
        require(installedAppId.isNotBlank())
        require(this.routes.all { it.id.isNotBlank() && it.title.isNotBlank() })
        require(this.routes.map { it.id }.distinct().size == this.routes.size) {
            "AYA import route IDs must be unique"
        }
    }

    /** A wrong-card match is rerouted in the UI; no import is attempted automatically. */
    fun inspect(file: AyaImportFile, cardRouteId: String? = null): AyaImportDecision {
        // An untrusted hint cannot force routing. Validators decide by content.
        val candidates = routes.filter { route ->
            try { route.recognizes(file) } catch (_: Exception) { false }
        }
        if (candidates.isEmpty()) return AyaImportDecision.Unrecognized
        if (candidates.size > 1) return AyaImportDecision.Ambiguous(candidates)
        val route = candidates.single()
        val validation = try { route.validate(file) } catch (_: Exception) {
            AyaImportValidation.Invalid("This file could not be validated.")
        }
        if (validation is AyaImportValidation.Invalid) {
            return AyaImportDecision.Unusable(route, validation.explanation)
        }
        return AyaImportDecision.Ready(
            route = route,
            validation = validation as AyaImportValidation.Valid,
            wrongCard = cardRouteId != null && cardRouteId != route.id,
            declaredTargetAppMismatch = file.hints()?.targetApp?.let { it != installedAppId } ?: false,
            artifact = file
        )
    }
}

sealed class AyaImportRead {
    data class Loaded(val artifact: AyaImportFile) : AyaImportRead()
    data class Rejected(val explanation: String) : AyaImportRead()
}

/** User-selectable SAF document picker. No storage permission or provider directory sweep. */
object AyaImportPicker {
    const val DEFAULT_MAX_BYTES = 4 * 1024 * 1024
    const val HARD_MAX_BYTES = 16 * 1024 * 1024

    fun openDocumentIntent(mimeTypes: List<String> = listOf("*/*"), initialUri: Uri? = null): Intent {
        val types = mimeTypes.distinct().filter { it.isNotBlank() }.ifEmpty { listOf("*/*") }
        return Intent(Intent.ACTION_OPEN_DOCUMENT).apply {
            addCategory(Intent.CATEGORY_OPENABLE)
            type = if (types.size == 1) types.single() else "*/*"
            if (types.size > 1) putExtra(Intent.EXTRA_MIME_TYPES, types.toTypedArray())
            // Only use a previously user-authorized SAF URI. Never infer storage
            // paths from the package chosen through Android's Sharesheet.
            if (Build.VERSION.SDK_INT >= 26 && initialUri?.scheme == "content") {
                putExtra(DocumentsContract.EXTRA_INITIAL_URI, initialUri)
            }
        }
    }

    /**
     * Use from a worker thread after a user picks a URI. Takes a capped snapshot:
     * re-opening the provider at commit time would allow TOCTOU substitution.
     */
    fun readSelected(
        context: Context,
        uri: Uri,
        maxBytes: Int = DEFAULT_MAX_BYTES
    ): AyaImportRead {
        require(maxBytes in 1..HARD_MAX_BYTES)
        if (uri.scheme != "content") {
            return AyaImportRead.Rejected("Choose a document through Android's file picker.")
        }
        return try {
            val bytes = ByteArrayOutputStream()
            context.contentResolver.openInputStream(uri)?.use { stream ->
                val buffer = ByteArray(8192)
                while (true) {
                    val count = stream.read(buffer)
                    if (count == -1) break
                    if (bytes.size() + count > maxBytes) {
                        return AyaImportRead.Rejected("Selected document exceeds the import size limit.")
                    }
                    bytes.write(buffer, 0, count)
                }
            } ?: return AyaImportRead.Rejected("The selected document could not be opened.")
            AyaImportRead.Loaded(
                AyaImportFile.fromBytes(
                    bytes.toByteArray(),
                    mimeType = context.contentResolver.getType(uri)
                )
            )
        } catch (_: IOException) {
            AyaImportRead.Rejected("The selected document could not be read.")
        } catch (_: SecurityException) {
            AyaImportRead.Rejected("Access to the selected document was denied.")
        } catch (_: Exception) {
            AyaImportRead.Rejected("The selected document could not be inspected.")
        }
    }
}
