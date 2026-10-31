package dev.aya.godot

import dev.aya.android.AyaBundledLaunchResult
import dev.aya.android.AyaComponentAction
import org.godotengine.godot.Godot
import org.godotengine.godot.plugin.GodotPlugin
import org.godotengine.godot.plugin.SignalInfo
import org.godotengine.godot.plugin.UsedByGodot

/**
 * The only Godot signals report opening local UI or rejection, never assistant
 * ingestion, replies, output imports or completion. IDs route among cards.
 */
class AyaGodotPlugin(godot: Godot) : GodotPlugin(godot) {
    companion object {
        private val LOCAL_STATUS = SignalInfo(
            "aya_local_status", String::class.java, String::class.java, String::class.java
        )
    }

    override fun getPluginName() = "AYA"
    override fun getPluginSignals() = setOf(LOCAL_STATUS)

    @UsedByGodot
    fun openHelp(
        requestId: String,
        guideAsset: String,
        screenName: String,
        question: String,
        askQuestion: Boolean
    ) {
        runOnHostThread {
            val host = activity
            val result = try {
                if (host == null || host.isFinishing || host.isDestroyed) {
                    AyaBundledLaunchResult.Rejected("Host Android Activity unavailable.")
                } else {
                    AyaComponentAction.Help(
                        guideAsset = guideAsset,
                        screenName = screenName.takeIf { it.isNotBlank() },
                        askQuestion = askQuestion
                    ).launch(host, text = question)
                }
            } catch (_: Exception) {
                AyaBundledLaunchResult.Rejected("Could not open the local AYA review.")
            }
            when (result) {
                AyaBundledLaunchResult.QuestionOpened ->
                    emitSignal(LOCAL_STATUS.name, requestId, "question_opened", "")
                AyaBundledLaunchResult.PreviewOpened ->
                    emitSignal(LOCAL_STATUS.name, requestId, "review_opened", "")
                is AyaBundledLaunchResult.Rejected ->
                    emitSignal(LOCAL_STATUS.name, requestId, "rejected", result.reason)
            }
        }
    }
}
