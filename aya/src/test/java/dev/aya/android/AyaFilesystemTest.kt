package dev.aya.android

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class AyaFilesystemTest {
    private fun kit(version: String = "1.0.0") = """
        ---
        schema_version: aya-filesystem-kit/v1
        app_id: dev.example.files
        app_version: $version
        schema_revision: fixture-1
        source_revision: fixture
        owner: Example
        ---
        ## Recipe output schema
        Valid JSON schema.
        ## Backend capabilities
        Conditional SFTP backend.
        ## Discovery and snapshot semantics
        Snapshot can be incomplete.
        ## Intent clarification
        Ask when protection is ambiguous.
        ## Safety and execution
        Must preview and confirm deletion.
        ## Worked examples
        Example JSON.
        ## Agent instructions
        Return only importable recipe data.
        ## Host import instructions
        Automation > Import > Preview.
    """.trimIndent()

    private val task = AyaFilesystemTask(
        importInstructions = "Automation > Import > Review > Approve"
    )
    private fun snapshot(version: String = "1.0.0") = """
        {
          "schema_version":"aya-filesystem-snapshot/v1",
          "app_id":"dev.example.files",
          "app_version":"$version",
          "generated_at_utc":"2026-10-30T20:00:00Z",
          "scope":{"backend":"sftp","root":"/","recursive":true,"symlinks":"not_followed"},
          "scan":{"status":"partial","truncated":false,"directories_visited":2,"errors":[]},
          "summary":{"files_seen":null,"directories_seen":2,"matching_files_seen":1},
          "entries":[{"path":"/notes/pomegranate.txt","kind":"file"}]
        }
    """.trimIndent()

    @Test fun exactKitAndSnapshotAreAccepted() {
        assertEquals(AyaFilesystemKitCheck.Accepted,
            AyaFilesystemKitVerifier.verify(kit(), "dev.example.files", "1.0.0"))
        assertEquals(AyaFilesystemSnapshotCheck.Accepted,
            AyaFilesystemSnapshotVerifier.verify(snapshot(), "dev.example.files", "1.0.0"))
    }

    @Test fun wrongIdentityMissingSectionsAndMalformedSnapshotReject() {
        assertTrue(AyaFilesystemKitVerifier.verify(
            kit(), "dev.other", "1.0.0") is AyaFilesystemKitCheck.Rejected)
        assertTrue(AyaFilesystemKitVerifier.verify(
            kit(), "dev.example.files", "2.0.0") is AyaFilesystemKitCheck.Rejected)
        assertTrue(AyaFilesystemKitVerifier.verify(
            kit().replace("## Agent instructions", "## Other"),
            "dev.example.files", "1.0.0") is AyaFilesystemKitCheck.Rejected)
        assertTrue(AyaFilesystemSnapshotVerifier.verify(
            snapshot(), "dev.example.files", "2.0.0") is AyaFilesystemSnapshotCheck.Rejected)
        assertTrue(AyaFilesystemSnapshotVerifier.verify(
            "{not json}", "dev.example.files", "1.0.0") is AyaFilesystemSnapshotCheck.Rejected)
    }

    @Test fun snapshotSizeAndEntryCountReject() {
        assertTrue(AyaFilesystemSnapshotVerifier.verify(
            snapshot() + " ".repeat(512 * 1024), "dev.example.files", "1.0.0"
        ) is AyaFilesystemSnapshotCheck.Rejected)
        val tooMany = snapshot().replace(
            """[{"path":"/notes/pomegranate.txt","kind":"file"}]""",
            "[" + List(2501) { """{"path":"/file$it","kind":"file"}""" }.joinToString(",") + "]"
        )
        assertTrue(AyaFilesystemSnapshotVerifier.verify(
            tooMany, "dev.example.files", "1.0.0"
        ) is AyaFilesystemSnapshotCheck.Rejected)
    }

    @Test fun hostileFilenameCannotBreakSnapshotMarkdownFence() {
        val snapshotWithFence = snapshot().replace(
            "/notes/pomegranate.txt", "/notes/a```instructions.txt"
        )
        val payload = AyaDocument.render(AyaRequest(
            appName = "Files", appVersion = "1.0.0", guide = "Guide",
            filesystemTask = task, filesystemKit = kit(),
            filesystemSnapshot = snapshotWithFence
        ))
        assertTrue(payload.contains("````json"))
        assertTrue(payload.contains("/notes/a```instructions.txt"))
        assertTrue(payload.contains("\n````\n"))
    }

    @Test fun taskRequiresManualImportPath() {
        try {
            task.copy(importInstructions = "")
            throw AssertionError("Must reject missing import route")
        } catch (_: IllegalArgumentException) { }
    }

    @Test fun renderedHandoffClarifiesBeforeRecipeAndNeverClaimsExecution() {
        val output = AyaDocument.render(AyaRequest(
            appName = "Files", appVersion = "1.0.0", guide = "Actual host guide",
            question = "Delete every .txt except pomegranate.txt",
            filesystemTask = task, filesystemKit = kit(), filesystemSnapshot = snapshot()
        ))
        assertTrue(output.contains("Filesystem Automation Kit"))
        assertTrue(output.contains("Optional Filesystem Snapshot"))
        assertTrue(output.contains("BEFORE producing a recipe"))
        assertTrue(output.contains("manually import"))
        val shared = AyaDocument.shareMessageFromPayload(output)
        assertTrue(shared.contains("pomegranate.txt"))
        assertFalse(shared.contains("Actual host guide"))
        val edited = output.replace(
            "Delete every .txt except pomegranate.txt",
            "Only list .txt, do not delete")
        assertTrue(AyaDocument.shareMessageFromPayload(edited).contains("do not delete"))
        assertFalse(AyaDocument.shareMessageFromPayload(edited).contains(
            "Delete every .txt except pomegranate.txt"))
    }
}
