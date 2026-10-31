package dev.aya.sample

import android.app.Instrumentation
import android.content.Intent
import android.widget.EditText
import android.widget.TextView
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import dev.aya.android.AyaCardDensity
import dev.aya.android.AyaCardView
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith

/** Host-side smoke tests; receiving-assistant ingestion still needs separate device QA. */
@RunWith(AndroidJUnit4::class)
class AyaCardUiTest {
    @Test fun sampleCardHasEditableOptionalQuestionAndReviewAction() {
        val instrumentation: Instrumentation = InstrumentationRegistry.getInstrumentation()
        val context = instrumentation.targetContext
        val intent = Intent(context, MainActivity::class.java).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        val activity = instrumentation.startActivitySync(intent) as MainActivity
        try {
            val card = activity.findViewById<AyaCardView>(R.id.aya_sample_open_help)
            assertNotNull(card)
            val question = activity.findViewById<EditText>(R.id.aya_sample_help_question)
            assertNotNull(question)
            assertTrue(question.hint.toString().contains("optional"))
            instrumentation.runOnMainSync { question.setText("What does this sample demonstrate?") }
            assertEquals("What does this sample demonstrate?", question.text.toString())
            assertTrue(card.childCount >= 4)
        } finally {
            instrumentation.runOnMainSync { activity.finish() }
        }
    }

    @Test fun optionalImportActionOnlyInvokesHostCallback() {
        val instrumentation = InstrumentationRegistry.getInstrumentation()
        val context = instrumentation.targetContext
        val activity = instrumentation.startActivitySync(
            Intent(context, MainActivity::class.java).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        ) as MainActivity
        try {
            var requests = 0
            instrumentation.runOnMainSync {
                val card = AyaCardView(
                    context, activity,
                    outputInstructions = "Import your saved result via the file picker.",
                    onImportRequested = { requests++ }
                )
                val action = card.getChildAt(card.childCount - 1) as android.widget.Button
                assertEquals("Import agent output", action.text.toString())
                action.performClick()
            }
            assertEquals(1, requests)
        } finally {
            instrumentation.runOnMainSync { activity.finish() }
        }
    }

    @Test fun specializedCardDelegatesToTypedHostHandoffWithoutDuplicateComposer() {
        val instrumentation = InstrumentationRegistry.getInstrumentation()
        val context = instrumentation.targetContext
        val activity = instrumentation.startActivitySync(
            Intent(context, MainActivity::class.java).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        ) as MainActivity
        try {
            var captured: String? = null
            instrumentation.runOnMainSync {
                val card = AyaCardView(
                    context, activity,
                    title = "Ask for artwork",
                    outputInstructions = "Save the generated image and import it here.",
                    questionHint = "Describe your image",
                    onAskRequested = { captured = it }
                )
                card.questionInput.setText("Purple skyline")
                assertEquals("Describe your image", card.questionInput.hint.toString())
                val button = card.getChildAt(card.childCount - 1) as android.widget.Button
                button.performClick()
            }
            assertEquals("Purple skyline", captured)
        } finally {
            instrumentation.runOnMainSync { activity.finish() }
        }
    }

    @Test fun compactCardPreservesOptionalEditorAndAction() {
        val instrumentation = InstrumentationRegistry.getInstrumentation()
        val context = instrumentation.targetContext
        val activity = instrumentation.startActivitySync(
            Intent(context, MainActivity::class.java).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        ) as MainActivity
        try {
            lateinit var card: AyaCardView
            instrumentation.runOnMainSync {
                card = AyaCardView(context, activity, outputInstructions = "Return to the sample and use the answer manually.", densityMode = AyaCardDensity.COMPACT)
            }
            assertEquals(1, card.questionInput.minLines)
            assertTrue(card.childCount >= 3)
            assertTrue(card.getChildAt(card.childCount - 1) is android.widget.Button)
        } finally {
            instrumentation.runOnMainSync { activity.finish() }
        }
    }
}
