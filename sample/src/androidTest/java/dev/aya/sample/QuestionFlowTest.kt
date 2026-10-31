package dev.aya.sample

import android.widget.Button
import java.io.ByteArrayOutputStream
import android.widget.EditText
import dev.aya.android.AyaCardView
import dev.aya.android.AyaBundledLaunchResult
import dev.aya.android.AyaComponentAction
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.ext.junit.rules.ActivityScenarioRule
import androidx.test.platform.app.InstrumentationRegistry
import androidx.test.uiautomator.By
import androidx.test.uiautomator.BySelector
import androidx.test.uiautomator.UiDevice
import androidx.test.uiautomator.UiObject2
import androidx.test.uiautomator.UiScrollable
import androidx.test.uiautomator.UiSelector
import androidx.test.uiautomator.Until
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

/**
 * Real device-level tests. UI Automator does not require Espresso to own the
 * foreground window, which can be unreliable around dialogs/IME on emulators.
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

    private fun find(selector: BySelector): UiObject2 {
        val found = device.wait(Until.findObject(selector), 15000)
        if (found != null) return found
        val tree = ByteArrayOutputStream()
        val hierarchy = try {
            device.dumpWindowHierarchy(tree)
            tree.toString(Charsets.UTF_8.name()).take(10000)
        } catch (e: Exception) {
            "Hierarchy unavailable: " + e.javaClass.simpleName
        }
        throw AssertionError(
            "UI not found: $selector. Foreground package: " +
                device.currentPackageName + ". Hierarchy: " + hierarchy
        )
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
        val preview = find(By.desc("Reviewed AYA help document"))
        assertTrue("Typed action must preserve the supplied question", preview.text.contains(question))
        assertFalse("Host-provided question must not trigger duplicate entry",
            device.hasObject(By.desc("Your question for the assistant (optional)")))
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
        assertFalse("No review should be shown for a missing guide",
            device.hasObject(By.desc("Reviewed AYA help document")))
    }

    @Test fun cardQuestionFeedsTheActualReviewedDocumentWithoutDuplicateComposer() {
        val question = "Why does the help attachment need a file provider?"
        scenario.scenario.onActivity {
            it.findViewById<EditText>(R.id.aya_sample_help_question).setText(question)
        }
        submitCard()
        val preview = find(By.desc("Reviewed AYA help document"))
        assertTrue("Approved preview must contain the typed question", preview.text.contains(question))
        assertFalse("Host card must not open a duplicate composer",
            device.hasObject(By.desc("Your question for the assistant (optional)")))
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
        val preview = find(By.desc("Reviewed AYA help document"))
        assertTrue(preview.text.contains("Help me understand and use this application."))
        assertFalse(device.hasObject(By.desc("Your question for the assistant (optional)")))
    }

    @Test fun creativeEditorIsPromptFirstAndFullGuidePreservesEdits() {
        tapHost(R.id.aya_sample_open_artwork)
        val scroller = UiScrollable(UiSelector().scrollable(true))
        // On large devices this short example fits without a scrollable view;
        // scroll only when Android exposes an actual scroll container.
        if (scroller.exists()) {
            scroller.scrollIntoView(
                UiSelector().description("Review the creative image request before sharing")
            )
        }
        find(By.desc("Review the creative image request before sharing")).click()
        val shortRequest = find(By.desc("Edit the image request before sharing"))
        assertTrue(shortRequest.text.contains("Aurora Station"))
        val edited = "Generate a square poster with a luminous purple skyline."
        shortRequest.setText(edited)
        // Full guide is the neutral AlertDialog button, not the default share action.
        find(By.res("android", "button3")).click()
        val full = find(By.desc("Reviewed AYA creative document"))
        assertTrue("Expanded reference must retain exact short prompt", full.text.contains(edited))
        assertFalse("Expanded reference must not regenerate the sample's original direction",
            full.text.contains("Atmospheric science-fiction season art"))
    }

    @Test fun cancelCardReviewKeepsHostAppOpenAndDraftIntact() {
        val question = "Can I cancel before sharing?"
        scenario.scenario.onActivity {
            it.findViewById<EditText>(R.id.aya_sample_help_question).setText(question)
        }
        submitCard()
        find(By.desc("Reviewed AYA help document"))
        // The review's negative button cancels without invoking ACTION_SEND.
        find(By.res("android", "button2")).click()
        assertTrue("Cancel must close review",
            device.wait(Until.gone(By.desc("Reviewed AYA help document")), 5000))
        scenario.scenario.onActivity {
            assertFalse("Cancelling AYA must not finish the host", it.isFinishing)
            assertFalse("Cancelling AYA must not destroy the host", it.isDestroyed)
            assertTrue("The host card retains the question after cancellation",
                it.findViewById<EditText>(R.id.aya_sample_help_question).text.toString() == question)
        }
    }
}
