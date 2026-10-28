package dev.aya.sample

import android.app.Activity
import android.os.Bundle
import android.view.ViewGroup
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView
import dev.aya.android.Aya
import dev.aya.android.AyaRequest

/** Exercises AYA with a wholly fictional reference, without real user data. */
class MainActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val padding = (20 * resources.displayMetrics.density).toInt()
        val column = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(padding, padding, padding, padding)
        }
        val title = TextView(this).apply {
            text = "AYA: Ask Your Agent"
            textSize = 26f
        }
        column.addView(title)
        column.addView(TextView(this).apply {
            text = "This demonstrates Android's share handoff using a fictional " +
                "ParcelPad guide. ParcelPad itself is not implemented here. " +
                "Never share a real password or token with an assistant."
            textSize = 16f
        }, LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT
        ))
        val button = Button(this).apply {
            text = "Ask your agent"
            contentDescription = "Ask your agent about the fictional ParcelPad app"
            setOnClickListener {
                val guide = assets.open("EXAMPLE_PARCELPAD.md")
                    .bufferedReader(Charsets.UTF_8).use { it.readText() }
                Aya.launch(this@MainActivity, AyaRequest(
                    appName = "ParcelPad (fictional demonstration)",
                    appVersion = "1.0.0",
                    guide = guide,
                    screenName = "AYA demonstration",
                    question = "How do I add a parcel, and does carrier tracking work?"
                ))
            }
        }
        column.addView(button)
        setContentView(column)
    }
}
