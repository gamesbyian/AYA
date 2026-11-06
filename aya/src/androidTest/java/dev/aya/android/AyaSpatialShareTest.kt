package dev.aya.android

import android.app.PendingIntent
import android.content.BroadcastReceiver
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.graphics.Bitmap
import android.net.Uri
import android.os.Build
import android.os.Bundle
import androidx.core.content.FileProvider
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import org.json.JSONArray
import org.json.JSONObject
import org.junit.Assert.*
import org.junit.Test
import org.junit.runner.RunWith
import java.io.File
import java.security.MessageDigest
import java.util.UUID
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicReference

/**
 * Android and separate-UID acceptance evidence for spatial ACTION_SEND_MULTIPLE.
 * A synthetic QA receiver proves attachment grant and bytes, not assistant ingestion.
 */
@RunWith(AndroidJUnit4::class)
class AyaSpatialShareTest {
    private val context get() = InstrumentationRegistry.getInstrumentation().targetContext

    private fun hash(bytes: ByteArray): String =
        MessageDigest.getInstance("SHA-256").digest(bytes)
            .joinToString("") { "%02x".format(it.toInt() and 0xff) }

    private fun fixture(): Pair<AyaSpatialShareTask, List<ByteArray>> {
        val files = mutableListOf<AyaSpatialImage>()
        val images = mutableListOf<ByteArray>()
        fun picture(path: String, color: Int): JSONObject {
            val bitmap = Bitmap.createBitmap(8, 8, Bitmap.Config.ARGB_8888)
            bitmap.eraseColor(color)
            val output = java.io.ByteArrayOutputStream()
            bitmap.compress(Bitmap.CompressFormat.PNG, 100, output)
            bitmap.recycle()
            val bytes = output.toByteArray()
            images.add(bytes)
            val file = File(context.cacheDir, "aya/spatial-test-${UUID.randomUUID()}.png")
            file.parentFile!!.mkdirs()
            file.writeBytes(bytes)
            val uri = FileProvider.getUriForFile(context, "${context.packageName}.aya.files", file)
            files.add(AyaSpatialImage(path, uri))
            return JSONObject().put("path", path).put("mime", "image/png")
                .put("sha256", hash(bytes)).put("bytes", bytes.size)
                .put("width", 8).put("height", 8)
        }
        val src = picture("source/room.png", 0xffff0000.toInt())
        val ref = picture("references/replacement.png", 0xff0000ff.toInt())
        val manifest = JSONObject().put("format", "aya-spatial-composition/v1")
            .put("source", src)
            .put("assets", JSONArray().put(JSONObject().put("id", "replacement")
                .put("name", "Fictional replacement").put("category", "fixture")
                .put("views", JSONArray().put(JSONObject()
                    .put("angle", "front").put("image", ref)))))
            .put("annotations", JSONArray().put(JSONObject().put("id", "B")
                .put("label", "Existing unit")
                .put("geometry", JSONObject().put("kind", "point")
                    .put("point", JSONObject().put("x", 0.4).put("y", 0.6)))))
            .put("operations", JSONArray().put(JSONObject().put("targetAnnotationId", "B")
                .put("kind", "replace").put("assetId", "replacement")))
            .put("constraints", JSONObject().put("preserveUnmarked", true)
                .put("engineeringVerified", false))
            .put("instructions", "Replace B with fictional replacement")
        return AyaSpatialShareTask(manifest.toString(), files) to images
    }

    @Test fun manifestsAndStagedFilesHaveExactReadOnlyStreams() {
        val (task, images) = fixture()
        val edited = JSONObject(task.manifestJson)
            .put("instructions", "Use the replacement; preserve the surrounding wall.").toString()
        val intent = AyaSpatialHandoff.prepare(context, task, edited)
        assertEquals(Intent.ACTION_SEND_MULTIPLE, intent.action)
        assertEquals("*/*", intent.type)
        assertEquals(0, intent.flags and Intent.FLAG_GRANT_WRITE_URI_PERMISSION)
        assertTrue(intent.flags and Intent.FLAG_GRANT_READ_URI_PERMISSION != 0)
        val streams = intent.getParcelableArrayListExtra<Uri>(Intent.EXTRA_STREAM)!!
        assertEquals(3, streams.size)
        assertEquals(3, intent.clipData!!.itemCount)
        assertTrue(streams[1].path!!.endsWith("/source/room.png"))
        assertTrue(streams[2].path!!.endsWith("/references/replacement.png"))
        assertTrue(intent.getStringExtra(Intent.EXTRA_TEXT)!!.contains("preserve the surrounding wall"))
        assertFalse(intent.getStringExtra(Intent.EXTRA_TEXT)!!.contains("Replace B with fictional replacement"))
        assertEquals(edited, context.contentResolver.openInputStream(streams[0])!!
            .bufferedReader().use { it.readText() })
        for (i in 1 until streams.size) {
            assertArrayEquals(images[i - 1], context.contentResolver.openInputStream(streams[i])!!.use { it.readBytes() })
        }
    }

    @Test fun tamperedImageRejectedAndNoSuccessfulShare() {
        val (task, _) = fixture()
        val changed = JSONObject(task.manifestJson)
        changed.getJSONObject("source").put("sha256", "0".repeat(64))
        try {
            AyaSpatialHandoff.prepare(context, task.copy(manifestJson = changed.toString()), changed.toString())
            fail("Tampered image must fail before a share intent is returned")
        } catch (expected: IllegalArgumentException) {
            assertTrue(expected.message!!.contains("changed"))
        }
    }

    @Test fun rejectsMissingImageAndUnapprovedFileScheme() {
        val (task, _) = fixture()
        assertTrue(runCatching { AyaSpatialManifest.validate(task.copy(images = task.images.take(1))) }.isFailure)
        val unapproved = task.copy(images = task.images.mapIndexed { i, a ->
            if (i == 0) a.copy(contentUri = Uri.parse("file:///private/room.png")) else a
        })
        assertTrue(runCatching { AyaSpatialManifest.validate(unapproved) }.isFailure)
    }

    @Test fun rejectsNestedPathTraversal() {
        val (task, _) = fixture()
        val changed = JSONObject(task.manifestJson)
        changed.getJSONObject("source").put("path", "source/folder/../room.png")
        assertTrue(runCatching {
            AyaSpatialManifest.validate(task.copy(manifestJson = changed.toString()))
        }.isFailure)
    }

    @Test fun rejectsHiddenFieldsAndDangerousChangeTargets() {
        val (task, _) = fixture()
        val extra = JSONObject(task.manifestJson).put("backgroundUpload", true)
        assertTrue(runCatching {
            AyaSpatialManifest.validate(task.copy(manifestJson = extra.toString()))
        }.isFailure)
        val protected = JSONObject(task.manifestJson)
        protected.getJSONObject("constraints")
            .put("protectedAnnotationIds", JSONArray().put("B"))
        assertTrue(runCatching {
            AyaSpatialManifest.validate(task.copy(manifestJson = protected.toString()))
        }.isFailure)
    }

    @Test fun foreignAppReadsAllManifestAndImagesUnderTemporaryGrant() {
        val (task, images) = fixture()
        val edited = JSONObject(task.manifestJson).put("instructions", "Changed by the user").toString()
        val outgoing = AyaSpatialHandoff.prepare(context, task, edited)
        val result = deliverToOtherApp(outgoing)
        assertTrue(result.getBoolean("receiver_ack"))
        assertNotEquals(context.applicationInfo.uid, result.getInt("receiver_uid"))
        assertEquals("read", result.getString("status"))
        assertTrue(result.getBoolean("received_grant_flag"))
        assertEquals(3, result.getInt("attachment_count"))
        val hashes = result.getStringArrayList("sha256_all")!!
        val counts = result.getIntegerArrayList("bytes_all")!!
        val expectedBytes = listOf(edited.toByteArray(Charsets.UTF_8)) + images
        for (i in expectedBytes.indices) {
            assertEquals(hash(expectedBytes[i]), hashes[i])
            assertEquals(expectedBytes[i].size, counts[i])
        }
        assertTrue(result.getString("received_text")!!.contains("Changed by the user"))
    }

    private fun deliverToOtherApp(intent: Intent): Bundle {
        val done = CountDownLatch(1)
        val result = AtomicReference<Bundle>()
        val action = "dev.aya.spatial.TEST_" + UUID.randomUUID()
        val receiver = object : BroadcastReceiver() {
            override fun onReceive(context: Context, reply: Intent) {
                result.set(reply.getBundleExtra("dev.aya.qa.receiver.EVIDENCE"))
                done.countDown()
            }
        }
        if (Build.VERSION.SDK_INT >= 33) {
            context.registerReceiver(receiver, IntentFilter(action), Context.RECEIVER_NOT_EXPORTED)
        } else {
            context.registerReceiver(receiver, IntentFilter(action))
        }
        val callback = PendingIntent.getBroadcast(context, 0, Intent(action).setPackage(context.packageName),
            PendingIntent.FLAG_ONE_SHOT or PendingIntent.FLAG_MUTABLE)
        try {
            intent.component = ComponentName("dev.aya.qa.receiver", "dev.aya.qa.receiver.ReceiverActivity")
            intent.putExtra("dev.aya.qa.receiver.RESULT_CALLBACK", callback)
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            context.startActivity(intent)
            assertTrue("No distinct-UID receiver reply", done.await(20, TimeUnit.SECONDS))
            return result.get() ?: throw AssertionError("Missing receiver evidence")
        } finally {
            callback.cancel()
            context.unregisterReceiver(receiver)
        }
    }
}
