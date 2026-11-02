package dev.aya.qa.receiver

import android.app.Activity
import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.os.ResultReceiver
import java.security.MessageDigest

/**
 * Test-only independent Android app/UID. A ResultReceiver reports a digest,
 * never the shared document body. It cannot grant permissions to itself.
 */
class ReceiverActivity : Activity() {
    @Suppress("DEPRECATION")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val callback = if (Build.VERSION.SDK_INT >= 33) {
            intent.getParcelableExtra(EXTRA_CALLBACK, ResultReceiver::class.java)
        } else {
            intent.getParcelableExtra<ResultReceiver>(EXTRA_CALLBACK)
        }
        val uri = if (Build.VERSION.SDK_INT >= 33) {
            intent.getParcelableExtra(Intent.EXTRA_STREAM, Uri::class.java)
        } else {
            intent.getParcelableExtra<Uri>(Intent.EXTRA_STREAM)
        }
        val result = Bundle()
        val status = if (uri?.scheme != "content") {
            "invalid_uri"
        } else {
            try {
                val bytes = contentResolver.openInputStream(uri)?.use { it.readBytes() }
                if (bytes == null) {
                    "unreadable"
                } else {
                    val digest = MessageDigest.getInstance("SHA-256").digest(bytes)
                        .joinToString("") { "%02x".format(it.toInt() and 0xff) }
                    result.putString("sha256", digest)
                    result.putInt("bytes", bytes.size)
                    "read"
                }
            } catch (_: SecurityException) {
                "denied"
            } catch (_: Exception) {
                "unreadable"
            }
        }
        result.putString("status", status)
        callback?.send(if (status == "read") Activity.RESULT_OK else Activity.RESULT_CANCELED, result)
        finish()
    }

    companion object {
        const val EXTRA_CALLBACK = "dev.aya.qa.receiver.RESULT_CALLBACK"
    }
}
