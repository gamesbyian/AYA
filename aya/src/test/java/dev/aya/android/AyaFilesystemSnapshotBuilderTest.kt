package dev.aya.android

import org.json.JSONArray
import org.json.JSONObject
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class AyaFilesystemSnapshotBuilderTest {
    private fun input() = AyaFilesystemSnapshotInput(
        appId = "dev.example.files",
        appVersion = "1.0.0",
        generatedAtUtc = "2026-10-30T20:00:00Z",
        backend = "sftp",
        scopeRoot = "/",
        recursive = true,
        symlinks = "not_followed",
        status = AyaFilesystemScanStatus.COMPLETE,
        directoriesVisited = 2,
        filesSeen = 3,
        directoriesSeen = 2,
        matchingFilesSeen = 2,
        entries = listOf(AyaFilesystemEntry("/docs/pomegranate.txt", "file", 123))
    )

    @Test fun deterministicValidSnapshotAndNoCredentialsField() {
        val a = AyaFilesystemSnapshotBuilder.build(input())
        assertEquals(a, AyaFilesystemSnapshotBuilder.build(input()))
        val objectJson = JSONObject(a)
        assertEquals("sftp", objectJson.getJSONObject("scope").getString("backend"))
        assertEquals(1, objectJson.getJSONArray("entries").length())
        assertTrue(!objectJson.has("credentials"))
        assertEquals(AyaFilesystemSnapshotCheck.Accepted,
            AyaFilesystemSnapshotVerifier.verify(a, "dev.example.files", "1.0.0"))
    }

    @Test fun impossibleCompletenessAndSilentTruncationReject() {
        for (invalid in listOf(
            input().copy(errors = listOf(AyaFilesystemScanError("permission", "/private"))),
            input().copy(truncated = true),
            input().copy(entries = List(2501) { AyaFilesystemEntry("/file" + it, "file") })
        )) {
            try {
                AyaFilesystemSnapshotBuilder.build(invalid)
                throw AssertionError("Must reject invalid snapshot")
            } catch (_: IllegalArgumentException) { }
        }
    }

    @Test fun standaloneMalformedSnapshotCannotLieAboutCompleteness() {
        // Exercise the public verifier directly: callers need not use the builder.
        val doc = JSONObject(AyaFilesystemSnapshotBuilder.build(input()))
        val scan = doc.getJSONObject("scan")
        fun check(): AyaFilesystemSnapshotCheck = AyaFilesystemSnapshotVerifier.verify(
            doc.toString(), "dev.example.files", "1.0.0")

        scan.put("errors", JSONArray().put(JSONObject().put("kind", "permission")))
        assertTrue(check() is AyaFilesystemSnapshotCheck.Rejected)
        scan.put("status", "partial")
        assertEquals(AyaFilesystemSnapshotCheck.Accepted, check())
        scan.put("errors", JSONArray())
        scan.put("status", "complete")
        scan.put("truncated", true)
        assertTrue(check() is AyaFilesystemSnapshotCheck.Rejected)
        scan.put("truncation_reason", "listing entries omitted for privacy")
        // A complete scan and a shortened exported listing are not contradictory.
        assertEquals(AyaFilesystemSnapshotCheck.Accepted, check())
        scan.remove("errors")
        assertTrue(check() is AyaFilesystemSnapshotCheck.Rejected)
    }

    @Test fun partialScanExplicitlyRecordsErrors() {
        val doc = JSONObject(AyaFilesystemSnapshotBuilder.build(input().copy(
            status = AyaFilesystemScanStatus.PARTIAL,
            filesSeen = null,
            errors = listOf(AyaFilesystemScanError("permission", "/restricted")),
            truncated = true,
            truncationReason = "privacy summary"
        )))
        assertEquals("partial", doc.getJSONObject("scan").getString("status"))
        assertTrue(doc.getJSONObject("summary").isNull("files_seen"))
        assertEquals("privacy summary", doc.getJSONObject("scan").getString("truncation_reason"))
    }
}
