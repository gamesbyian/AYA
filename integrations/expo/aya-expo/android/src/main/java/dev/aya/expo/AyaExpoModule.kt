package dev.aya.expo

import dev.aya.android.AyaBundledLaunchResult
import dev.aya.android.AyaComponentAction
import expo.modules.kotlin.Promise
import expo.modules.kotlin.modules.Module
import expo.modules.kotlin.modules.ModuleDefinition

/**
 * Android-only Expo Modules API bridge. The user remains in control:
 * this opens local AYA question/review, never an assistant or a file import.
 */
class AyaExpoModule : Module() {
    override fun definition() = ModuleDefinition {
        Name("AyaExpo")

        AsyncFunction("openHelp") { guideAsset: String,
                                    screenName: String?,
                                    question: String,
                                    askQuestion: Boolean,
                                    promise: Promise ->
            val host = appContext.currentActivity
            if (host == null || host.isFinishing || host.isDestroyed) {
                promise.resolve(rejected("An active Android screen is required."))
                return@AsyncFunction
            }
            host.runOnUiThread {
                if (appContext.currentActivity !== host ||
                    host.isFinishing || host.isDestroyed) {
                    promise.resolve(rejected("The Android screen is no longer active."))
                    return@runOnUiThread
                }
                val result = try {
                    AyaComponentAction.Help(
                        guideAsset = guideAsset,
                        screenName = screenName,
                        askQuestion = askQuestion
                    ).launch(host, text = question)
                } catch (_: Exception) {
                    AyaBundledLaunchResult.Rejected("Local AYA review could not open.")
                }
                val response: Map<String, String> = when (result) {
                    AyaBundledLaunchResult.QuestionOpened ->
                        mapOf("status" to "question_opened")
                    AyaBundledLaunchResult.PreviewOpened ->
                        mapOf("status" to "review_opened")
                    is AyaBundledLaunchResult.Rejected -> rejected(result.reason)
                }
                promise.resolve(response)
            }
        }
    }

    private fun rejected(reason: String): Map<String, String> =
        mapOf("status" to "rejected", "reason" to reason)
}
