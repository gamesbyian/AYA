package dev.aya.android

import android.app.Activity
import android.app.AlertDialog
import android.content.ClipData
import android.content.Context
import android.content.Intent
import android.graphics.BitmapFactory
import android.net.Uri
import android.os.Handler
import android.os.Looper
import android.text.InputType
import android.view.ViewGroup
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import androidx.core.content.FileProvider
import org.json.JSONArray
import org.json.JSONObject
import java.io.File
import java.io.FileOutputStream
import java.security.MessageDigest
import java.util.UUID

/**
 * Host-neutral, source-preview transport for aya-spatial-composition/v1.
 * The adopting host owns canvas edits, source/photo authorization and returned-image import.
 * No assistant receives anything before the person reviews and confirms the precise inventory.
 */
data class AyaSpatialImage(
    val path: String,
    val contentUri: Uri
)

data class AyaSpatialShareTask(
    val manifestJson: String,
    val images: List<AyaSpatialImage>
)

/** A local share chooser launch is not evidence that an assistant ingested attachments. */
object AyaSpatialHandoff {
    private const val MAX_IMAGES = 24
    private const val MAX_IMAGE_BYTES = 20L * 1024 * 1024
    private const val MAX_TOTAL_BYTES = 100L * 1024 * 1024
    private const val MAX_MANIFEST_BYTES = 2 * 1024 * 1024
    private const val RETENTION_MS = 7L * 24 * 60 * 60 * 1000

    /**
     * Called on the UI thread. An explicit second button press in the review authorizes copying
     * and a Sharesheet. No app selection, recipient success or later import is observed.
     *
     * The host must give us source/reference content URIs it has permission to read and
     * must preserve the draft itself across Activity recreation. No raw filesystem paths.
     */
    fun launch(activity: Activity, task: AyaSpatialShareTask) {
        val spec = try {
            AyaSpatialManifest.validate(task)
        } catch (e: Exception) {
            AlertDialog.Builder(activity).setTitle("Cannot prepare composition")
                .setMessage(e.message ?: "Invalid composition packet").setPositiveButton("OK", null)
                .show()
            return
        }
        val root = LinearLayout(activity).apply {
            orientation = LinearLayout.VERTICAL
            val pad = (16 * resources.displayMetrics.density).toInt()
            setPadding(pad, pad, pad, pad)
        }
        root.addView(TextView(activity).apply {
            text = "Review every attachment and the instructions before choosing an external app. " +
                "The selected app may upload site photographs and product references to its own service. " +
                "It may ignore some files or the manifest. A visualization is not an engineered design."
            textSize = 15f
        })
        root.addView(TextView(activity).apply {
            text = "Files to share (${spec.images.size} photographs + manifest):\n" +
                spec.images.joinToString("\n") { "• ${it.path} (${it.bytes} bytes, SHA-256 ${it.sha256.take(12)}…)" } +
                "\n\nRequested edits:\n" + spec.operations.joinToString("\n") { "• $it" }
            textSize = 13f
            contentDescription = text
        })
        val direction = EditText(activity).apply {
            setText(spec.instructions)
            minLines = 3
            maxLines = 8
            inputType = InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_FLAG_MULTI_LINE
            contentDescription = "Edit the exact composition instructions before sharing"
        }
        root.addView(direction, LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT
        ))
        root.addView(Button(activity).apply {
            text = "Inspect complete manifest"
            contentDescription = "Inspect all structured data before sharing"
            setOnClickListener {
                val current = JSONObject(task.manifestJson)
                    .put("instructions", direction.text.toString()).toString(2)
                val detailView = TextView(activity).apply {
                    text = current
                    setTextIsSelectable(true)
                    setPadding(24, 16, 24, 16)
                }
                AlertDialog.Builder(activity).setTitle("Complete outgoing manifest")
                    .setMessage("This entire JSON document will accompany the photographs.")
                    .setView(ScrollView(activity).apply { addView(detailView) })
                    .setPositiveButton("Back to review", null).show()
            }
        })
        val scroll = ScrollView(activity).apply { addView(root) }
        val dialog = AlertDialog.Builder(activity).setTitle("Review visual composition")
            .setView(scroll)
            .setNegativeButton("Cancel", null)
            .setPositiveButton("Share files", null)
            .create()
        dialog.setOnShowListener {
            dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener {
                val edited = direction.text.toString()
                if (edited.isBlank() || edited.length > 12000) {
                    direction.error = "Use 1 to 12000 characters"
                    return@setOnClickListener
                }
                // Preserve user edits, and don't resurface an earlier hidden instruction.
                val reviewed = JSONObject(task.manifestJson).put("instructions", edited).toString()
                dialog.dismiss()
                Thread {
                    val attempt = runCatching { prepare(activity.applicationContext, task, reviewed) }
                    Handler(Looper.getMainLooper()).post {
                        if (activity.isFinishing || activity.isDestroyed) return@post
                        attempt.onSuccess { share ->
                            try {
                                activity.startActivity(Intent.createChooser(share, "Send composition to your agent"))
                            } catch (error: Exception) {
                                AlertDialog.Builder(activity).setTitle("No compatible share target")
                                    .setMessage(error.message ?: "Android could not open the share chooser")
                                    .setPositiveButton("OK", null).show()
                            }
                        }.onFailure { error ->
                            AlertDialog.Builder(activity).setTitle("Composition not shared")
                                .setMessage(error.message ?: "Unable to prepare approved attachments")
                                .setPositiveButton("OK", null).show()
                        }
                    }
                }.start()
            }
        }
        dialog.show()
    }

    /** Explicitly reviewed material only. Primarily useful for host/device acceptance tests. */
    internal fun prepare(context: Context, task: AyaSpatialShareTask, reviewedManifest: String): Intent {
        val spec = AyaSpatialManifest.validate(task.copy(manifestJson = reviewedManifest))
        val folder = File(context.cacheDir, "aya/spatial/${UUID.randomUUID()}").apply {
            check(mkdirs()) { "Cannot create share staging directory" }
        }
        try {
            val streams = ArrayList<Uri>(spec.images.size + 1)
            val manifestFile = File(folder, "aya-spatial-manifest.json")
            val manifestBytes = reviewedManifest.toByteArray(Charsets.UTF_8)
            require(manifestBytes.size <= MAX_MANIFEST_BYTES) { "Manifest exceeds 2 MiB" }
            manifestFile.writeBytes(manifestBytes)
            streams.add(fileUri(context, manifestFile))
            for ((index, expected) in spec.images.withIndex()) {
                val original = task.images.single { it.path == expected.path }.contentUri
                val extension = expected.path.substringAfterLast('.')
                val staged = File(folder, "image-${index.toString().padStart(2, '0')}.$extension")
                val actual = MessageDigest.getInstance("SHA-256")
                var count = 0L
                val signature = ByteArray(16)
                var signatureSize = 0
                context.contentResolver.openInputStream(original)?.use { input ->
                    FileOutputStream(staged).use { output ->
                        val buffer = ByteArray(8192)
                        while (true) {
                            val n = input.read(buffer)
                            if (n < 0) break
                            if (n == 0) continue
                            if (count + n > MAX_IMAGE_BYTES || count + n > expected.bytes) {
                                throw IllegalArgumentException("Attachment changed or exceeds size: ${expected.path}")
                            }
                            if (signatureSize < signature.size) {
                                val take = minOf(n, signature.size - signatureSize)
                                buffer.copyInto(signature, signatureSize, 0, take)
                                signatureSize += take
                            }
                            output.write(buffer, 0, n)
                            actual.update(buffer, 0, n)
                            count += n
                        }
                    }
                } ?: throw IllegalArgumentException("Cannot read selected image ${expected.path}")
                val digest = actual.digest().joinToString("") { "%02x".format(it.toInt() and 0xff) }
                require(count == expected.bytes && digest == expected.sha256) {
                    "Attachment changed since review: ${expected.path}"
                }
                require(AyaSpatialManifest.matchesMagic(expected.mime, signature, signatureSize)) {
                    "Image signature does not match declared type: ${expected.path}"
                }
                val opts = BitmapFactory.Options().apply { inJustDecodeBounds = true }
                BitmapFactory.decodeFile(staged.absolutePath, opts)
                require(opts.outWidth == expected.width && opts.outHeight == expected.height) {
                    "Image dimensions do not match manifest: ${expected.path}"
                }
                streams.add(fileUri(context, staged))
            }
            val clips = ClipData.newRawUri("AYA spatial composition manifest", streams[0])
            streams.drop(1).forEach { clips.addItem(ClipData.Item(it)) }
            val shortMessage = buildString {
                appendLine("Generate a conceptual edited image from the attached original and reference images.")
                appendLine("The attached JSON manifest contains the reviewed edits and normalized location markers.")
                appendLine("Preserve unmarked areas and perspective; do not infer engineering compliance.")
                appendLine("Reviewed direction: ${spec.instructions}")
            }
            // The full instructions are ALWAYS in the attached manifest. A short summary must
            // not silently drop part of a complex edit: refer to the full manifest instead.
            val text = if (shortMessage.length <= 4000) shortMessage else
                "Generate a conceptual edit using ALL attached references and the complete reviewed " +
                    "JSON manifest. Preserve unmarked areas and perspective. This is not engineering verification."
            return Intent(Intent.ACTION_SEND_MULTIPLE).apply {
                type = "*/*"
                putParcelableArrayListExtra(Intent.EXTRA_STREAM, streams)
                putExtra(Intent.EXTRA_TEXT, text)
                putExtra(Intent.EXTRA_SUBJECT, "AYA spatial composition")
                clipData = clips
                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            }
        } catch (e: Exception) {
            folder.deleteRecursively()
            throw e
        } finally {
            // Old successful packets are retained for recipients that read after the chooser closes.
            File(context.cacheDir, "aya/spatial").listFiles()?.filter {
                it.isDirectory && it != folder && System.currentTimeMillis() - it.lastModified() > RETENTION_MS
            }?.forEach { it.deleteRecursively() }
        }
    }

    private fun fileUri(context: Context, file: File): Uri =
        FileProvider.getUriForFile(context, "${context.packageName}.aya.files", file)
}

/** Semantic checks supplement the published JSON Schema; never assume JSON alone verifies image bytes. */
internal object AyaSpatialManifest {
    data class Image(val path: String, val mime: String, val sha256: String, val bytes: Long,
                     val width: Int, val height: Int)
    data class Spec(val images: List<Image>, val operations: List<String>, val instructions: String)
    private val validPath = Regex("^(source|references|overlays)/[A-Za-z0-9_-]+(?:/[A-Za-z0-9_.-]+)*\\.(jpg|jpeg|png|webp)$")
    private val digest = Regex("^[a-f0-9]{64}$")
    private val ident = Regex("^[A-Za-z][A-Za-z0-9_-]{0,63}$")

    private fun keys(node: JSONObject, allowed: Set<String>) {
        val names = node.keys()
        while (names.hasNext()) {
            val name = names.next()
            require(name in allowed) { "Unexpected unreviewed manifest field: $name" }
        }
    }

    fun validate(task: AyaSpatialShareTask): Spec {
        require(task.manifestJson.toByteArray(Charsets.UTF_8).size <= 2 * 1024 * 1024)
        val root = try { JSONObject(task.manifestJson) } catch (_: Exception) {
            throw IllegalArgumentException("Invalid manifest JSON")
        }
        require(root.optString("format") == "aya-spatial-composition/v1") { "Unsupported packet version" }
        keys(root, setOf("format", "source", "overlay", "assets", "annotations", "operations", "constraints", "instructions"))
        val images = mutableListOf<Image>()
        fun readImage(node: JSONObject, prefix: String) {
            keys(node, setOf("path", "mime", "sha256", "bytes", "width", "height"))
            val path = node.optString("path")
            val mime = node.optString("mime")
            val bytes = node.optLong("bytes", -1)
            val width = node.optInt("width", -1)
            val height = node.optInt("height", -1)
            val hash = node.optString("sha256")
            require(validPath.matches(path) && path.startsWith("$prefix/")) { "Invalid attachment path: $path" }
            val ext = path.substringAfterLast('.')
            require((mime == "image/jpeg" && ext in setOf("jpg", "jpeg")) ||
                (mime == "image/png" && ext == "png") || (mime == "image/webp" && ext == "webp")) {
                "Incorrect image extension or MIME for $path"
            }
            require(digest.matches(hash) && bytes in 1..(20L * 1024 * 1024) &&
                width in 1..32768 && height in 1..32768) { "Invalid image metadata: $path" }
            require(images.none { it.path == path }) { "Repeated attachment path: $path" }
            images.add(Image(path, mime, hash, bytes, width, height))
        }
        readImage(root.getJSONObject("source"), "source")
        root.optJSONObject("overlay")?.let {
            readImage(it, "overlays")
            require(it.optInt("width") == images[0].width && it.optInt("height") == images[0].height) {
                "Overlay does not match source dimensions"
            }
        }
        val assetIds = mutableSetOf<String>()
        val assetNames = mutableMapOf<String, String>()
        val assets = root.getJSONArray("assets")
        require(assets.length() <= 100)
        for (i in 0 until assets.length()) {
            val asset = assets.getJSONObject(i)
            keys(asset, setOf("id", "name", "category", "dimensionsMm", "views"))
            val id = asset.getString("id")
            require(ident.matches(id) && assetIds.add(id)) { "Invalid or repeated asset ID" }
            require(asset.optString("name").isNotBlank() && asset.optString("category").isNotBlank())
            assetNames[id] = asset.getString("name")
            asset.optJSONObject("dimensionsMm")?.let { dim ->
                keys(dim, setOf("width", "height", "depth"))
                for (axis in listOf("width", "height", "depth")) {
                    require(dim.getDouble(axis).isFinite() && dim.getDouble(axis) > 0) {
                        "Invalid asset dimension"
                    }
                }
            }
            val views = asset.getJSONArray("views")
            require(views.length() in 1..12)
            for (j in 0 until views.length()) {
                val view = views.getJSONObject(j)
                keys(view, setOf("angle", "image"))
                require(view.optString("angle") in setOf("front","rear","left","right","three-quarter","detail","other"))
                readImage(view.getJSONObject("image"), "references")
            }
        }
        require(images.size in 1..MAX_IMAGES && images.sumOf { it.bytes } <= MAX_TOTAL_BYTES) {
            "Too many or too large attachments"
        }
        val names = task.images.map { it.path }
        require(names.size == names.toSet().size && names.toSet() == images.map { it.path }.toSet()) {
            "Selected attachments must exactly match the manifest"
        }
        require(task.images.all { it.contentUri.scheme == "content" && it.contentUri.authority != null }) {
            "Only explicitly supplied content URIs are allowed"
        }
        val ann = root.getJSONArray("annotations")
        require(ann.length() in 1..200)
        val ids = mutableSetOf<String>()
        val labels = mutableSetOf<String>()
        val labelNames = mutableMapOf<String, String>()
        fun coord(v: Double) = require(v.isFinite() && v in 0.0..1.0) { "Invalid normalized coordinate" }
        for (i in 0 until ann.length()) {
            val a = ann.getJSONObject(i)
            keys(a, setOf("id", "label", "geometry"))
            require(ident.matches(a.getString("id")) && ids.add(a.getString("id")))
            val label = a.getString("label").trim().lowercase()
            require(label.isNotEmpty() && labels.add(label))
            labelNames[a.getString("id")] = a.getString("label")
            val geo = a.getJSONObject("geometry")
            when (geo.getString("kind")) {
                "point" -> {
                    keys(geo, setOf("kind", "point"))
                    val p = geo.getJSONObject("point")
                    keys(p, setOf("x", "y"))
                    coord(p.getDouble("x")); coord(p.getDouble("y"))
                }
                "rect" -> {
                    keys(geo, setOf("kind", "x", "y", "width", "height"))
                    val x=geo.getDouble("x"); val y=geo.getDouble("y")
                    val w=geo.getDouble("width"); val h=geo.getDouble("height")
                    coord(x); coord(y); coord(w); coord(h)
                    require(w > 0 && h > 0 && x + w <= 1 && y + h <= 1)
                }
                "polygon" -> {
                    keys(geo, setOf("kind", "vertices"))
                    val vv = geo.getJSONArray("vertices")
                    require(vv.length() in 3..500)
                    var area = 0.0
                    for (j in 0 until vv.length()) {
                        val p=vv.getJSONObject(j); val q=vv.getJSONObject((j+1)%vv.length())
                        keys(p, setOf("x", "y"))
                        val x=p.getDouble("x"); val y=p.getDouble("y")
                        coord(x); coord(y)
                        area += x*q.getDouble("y")-q.getDouble("x")*y
                    }
                    require(kotlin.math.abs(area) > 1e-8) { "Degenerate polygon" }
                }
                else -> throw IllegalArgumentException("Unknown geometry")
            }
        }
        val constraints = root.getJSONObject("constraints")
        keys(constraints, setOf("preserveUnmarked", "engineeringVerified", "protectedAnnotationIds"))
        require(constraints.opt("preserveUnmarked") == true && constraints.opt("engineeringVerified") == false) {
            "Preservation and conceptual-only constraints are required"
        }
        val protected = mutableSetOf<String>()
        val p = constraints.optJSONArray("protectedAnnotationIds") ?: JSONArray()
        for (i in 0 until p.length()) {
            val id = p.getString(i)
            require(id in ids && protected.add(id)) { "Invalid protected region" }
        }
        val ops = root.getJSONArray("operations")
        require(ops.length() in 1..200)
        val touched = mutableSetOf<String>()
        val operations = mutableListOf<String>()
        for (i in 0 until ops.length()) {
            val op = ops.getJSONObject(i)
            keys(op, setOf("targetAnnotationId", "kind", "assetId", "detail"))
            val id = op.getString("targetAnnotationId")
            require(id in ids && id !in protected && touched.add(id)) { "Invalid or conflicting operation target" }
            val kind = op.getString("kind")
            require(kind in setOf("add", "replace", "remove", "clean", "modify"))
            val asset = op.optString("assetId")
            require((kind !in setOf("add","replace") || asset.isNotBlank()) &&
                (asset.isBlank() || asset in assetIds)) { "Invalid operation asset" }
            operations.add("$id (${labelNames[id]}): $kind${if (asset.isNotBlank()) " (${assetNames[asset]})" else ""}" +
                op.optString("detail").takeIf { it.isNotBlank() }?.let { " — $it" }.orEmpty())
        }
        val instructions = root.getString("instructions")
        require(instructions.isNotBlank() && instructions.length <= 12000) { "Invalid instructions" }
        return Spec(images, operations, instructions)
    }

    fun matchesMagic(mime: String, data: ByteArray, length: Int): Boolean = when (mime) {
        "image/jpeg" -> length >= 3 && data[0] == 0xff.toByte() && data[1] == 0xd8.toByte() &&
            data[2] == 0xff.toByte()
        "image/png" -> length >= 8 && byteArrayOf(137.toByte(),80,78,71,13,10,26,10)
            .indices.all { data[it] == byteArrayOf(137.toByte(),80,78,71,13,10,26,10)[it] }
        "image/webp" -> length >= 12 && String(data, 0, 4, Charsets.US_ASCII) == "RIFF" &&
            String(data, 8, 4, Charsets.US_ASCII) == "WEBP"
        else -> false
    }

    private const val MAX_IMAGES = 24
    private const val MAX_TOTAL_BYTES = 100L * 1024 * 1024
}
