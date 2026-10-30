package dev.aya.android

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class AyaTranslationKitTest {
    private fun kit(version: String = "1.0.0") = """
        ---
        schema_version: aya-translation-kit/v1
        app_id: dev.example.app
        app_version: $version
        catalog_revision: cat-v1
        source_revision: build-1
        source_locale: en
        owner: app team
        ---
        ## Output schema
        {"type":"object"}
        ## Source catalog
        keys from APK
        ## Rosetta and glossary
        Remove never means delete.
        ## Style and meaning constraints
        Preserve warnings.
        ## Worked examples
        Example.
        ## Agent instructions
        Return a file.
        ## Host import instructions
        Settings > Language > Add language pack.
    """.trimIndent()

    private val task = AyaTranslationTask(
        kind = AyaTranslationKind.PERSONALITY,
        target = "Pirate English",
        importInstructions = "Settings > Language > Add language pack."
    )

    @Test fun exactVersionAndRequiredSectionsAreAccepted() {
        assertEquals(AyaTranslationKitCheck.Accepted,
            AyaTranslationKitVerifier.verify(kit(), "dev.example.app", "1.0.0"))
    }

    @Test fun foreignAndStaleKitsAreRejected() {
        assertTrue(AyaTranslationKitVerifier.verify(
            kit(), "dev.other.app", "1.0.0") is AyaTranslationKitCheck.Rejected)
        assertTrue(AyaTranslationKitVerifier.verify(
            kit(), "dev.example.app", "2.0.0") is AyaTranslationKitCheck.Rejected)
    }

    @Test fun missingSectionAndDuplicateMetadataAreRejected() {
        assertTrue(AyaTranslationKitVerifier.verify(
            kit().replace("## Agent instructions", "## Unrelated"),
            "dev.example.app", "1.0.0") is AyaTranslationKitCheck.Rejected)
        assertTrue(AyaTranslationKitVerifier.verify(
            kit().replace("owner: app team", "owner: app team\nowner: another"),
            "dev.example.app", "1.0.0") is AyaTranslationKitCheck.Rejected)
    }

    @Test fun taskCannotOmitRealImportPath() {
        try {
            task.copy(importInstructions = " ")
            throw AssertionError("Blank manual import steps must reject")
        } catch (_: IllegalArgumentException) {
            // expected
        }
    }

    @Test fun createdRequestIsSelfContainedAndPreservesSafetyLanguage() {
        val request = AyaRequest(
            appName = "Example",
            appVersion = "1.0.0",
            guide = "Verified host guide",
            question = "Friendly nautical phrasing.",
            translationTask = task,
            translationKit = kit()
        )
        val payload = AyaDocument.render(request)
        val message = AyaDocument.shareMessageFromPayload(payload)
        assertTrue(message.contains("Pirate English"))
        assertTrue(message.contains("Friendly nautical phrasing"))
        assertTrue(message.contains("destructive actions"))
        assertTrue(message.contains("Add language pack"))
        assertFalse(message.contains("Verified host guide"))
        assertTrue(payload.contains("App-specific Translation Kit"))
        assertTrue(payload.contains("## Output schema"))
        assertTrue(payload.contains("Verified host guide"))
    }

    @Test fun approvedEditsReplaceTheDirectionWithoutLeakingOriginal() {
        val original = AyaDocument.render(AyaRequest(
            "Example", "1", "Guide", question = "Delete original phrase",
            translationTask = task, translationKit = kit()
        ))
        val edited = original.replace("Delete original phrase", "Keep this replacement")
        assertTrue(AyaDocument.shareMessageFromPayload(edited).contains("Keep this replacement"))
        assertFalse(AyaDocument.shareMessageFromPayload(edited).contains("Delete original phrase"))
    }

    @Test fun oldHelpHandoffIsUnchanged() {
        val output = AyaDocument.render(AyaRequest("Example", "1", "Guide", question = "Help"))
        assertEquals("Help", AyaDocument.shareMessageFromPayload(output))
        assertFalse(output.contains("App-specific Translation Kit"))
    }
}
