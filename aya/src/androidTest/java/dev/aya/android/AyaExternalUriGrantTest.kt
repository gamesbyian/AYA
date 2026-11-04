package dev.aya.android

import android.content.ComponentName
import android.content.BroadcastReceiver
import android.app.Activity
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
        // The system invokes this local final ordered-broadcast receiver even
        // when the external receiver is missing. This makes absent delivery an
        // explicit failed assertion instead of a missing Parcelable callback.
        val finalReceiver = object : BroadcastReceiver() {
            override fun onReceive(context: Context, intent: Intent) {
                result.set(getResultExtras(false))
                done.countDown()
            }
        }
        intent.component = ComponentName(
            "dev.aya.qa.receiver", "dev.aya.qa.receiver.ReceiverActivity"
        )
        // A fresh CI APK may still be in Android's stopped-package state.
        // Ordered delivery returns evidence without a Parcelable callback
        // crossing the test and foreign-app process boundary.
        intent.addFlags(Intent.FLAG_INCLUDE_STOPPED_PACKAGES)
        context.sendOrderedBroadcast(
            intent, null, finalReceiver, Handler(Looper.getMainLooper()),
            Activity.RESULT_OK, null, Bundle()
        )
        assertTrue("Ordered broadcast did not complete", done.await(20, TimeUnit.SECONDS))
        val evidence = result.get() ?: throw AssertionError("Ordered broadcast returned no bundle")
        assertTrue("Foreign receiver never handled the broadcast", evidence.getBoolean("receiver_ack"))
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
        assertEquals("Without an Android grant, cross-UID reads must be denied",
            "denied", denied.getString("status"))
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
