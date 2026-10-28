package dev.aya.android

import android.content.ClipData
import android.content.Context
import android.content.Intent
import androidx.core.content.FileProvider
import java.io.File

/** Visible to Android instrumentation tests; consumers use Aya.launchBundled(). */
internal object AyaShareIntents {
    private const val RETAIN_CACHE_DAYS = 7L
    fun create(context: Context, payload: String): Intent {
        require(payload.isNotBlank()) { "Cannot share an empty document" }
        require(payload.toByteArray(Charsets.UTF_8).size <= 2 * 1024 * 1024) {
            "Document too large"
        }
        val directory = File(context.cacheDir, "aya").apply {
            check(exists() || mkdirs()) { "Unable to create AYA cache directory" }
        }
        // Do not invalidate pending recipients by deleting recently shared files.
        val cutoff = System.currentTimeMillis() - RETAIN_CACHE_DAYS * 24 * 60 * 60 * 1000
        directory.listFiles()?.filter {
            it.isFile && it.name.startsWith("aya-") && it.name.endsWith(".txt") &&
                it.lastModified() < cutoff
        }?.forEach { it.delete() }
        val file = File.createTempFile("aya-", ".txt", directory)
        try {
            file.writeText(payload, Charsets.UTF_8)
            val uri = FileProvider.getUriForFile(
                context, "${context.packageName}.aya.files", file
            )
            return Intent(Intent.ACTION_SEND).apply {
                type = "text/plain"
                putExtra(Intent.EXTRA_STREAM, uri)
                clipData = ClipData.newRawUri("AYA help context", uri)
                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            }
        } catch (error: Exception) {
            file.delete()
            throw error
        }
    }
}
