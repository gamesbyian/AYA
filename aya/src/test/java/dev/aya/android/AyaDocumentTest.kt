package dev.aya.android

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class AyaDocumentTest {
    @Test fun hasVersionGuideAndSourceHint() {
        val result = AyaDocument.render(AyaRequest("Chunks", "0.3", "Feature X", "Settings"))
        assertTrue(result.contains("Installed version: 0.3"))
        assertTrue(result.contains("Current screen (host supplied): Settings"))
        assertTrue(result.contains("Feature X"))
        assertTrue(result.contains("Only claim that features exist").not()) // policy wording is version-aware
        assertTrue(result.contains("First check that the reference covers"))
    }

    @Test fun absentScreenOmitted() {
        val result = AyaDocument.render(AyaRequest("AYA", "1", "Guide"))
        assertFalse(result.contains("Current screen (host supplied):"))
        assertTrue(result.contains("Help me understand and use this application."))
    }

    @Test fun explicitQuestionIncluded() {
        val result = AyaDocument.render(AyaRequest("AYA", "1", "Guide", question = "Where is Export?"))
        assertTrue(result.contains("Where is Export?"))
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
