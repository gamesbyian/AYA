package dev.aya.android

import android.app.Activity
import android.content.Context
import android.content.res.ColorStateList
import android.graphics.drawable.GradientDrawable
import android.text.InputType
import android.util.TypedValue
import android.view.Gravity
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.EditText
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast

/** AYA density. Both modes use the same accessible, full-width submission flow. */
enum class AyaCardDensity { STANDARD, COMPACT }

/**
 * A host-native, optional question-first card. No data is transmitted from this view.
 * The button opens the SDK's installed-version-checked review, not a recipient app.
 * Host supplies truthful task-specific copy and must not insert private diagnostics.
 *
 * Uses platform Views: compatible with Activity/Fragment and Compose AndroidView,
 * without making Compose a transitive dependency of the base AYA SDK.
 */
class AyaCardView(
    context: Context,
    private val activity: Activity,
    private val guideAsset: String = "aya-guide.md",
    private val screenName: String? = null,
    title: String = "Ask Your Agent",
    description: String = "Ask for help with this app. You can review the app reference before sharing it.",
    attachmentDisclosure: String = "App reference offered for sharing; your AI app may not accept files.",
    outputInstructions: String,
    cornerRadiusDp: Float = 12f,
    densityMode: AyaCardDensity = AyaCardDensity.STANDARD,
    private val onRejected: (String) -> Unit = {
        Toast.makeText(context, "AYA unavailable: $it", Toast.LENGTH_LONG).show()
    }
) : LinearLayout(context) {

    val questionInput: EditText = EditText(context)
    private val shareDetails: TextView = TextView(context)
    private val returnDetails: TextView = TextView(context)
    private val density = resources.displayMetrics.density
    private val compact = densityMode == AyaCardDensity.COMPACT

    init {
        orientation = VERTICAL
        val foreground = themedColor(android.R.attr.textColorPrimary, 0xff222222.toInt())
        val secondary = themedColor(android.R.attr.textColorSecondary, foreground)
        val outline = themedColor(android.R.attr.colorControlNormal, secondary)
        background = GradientDrawable().apply {
            setColor(themedColor(android.R.attr.colorBackground, 0xffffffff.toInt()))
            setStroke(dp(1), outline)
            cornerRadius = dpF(cornerRadiusDp.coerceAtLeast(0f))
        }
        val inset = if (compact) 12 else 16
        setPadding(dp(inset), dp(inset), dp(inset), dp(inset))

        val header = LinearLayout(context).apply { orientation = HORIZONTAL; gravity = Gravity.TOP }
        val logo = ImageView(context).apply {
            setImageResource(R.drawable.aya_card_mark)
            imageTintList = ColorStateList.valueOf(foreground)
            contentDescription = null
            importantForAccessibility = View.IMPORTANT_FOR_ACCESSIBILITY_NO
        }
        val logoSize = if (compact) 48 else 64
        header.addView(logo, LayoutParams(dp(logoSize), dp(logoSize)).apply { rightMargin = dp(if (compact) 8 else 12) })
        val copy = LinearLayout(context).apply { orientation = VERTICAL }
        val heading = TextView(context).apply {
            text = title
            setTextColor(foreground)
            setTextSize(TypedValue.COMPLEX_UNIT_SP, if (compact) 16f else 17f)
            setTypeface(typeface, android.graphics.Typeface.BOLD)
        }
        copy.addView(heading)
        copy.addView(TextView(context).apply {
            text = description
            setTextColor(secondary)
            setTextSize(TypedValue.COMPLEX_UNIT_SP, 14f)
        })
        header.addView(copy, LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f))
        addView(header)

        shareDetails.text = attachmentDisclosure
        shareDetails.setTextColor(secondary)
        shareDetails.setTextSize(TypedValue.COMPLEX_UNIT_SP, 12f)
        shareDetails.setPadding(0, dp(if (compact) 8 else 12), 0, dp(if (compact) 4 else 8))
        addView(shareDetails)

        require(outputInstructions.isNotBlank()) { "Host-specific output-use instructions are required." }
        returnDetails.text = "After your agent replies: " + outputInstructions.trim()
        returnDetails.setTextColor(secondary)
        returnDetails.setTextSize(TypedValue.COMPLEX_UNIT_SP, 12f)
        returnDetails.setPadding(0, 0, 0, dp(if (compact) 8 else 12))
        addView(returnDetails)

        questionInput.apply {
            hint = "What would you like help with? (optional)"
            inputType = InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_FLAG_MULTI_LINE or InputType.TYPE_TEXT_FLAG_CAP_SENTENCES
            minLines = if (compact) 1 else 2
            setHorizontallyScrolling(false)
            // Grow with input; the host screen, rather than an inner card viewport, scrolls.
            setSingleLine(false)
            contentDescription = "Question for your agent, optional"
            id = View.generateViewId()
        }
        addView(questionInput, LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT))

        addView(Button(context).apply {
            text = "Ask Your Agent"
            contentDescription = "Review your question and app reference before sharing"
            minHeight = dp(48)
            setOnClickListener {
                val result = Aya.launchBundled(
                    activity = activity,
                    guideAsset = guideAsset,
                    screenName = screenName,
                    question = questionInput.text.toString(),
                    askQuestion = false
                )
                if (result is AyaBundledLaunchResult.Rejected) onRejected(result.reason.toString())
            }
        }, LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT).apply {
            topMargin = dp(if (compact) 4 else 8)
        })
    }

    /** Host may revise disclosure when its actual attachment selection changes. */
    fun setAttachmentDisclosure(value: String) { shareDetails.text = value }

    /** Keep this aligned with the host’s real, version-verified import/use flow. */
    fun setOutputInstructions(value: String) {
        require(value.isNotBlank()) { "Host-specific output-use instructions are required." }
        returnDetails.text = "After your agent replies: " + value.trim()
    }

    private fun dp(value: Int): Int = (value * density + 0.5f).toInt()
    private fun dpF(value: Float): Float = value * density
    private fun themedColor(attribute: Int, fallback: Int): Int {
        val v = TypedValue()
        return if (context.theme.resolveAttribute(attribute, v, true)) {
            if (v.resourceId != 0) {
                try { androidx.core.content.ContextCompat.getColor(context, v.resourceId) }
                catch (_: Exception) { fallback }
            } else if (v.type in TypedValue.TYPE_FIRST_COLOR_INT..TypedValue.TYPE_LAST_COLOR_INT) v.data
            else fallback
        } else fallback
    }
}
