package dev.aya.android

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class AyaReferenceVerifierTest {
    private fun validGuide(packageId: String = "dev.aya.sample", version: String = "1.0.0"): String =
        """
        ---
        schema_version: aya-reference/v1
        app_id: $packageId
        app_name: AYA Sample
        app_version_min: $version
        app_version_max: $version
        platform: android
        locale: en
        guide_revision: 1
        source_revision: sample-v1
        last_verified_utc: 2026-10-28T00:00:00Z
        owner: AYA maintainers
        ---
        # AYA Sample
        ## Scope and version
        ## Quick orientation
        ## Navigation map
        ## Task recipes
        ## Features and settings
        ## Troubleshooting
        ## Limitations and unsupported behavior
        ## Privacy and data handling
        ## Glossary and synonyms
        ## Evidence and provenance
        ## Unknowns and escalation
        ## Assistant answer policy
        """.trimIndent()

    @Test fun acceptsExactHostPackageAndVersion() {
        val result = AyaReferenceVerifier.verify(validGuide(), "dev.aya.sample", "1.0.0")
        assertTrue(result is AyaReferenceCheck.Accepted)
        assertEquals("AYA Sample", (result as AyaReferenceCheck.Accepted).reference.appName)
    }

    @Test fun refusesAnotherPackage() {
        assertTrue(AyaReferenceVerifier.verify(validGuide(), "dev.another.app", "1.0.0")
            is AyaReferenceCheck.Rejected)
    }

    @Test fun refusesAnOldOrFutureVersion() {
        assertTrue(AyaReferenceVerifier.verify(validGuide(), "dev.aya.sample", "1.0.1")
            is AyaReferenceCheck.Rejected)
        assertTrue(AyaReferenceVerifier.verify(validGuide(), "dev.aya.sample", "0.9.0")
            is AyaReferenceCheck.Rejected)
    }

    @Test fun refusesLooseVersionRange() {
        val changed = validGuide().replace("app_version_max: 1.0.0", "app_version_max: 2.0.0")
        assertTrue(AyaReferenceVerifier.verify(changed, "dev.aya.sample", "1.0.0")
            is AyaReferenceCheck.Rejected)
    }

    @Test fun refusesDuplicateMetadata() {
        val changed = validGuide().replace("app_id: dev.aya.sample", "app_id: dev.aya.sample\napp_id: dev.aya.sample")
        assertTrue(AyaReferenceVerifier.verify(changed, "dev.aya.sample", "1.0.0")
            is AyaReferenceCheck.Rejected)
    }

    @Test fun refusesMissingSection() {
        val changed = validGuide().replace("## Troubleshooting", "## Troubleshoot")
        assertTrue(AyaReferenceVerifier.verify(changed, "dev.aya.sample", "1.0.0")
            is AyaReferenceCheck.Rejected)
    }

    @Test fun refusesUnresolvedPlaceholders() {
        val changed = validGuide().replace("owner: AYA maintainers", "owner: <owner-team>")
        assertTrue(AyaReferenceVerifier.verify(changed, "dev.aya.sample", "1.0.0")
            is AyaReferenceCheck.Rejected)
    }

    @Test fun rejectsAbsentOrBrokenFrontMatter() {
        assertTrue(AyaReferenceVerifier.verify("# hello", "dev.aya.sample", "1.0.0")
            is AyaReferenceCheck.Rejected)
        assertTrue(AyaReferenceVerifier.verify("---\napp_id: dev.aya.sample", "dev.aya.sample", "1.0.0")
            is AyaReferenceCheck.Rejected)
    }

    @Test fun localeVariantsAreHostSelectedAndNotAutoDetectedByV1() {
        // v1 requires nonblank locale provenance but has no requested-locale
        // parameter. Host code must choose the correct variant/locale asset.
        val guide = validGuide().replace("locale: en", "locale: fr-CA")
        assertTrue(AyaReferenceVerifier.verify(guide, "dev.aya.sample", "1.0.0")
            is AyaReferenceCheck.Accepted)
        val missing = guide.replace("locale: fr-CA", "locale: ")
        assertTrue(AyaReferenceVerifier.verify(missing, "dev.aya.sample", "1.0.0")
            is AyaReferenceCheck.Rejected)
        val stale = guide.replace("app_version_min: 1.0.0", "app_version_min: 1.0.1")
        assertTrue(AyaReferenceVerifier.verify(stale, "dev.aya.sample", "1.0.0")
            is AyaReferenceCheck.Rejected)
    }

    @Test fun preservesGuideUnchanged() {
        val input = validGuide()
        val result = AyaReferenceVerifier.verify(input, "dev.aya.sample", "1.0.0")
        assertEquals(input, (result as AyaReferenceCheck.Accepted).reference.guide)
    }
}
