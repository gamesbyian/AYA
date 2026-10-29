package dev.aya.sample

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
        // CLEAR_TOP + NEW_TASK returns to the test's actual home Activity,
        // clearing a previously visited artwork screen or its dialog.
        device.pressHome()
        device.executeShellCommand("am start -n dev.aya.sample/.MainActivity -f 0x14000000")
        // UiAutomator exposes contentDescription rather than displayed text for
        // these host controls: searching By.text() made every emulator test fail
        // even though the sample rendered the button correctly.
        find(By.desc("Review my question with the app reference before sharing"))
    }

    private fun find(selector: BySelector): UiObject2 =
        device.wait(Until.findObject(selector), 15000)
            ?: throw AssertionError("UI not found: $selector")

    @Test fun builtInComposerFeedsTheActualReviewedDocument() {
        val question = "Why does the help attachment need a file provider?"
        find(By.desc("Open AYA help with a version-matched reference")).click()
        find(By.desc("Your question for the assistant (optional)")).setText(question)
        // Android AlertDialog can transform or localize button labels; use stable IDs.
        find(By.res("android", "button1")).click()
        val preview = find(By.hint("Help context to share"))
        assertTrue("Approved preview must contain the typed question", preview.text.contains(question))
    }

    @Test fun hostProvidedQuestionSkipsDuplicateComposer() {
        val question = "How can I verify the share?"
        find(By.desc("Type a question in the host app")).setText(question)
        find(By.desc("Review my question with the app reference before sharing")).click()
        val preview = find(By.hint("Help context to share"))
        assertTrue("Host question must appear in review", preview.text.contains(question))
        assertFalse("Host flow must not open a second question box",
            device.hasObject(By.desc("Your question for the assistant (optional)")))
    }

    @Test fun creativeEditorIsPromptFirstAndFullGuidePreservesEdits() {
        find(By.desc("Open artwork generation demo")).click()
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
        val full = find(By.hint("Creative request to share"))
        assertTrue("Expanded reference must retain exact short prompt", full.text.contains(edited))
        assertFalse("Expanded reference must not regenerate the sample's original direction",
            full.text.contains("Atmospheric science-fiction season art"))
    }

    @Test fun cancelQuestionComposerKeepsHostAppOpen() {
        find(By.desc("Open AYA help with a version-matched reference")).click()
        find(By.desc("Your question for the assistant (optional)"))
        find(By.res("android", "button2")).click()
        // Cancellation must close the composer and leave the host Activity
        // alive. The IME can still obscure a lower button on small emulators,
        // so visibility of that button is not a reliable lifecycle assertion.
        scenario.scenario.onActivity {
            assertFalse("Cancelling AYA must not finish the host", it.isFinishing)
            assertFalse("Cancelling AYA must not destroy the host", it.isDestroyed)
        }
        assertFalse(device.hasObject(By.desc("Your question for the assistant (optional)")))
        assertFalse(device.hasObject(By.hint("Help context to share")))
    }
}
