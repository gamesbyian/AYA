package dev.aya.sample

import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performClick
import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.action.ViewActions.click
import androidx.test.espresso.action.ViewActions.closeSoftKeyboard
import androidx.test.espresso.action.ViewActions.replaceText
import androidx.test.espresso.assertion.ViewAssertions.matches
import androidx.test.espresso.matcher.ViewMatchers.withContentDescription
import androidx.test.espresso.matcher.ViewMatchers.withText
import org.hamcrest.Matchers.containsString
import org.junit.Rule
import org.junit.Test

/** Runtime use of the Compose adapter against the installed demo reference. */
class ComposeDropInTest {
    @get:Rule val rule = createAndroidComposeRule<ComposeDemoActivity>()

    @Test fun embeddedCardPassesEditedQuestionToGuardedReview() {
        val question = "Is the Compose card using the installed-version guard?"
        onView(withContentDescription("Question for your agent, optional"))
            .perform(replaceText(question), closeSoftKeyboard())
        onView(withContentDescription("Review your question and app reference before sharing"))
            .perform(click())
        onView(withContentDescription("Reviewed AYA help document"))
            .check(matches(withText(containsString(question))))
    }

    @Test fun existingComposeButtonUsesTypedLauncher() {
        rule.onNodeWithText("Ask from existing Compose button").performClick()
        onView(withContentDescription("Reviewed AYA help document"))
            .check(matches(withText(containsString("How does the Compose action open AYA review?"))))
    }

    @Test fun unsentDraftSurvivesActivityRecreation() {
        val question = "Keep this unsent draft across Activity recreation."
        onView(withContentDescription("Question for your agent, optional"))
            .perform(replaceText(question), closeSoftKeyboard())
        rule.activityRule.scenario.recreate()
        onView(withContentDescription("Question for your agent, optional"))
            .check(matches(withText(question)))
    }
}
