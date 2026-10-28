package dev.aya.sample

import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.ext.junit.rules.ActivityScenarioRule
import androidx.test.platform.app.InstrumentationRegistry
import androidx.test.uiautomator.By
import androidx.test.uiautomator.BySelector
import androidx.test.uiautomator.UiDevice
import androidx.test.uiautomator.UiObject2
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
        // Reuse the Activity when possible while bringing it to the foreground.
        device.executeShellCommand("am start -n dev.aya.sample/.MainActivity -f 0x24000000")
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
        find(By.text("Review details")).click()
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

    @Test fun cancelQuestionComposerKeepsHostAppOpen() {
        find(By.desc("Open AYA help with a version-matched reference")).click()
        find(By.desc("Your question for the assistant (optional)"))
        find(By.text("Cancel")).click()
        find(By.desc("Review my question with the app reference before sharing"))
        assertFalse(device.hasObject(By.hint("Help context to share")))
    }
}
