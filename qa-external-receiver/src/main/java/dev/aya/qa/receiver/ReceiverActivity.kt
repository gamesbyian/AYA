package dev.aya.qa.receiver

import android.app.Activity
import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.app.PendingIntent
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
            intent.getParcelableExtra(EXTRA_CALLBACK, PendingIntent::class.java)
        } else {
            intent.getParcelableExtra<PendingIntent>(EXTRA_CALLBACK)
        }
        Log.i("AYA_URI_QA", "foreign Activity created; callbackPresent=" + (callback != null)
            + " grantFlag=" + (intent.flags and Intent.FLAG_GRANT_READ_URI_PERMISSION != 0))
        val uri = if (Build.VERSION.SDK_INT >= 33) {
            intent.getParcelableExtra(Intent.EXTRA_STREAM, Uri::class.java)
        } else {
            intent.getParcelableExtra<Uri>(Intent.EXTRA_STREAM)
        }
        val result = Bundle()
        // Independent support for the spatial packet's separate manifest and image URIs.
        // Report only content hashes/lengths, never the private image or manifest body.
        if (intent.action == Intent.ACTION_SEND_MULTIPLE) {
            val uris = intent.getParcelableArrayListExtra<Uri>(Intent.EXTRA_STREAM)
            val hashes = arrayListOf<String>()
            val lengths = arrayListOf<Int>()
            var status = "read"
            if (uris.isNullOrEmpty()) {
                status = "invalid_uri"
            } else {
                for (item in uris) {
                    if (item.scheme != "content") { status = "invalid_uri"; break }
                    try {
                        val hash = MessageDigest.getInstance("SHA-256")
                        var length = 0
                        contentResolver.openInputStream(item)?.use { input ->
                            val buffer = ByteArray(8192)
                            while (true) {
                                val n = input.read(buffer)
                                if (n < 0) break
                                if (n > 0) { hash.update(buffer, 0, n); length += n }
                            }
                        } ?: throw IllegalStateException("Cannot open image stream")
                        hashes.add(hash.digest().joinToString("") { "%02x".format(it.toInt() and 0xff) })
                        lengths.add(length)
                    } catch (_: SecurityException) {
                        status = "denied"; break
                    } catch (_: Exception) {
                        status = "unreadable"; break
                    }
                }
            }
            result.putString("status", status)
            result.putInt("receiver_uid", android.os.Process.myUid())
            result.putBoolean("receiver_ack", true)
            result.putBoolean("received_grant_flag",
                intent.flags and Intent.FLAG_GRANT_READ_URI_PERMISSION != 0)
            result.putInt("attachment_count", hashes.size)
            result.putStringArrayList("sha256_all", hashes)
            result.putIntegerArrayList("bytes_all", lengths)
            result.putString("received_text", intent.getStringExtra(Intent.EXTRA_TEXT))
            try {
                callback?.send(this, if (status == "read") 1 else 0, Intent().apply {
                    putExtra(EXTRA_EVIDENCE, result)
                })
            } catch (_: PendingIntent.CanceledException) {
                Log.i("AYA_URI_QA", "foreign multi-file callback canceled")
            }
            finish()
            return
        }
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
        result.putBoolean(
            "received_grant_flag",
            intent.flags and Intent.FLAG_GRANT_READ_URI_PERMISSION != 0
        )
        Log.i("AYA_URI_QA", "foreign Activity read status=" + status +
            " byteCount=" + result.getInt("bytes", 0))
        try {
            // Send metadata through the creator app's framework PendingIntent.
            // The callback cannot serialize a private test-only class.
            callback?.send(this, if (status == "read") 1 else 0, Intent().apply {
                putExtra(EXTRA_EVIDENCE, result)
            })
            Log.i("AYA_URI_QA", "foreign Activity sent platform callback; present=" + (callback != null))
        } catch (_: PendingIntent.CanceledException) {
            Log.i("AYA_URI_QA", "foreign Activity callback was canceled")
        }
        finish()
    }

    companion object {
        const val EXTRA_CALLBACK = "dev.aya.qa.receiver.RESULT_CALLBACK"
        const val EXTRA_EVIDENCE = "dev.aya.qa.receiver.EVIDENCE"
    }
}
