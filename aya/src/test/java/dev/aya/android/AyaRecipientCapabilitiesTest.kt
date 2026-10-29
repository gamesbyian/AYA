package dev.aya.android

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class AyaRecipientCapabilitiesTest {
    private fun record(
        level: AyaEvidenceLevel = AyaEvidenceLevel.DEVICE_QA,
        result: AyaCapabilityResult = AyaCapabilityResult.SUPPORTED
    ) = AyaRecipientEvidence(
        packageName = "org.example.assistant",
        appVersionName = "1.2.3",
        androidSdk = 35,
        accountState = AyaAccountState.SIGNED_IN,
        transport = AyaTransport.TEXT_AND_TXT_REFERENCE,
        result = result,
        level = level,
        evidenceId = "qa-fixture-1",
        testedDateUtc = "2026-10-29"
    )

    @Test fun declaredIntentAndPublishedDocumentationCannotVerifyIngestion() {
        val registry = AyaRecipientCapabilityRegistry(listOf(
            record(AyaEvidenceLevel.DECLARED_INTENT_FILTER),
            record(AyaEvidenceLevel.PUBLISHED_DOCUMENTATION)
        ))
        assertEquals(AyaCapabilityConfidence.UNKNOWN, registry.assess(
            "org.example.assistant", "1.2.3", 35, AyaAccountState.SIGNED_IN,
            AyaTransport.TEXT_AND_TXT_REFERENCE
        ).confidence)
    }

    @Test fun matchingQaConfirmsExactlyOneTransport() {
        val registry = AyaRecipientCapabilityRegistry(listOf(record()))
        val known = registry.assess(
            "org.example.assistant", "1.2.3", 35, AyaAccountState.SIGNED_IN,
            AyaTransport.TEXT_AND_TXT_REFERENCE
        )
        assertEquals(AyaCapabilityConfidence.VERIFIED_SUPPORTED, known.confidence)
        assertEquals(listOf("qa-fixture-1"), known.evidenceIds)
        assertEquals(AyaCapabilityConfidence.UNKNOWN, registry.assess(
            "org.example.assistant", "1.2.3", 35, AyaAccountState.SIGNED_IN,
            AyaTransport.TEXT_ONLY
        ).confidence)
    }

    @Test fun differentBuildAndroidVersionAndAccountStateCannotBorrowQa() {
        val registry = AyaRecipientCapabilityRegistry(listOf(record()))
        for ((version, sdk, state) in listOf(
            Triple("1.2.4", 35, AyaAccountState.SIGNED_IN),
            Triple("1.2.3", 36, AyaAccountState.SIGNED_IN),
            Triple("1.2.3", 35, AyaAccountState.SIGNED_OUT)
        )) {
            assertEquals(AyaCapabilityConfidence.UNKNOWN, registry.assess(
                "org.example.assistant", version, sdk, state,
                AyaTransport.TEXT_AND_TXT_REFERENCE
            ).confidence)
        }
        assertEquals(AyaCapabilityConfidence.UNKNOWN, registry.assess(
            "org.example.assistant", "1.2.3", 35, null,
            AyaTransport.TEXT_AND_TXT_REFERENCE
        ).confidence)
    }

    @Test fun conflictingEndToEndEvidenceStaysUnknownForRecommendation() {
        val registry = AyaRecipientCapabilityRegistry(listOf(
            record(), record(result = AyaCapabilityResult.UNSUPPORTED).copy(evidenceId = "qa-fixture-2")
        ))
        val assessment = registry.assess(
            "org.example.assistant", "1.2.3", 35, AyaAccountState.SIGNED_IN,
            AyaTransport.TEXT_AND_TXT_REFERENCE
        )
        assertEquals(AyaCapabilityConfidence.CONFLICTING, assessment.confidence)
        assertEquals(2, assessment.evidenceIds.size)
    }

    @Test(expected = IllegalArgumentException::class)
    fun qaMustHaveUtcTestDate() { record().copy(testedDateUtc = null) }

    @Test(expected = IllegalArgumentException::class)
    fun nonPackageGarbageIsRejected() { record().copy(packageName = "https://example.org") }

    @Test fun emptyRegistryIsProviderNeutral() {
        assertTrue(AyaRecipientCapabilityRegistry(emptyList()).assess(
            "org.example.assistant", "1.2.3", 35, AyaAccountState.SIGNED_IN,
            AyaTransport.TEXT_ONLY
        ).evidenceIds.isEmpty())
    }
}
