package dev.aya.sample

import android.widget.Button
import android.widget.EditText
import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.assertion.ViewAssertions.doesNotExist
import androidx.test.espresso.assertion.ViewAssertions.matches
import androidx.test.espresso.action.ViewActions.click
import androidx.test.espresso.action.ViewActions.replaceText
import androidx.test.espresso.action.ViewActions.scrollTo
import androidx.test.espresso.matcher.ViewMatchers.isDisplayed
import androidx.test.espresso.matcher.ViewMatchers.withContentDescription
import androidx.test.espresso.matcher.ViewMatchers.withId
import androidx.test.espresso.matcher.ViewMatchers.withText
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.ext.junit.rules.ActivityScenarioRule
import dev.aya.android.AyaBundledLaunchResult
import dev.aya.android.AyaCardView
import dev.aya.android.AyaComponentAction
import org.hamcrest.Matchers.containsString
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

/**
 * Real Android UI tests. Espresso observes the app's dialog windows directly:
 * Android's accessibility/window hierarchy is not a reliable source for modal
 * EditText discovery across Android emulator images and software keyboards.
 * This does not test whether an external assistant consumes a share.
 */
@RunWith(AndroidJUnit4::class)
class QuestionFlowTest {
    @get:Rule val scenario = ActivityScenarioRule(MainActivity::class.java)

    private fun submitCard() {
        scenario.scenario.onActivity {
            val card = it.findViewById<AyaCardView>(R.id.aya_sample_open_help)
                ?: throw AssertionError("Missing AYA card")
            val button = card.getChildAt(card.childCount - 1) as Button
            assertTrue("Card action should accept empty questions", button.isEnabled)
            button.performClick()
        }
    }

    @Test fun cardQuestionFeedsTheActualReviewedDocumentWithoutDuplicateComposer() {
        val question = "Why does the help attachment need a file provider?"
        scenario.scenario.onActivity {
            it.findViewById<EditText>(R.id.aya_sample_help_question).setText(question)
        }
        submitCard()
        onView(withContentDescription("Reviewed AYA help document"))
            .check(matches(withText(containsString(question))))
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
        onView(withContentDescription("Reviewed AYA help document"))
            .check(matches(withText(containsString("Help me understand and use this application."))))
        onView(withContentDescription("Your question for the assistant (optional)"))
            .check(doesNotExist())
    }

    @Test fun creativeEditorIsPromptFirstAndFullGuidePreservesEdits() {
        onView(withId(R.id.aya_sample_open_artwork)).perform(scrollTo(), click())
        onView(withContentDescription("Review the creative image request before sharing"))
            .perform(scrollTo(), click())
        onView(withContentDescription("Edit the image request before sharing"))
            .check(matches(withText(containsString("Aurora Station"))))
        val edited = "Generate a square poster with a luminous purple skyline."
        onView(withContentDescription("Edit the image request before sharing"))
            .perform(replaceText(edited))
        onView(withId(android.R.id.button3)).perform(click())
        onView(withContentDescription("Reviewed AYA creative document"))
            .check(matches(withText(containsString(edited))))
        onView(withContentDescription("Reviewed AYA creative document"))
            .check(matches(isDisplayed()))
    }

    @Test fun cancelCardReviewKeepsHostAppOpenAndDraftIntact() {
        val question = "Can I cancel before sharing?"
        scenario.scenario.onActivity {
            it.findViewById<EditText>(R.id.aya_sample_help_question).setText(question)
        }
        submitCard()
        onView(withContentDescription("Reviewed AYA help document")).check(matches(isDisplayed()))
        onView(withId(android.R.id.button2)).perform(click())
        onView(withContentDescription("Reviewed AYA help document")).check(doesNotExist())
        scenario.scenario.onActivity {
            assertFalse("Cancel must not finish the host", it.isFinishing)
            assertFalse("Cancel must not destroy the host", it.isDestroyed)
            assertTrue(it.findViewById<EditText>(R.id.aya_sample_help_question)
                .text.toString() == question)
        }
    }

    @Test fun typedComponentActionUsesVersionGuardAndOpensReviewedDocument() {
        val question = "How is this component integrated into the sample?"
        scenario.scenario.onActivity { activity ->
            val result = AyaComponentAction.Help(
                guideAsset = "aya-guide.md", screenName = "Home", askQuestion = false
            ).launch(activity, text = question)
            assertTrue("Only the local review opening can be reported",
                result is AyaBundledLaunchResult.PreviewOpened)
        }
        onView(withContentDescription("Reviewed AYA help document"))
            .check(matches(withText(containsString(question))))
        onView(withContentDescription("Your question for the assistant (optional)"))
            .check(doesNotExist())
    }

    @Test fun typedFilesystemActionRequiresRealBundledKitWithoutWeakerFallback() {
        scenario.scenario.onActivity { activity ->
            val action = AyaComponentAction.Filesystem(
                task = dev.aya.android.AyaFilesystemTask(
                    recipePurpose = "file cleanup recipe",
                    importInstructions = "Automation > Import recipe > Review"
                ),
                kitAsset = "nonexistent-filesystem-kit.md",
                guideAsset = "aya-guide.md",
                askDirection = false
            )
            val result = action.launch(activity, text = "List possible duplicate files")
            assertTrue("Missing host kit must not open review or downgrade to Help",
                result is AyaBundledLaunchResult.Rejected)
        }
        onView(withContentDescription("Reviewed AYA help document")).check(doesNotExist())
    }

    @Test fun typedComponentActionRejectsMissingBundledGuideWithoutOpeningReview() {
        scenario.scenario.onActivity { activity ->
            val result = AyaComponentAction.Help(
                guideAsset = "nonexistent-aya-guide.md", askQuestion = false
            ).launch(activity, text = "Will not be shared")
            assertTrue("Missing guide must not bypass guarded launch",
                result is AyaBundledLaunchResult.Rejected)
        }
        onView(withContentDescription("Reviewed AYA help document")).check(doesNotExist())
    }
}
