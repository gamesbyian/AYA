package dev.aya.android

import android.content.Context
import android.content.Intent
import android.net.Uri
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith
import java.io.File

/** Device/emulator contract tests, independent of third-party AI clients. */
@RunWith(AndroidJUnit4::class)
class AyaShareIntentsTest {
    private val context: Context
        get() = InstrumentationRegistry.getInstrumentation().targetContext

    @Test fun sharedFileIsUtf8AndGrantedReadOnly() {
        val payload = "AYA hello ✓\nHello 🌈"
        val intent = AyaShareIntents.create(context, payload)
        assertEquals(Intent.ACTION_SEND, intent.action)
        assertEquals("text/plain", intent.type)
        assertTrue((intent.flags and Intent.FLAG_GRANT_READ_URI_PERMISSION) != 0)
        assertTrue((intent.flags and Intent.FLAG_GRANT_WRITE_URI_PERMISSION) == 0)
        val uri = intent.getParcelableExtra<Uri>(Intent.EXTRA_STREAM)!!
        assertEquals("content", uri.scheme)
        assertEquals("${context.packageName}.aya.files", uri.authority)
        assertEquals(uri, intent.clipData!!.getItemAt(0).uri)
        val actual = context.contentResolver.openInputStream(uri)!!.bufferedReader(Charsets.UTF_8).use { it.readText() }
        assertEquals(payload, actual)
    }

    @Test fun repeatedSharesDoNotOverwriteFiles() {
        val first = AyaShareIntents.create(context, "first")
        val second = AyaShareIntents.create(context, "second")
        val a = first.getParcelableExtra<Uri>(Intent.EXTRA_STREAM)!!
        val b = second.getParcelableExtra<Uri>(Intent.EXTRA_STREAM)!!
        assertNotEquals(a, b)
        assertEquals("first", context.contentResolver.openInputStream(a)!!.bufferedReader().use { it.readText() })
    }

    @Test fun providerCannotExposeUnrelatedCacheFile() {
        val outside = File(context.cacheDir, "aya-secret-probe.txt")
        outside.writeText("out of scope")
        try {
            var denied = false
            try {
                androidx.core.content.FileProvider.getUriForFile(
                    context, "${context.packageName}.aya.files", outside
                )
            } catch (_: IllegalArgumentException) {
                denied = true
            }
            assertTrue("Provider must not expose unrelated cache path", denied)
        } finally {
            outside.delete()
        }
    }

    @Test fun refusesBlankOrOversizedPayload() {
        var blankDenied = false
        try { AyaShareIntents.create(context, " ") } catch (_: IllegalArgumentException) { blankDenied = true }
        assertTrue(blankDenied)
        var sizeDenied = false
        try { AyaShareIntents.create(context, "a".repeat(2 * 1024 * 1024 + 1)) }
        catch (_: IllegalArgumentException) { sizeDenied = true }
        assertTrue(sizeDenied)
    }
}
