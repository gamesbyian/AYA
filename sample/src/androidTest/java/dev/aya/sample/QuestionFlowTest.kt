package dev.aya.sample

import android.widget.Button
import android.widget.EditText
import dev.aya.android.AyaCardView
import dev.aya.android.AyaBundledLaunchResult
import dev.aya.android.AyaComponentAction
import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.action.ViewActions.click
import androidx.test.espresso.action.ViewActions.closeSoftKeyboard
import androidx.test.espresso.action.ViewActions.replaceText
import androidx.test.espresso.action.ViewActions.scrollTo
import androidx.test.espresso.assertion.ViewAssertions.doesNotExist
import androidx.test.espresso.assertion.ViewAssertions.matches
import androidx.test.espresso.matcher.ViewMatchers.withContentDescription
import androidx.test.espresso.matcher.ViewMatchers.withId
import androidx.test.espresso.matcher.ViewMatchers.withText
import org.hamcrest.Matchers.containsString
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.ext.junit.rules.ActivityScenarioRule
import androidx.test.platform.app.InstrumentationRegistry
import androidx.test.uiautomator.UiDevice
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

/**
 * In-app AYA dialogs are queried through Espresso's application-window matcher.
 * UI Automator can report the Android IME as the foreground package even while
 * the real AYA review dialog is open; it is reserved for device wake/unlock.
 */
@RunWith(AndroidJUnit4::class)
class QuestionFlowTest {
    @get:Rule
    val scenario = ActivityScenarioRule(MainActivity::class.java)

    private lateinit var device: UiDevice

    @Before fun showApp() {
        device = UiDevice.getInstance(InstrumentationRegistry.getInstrumentation())
        device.wakeUp()
        device.executeShellCommand("wm dismiss-keyguard")
        // ActivityScenarioRule owns the Activity. Recreate it through the rule
        // to clear old dialogs without an external am-start that destroys the
        // rule's instance (CLEAR_TOP caused flaky lifecycle assertions).
        scenario.scenario.recreate()
        // Verify the consuming Activity is alive using its stable view IDs.
        // UiAutomator foreground discovery is unreliable immediately after
        // ActivityScenario recreation and can fail before testing any AYA UI.
        scenario.scenario.onActivity {
            assertTrue("Sample host action must exist",
                it.findViewById<AyaCardView>(R.id.aya_sample_open_help) != null)
        }
        device.waitForIdle()
    }

    private fun assertDialogText(description: String, expected: String) {
        onView(withContentDescription(description))
            .check(matches(withText(containsString(expected))))
    }

    private fun tapHost(id: Int) {
        scenario.scenario.onActivity {
            val control = it.findViewById<Button>(id)
                ?: throw AssertionError("Missing consuming host control: $id")
            assertTrue("Host control should be enabled", control.isEnabled)
            control.performClick()
        }
    }

    private fun submitCard() {
        scenario.scenario.onActivity {
            val card = it.findViewById<AyaCardView>(R.id.aya_sample_open_help)
                ?: throw AssertionError("Missing AYA card")
            val button = card.getChildAt(card.childCount - 1) as Button
            assertTrue("Card action should be enabled for blank or nonblank questions", button.isEnabled)
            button.performClick()
        }
    }

    @Test fun typedComponentActionUsesVersionGuardAndOpensReviewedDocument() {
        val question = "How is this component integrated into the sample?"
        scenario.scenario.onActivity { activity ->
            val result = AyaComponentAction.Help(
                guideAsset = "aya-guide.md",
                screenName = "Home",
                askQuestion = false
            ).launch(activity, text = question)
            assertTrue("Only the local review opening can be reported",
                result is AyaBundledLaunchResult.PreviewOpened)
        }
        assertDialogText("Reviewed AYA help document", question)
        onView(withContentDescription("Your question for the assistant (optional)"))
            .check(doesNotExist())
    }

    @Test fun typedComponentActionRejectsMissingBundledGuideWithoutOpeningReview() {
        scenario.scenario.onActivity { activity ->
            val result = AyaComponentAction.Help(
                guideAsset = "nonexistent-aya-guide.md",
                askQuestion = false
            ).launch(activity, text = "Will not be shared")
            assertTrue("Invalid/missing reference must not fall back to raw launch",
                result is AyaBundledLaunchResult.Rejected)
        }
        onView(withContentDescription("Reviewed AYA help document"))
            .check(doesNotExist())
    }

    @Test fun cardQuestionFeedsTheActualReviewedDocumentWithoutDuplicateComposer() {
        val question = "Why does the help attachment need a file provider?"
        scenario.scenario.onActivity {
            it.findViewById<EditText>(R.id.aya_sample_help_question).setText(question)
        }
        submitCard()
        assertDialogText("Reviewed AYA help document", question)
        onView(withContentDescription("Your question for the assistant (optional)"))
            .check(doesNotExist())
    }

    @Test fun cardQuestionDraftSurvivesHostRecreation() {
        val question = "Does this draft survive rotation and Activity recreation?"
        scenario.scenario.onActivity {
            it.findViewById<EditText>(R.id.aya_sample_help_question).setText(question)
        }
        scenario.scenario.recreate()
        scenario.scenario.onActivity {
            assertTrue(
                "The host saves its own AYA card question field",
                it.findViewById<EditText>(R.id.aya_sample_help_question).text.toString() == question
            )
        }
    }

    @Test fun blankCardQuestionIsAllowedAndGetsGenericHelpRequest() {
        scenario.scenario.onActivity {
            assertTrue(it.findViewById<EditText>(R.id.aya_sample_help_question).text.isBlank())
        }
        submitCard()
        assertDialogText("Reviewed AYA help document", "Help me understand and use this application.")
        onView(withContentDescription("Your question for the assistant (optional)"))
            .check(doesNotExist())
    }

    @Test fun creativeEditorIsPromptFirstAndFullGuidePreservesEdits() {
        tapHost(R.id.aya_sample_open_artwork)
        onView(withContentDescription("Review the creative image request before sharing"))
            .perform(scrollTo(), click())
        assertDialogText("Edit the image request before sharing", "Aurora Station")
        val edited = "Generate a square poster with a luminous purple skyline."
        onView(withContentDescription("Edit the image request before sharing"))
            .perform(replaceText(edited), closeSoftKeyboard())
        // Full guide is the neutral AlertDialog button, not the default share action.
        onView(withId(android.R.id.button3)).perform(click())
        assertDialogText("Reviewed AYA creative document", edited)
        onView(withContentDescription("Reviewed AYA creative document"))
            .check(matches(withText(org.hamcrest.Matchers.not(
                containsString("Atmospheric science-fiction season art")
            ))))
    }

    @Test fun cancelCardReviewKeepsHostAppOpenAndDraftIntact() {
        val question = "Can I cancel before sharing?"
        scenario.scenario.onActivity {
            it.findViewById<EditText>(R.id.aya_sample_help_question).setText(question)
        }
        submitCard()
        onView(withContentDescription("Reviewed AYA help document"))
            .check(matches(org.hamcrest.Matchers.anything()))
        // The review's negative button cancels without invoking ACTION_SEND.
        onView(withId(android.R.id.button2)).perform(click())
        onView(withContentDescription("Reviewed AYA help document"))
            .check(doesNotExist())
        scenario.scenario.onActivity {
            assertFalse("Cancelling AYA must not finish the host", it.isFinishing)
            assertFalse("Cancelling AYA must not destroy the host", it.isDestroyed)
            assertTrue("The host card retains the question after cancellation",
                it.findViewById<EditText>(R.id.aya_sample_help_question).text.toString() == question)
        }
    }
}
