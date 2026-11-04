package dev.aya.android

import android.content.ComponentName
import android.os.ResultReceiver
import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith
import java.security.MessageDigest
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicReference

/**
 * Real two-APK, distinct-UID test of Android FileProvider URI grants.
 * This is NOT an actual ChatGPT/Claude/Gemini ingestion test.
 */
@RunWith(AndroidJUnit4::class)
class AyaExternalUriGrantTest {
    private val context: Context
        get() = InstrumentationRegistry.getInstrumentation().targetContext

    private fun sendToSeparateApp(intent: Intent): Bundle {
        val done = CountDownLatch(1)
        val result = AtomicReference<Bundle>()
        val callback = object : ResultReceiver(Handler(Looper.getMainLooper())) {
            override fun onReceiveResult(resultCode: Int, resultData: Bundle?) {
                result.set(resultData)
                done.countDown()
            }
        }
        intent.component = ComponentName(
            "dev.aya.qa.receiver", "dev.aya.qa.receiver.ReceiverActivity"
        )
        intent.putExtra("dev.aya.qa.receiver.RESULT_CALLBACK", callback)
        // FileProvider's intent URI grant is lifetime-scoped to a receiving
        // Activity stack. A BroadcastReceiver cannot qualify that contract.
        // The separate disposable Activity reads and returns only metadata.
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        context.startActivity(intent)
        assertTrue("Independent Activity did not return evidence", done.await(20, TimeUnit.SECONDS))
        val evidence = result.get() ?: throw AssertionError("Receiver Activity returned no bundle")
        assertTrue("Separate receiver Activity never processed the intent", evidence.getBoolean("receiver_ack"))
        return evidence
    }

    @Test fun externalAppCannotOpenUngrantedUriButReadsSameUriWithExplicitReadGrant() {
        val text = "AYA separate-UID FileProvider grant test: yellow, violet, and blue."
        val reviewedShare = AyaShareIntents.create(context, text, "Explain the test document")
        val uri = reviewedShare.getParcelableExtra<Uri>(Intent.EXTRA_STREAM)!!
        assertEquals("content", uri.scheme)

        // A share target knowing the URI string must not be able to read it
        // without a temporary permission grant. No ClipData or grant flags.
        val ungranted = Intent(Intent.ACTION_SEND).apply {
            type = "text/plain"
            putExtra(Intent.EXTRA_STREAM, uri)
        }
        val denied = sendToSeparateApp(ungranted)
        // Android may surface an ungranted provider lookup as either a
        // SecurityException ("denied") or an unreadable URI. The negative
        // alone proves nothing about the file's existence. Require the
        // granted *same URI* below to return the exact original bytes.
        val ungrantedStatus = denied.getString("status")
        assertTrue(
            "Foreign app unexpectedly read ungranted URI or supplied invalid status: $ungrantedStatus",
            ungrantedStatus == "denied" || ungrantedStatus == "unreadable"
        )
        assertTrue("Ungranted read must not include document digest", !denied.containsKey("sha256"))
        assertTrue("Ungranted read must not include document bytes", !denied.containsKey("bytes"))
        assertTrue("Receiver must have a different Android UID",
            denied.getInt("receiver_uid") != context.applicationInfo.uid)

        // Deliver the exact AYA-produced intent, including its ClipData grant.
        val accepted = sendToSeparateApp(reviewedShare)
        assertEquals("read", accepted.getString("status"))
        assertEquals(denied.getInt("receiver_uid"), accepted.getInt("receiver_uid"))
        assertEquals(text.toByteArray(Charsets.UTF_8).size, accepted.getInt("bytes"))
        val expectedHash = MessageDigest.getInstance("SHA-256")
            .digest(text.toByteArray(Charsets.UTF_8))
            .joinToString("") { "%02x".format(it.toInt() and 0xff) }
        assertEquals(expectedHash, accepted.getString("sha256"))
    }
}
