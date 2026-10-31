package dev.aya.compose

import android.app.Activity
import android.text.Editable
import android.text.TextWatcher
import android.widget.Toast
import androidx.compose.runtime.Composable
import androidx.compose.runtime.key
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberUpdatedState
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Modifier
import androidx.compose.ui.viewinterop.AndroidView
import dev.aya.android.AyaBundledLaunchResult
import dev.aya.android.AyaCardDensity
import dev.aya.android.AyaCardView
import dev.aya.android.AyaComponentAction

/**
 * An actual Compose drop-in for the host-themed, accessible AYA SDK card.
 * The core SDK remains free of Compose dependencies, and the guarded review
 * and Android Share logic stay in AyaCardView. No agent replies are observed.
 *
 * [componentId] is a stable, nonblank key for the integration location.
 * For repeated items in a LazyColumn, surround calls with Compose key(item.id).
 * [initialQuestion] seeds a new draft; Compose saves/restores subsequent edits.
 */
@Composable
fun AyaCard(
    activity: Activity,
    componentId: String,
    outputInstructions: String,
    modifier: Modifier = Modifier,
    guideAsset: String = "aya-guide.md",
    screenName: String? = null,
    title: String = "Ask Your Agent",
    description: String = "Ask for help with this app. You can review the app reference before sharing it.",
    attachmentDisclosure: String = "App reference offered for sharing; your AI app may not accept files.",
    densityMode: AyaCardDensity = AyaCardDensity.STANDARD,
    cornerRadiusDp: Float = 12f,
    initialQuestion: String = "",
    onQuestionChanged: (String) -> Unit = {},
    onRejected: ((String) -> Unit)? = null
) {
    require(componentId.isNotBlank()) { "A stable componentId is required" }
    require(outputInstructions.isNotBlank()) { "Host-specific output instructions are required" }

    val draft = rememberSaveable(componentId) { mutableStateOf(initialQuestion) }
    val currentQuestionChanged = rememberUpdatedState(onQuestionChanged)
    val currentRejected = rememberUpdatedState(onRejected)

    // Configuration changes recreate the native View, while the typed draft
    // persists through Compose state. Dynamic copy is updated without rebuild.
    key(activity, componentId, guideAsset, screenName, title, description, densityMode, cornerRadiusDp) {
        AndroidView(
            modifier = modifier,
            factory = { context ->
                AyaCardView(
                    context = context,
                    activity = activity,
                    guideAsset = guideAsset,
                    screenName = screenName,
                    title = title,
                    description = description,
                    attachmentDisclosure = attachmentDisclosure,
                    outputInstructions = outputInstructions,
                    cornerRadiusDp = cornerRadiusDp,
                    densityMode = densityMode,
                    onRejected = { reason ->
                        val handler = currentRejected.value
                        if (handler != null) handler(reason)
                        else Toast.makeText(activity, "AYA unavailable: $reason", Toast.LENGTH_LONG).show()
                    }
                ).apply {
                    questionInput.setText(draft.value)
                    questionInput.addTextChangedListener(object : TextWatcher {
                        override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) = Unit
                        override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) = Unit
                        override fun afterTextChanged(s: Editable?) {
                            val next = s?.toString().orEmpty()
                            if (draft.value != next) {
                                draft.value = next
                                currentQuestionChanged.value(next)
                            }
                        }
                    })
                }
            },
            update = { card ->
                card.setAttachmentDisclosure(attachmentDisclosure)
                card.setOutputInstructions(outputInstructions)
                if (card.questionInput.text.toString() != draft.value) {
                    card.questionInput.setText(draft.value)
                }
            }
        )
    }
}

/**
 * Headless action for any Compose Button, menu item or graph trigger.
 * Exposes ONLY local question/review opening or rejection, never recipient
 * processing, assistant replies, or host-file import.
 */
@Composable
fun rememberAyaLauncher(
    activity: Activity,
    action: AyaComponentAction
): (String?) -> AyaBundledLaunchResult {
    val currentActivity = rememberUpdatedState(activity)
    val currentAction = rememberUpdatedState(action)
    return remember {
        { text: String? -> currentAction.value.launch(currentActivity.value, text) }
    }
}
