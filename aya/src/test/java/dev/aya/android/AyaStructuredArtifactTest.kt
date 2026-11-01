package dev.aya.android

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class AyaStructuredArtifactTest {
    private fun kit(version: String = "1.0") = """
        ---
        schema_version: aya-structured-kit/v1
        app_id: dev.example.chart
        app_version: $version
        schema_revision: chart-3
        artifact_extension: .json
        artifact_mime: application/json
        source_revision: checkout-1
        owner: Example developer
        ---
        ## Artifact output contract
        Shipped importer accepts strict-root JSON, without an AYA envelope.
        ## Field semantics and bounds
        Numeric values have documented units and bounds.
        ## Interactions and precedence
        The axis mode controls conditional fields.
        ## State preservation and migration
        Preserve stable IDs; no rollback is promised.
        ## Worked valid and invalid examples
        Minimal valid and invalid JSON have been tested in the host.
        ## Agent clarification and safety
        Ask when activation semantics are unclear.
        ## Host import and recovery
        File > Import > Preview > Apply.
    """.trimIndent()
    private val task = AyaStructuredTask(
        artifactRole = "chart configuration",
        fileExtension = ".json",
        mimeType = "application/json",
        schemaVersion = "chart-3",
        importInstructions = "File > Import > Preview > Apply"
    )

    @Test fun exactInstalledAppKitPasses() {
        assertEquals(AyaStructuredKitCheck.Accepted,
            AyaStructuredKitVerifier.verify(kit(), "dev.example.chart", "1.0", task))
    }

    @Test fun staleForeignMissingDuplicateAndOversizedKitsFailClosed() {
        val examples = listOf(
            kit() to ("dev.other.app" to "1.0"),
            kit() to ("dev.example.chart" to "2.0"),
            kit().replace("## Interactions and precedence", "## Other") to
                ("dev.example.chart" to "1.0"),
            kit().replace("owner: Example developer", "owner: X\nowner: Y") to
                ("dev.example.chart" to "1.0"),
            kit().replace("schema_revision: chart-3", "schema_revision: <TODO>") to
                ("dev.example.chart" to "1.0"),
            (kit() + "x".repeat(1024 * 1024)) to ("dev.example.chart" to "1.0")
        )
        examples.forEach { (value, identity) ->
            assertTrue(AyaStructuredKitVerifier.verify(value, identity.first, identity.second, task)
                is AyaStructuredKitCheck.Rejected)
        }
    }

    @Test fun kitAndDeclaredTaskMustAgreeOnActualImporterContract() {
        assertTrue(AyaStructuredKitVerifier.verify(
            kit().replace("artifact_extension: .json", "artifact_extension: .svg"),
            "dev.example.chart", "1.0", task) is AyaStructuredKitCheck.Rejected)
        assertTrue(AyaStructuredKitVerifier.verify(
            kit(), "dev.example.chart", "1.0",
            task.copy(schemaVersion = "chart-4")) is AyaStructuredKitCheck.Rejected)
        assertTrue(AyaStructuredKitVerifier.verify(
            kit(), "dev.example.chart", "1.0",
            task.copy(mimeType = "application/xml")) is AyaStructuredKitCheck.Rejected)
    }

    @Test fun emptySectionIsRejectedRatherThanSentToAssistant() {
        val empty = kit().replace(
            "## Field semantics and bounds\nNumeric values have documented units and bounds.",
            "## Field semantics and bounds\n        "
        )
        assertTrue(AyaStructuredKitVerifier.verify(
            empty, "dev.example.chart", "1.0", task
        ) is AyaStructuredKitCheck.Rejected)
        val headingOnly = kit().replace(
            "## Host import and recovery\nFile > Import > Preview > Apply.",
            "## Host import and recovery\n        "
        )
        assertTrue(AyaStructuredKitVerifier.verify(
            headingOnly, "dev.example.chart", "1.0", task
        ) is AyaStructuredKitCheck.Rejected)
    }

    @Test fun taskRejectsFakeOrUnsafeFileContract() {
        for (badExtension in listOf("", "../json", ".JSON", ".a/b", ".zip\n")) {
            try {
                task.copy(fileExtension = badExtension)
                throw AssertionError("Should reject extension: " + badExtension)
            } catch (_: IllegalArgumentException) { }
        }
        try {
            task.copy(mimeType = "invalid mime")
            throw AssertionError("Must reject invalid MIME")
        } catch (_: IllegalArgumentException) { }
        try {
            task.copy(importInstructions = "")
            throw AssertionError("Must require a real host importer")
        } catch (_: IllegalArgumentException) { }
    }

    @Test fun renderedPromptPreservesExactHostContractAndUserEdits() {
        val output = AyaDocument.render(AyaRequest(
            appName = "Example", appVersion = "1.0", guide = "Verified application guide",
            question = "Create a categorical horizontal chart",
            structuredTask = task, structuredKit = kit()
        ))
        assertTrue(output.contains("App-specific Structured Artifact Kit"))
        assertTrue(output.contains("schema/version chart-3"))
        assertTrue(output.contains("The host reports its importer expects"))
        assertFalse(output.contains("The verified host importer"))
        assertTrue(output.contains("without adding an AYA wrapper"))
        assertTrue(output.contains("File > Import > Preview > Apply"))
        assertTrue(output.contains("## Interactions and precedence"))
        val edited = output.replace("categorical horizontal", "stacked vertical")
        val message = AyaDocument.shareMessageFromPayload(edited)
        assertTrue(message.contains("stacked vertical"))
        assertFalse(message.contains("categorical horizontal"))
        assertFalse(message.contains("Verified application guide"))
    }

    @Test fun modelIsHostNeutralAcrossUnrelatedArtifactRoles() {
        val scene = task.copy(
            artifactRole = "scene layout",
            fileExtension = ".scene",
            mimeType = "application/x-scene",
            schemaVersion = "scene-2",
            importInstructions = "Scene > Import > Confirm"
        )
        val result = AyaStructuredDocument.prompt(scene, "Arrange three nodes")
        assertTrue(result.contains("scene layout"))
        assertTrue(result.contains("Scene > Import > Confirm"))
        assertFalse(result.contains("chart configuration"))
        assertFalse(AyaDocument.render(AyaRequest(
            appName = "Example", appVersion = "1", guide = "Guide",
            question = "Help"
        )).contains("Structured Artifact Kit"))
    }
}
