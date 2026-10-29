package dev.aya.sample

import android.app.Activity
import android.content.Intent
import android.graphics.BitmapFactory
import android.net.Uri
import android.os.Bundle
import android.text.InputType
import android.view.ViewGroup
import android.widget.Button
import android.widget.EditText
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import android.widget.Toast
import dev.aya.android.Aya
import dev.aya.android.AyaBundledLaunchResult
import dev.aya.android.AyaCreativeTask
import dev.aya.android.AyaImageRequirements

/** Self-contained artwork selector example; returning from an assistant is manual. */
class ArtworkActivity : Activity() {
    private lateinit var artworkPreview: ImageView
    private var artworkUri: Uri? = null

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        artworkUri?.let { outState.putString("artwork_uri", it.toString()) }
    }

    @Deprecated("Compatibility with API 23 sample")
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == 42 && resultCode == RESULT_OK) {
            val uri = data?.data ?: return
            val type = contentResolver.getType(uri)
            if (type !in setOf("image/png", "image/jpeg") || !showImportedArtwork(uri)) {
                Toast.makeText(this, "Choose a valid PNG or JPEG image.", Toast.LENGTH_LONG).show()
                return
            }
            try {
                contentResolver.takePersistableUriPermission(
                    uri, Intent.FLAG_GRANT_READ_URI_PERMISSION
                )
            } catch (_: SecurityException) {
                // The picker may grant only transient access.
            }
            artworkUri = uri
            Toast.makeText(this, "Image selected for this demo", Toast.LENGTH_SHORT).show()
        }
    }

    private fun showImportedArtwork(uri: Uri): Boolean {
        return try {
            val bounds = BitmapFactory.Options().apply { inJustDecodeBounds = true }
            val metadataStream = contentResolver.openInputStream(uri) ?: return false
            metadataStream.use { BitmapFactory.decodeStream(it, null, bounds) }
            if (bounds.outWidth <= 0 || bounds.outHeight <= 0) return false
            var sampleSize = 1
            while (bounds.outWidth / sampleSize > 1024 ||
                bounds.outHeight / sampleSize > 1024) sampleSize *= 2
            val options = BitmapFactory.Options().apply { inSampleSize = sampleSize }
            val bitmap = contentResolver.openInputStream(uri)?.use {
                BitmapFactory.decodeStream(it, null, options)
            } ?: return false
            artworkPreview.setImageBitmap(bitmap)
            true
        } catch (_: Exception) {
            false
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val padding = (20 * resources.displayMetrics.density).toInt()
        val column = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(padding, padding, padding, padding)
        }
        column.addView(Button(this).apply {
            text = "Back to AYA sample"
            contentDescription = "Return to sample home screen"
            setOnClickListener { finish() }
        })
        column.addView(TextView(this).apply {
            text = "Artwork generation demo"
            textSize = 22f
        })
        column.addView(TextView(this).apply {
            text = "Imagine an artwork picker whose recommended covers aren't right. " +
                "Describe an image, hand it to your own AI app, save the result, " +
                "then come back and import it here. This demo doesn't modify a media library."
        })
        val creativeDirection = EditText(this).apply {
            id = R.id.aya_sample_artwork_direction
            hint = "Describe square cover artwork"
            contentDescription = "Describe artwork in the sample host"
            setText("Atmospheric science-fiction season art with a luminous space station and no text.")
            minLines = 3
            inputType = InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_FLAG_MULTI_LINE
        }
        column.addView(creativeDirection, LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT
        ))
        column.addView(Button(this).apply {
            text = "Generate artwork with my agent"
            contentDescription = "Review the creative image request before sharing"
            setOnClickListener {
                val result = Aya.launchCreativeBundled(
                    activity = this@MainActivity,
                    task = AyaCreativeTask(
                        subject = "Aurora Station (fictional series), Season 4",
                        assetRole = "Square season key art",
                        image = AyaImageRequirements(
                            aspectWidth = 1,
                            aspectHeight = 1,
                            preferredWidthPx = 2000,
                            preferredHeightPx = 2000,
                            acceptedMimeTypes = listOf("image/png", "image/jpeg"),
                            transparentBackground = false,
                            safeMarginPercent = 8
                        ),
                        importInstructions = "Return to this AYA Sample screen, " +
                            "tap Import saved image, then choose the downloaded artwork."
                    ),
                    screenName = "Artwork generation demo",
                    direction = creativeDirection.text.toString(),
                    askDirection = false
                )
                if (result is AyaBundledLaunchResult.Rejected) {
                    Toast.makeText(
                        this@MainActivity, "AYA reference unavailable: ${result.reason}",
                        Toast.LENGTH_LONG
                    ).show()
                }
            }
        })
        column.addView(Button(this).apply {
            text = "Import saved image"
            contentDescription = "Select a generated image from device storage"
            setOnClickListener {
                startActivityForResult(Intent(Intent.ACTION_OPEN_DOCUMENT).apply {
                    addCategory(Intent.CATEGORY_OPENABLE)
                    type = "image/*"
                    putExtra(Intent.EXTRA_MIME_TYPES, arrayOf("image/png", "image/jpeg"))
                    addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION or
                        Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION)
                }, 42)
            }
        })
        artworkPreview = ImageView(this).apply {
            contentDescription = "Imported artwork preview for this demo"
            adjustViewBounds = true
            maxHeight = (320 * resources.displayMetrics.density).toInt()
        }
        column.addView(artworkPreview, LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT
        ))
        savedInstanceState?.getString("artwork_uri")?.let {
            artworkUri = Uri.parse(it)
            artworkUri?.let { if (!showImportedArtwork(it)) artworkUri = null }
        }

        setContentView(ScrollView(this).apply {
            isFillViewport = true
            addView(column)
        })
    }
}
