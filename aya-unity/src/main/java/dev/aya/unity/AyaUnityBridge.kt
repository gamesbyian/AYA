package dev.aya.unity

import android.app.Activity
import android.os.Looper
import dev.aya.android.AyaBundledLaunchResult
import dev.aya.android.AyaComponentAction
import org.json.JSONObject

/**
 * Java-visible, host-neutral Unity entry point. Unity invokes this on the
 * Activity UI thread and marshals the resulting LOCAL status back to C#.
 * No agent callback, output import, direct sharing or recipient observation.
 */
object AyaUnityBridge {
    @JvmStatic
    fun openHelp(
        activity: Activity?,
        guideAsset: String,
        screenName: String?,
        question: String?,
        askQuestion: Boolean
    ): String {
        if (activity == null || activity.isFinishing || activity.isDestroyed) {
            return rejected("An active Android Activity is required.")
        }
        if (Looper.myLooper() != Looper.getMainLooper()) {
            return rejected("AYA help must open on Android's UI thread.")
        }
        // Keep bad asset names out of the canonical reference verifier.
        // This check is only a conservative input guard; AYA additionally
        // validates the actual installed app/version and bundled guide.
        if (!Regex("^[A-Za-z0-9_-]+(?:/[A-Za-z0-9_-]+)*\\.md$").matches(guideAsset)) {
            return rejected("Invalid bundled AYA reference asset path.")
        }

        val outcome = try {
            AyaComponentAction.Help(
                guideAsset = guideAsset,
                screenName = screenName?.takeIf { it.isNotBlank() },
                askQuestion = askQuestion
            ).launch(activity, text = question)
        } catch (_: Exception) {
            AyaBundledLaunchResult.Rejected("Local AYA review could not open.")
        }
        return when (outcome) {
            AyaBundledLaunchResult.QuestionOpened -> localStatus("question_opened")
            AyaBundledLaunchResult.PreviewOpened -> localStatus("review_opened")
            is AyaBundledLaunchResult.Rejected -> rejected(outcome.reason)
        }
    }

    private fun localStatus(status: String): String =
        JSONObject().put("status", status).toString()

    private fun rejected(reason: String): String =
        JSONObject().put("status", "rejected").put("reason", reason).toString()
}
