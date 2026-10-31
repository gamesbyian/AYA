package dev.aya.android

import android.app.Activity

/**
 * A stable, typed action surface for Android UI builders, workflow graphs and
 * future platform adapters. It delegates to the same exact-version-guarded SDK
 * paths as host-written Kotlin. It NEVER starts a receiver automatically,
 * monitors assistant responses or receives generated files.
 *
 * The result only reports opening local AYA UI or local rejection. It does not
 * report that Android sharing was completed or a recipient accepted anything.
 *
 * This is intentionally independent of Compose/Flutter/React Native/Godot.
 * Their optional bridges should call these actions rather than fork transport.
 */
sealed class AyaComponentAction {
    abstract fun launch(activity: Activity, text: String? = null): AyaBundledLaunchResult

    /** Help action for existing buttons, menus, nodes and visual workflows. */
    data class Help(
        val guideAsset: String = "aya-guide.md",
        val screenName: String? = null,
        val askQuestion: Boolean = true
    ) : AyaComponentAction() {
        override fun launch(activity: Activity, text: String?): AyaBundledLaunchResult =
            Aya.launchBundled(
                activity = activity,
                guideAsset = guideAsset,
                screenName = screenName,
                question = text,
                askQuestion = askQuestion
            )
    }

    /** Image generation; host supplies verified constraints and manual import steps. */
    data class GenerateImage(
        val task: AyaCreativeTask,
        val guideAsset: String = "aya-guide.md",
        val screenName: String? = null,
        val askDirection: Boolean = true
    ) : AyaComponentAction() {
        override fun launch(activity: Activity, text: String?): AyaBundledLaunchResult =
            Aya.launchCreativeBundled(
                activity = activity,
                task = task,
                guideAsset = guideAsset,
                screenName = screenName,
                direction = text,
                askDirection = askDirection
            )
    }

    /** Language/personality pack handoff; the host alone validates imported packs. */
    data class Translation(
        val task: AyaTranslationTask,
        val kitAsset: String = "aya-translation-kit.md",
        val guideAsset: String = "aya-guide.md",
        val screenName: String? = "Language",
        val askDirection: Boolean = false
    ) : AyaComponentAction() {
        override fun launch(activity: Activity, text: String?): AyaBundledLaunchResult =
            Aya.launchTranslationBundled(
                activity = activity,
                task = task,
                kitAsset = kitAsset,
                guideAsset = guideAsset,
                screenName = screenName,
                direction = text,
                askDirection = askDirection
            )
    }
}
