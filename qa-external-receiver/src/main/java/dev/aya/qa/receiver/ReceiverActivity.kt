package dev.aya.qa.receiver

import android.app.Activity
import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.os.ResultReceiver
import android.util.Log
import java.security.MessageDigest

/**
 * Disposable, external-UID share Activity. The system grants a read-only
 * FileProvider URI only for a granted incoming Intent. No document body is
 * sent to the synthetic test callback and no user app depends on this APK.
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
        Log.i("AYA_URI_QA", "foreign Activity created; callbackPresent=" + (callback != null)
            + " grantFlag=" + (intent.flags and Intent.FLAG_GRANT_READ_URI_PERMISSION != 0))
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
                // Some Android providers report an ungranted URI as an
                // unreadable file instead of a SecurityException. The
                // *same URI* must still pass the granted positive control.
                "unreadable"
            }
        }
        result.putString("status", status)
        result.putInt("receiver_uid", android.os.Process.myUid())
        result.putBoolean("receiver_ack", true)
        Log.i("AYA_URI_QA", "foreign Activity read status=" + status +
            " byteCount=" + result.getInt("bytes", 0))
        callback?.send(if (status == "read") 1 else 0, result)
        Log.i("AYA_URI_QA", "foreign Activity sent callback; callbackPresent=" + (callback != null))
        finish()
    }

    companion object {
        const val EXTRA_CALLBACK = "dev.aya.qa.receiver.RESULT_CALLBACK"
    }
}
