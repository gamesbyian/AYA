package dev.aya.sample

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.unit.dp
import dev.aya.android.AyaBundledLaunchResult
import dev.aya.android.AyaCardDensity
import dev.aya.android.AyaComponentAction
import dev.aya.compose.AyaCard
import dev.aya.compose.rememberAyaLauncher

/** First-party actual consuming Compose screen, no simulated provider or reply. */
class ComposeDemoActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                Column(
                    modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Text("AYA Compose drop-in demo", style = MaterialTheme.typography.headlineSmall)
                    Text("This reuses the native AYA card and exact-version guide. Review is always required.")
                    AyaCard(
                        activity = this@ComposeDemoActivity,
                        componentId = "sample.compose.help",
                        guideAsset = "aya-guide.md",
                        screenName = "Compose demo",
                        title = "Ask Your Agent",
                        description = "Ask about this sample or the Compose handoff.",
                        attachmentDisclosure = "An editable app guide may be offered as a text attachment.",
                        outputInstructions = "Read the response and apply useful advice yourself. This sample does not import help replies.",
                        densityMode = AyaCardDensity.COMPACT,
                        modifier = Modifier.fillMaxWidth()
                    )
                    Spacer(Modifier.height(8.dp))
                    Text("Or connect an existing Compose action:")
                    var question by rememberSaveable { mutableStateOf("") }
                    OutlinedTextField(
                        value = question,
                        onValueChange = { question = it },
                        label = { Text("Question for headless action") },
                        modifier = Modifier.fillMaxWidth()
                    )
                    val action = remember {
                        AyaComponentAction.Help(
                            guideAsset = "aya-guide.md",
                            screenName = "Compose demo",
                            askQuestion = false
                        )
                    }
                    val launch = rememberAyaLauncher(this@ComposeDemoActivity, action)
                    var failure by rememberSaveable { mutableStateOf<String?>(null) }
                    Button(
                        onClick = {
                            failure = when (val result = launch(question)) {
                                is AyaBundledLaunchResult.Rejected -> result.reason
                                else -> null
                            }
                        },
                        modifier = Modifier.fillMaxWidth().semantics {
                            contentDescription = "Review Compose headless AYA action"
                        }
                    ) {
                        Text("Review headless AYA action")
                    }
                    failure?.let { Text("AYA unavailable: $it") }
                }
            }
        }
    }
}
