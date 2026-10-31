package dev.aya.sample

import android.os.Bundle
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import dev.aya.android.AyaComponentAction
import dev.aya.compose.AyaCard
import dev.aya.compose.rememberAyaLauncher

/** Separate real APK consumer of the optional Compose AAR and guarded SDK. */
class ComposeDemoActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { ComposeDemoScreen() }
    }

    @Composable
    private fun ComposeDemoScreen() {
        val helpAction = rememberAyaLauncher(
            activity = this,
            action = AyaComponentAction.Help(
                guideAsset = "aya-guide.md",
                screenName = "Compose demo",
                askQuestion = false
            )
        )
        MaterialTheme {
            Column(
                modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Text("AYA Compose integration demo", style = MaterialTheme.typography.titleLarge)
                Text("This screen embeds the same version-checked AYA card as the View sample. " +
                    "The agent's response must be used manually.")
                AyaCard(
                    activity = this@ComposeDemoActivity,
                    componentId = "sample.compose.help",
                    modifier = Modifier.fillMaxWidth(),
                    guideAsset = "aya-guide.md",
                    screenName = "Compose demo",
                    outputInstructions = "Return to the sample and use the agent's advice yourself. " +
                        "This demonstration does not apply responses automatically."
                )
                Button(
                    modifier = Modifier.fillMaxWidth(),
                    onClick = {
                        helpAction.launch("How does the Compose action open AYA review?")
                    }
                ) {
                    Text("Ask from existing Compose button")
                }
            }
        }
    }
}
