package dev.aya.sample

import android.view.LayoutInflater
import android.view.ViewGroup
import android.widget.EditText
import android.widget.LinearLayout
import androidx.test.ext.junit.rules.ActivityScenarioRule
import androidx.test.ext.junit.runners.AndroidJUnit4
import dev.aya.android.AyaXmlCardView
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

/** Android Studio XML card is a real runtime card with no alternative transport. */
@RunWith(AndroidJUnit4::class)
class AyaXmlCardTest {
    @get:Rule val scenario = ActivityScenarioRule(MainActivity::class.java)

    @Test fun xmlCardInflatesWithStableQuestionInputAndValidRuntimeAction() {
        scenario.scenario.onActivity { activity ->
            val root = LayoutInflater.from(activity)
                .inflate(R.layout.aya_xml_card_demo, null, false) as LinearLayout
            activity.setContentView(root)
            val card = root.findViewById<AyaXmlCardView>(R.id.aya_sample_xml_card)
            assertNotNull(card)
            assertTrue("Card must delegate to the existing guarded AYA View", card.canOpenReview)
            assertEquals(R.id.aya_sample_xml_question, card.questionInput?.id)
            assertTrue(card.questionInput is EditText)
            assertTrue((card.getChildAt(0) as ViewGroup).childCount >= 4)
        }
    }

    @Test fun xmlCardWithoutReturnInstructionsFailsClosed() {
        scenario.scenario.onActivity { activity ->
            val view = LayoutInflater.from(activity)
                .inflate(R.layout.aya_xml_card_invalid_demo, null, false) as AyaXmlCardView
            assertFalse("Missing output-use instructions must not enable review", view.canOpenReview)
            assertEquals(null, view.questionInput)
        }
    }
}
