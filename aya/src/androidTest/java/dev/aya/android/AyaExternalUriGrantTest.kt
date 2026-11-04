package dev.aya.android

import android.content.ComponentName
import android.app.PendingIntent
import android.content.BroadcastReceiver
import android.content.IntentFilter
import android.os.Build
import java.util.UUID
import android.util.Log
import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Bundle
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
        val callbackAction = "dev.aya.android.AYA_URI_QA_" + UUID.randomUUID().toString()
        val evidenceReceiver = object : BroadcastReceiver() {
            override fun onReceive(context: Context, reply: Intent) {
                result.set(reply.getBundleExtra("dev.aya.qa.receiver.EVIDENCE"))
                done.countDown()
            }
        }
        // Only the test app receives a unique, same-package PendingIntent
        // callback. Its parcel is a framework type, so a foreign APK needs
        // no private instrumentation classes to deserialize it.
        val filter = IntentFilter(callbackAction)
        if (Build.VERSION.SDK_INT >= 33) {
            context.registerReceiver(evidenceReceiver, filter, Context.RECEIVER_NOT_EXPORTED)
        } else {
            context.registerReceiver(evidenceReceiver, filter)
        }
        val callback = PendingIntent.getBroadcast(
            context,
            0,
            Intent(callbackAction).setPackage(context.packageName),
            PendingIntent.FLAG_ONE_SHOT or PendingIntent.FLAG_MUTABLE
        )
        try {
            intent.component = ComponentName(
                "dev.aya.qa.receiver", "dev.aya.qa.receiver.ReceiverActivity"
            )
            intent.putExtra("dev.aya.qa.receiver.RESULT_CALLBACK", callback)
            // The system scopes FileProvider grants to the foreign Activity
            // stack; do not downgrade to a broad manual grant.
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            Log.i("AYA_URI_QA", "test dispatch foreign Activity with grant=" +
                (intent.flags and Intent.FLAG_GRANT_READ_URI_PERMISSION != 0))
            context.startActivity(intent)
            assertTrue("Independent Activity did not return evidence", done.await(20, TimeUnit.SECONDS))
            val evidence = result.get() ?: throw AssertionError("Foreign Activity returned no evidence bundle")
            assertTrue("Foreign Activity never acknowledged URI inspection", evidence.getBoolean("receiver_ack"))
            return evidence
        } finally {
            callback.cancel()
            context.unregisterReceiver(evidenceReceiver)
        }
    }

    @Test fun externalAppCannotOpenUngrantedUriButReadsSameUriWithExplicitReadGrant() {
        val text = "AYA separate-UID FileProvider grant test: yellow, violet, and blue."
        val reviewedShare = AyaShareIntents.create(context, text, "Explain the test document")
        val uri = reviewedShare.getParcelableExtra<Uri>(Intent.EXTRA_STREAM)!!
        assertEquals("content", uri.scheme)

        // A share target knowing the URI string must not be able to read it
        // without a temporary permission grant. No ClipData or grant flags.
        // ACTION_SEND is special: when an Activity is started Android can
        // migrate EXTRA_STREAM to ClipData and add a temporary URI grant
        // automatically. A neutral, explicitly targeted QA action avoids
        // accidentally granting the very permission this negative control
        // is meant to withhold. The positive control below still dispatches
        // the original genuine AYA ACTION_SEND and checks identical bytes.
        val ungranted = Intent("dev.aya.qa.receiver.TEST_UNGRANTED").apply {
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
