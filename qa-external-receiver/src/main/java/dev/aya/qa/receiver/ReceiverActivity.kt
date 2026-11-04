package dev.aya.qa.receiver

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.Bundle
import java.security.MessageDigest

/**
 * Test-only independent Android app/UID. A ResultReceiver reports a digest,
 * never the shared document body. It cannot grant permissions to itself.
 */
class ReceiverActivity : BroadcastReceiver() {
    @Suppress("DEPRECATION")
    override fun onReceive(context: Context, intent: Intent) {
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
                val bytes = context.contentResolver.openInputStream(uri)?.use { it.readBytes() }
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
        result.putInt("receiver_uid", android.os.Process.myUid())
        result.putBoolean("receiver_ack", true)
        // The sending instrumentation test receives these metadata-only
        // extras from Android's ordered broadcast. No document body leaves
        // this process through the evidence channel.
        setResultExtras(result)
        setResultCode(if (status == "read") 1 else 0)
    }

}
