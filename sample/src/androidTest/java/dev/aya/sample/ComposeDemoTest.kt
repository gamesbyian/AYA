package dev.aya.sample

import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.assertion.ViewAssertions.matches
import androidx.test.espresso.action.ViewActions.click
import androidx.test.espresso.action.ViewActions.replaceText
import androidx.test.espresso.matcher.ViewMatchers.withContentDescription
import androidx.test.espresso.matcher.ViewMatchers.withText
import androidx.test.ext.junit.rules.ActivityScenarioRule
import androidx.test.ext.junit.runners.AndroidJUnit4
import org.hamcrest.Matchers.containsString
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

/** Native View inside Compose must still enforce the usual guarded review. */
@RunWith(AndroidJUnit4::class)
class ComposeDemoTest {
    @get:Rule val scenario = ActivityScenarioRule(ComposeDemoActivity::class.java)

    @Test fun compactComposeCardOpensEditableReviewedHelp() {
        val question = "Can my Compose card share this guide without my approval?"
        onView(withContentDescription("Question for your agent, optional"))
            .perform(replaceText(question))
        onView(withContentDescription("Review your question and app reference before sharing"))
            .perform(click())
        onView(withContentDescription("Reviewed AYA help document"))
            .check(matches(withText(containsString(question))))
    }
}
