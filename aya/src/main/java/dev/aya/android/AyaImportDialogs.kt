package dev.aya.android

import android.app.Activity
import android.app.AlertDialog

/**
 * Optional UI for user-selected output imports. Only routes to a host importer,
 * never executes, writes, activates, or applies any generated artifact.
 */
object AyaImportDialogs {
    fun show(
        activity: Activity,
        decision: AyaImportDecision,
        onContinueToHostImporter: (AyaImportDecision.Ready) -> Unit,
        onChooseAnotherFile: (() -> Unit)? = null,
        onChooseAmbiguousRoute: ((AyaImportRoute) -> Unit)? = null
    ) {
        when (decision) {
            is AyaImportDecision.Ready -> {
                val warnings = buildList {
                    if (decision.wrongCard) add(
                        "This file belongs to the ${decision.route.title} importer, not this AYA card."
                    )
                    if (decision.declaredTargetAppMismatch) add(
                        "The file claims to target a different app. Treat this claim as untrusted."
                    )
                    addAll(decision.validation.warnings)
                }
                val title = if (decision.wrongCard) "Output for another AYA card" else "Review agent output"
                val details = buildString {
                    append("Recognized: ${decision.route.title}\n\n")
                    append(decision.validation.preview.take(1200))
                    if (decision.validation.preview.length > 1200) append("…")
                    if (warnings.isNotEmpty()) append("\n\n").append(warnings.joinToString("\n"))
                    append("\n\nThe host will still check compatibility, show any impact and ask for permission before applying changes.")
                }
                AlertDialog.Builder(activity)
                    .setTitle(title)
                    .setMessage(details)
                    .setNegativeButton("Cancel", null)
                    .setPositiveButton("Continue to importer") { _, _ ->
                        onContinueToHostImporter(decision)
                    }
                    .show()
            }
            is AyaImportDecision.Unusable -> AlertDialog.Builder(activity)
                .setTitle("File cannot be used")
                .setMessage("Recognized as ${decision.route.title}, but validation failed:\n${decision.explanation}\n\nThe original file has not been changed.")
                .setNegativeButton("Cancel", null)
                .apply {
                    if (onChooseAnotherFile != null) setPositiveButton("Choose another file") { _, _ -> onChooseAnotherFile() }
                }.show()
            is AyaImportDecision.Unrecognized -> AlertDialog.Builder(activity)
                .setTitle("Unrecognized output")
                .setMessage("This app does not recognize the selected file as a supported output. Nothing was imported. Choose a different file or check the format requested from your agent.")
                .setNegativeButton("Cancel", null)
                .apply {
                    if (onChooseAnotherFile != null) setPositiveButton("Choose another file") { _, _ -> onChooseAnotherFile() }
                }.show()
            is AyaImportDecision.Ambiguous -> {
                val options = decision.routes.map { it.title }.toTypedArray()
                AlertDialog.Builder(activity)
                    .setTitle("Which importer should handle this file?")
                    .setItems(options) { _, index ->
                        onChooseAmbiguousRoute?.invoke(decision.routes[index])
                    }
                    .setNegativeButton("Cancel", null)
                    .show()
            }
        }
    }
}
