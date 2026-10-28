package dev.aya.android

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class AyaDocumentTest {
    @Test fun hasVersionAndGuide() {
        val result = AyaDocument.render(AyaRequest("Chunks", "0.3", "Feature X", "Settings"))
        assertTrue(result.contains("Installed version: 0.3"))
        assertTrue(result.contains("Current screen: Settings"))
        assertTrue(result.contains("Feature X"))
    }
    @Test fun absentScreenOmitted() {
        assertFalse(AyaDocument.render(AyaRequest("AYA", "1", "Guide")).contains("Current screen:"))
    }
    @Test(expected = IllegalArgumentException::class)
    fun rejectsEmptyGuide() { AyaDocument.render(AyaRequest("AYA", "1", " ")) }
}
