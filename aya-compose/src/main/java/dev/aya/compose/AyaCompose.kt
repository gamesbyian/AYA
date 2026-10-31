package dev.aya.compose

import android.app.Activity
import android.text.Editable
import android.text.TextWatcher
import android.widget.Toast
import androidx.compose.runtime.Composable
import androidx.compose.runtime.key
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberUpdatedState
import androidx.compose.runtime.setValue
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Modifier
import androidx.compose.ui.viewinterop.AndroidView
import dev.aya.android.AyaBundledLaunchResult
import dev.aya.android.AyaCardDensity
import dev.aya.android.AyaCardView
import dev.aya.android.AyaComponentAction

/**
 * A thin, first-party Compose adapter. The host retains all packet authoring,
 * installed-version truth, review, sharing and final artifact import obligations.
 * The visible card uses the exact same Android View implementation as classic
 * host apps. Neither this library nor its callbacks can read assistant replies.
 *
 * Host must provide Activity and arrange one sensible scrolling parent.
 * Use Compose key(stableHostCardId) when rendering cards in changing lists.
 */
@Composable
fun AyaCard(
    activity: Activity,
    outputInstructions: String,
    modifier: Modifier = Modifier,
    guideAsset: String = "aya-guide.md",
    screenName: String? = null,
    title: String = "Ask Your Agent",
    description: String = "Ask for help with this app. Review its reference before sharing.",
    attachmentDisclosure: String = "App reference offered for sharing; your AI app may not accept files.",
    densityMode: AyaCardDensity = AyaCardDensity.STANDARD,
    onRejected: ((String) -> Unit)? = null
) {
    // Compose is the sole state owner. AndroidView may be reconstructed on host
    // state or configuration changes; the user's unsent question is preserved.
    var draft by rememberSaveable { mutableStateOf("") }
    val latestRejection = rememberUpdatedState(onRejected)

    key(activity, guideAsset, screenName, title, description, densityMode) {
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
                    densityMode = densityMode,
                    onRejected = { reason ->
                        val callback = latestRejection.value
                        if (callback != null) callback(reason)
                        else Toast.makeText(activity, "AYA unavailable: " + reason, Toast.LENGTH_LONG).show()
                    }
                ).apply {
                    questionInput.setText(draft)
                    questionInput.addTextChangedListener(object : TextWatcher {
                        override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
                        override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {
                            val updated = s?.toString().orEmpty()
                            if (updated != draft) draft = updated
                        }
                        override fun afterTextChanged(s: Editable?) {}
                    })
                }
            },
            update = { card ->
                card.setAttachmentDisclosure(attachmentDisclosure)
                card.setOutputInstructions(outputInstructions)
                // Avoid resetting cursor, selection or active IME composition
                // during an ordinary recomposition.
                if (card.questionInput.text.toString() != draft) card.questionInput.setText(draft)
            }
        )
    }
}

/**
 * Headless action for an existing Compose button/menu item or visual workflow.
 * Call launch() only in a user event handler, never from a composable effect.
 * Result means local AYA UI opened/rejected, NOT recipient ingestion.
 */
class AyaLauncher internal constructor(
    private val dispatch: (String?) -> AyaBundledLaunchResult
) {
    fun launch(text: String? = null): AyaBundledLaunchResult = dispatch(text)
}

@Composable
fun rememberAyaLauncher(
    activity: Activity,
    action: AyaComponentAction,
    onRejected: ((String) -> Unit)? = null
): AyaLauncher {
    val latestAction = rememberUpdatedState(action)
    val latestRejection = rememberUpdatedState(onRejected)

    return remember(activity) {
        AyaLauncher { text ->
            val result = if (activity.isFinishing || activity.isDestroyed) {
                AyaBundledLaunchResult.Rejected("Host activity is no longer available.")
            } else {
                latestAction.value.launch(activity, text)
            }
            if (result is AyaBundledLaunchResult.Rejected) {
                val callback = latestRejection.value
                if (callback != null) callback(result.reason)
                else Toast.makeText(activity, "AYA unavailable: " + result.reason, Toast.LENGTH_LONG).show()
            }
            result
        }
    }
}
