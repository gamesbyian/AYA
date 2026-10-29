package dev.aya.sample

import android.app.Activity
import android.content.Intent
import android.os.Bundle
import android.view.ViewGroup
import android.widget.Button
import android.widget.EditText
import android.text.InputType
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast
import dev.aya.android.Aya
import dev.aya.android.AyaBundledLaunchResult

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
        column.addView(Button(this).apply {
            text = "Ask your agent"
            contentDescription = "Open AYA help with a version-matched reference"
            setOnClickListener {
                val result = Aya.launchBundled(
                    activity = this@MainActivity,
                    guideAsset = "aya-guide.md",
                    screenName = "Home",
                    question = null // user writes their own question in AYA's composer
                )
                if (result is AyaBundledLaunchResult.Rejected) {
                    Toast.makeText(
                        this@MainActivity, "AYA reference unavailable: ${result.reason}",
                        Toast.LENGTH_LONG
                    ).show()
                }
            }
        })
        val hostQuestion = EditText(this).apply {
            id = R.id.aya_sample_help_question
            hint = "Or type your question here"
            contentDescription = "Type a question in the host app"
            minLines = 2
            inputType = InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_FLAG_MULTI_LINE
        }
        column.addView(hostQuestion, LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT
        ))
        column.addView(Button(this).apply {
            text = "Ask using my question"
            contentDescription = "Review my question with the app reference before sharing"
            setOnClickListener {
                val result = Aya.launchBundled(
                    activity = this@MainActivity,
                    guideAsset = "aya-guide.md",
                    screenName = "Home",
                    question = hostQuestion.text.toString(),
                    askQuestion = false // host already captured the question
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
            text = "Open artwork generation demo"
            contentDescription = "Open artwork generation demo"
            setOnClickListener { startActivity(Intent(this@MainActivity, ArtworkActivity::class.java)) }
        })
        setContentView(column)
    }
}
