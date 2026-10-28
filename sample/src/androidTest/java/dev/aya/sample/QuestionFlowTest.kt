package dev.aya.sample

import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.ext.junit.rules.ActivityScenarioRule
import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.Espresso.pressBack
import androidx.test.espresso.action.ViewActions.click
import androidx.test.espresso.action.ViewActions.closeSoftKeyboard
import androidx.test.espresso.action.ViewActions.replaceText
import androidx.test.espresso.assertion.ViewAssertions.matches
import androidx.test.espresso.assertion.ViewAssertions.doesNotExist
import androidx.test.espresso.matcher.ViewMatchers.isDisplayed
import androidx.test.espresso.matcher.ViewMatchers.withHint
import androidx.test.espresso.matcher.ViewMatchers.withText
import org.hamcrest.Matchers.containsString
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

/** Exercises genuine question entry inside the host application. */
@RunWith(AndroidJUnit4::class)
class QuestionFlowTest {
    @get:Rule
    val scenario = ActivityScenarioRule(MainActivity::class.java)

    @Test fun builtInComposerFeedsTheActualReviewedDocument() {
        val question = "Why does the help attachment need a file provider?"
        onView(withText("Ask your agent")).perform(click())
        onView(withHint("e.g. Why won't this connection work?"))
            .perform(replaceText(question), closeSoftKeyboard())
        onView(withText("Review details")).perform(click())
        onView(withHint("Help context to share"))
            .check(matches(withText(containsString(question))))
    }

    @Test fun hostProvidedQuestionSkipsDuplicateComposer() {
        val question = "How can I verify the share?"
        onView(withHint("Or type your question here"))
            .perform(replaceText(question), closeSoftKeyboard())
        onView(withText("Ask using my question")).perform(click())
        onView(withHint("Help context to share"))
            .check(matches(withText(containsString(question))))
        onView(withHint("e.g. Why won't this connection work?")).check(doesNotExist())
    }

    @Test fun cancelQuestionComposerKeepsHostAppOpen() {
        onView(withText("Ask your agent")).perform(click())
        onView(withHint("e.g. Why won't this connection work?"))
            .check(matches(isDisplayed()))
        pressBack()
        onView(withText("Ask using my question")).check(matches(isDisplayed()))
        onView(withHint("Help context to share")).check(doesNotExist())
    }
}
