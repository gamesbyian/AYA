package dev.aya.android

/**
 * Local, read-only developer QA evidence about Android recipient behavior.
 *
 * An Android intent filter, marketing claim or generic model capability is
 * NEVER proof that a receiver ingests a specific AYA handoff. No package scan,
 * provider account access, feedback collection or user-session tracking occurs.
 */
enum class AyaTransport {
    TEXT_ONLY,
    TEXT_AND_TXT_REFERENCE,
    TXT_REFERENCE_ONLY,
    IMAGE_ATTACHMENT,
    MULTIPLE_ATTACHMENTS,
    PROCESS_TEXT
}

enum class AyaAccountState { SIGNED_IN, SIGNED_OUT, NOT_APPLICABLE }

/** Differentiate affordance/claim from observed end-to-end receiving behavior. */
enum class AyaEvidenceLevel {
    DECLARED_INTENT_FILTER,
    PUBLISHED_DOCUMENTATION,
    DEVICE_QA
}

enum class AyaCapabilityResult { SUPPORTED, UNSUPPORTED }

data class AyaRecipientEvidence(
    val packageName: String,
    val appVersionName: String,
    val androidSdk: Int,
    val accountState: AyaAccountState,
    val transport: AyaTransport,
    val result: AyaCapabilityResult,
    val level: AyaEvidenceLevel,
    val evidenceId: String,
    val testedDateUtc: String? = null
) {
    init {
        require(packageName.matches(Regex("[A-Za-z][A-Za-z0-9_]*(\\.[A-Za-z][A-Za-z0-9_]*)+"))) {
            "An exact Android package name is required"
        }
        require(appVersionName.isNotBlank() && appVersionName.length <= 100)
        require(androidSdk in 23..100)
        require(evidenceId.isNotBlank() && evidenceId.length <= 240)
        if (level == AyaEvidenceLevel.DEVICE_QA) {
            require(testedDateUtc != null &&
                testedDateUtc.matches(Regex("\\d{4}-\\d{2}-\\d{2}"))) {
                "Device QA evidence requires a date in UTC YYYY-MM-DD"
            }
        }
    }
}

enum class AyaCapabilityConfidence {
    /** No exact version/Android/account-state QA record supports a claim. */
    UNKNOWN,
    /** One or more matching device QA records independently confirm success. */
    VERIFIED_SUPPORTED,
    /** Device QA reproduced unsupported behavior for this exact environment. */
    VERIFIED_UNSUPPORTED,
    /** Contradictory QA observations; do not rank or automate. */
    CONFLICTING
}

data class AyaRecipientAssessment(
    val confidence: AyaCapabilityConfidence,
    val evidenceIds: List<String>
)

/**
 * Registry entries are host- or maintainer-supplied research fixtures, not
 * dynamically learned from users. They can assist a user-visible choice, but
 * must not filter other apps, force a target, or initiate a conversation.
 *
 * No evidence is bundled for ChatGPT, Claude, Gemini, Grok or local LLMs
 * without reproducible version-specific Android tests.
 */
class AyaRecipientCapabilityRegistry(records: List<AyaRecipientEvidence>) {
    private val observations = records.toList()

    fun assess(
        packageName: String,
        appVersionName: String,
        androidSdk: Int,
        accountState: AyaAccountState?,
        transport: AyaTransport
    ): AyaRecipientAssessment {
        // Unknown account state is not a wildcard for signed-in QA evidence.
        if (accountState == null) {
            return AyaRecipientAssessment(AyaCapabilityConfidence.UNKNOWN, emptyList())
        }
        val matched = observations.filter {
            it.level == AyaEvidenceLevel.DEVICE_QA &&
                it.packageName == packageName &&
                it.appVersionName == appVersionName &&
                it.androidSdk == androidSdk &&
                it.accountState == accountState &&
                it.transport == transport
        }
        val ids = matched.map { it.evidenceId }.distinct().sorted()
        val supports = matched.any { it.result == AyaCapabilityResult.SUPPORTED }
        val rejects = matched.any { it.result == AyaCapabilityResult.UNSUPPORTED }
        val confidence = when {
            supports && rejects -> AyaCapabilityConfidence.CONFLICTING
            supports -> AyaCapabilityConfidence.VERIFIED_SUPPORTED
            rejects -> AyaCapabilityConfidence.VERIFIED_UNSUPPORTED
            else -> AyaCapabilityConfidence.UNKNOWN
        }
        return AyaRecipientAssessment(confidence, ids)
    }
}
