package dev.aya.android

import android.app.Activity
import android.app.PendingIntent
import android.content.BroadcastReceiver
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.os.Build

/**
 * Optional local-only Sharesheet choice hint. Disabled by default.
 * The selection is NOT proof that an attachment was consumed or an answer saved.
 * Hosts must obtain user consent before enabling this feature.
 */
object AyaShareTargetHints {
    private const val PREFS = "aya_share_target_hints"
    private const val ENABLED = "enabled"
    private const val PACKAGE = "last_chosen_package"

    fun setEnabled(context: Context, enabled: Boolean) {
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit().apply {
            putBoolean(ENABLED, enabled)
            if (!enabled) remove(PACKAGE)
        }.apply()
    }

    fun isEnabled(context: Context): Boolean =
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).getBoolean(ENABLED, false)

    fun lastChosenPackage(context: Context): String? =
        if (isEnabled(context)) context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
            .getString(PACKAGE, null) else null

    fun clear(context: Context) {
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit()
            .remove(PACKAGE).apply()
    }

    /** Fallback to an ordinary chooser when opt-in callback setup is unavailable. */
    fun createChooser(activity: Activity, sendIntent: Intent): Intent {
        if (!isEnabled(activity)) return Intent.createChooser(sendIntent, "Share with an assistant")
        return try {
            val flags = PendingIntent.FLAG_UPDATE_CURRENT or
                (if (Build.VERSION.SDK_INT >= 31) PendingIntent.FLAG_MUTABLE else 0)
            val callback = PendingIntent.getBroadcast(
                activity, 0,
                Intent(activity, AyaShareSelectionReceiver::class.java),
                flags
            )
            Intent.createChooser(sendIntent, "Share with an assistant", callback.intentSender)
        } catch (_: Exception) {
            Intent.createChooser(sendIntent, "Share with an assistant")
        }
    }

    internal fun recordSelection(context: Context, component: ComponentName?) {
        if (!isEnabled(context) || component == null) return
        val pkg = component.packageName
        if (pkg.isBlank() || pkg.length > 255) return
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit()
            .putString(PACKAGE, pkg).apply()
    }
}

/** Only reachable through the explicit OS chooser PendingIntent; not exported. */
class AyaShareSelectionReceiver : BroadcastReceiver() {
    @Suppress("DEPRECATION")
    override fun onReceive(context: Context, intent: Intent) {
        val component = if (Build.VERSION.SDK_INT >= 33) {
            intent.getParcelableExtra(Intent.EXTRA_CHOSEN_COMPONENT, ComponentName::class.java)
        } else {
            intent.getParcelableExtra(Intent.EXTRA_CHOSEN_COMPONENT)
        }
        AyaShareTargetHints.recordSelection(context, component)
    }
}
