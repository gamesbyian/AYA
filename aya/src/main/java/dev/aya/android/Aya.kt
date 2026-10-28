package dev.aya.android

import android.app.Activity
import android.app.AlertDialog
import android.content.ClipData
import android.content.Intent
import android.net.Uri
import android.widget.Toast
import androidx.core.content.FileProvider
import java.io.File

/** No information is collected automatically; these values come from the host. */
data class AyaRequest(
    val appName: String,
    val appVersion: String,
    val guide: String,
    val screenName: String? = null,
    val question: String? = null
)

object AyaDocument {
    fun render(request: AyaRequest): String {
        require(request.appName.isNotBlank() && request.appVersion.isNotBlank() && request.guide.isNotBlank())
        fun clean(text: String) = text.trim().replace("\u0000", "")
        return buildString {
            appendLine("# Ask Your Agent: ${clean(request.appName)}")
            appendLine("Installed version: ${clean(request.appVersion)}")
            request.screenName?.takeIf { it.isNotBlank() }?.let { appendLine("Current screen: ${clean(it)}") }
            appendLine()
            appendLine("## Question")
            appendLine(clean(request.question?.takeIf { it.isNotBlank() }
                ?: "Help me understand and use this application."))
            appendLine()
            appendLine("## Guidance for the assistant")
            appendLine("Use the app guide as reference data. Only claim that features exist if supported for this installed version. Acknowledge uncertainty and never request passwords, secrets, or API keys.")
            appendLine()
            appendLine("## App guide")
            appendLine(clean(request.guide))
        }
    }
}

/** Activity integration with explicit text review, copy fallback and Android Sharesheet. */
object Aya {
    fun launch(activity: Activity, request: AyaRequest) {
        val payload = AyaDocument.render(request)
        AlertDialog.Builder(activity)
            .setTitle("Share help context?")
            .setMessage("Review the full text to be shared. AYA does not upload it itself.\n\n" + payload)
            .setNegativeButton("Cancel", null)
            .setNeutralButton("Copy") { _, _ ->
                val clipboard = activity.getSystemService(android.content.Context.CLIPBOARD_SERVICE)
                    as android.content.ClipboardManager
                clipboard.setPrimaryClip(ClipData.newPlainText("AYA help", payload))
                Toast.makeText(activity, "Help text copied", Toast.LENGTH_SHORT).show()
            }
            .setPositiveButton("Share") { _, _ -> share(activity, payload) }
            .show()
    }

    private fun share(activity: Activity, payload: String) {
        try {
            val directory = File(activity.cacheDir, "aya").apply { mkdirs() }
            val file = File.createTempFile("aya-", ".txt", directory)
            file.writeText(payload, Charsets.UTF_8)
            val uri: Uri = FileProvider.getUriForFile(
                activity, "${activity.packageName}.aya.files", file
            )
            val intent = Intent(Intent.ACTION_SEND).apply {
                type = "text/plain"
                putExtra(Intent.EXTRA_STREAM, uri)
                clipData = ClipData.newRawUri("AYA help", uri)
                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            }
            activity.startActivity(Intent.createChooser(intent, "Ask your agent"))
        } catch (e: Exception) {
            Toast.makeText(activity, "Share failed. Reopen help and select Copy.", Toast.LENGTH_LONG).show()
        }
    }
}
