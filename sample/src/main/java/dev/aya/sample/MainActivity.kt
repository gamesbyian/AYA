package dev.aya.sample

import android.app.Activity
import android.os.Bundle
import android.view.ViewGroup
import android.widget.Button
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
        setContentView(column)
    }
}
