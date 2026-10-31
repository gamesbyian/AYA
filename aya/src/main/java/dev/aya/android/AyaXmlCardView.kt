package dev.aya.android

import android.app.Activity
import android.content.Context
import android.content.ContextWrapper
import android.graphics.drawable.GradientDrawable
import android.util.AttributeSet
import android.util.TypedValue
import android.view.View
import android.view.ViewGroup
import android.widget.EditText
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast

/**
 * Android Studio XML/layout-editor adapter for the canonical AYA View card.
 *
 * <dev.aya.android.AyaXmlCardView ... app:ayaOutputInstructions="..." />
 *
 * This is a host-owned view, NOT an assistant recipient or a special share
 * transport. The runtime always delegates to AyaCardView and its exact-version
 * guarded review. The layout editor shows an inert, labelled preview.
 *
 * An Activity is required at runtime. Without one, or without a real output-use
 * instruction, this view fails closed and only displays an explanation.
 */
class AyaXmlCardView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : LinearLayout(context, attrs, defStyleAttr) {
    private var runtimeCard: AyaCardView? = null

    /** Host-owned error handler, optional. Must never infer recipient success. */
    var onLocalRejected: ((String) -> Unit)? = null

    /** True only when a guarded runtime card exists (never in layout preview). */
    val canOpenReview: Boolean get() = runtimeCard != null

    /** Assign a stable app resource ID via ayaQuestionInputId to save draft text. */
    val questionInput: EditText? get() = runtimeCard?.questionInput

    init {
        orientation = VERTICAL
        val styled = context.obtainStyledAttributes(attrs, R.styleable.AyaXmlCardView, defStyleAttr, 0)
        val guide: String
        val screen: String?
        val heading: String
        val description: String
        val disclosure: String
        val output: String
        val density: AyaCardDensity
        val cornerRadius: Float
        val questionId: Int
        try {
            guide = styled.getString(R.styleable.AyaXmlCardView_ayaGuideAsset)
                ?.trim().orEmpty().ifBlank { "aya-guide.md" }
            screen = styled.getString(R.styleable.AyaXmlCardView_ayaScreenName)
                ?.trim()?.takeIf { it.isNotEmpty() }
            heading = styled.getString(R.styleable.AyaXmlCardView_ayaTitle)
                ?.trim().orEmpty().ifBlank { "Ask Your Agent" }
            description = styled.getString(R.styleable.AyaXmlCardView_ayaDescription)
                ?.trim().orEmpty().ifBlank {
                    "Ask about this app. Review the app reference before sharing."
                }
            disclosure = styled.getString(R.styleable.AyaXmlCardView_ayaAttachmentDisclosure)
                ?.trim().orEmpty().ifBlank {
                    "App reference offered for sharing; your AI app may not accept files."
                }
            output = styled.getString(R.styleable.AyaXmlCardView_ayaOutputInstructions)
                ?.trim().orEmpty()
            density = if (styled.getInt(R.styleable.AyaXmlCardView_ayaDensity, 0) == 1)
                AyaCardDensity.COMPACT else AyaCardDensity.STANDARD
            cornerRadius = styled.getDimension(R.styleable.AyaXmlCardView_ayaCornerRadius,
                12f * resources.displayMetrics.density) / resources.displayMetrics.density
            questionId = styled.getResourceId(R.styleable.AyaXmlCardView_ayaQuestionInputId,
                View.NO_ID)
        } finally {
            styled.recycle()
        }

        val activity = findActivity(context)
        val problem = when {
            isInEditMode -> "Layout preview only. Run the app to ask an assistant."
            activity == null -> "AYA requires a host Android Activity."
            output.isBlank() -> "AYA requires real, host-specific instructions for using the answer."
            else -> null
        }
        if (isInEditMode) {
            showEditorPreview(heading, description, disclosure, output, cornerRadius)
        } else if (problem != null) {
            addView(TextView(context).apply {
                text = "$heading\n$description\n$problem"
                setTextSize(TypedValue.COMPLEX_UNIT_SP, 14f)
                contentDescription = text
                setPadding(dp(12), dp(12), dp(12), dp(12))
            }, LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT))
        } else {
            runtimeCard = AyaCardView(
                context = context,
                activity = requireNotNull(activity),
                guideAsset = guide,
                screenName = screen,
                title = heading,
                description = description,
                attachmentDisclosure = disclosure,
                outputInstructions = output,
                cornerRadiusDp = cornerRadius,
                densityMode = density,
                onRejected = { reason ->
                    val handler = onLocalRejected
                    if (handler != null) handler(reason)
                    else Toast.makeText(context, "AYA unavailable: $reason", Toast.LENGTH_LONG).show()
                }
            ).also { card ->
                if (questionId != View.NO_ID && questionId != 0) {
                    card.questionInput.id = questionId
                }
                addView(card, LayoutParams(
                    ViewGroup.LayoutParams.MATCH_PARENT,
                    ViewGroup.LayoutParams.WRAP_CONTENT
                ))
            }
        }
    }

    private fun showEditorPreview(
        heading: String,
        description: String,
        disclosure: String,
        output: String,
        cornerRadius: Float
    ) {
        val outline = 0xff777777.toInt()
        background = GradientDrawable().apply {
            setColor(0x00ffffff)
            setStroke(dp(1), outline)
            this.cornerRadius = cornerRadius * resources.displayMetrics.density
        }
        setPadding(dp(12), dp(12), dp(12), dp(12))

        val header = LinearLayout(context).apply { orientation = HORIZONTAL }
        header.addView(ImageView(context).apply {
            setImageResource(R.drawable.aya_card_mark)
            contentDescription = null
            importantForAccessibility = View.IMPORTANT_FOR_ACCESSIBILITY_NO
        }, LayoutParams(dp(48), dp(48)))
        header.addView(TextView(context).apply {
            text = "$heading\\n$description"
            setTextSize(TypedValue.COMPLEX_UNIT_SP, 16f)
        }, LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f))
        addView(header)
        addView(TextView(context).apply {
            text = disclosure
            setTextSize(TypedValue.COMPLEX_UNIT_SP, 12f)
        })
        addView(TextView(context).apply {
            text = if (output.isNotBlank()) "After your agent replies: $output"
                else "Output-use instructions required before runtime sharing"
            setTextSize(TypedValue.COMPLEX_UNIT_SP, 12f)
        })
        addView(TextView(context).apply {
            text = "Optional question (layout preview)"
            setPadding(0, dp(8), 0, dp(8))
        })
        addView(TextView(context).apply {
            text = "Ask Your Agent (preview only)"
            setPadding(dp(12), dp(12), dp(12), dp(12))
        })
    }

    fun setAttachmentDisclosure(value: String) {
        runtimeCard?.setAttachmentDisclosure(value)
    }

    fun setOutputInstructions(value: String) {
        // A missing mandatory instruction cannot become an active card implicitly.
        runtimeCard?.setOutputInstructions(value)
            ?: throw IllegalStateException("Invalid or preview-only AYA card; reinflate with output instructions.")
    }

    private fun dp(value: Int): Int =
        (value * resources.displayMetrics.density + 0.5f).toInt()

    private fun findActivity(context: Context): Activity? {
        var current = context
        repeat(32) {
            val candidate = current
            if (candidate is Activity) return candidate
            val parent = (candidate as? ContextWrapper)?.baseContext ?: return null
            if (parent === current) return null
            current = parent
        }
        return null
    }
}
