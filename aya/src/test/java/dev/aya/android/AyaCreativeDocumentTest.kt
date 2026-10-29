package dev.aya.android

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class AyaCreativeDocumentTest {
    private val task = AyaCreativeTask(
        subject = "House, M.D., Season 4",
        assetRole = "Square season key art",
        image = AyaImageRequirements(
            aspectWidth = 1,
            aspectHeight = 1,
            preferredWidthPx = 2000,
            preferredHeightPx = 2000,
            acceptedMimeTypes = listOf("image/png", "image/jpeg"),
            safeMarginPercent = 8
        ),
        importInstructions = "Choose artwork > Import from device."
    )

    @Test fun imageRequestIsSelfContainedWhenTextOnlyRecipientIgnoresAttachment() {
        val payload = AyaDocument.render(AyaRequest(
            "Chunks", "1.0", "Reference", "Artwork picker",
            "Blue hospital lighting, minimal lettering.", task
        ))
        val text = AyaDocument.shareMessageFromPayload(payload)
        assertTrue(text.contains("Please generate an actual image"))
        assertTrue(text.contains("House, M.D., Season 4"))
        assertTrue(text.contains("Blue hospital lighting"))
        assertTrue(text.contains("1:1"))
        assertTrue(text.contains("2000 × 2000"))
        assertTrue(text.contains("image/png"))
        assertTrue(text.contains("at least 8% away from every edge"))
        assertTrue(text.contains("Import from device"))
        assertFalse(text.contains("Reference"))
        assertTrue(payload.contains("## App-specific reference"))
    }

    @Test fun blankDirectionStillRequestsGeneration() {
        val payload = AyaDocument.render(AyaRequest(
            "App", "1", "Guide", creativeTask = task
        ))
        assertTrue(AyaDocument.shareMessageFromPayload(payload).contains(
            "Choose an appropriate design"
        ))
        assertFalse(AyaDocument.shareMessageFromPayload(payload).contains(
            "Help me understand and use"
        ))
    }

    @Test fun finalReviewChangesAreUsedAndDeletedTextIsNeverReinstated() {
        val original = AyaDocument.render(AyaRequest(
            "App", "1", "Guide", question = "Secret direction", creativeTask = task
        ))
        val edited = original.replace("Secret direction", "Clean typography")
        assertTrue(AyaDocument.shareMessageFromPayload(edited).contains("Clean typography"))
        assertFalse(AyaDocument.shareMessageFromPayload(edited).contains("Secret direction"))
        val removed = edited.replace("## User's starting question", "## User request deleted")
        assertFalse(AyaDocument.shareMessageFromPayload(removed).contains("Secret direction"))
    }

    @Test fun multilineDirectionAndUnicodeSurvive() {
        val payload = AyaDocument.render(AyaRequest(
            "App", "1", "Guide", question = "Moody\n## Blues\nAurora 🌈", creativeTask = task
        ))
        assertTrue(AyaDocument.shareMessageFromPayload(payload).contains("Aurora 🌈"))
    }

    @Test fun optionalDimensionsKeepAspectWithoutInventingPixels() {
        val spec = AyaImageRequirements(16, 9, acceptedMimeTypes = listOf("image/webp"))
        assertTrue(spec.describe().contains("16:9"))
        assertFalse(spec.describe().contains("resolution:"))
    }

    @Test(expected = IllegalArgumentException::class)
    fun mismatchedDimensionsRejected() {
        AyaImageRequirements(1, 1, 1024, 768)
    }

    @Test(expected = IllegalArgumentException::class)
    fun unsupportedFormatRejected() {
        AyaImageRequirements(1, 1, acceptedMimeTypes = listOf("application/pdf"))
    }

    @Test(expected = IllegalArgumentException::class)
    fun missingImportWorkflowRejected() {
        task.copy(importInstructions = " ")
    }

    @Test fun approvedPromptCanBeSharedWithoutTheGuide() {
        val payload = AyaDocument.render(AyaRequest(
            "Host", "1", "Secret unrelated guide content", creativeTask = task,
            question = "Bold red and blue."
        ))
        val text = AyaDocument.textOnlyMessageFromPayload(payload)!!
        assertTrue(text.contains("Bold red and blue."))
        assertTrue(text.contains("House, M.D."))
        assertFalse(text.contains("Secret unrelated guide content"))
    }

    @Test fun textOnlyUsesEditedPromptNeverOriginalDirection() {
        val initial = AyaDocument.render(AyaRequest(
            "Host", "1", "Guide", creativeTask = task,
            question = "Remove this detail"
        ))
        val edited = initial.replace("Remove this detail", "Use a subtle gradient")
        assertTrue(AyaDocument.textOnlyMessageFromPayload(edited)!!.contains("Use a subtle gradient"))
        assertFalse(AyaDocument.textOnlyMessageFromPayload(edited)!!.contains("Remove this detail"))
    }

    @Test fun textOnlyRefusesLongPromptRatherThanOfferingInvalidAttachmentHint() {
        val payload = AyaDocument.render(AyaRequest(
            "Host", "1", "Guide", creativeTask = task,
            question = "x".repeat(4100)
        ))
        assertEquals(null, AyaDocument.textOnlyMessageFromPayload(payload))
        assertEquals(
            "My full question is in the attached AYA help document.",
            AyaDocument.shareMessageFromPayload(payload)
        )
    }

    @Test fun fullyRewrittenApprovedTextMayBeSharedDirectly() {
        assertEquals("Make a purple cover.", AyaDocument.textOnlyMessageFromPayload("Make a purple cover."))
    }

    @Test fun ordinaryHelpRemainsUnchanged() {
        val payload = AyaDocument.render(AyaRequest("App", "1", "Guide", question = "Help"))
        assertEquals("Help", AyaDocument.shareMessageFromPayload(payload))
        assertFalse(payload.contains("Please generate an actual image"))
    }
}
