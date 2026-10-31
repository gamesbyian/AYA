package dev.aya.android

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class AyaDocumentTest {
    @Test fun hasVersionGuideAndSourceHint() {
        val result = AyaDocument.render(AyaRequest("ExampleHost", "0.3", "Feature X", "Settings"))
        assertTrue(result.contains("Installed version: 0.3"))
        assertTrue(result.contains("Current screen (host supplied): Settings"))
        assertTrue(result.contains("Feature X"))
        assertTrue(result.contains("First check that the reference covers"))
    }

    @Test fun absentScreenOmitted() {
        val result = AyaDocument.render(AyaRequest("AYA", "1", "Guide"))
        assertFalse(result.contains("Current screen (host supplied):"))
        assertTrue(result.contains("Help me understand and use this application."))
    }

    @Test fun explicitQuestionIncludedInAttachmentAndExtractedText() {
        val question = "Where is Export?"
        val result = AyaDocument.render(AyaRequest("AYA", "1", "Guide", question = question))
        assertTrue(result.contains(question))
        assertEquals(question, AyaDocument.shareMessageFromPayload(result))
    }

    @Test fun questionCanBeMultilineAndRetainsNewlines() {
        val question = "Why did it fail?\nI was using remote mode."
        val result = AyaDocument.render(AyaRequest("AYA", "1", "Guide", question = question))
        assertEquals(question, AyaDocument.shareMessageFromPayload(result))
    }

    @Test fun headingsInsideMultilineQuestionSurviveMessageExtraction() {
        val question = "Why does sync stop?\n## Observations\nI tried Wi-Fi and mobile data.\n### Details\nIt says timeout."
        val result = AyaDocument.render(AyaRequest("AYA", "1", "Guide", question = question))
        assertEquals(question, AyaDocument.shareMessageFromPayload(result))
    }

    @Test fun finalReviewEditsControlExtraTextNotOriginalQuestion() {
        val initial = AyaDocument.render(AyaRequest("AYA", "1", "Guide", question = "Secret example removed"))
        val edited = initial.replace("Secret example removed", "How do I import?")
        assertEquals("How do I import?", AyaDocument.shareMessageFromPayload(edited))
        assertFalse(AyaDocument.shareMessageFromPayload(edited).contains("Secret example removed"))
    }

    @Test fun removingQuestionHeadingNeverRestoresThePriorQuestion() {
        val initial = AyaDocument.render(AyaRequest("AYA", "1", "Guide", question = "old question"))
        val edited = initial.replace("## User's starting question\nold question\n", "")
        assertFalse(AyaDocument.shareMessageFromPayload(edited).contains("old question"))
    }

    @Test fun longQuestionStaysInDocumentButUsesAttachmentMessage() {
        val question = "x".repeat(4200)
        val result = AyaDocument.render(AyaRequest("AYA", "1", "Guide", question = question))
        assertTrue(result.contains(question))
        assertEquals(
            "My full question is in the attached AYA help document.",
            AyaDocument.shareMessageFromPayload(result)
        )
    }

    @Test fun nullCharacterRemoved() {
        val result = AyaDocument.render(AyaRequest("AYA", "1", "Gu\u0000ide"))
        assertTrue(result.contains("Guide"))
        assertFalse(result.contains("\u0000"))
    }

    @Test(expected = IllegalArgumentException::class)
    fun rejectsEmptyGuide() { AyaDocument.render(AyaRequest("AYA", "1", " ")) }

    @Test(expected = IllegalArgumentException::class)
    fun rejectsEmptyVersion() { AyaDocument.render(AyaRequest("AYA", " ", "Guide")) }
}
