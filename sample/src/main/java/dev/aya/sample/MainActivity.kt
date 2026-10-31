package dev.aya.sample

import android.app.Activity
import android.content.Intent
import android.os.Bundle
import android.view.ViewGroup
import android.view.WindowManager
import android.widget.Button
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import dev.aya.android.AyaCardView

/** First-party consumer of the version-guarded AYA library. No user data is read. */
class MainActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val padding = (20 * resources.displayMetrics.density).toInt()
        val column = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(padding, padding, padding, padding)
        }
        column.addView(TextView(this).apply {
            text = "AYA: Ask Your Agent"
            textSize = 26f
        })
        column.addView(TextView(this).apply {
            text = "This real sample app exercises AYA's help handoff. " +
                "Its bundled reference describes this demo, not a fictional product. " +
                "Review all text before sharing with another application."
            textSize = 16f
        }, LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT
        ))
        column.addView(AyaCardView(
            context = this,
            activity = this,
            guideAsset = "aya-guide.md",
            screenName = "Home",
            title = "Ask Your Agent",
            description = "Ask about using this sample app or the AYA handoff. " +
                "You can review the complete reference before sharing.",
            attachmentDisclosure = "A reference for this sample app is offered as a text file. " +
                "Your selected AI app may not accept attachments.",
            cornerRadiusDp = 12f
        ).apply {
            id = R.id.aya_sample_open_help
            questionInput.id = R.id.aya_sample_help_question
        }, LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT,
            ViewGroup.LayoutParams.WRAP_CONTENT
        ))
        column.addView(Button(this).apply {
            id = R.id.aya_sample_open_artwork
            text = "Open artwork generation demo"
            contentDescription = "Open artwork generation demo"
            setOnClickListener { startActivity(Intent(this@MainActivity, ArtworkActivity::class.java)) }
        })
        // The host scrolls when large fonts or the keyboard exceed the viewport;
        // the AYA card itself does not introduce a nested scroll container.
        window.setSoftInputMode(
            WindowManager.LayoutParams.SOFT_INPUT_STATE_ALWAYS_HIDDEN or
                WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE
        )
        setContentView(ScrollView(this).apply {
            isFillViewport = true
            isFocusableInTouchMode = true
            addView(column)
            // Prevent a newly-created card EditText from summoning the IME on entry.
            requestFocus()
        })
    }
}
