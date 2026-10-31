package dev.aya.android

import org.json.JSONArray
import org.json.JSONObject

/** These entries are supplied by the host from its own authorized listing. */
data class AyaFilesystemEntry(
    val path: String,
    val kind: String,
    val sizeBytes: Long? = null,
    val reasonIncluded: String? = null
)

data class AyaFilesystemScanError(
    val kind: String,
    val path: String? = null,
    val detail: String? = null
)

enum class AyaFilesystemScanStatus(val wireValue: String) {
    COMPLETE("complete"), PARTIAL("partial"), FAILED("failed")
}

/**
 * Serializable, non-authoritative inventory prepared entirely by the host.
 * The host must separately scan, sanitize and obtain explicit disclosure consent.
 */
data class AyaFilesystemSnapshotInput(
    val appId: String,
    val appVersion: String,
    val generatedAtUtc: String,
    val backend: String,
    val scopeRoot: String,
    val recursive: Boolean,
    val symlinks: String,
    val status: AyaFilesystemScanStatus,
    val directoriesVisited: Int,
    val filesSeen: Long?,
    val directoriesSeen: Long?,
    val matchingFilesSeen: Long?,
    val entries: List<AyaFilesystemEntry>,
    val errors: List<AyaFilesystemScanError> = emptyList(),
    val truncated: Boolean = false,
    val truncationReason: String? = null,
    val redacted: Boolean = false,
    val omittedSensitivePaths: Boolean = false
)

/**
 * Builds a deterministic standard summary from *host-provided metadata* only.
 * No IO, network access, directory traversal, secret detection or background work.
 * Invalid/oversized data fails closed instead of silently dropping entries.
 */
object AyaFilesystemSnapshotBuilder {
    private val backends = setOf("local", "ftp", "ftps", "sftp", "saf", "webdav", "smb", "cloud", "other")
    private val symlinkModes = setOf("not_followed", "followed_within_scope", "unsupported", "unknown")
    private val kinds = setOf("file", "directory", "symlink", "unknown")
    private val errorKinds = setOf("permission", "timeout", "listing", "loop", "unsupported", "other")

    fun build(input: AyaFilesystemSnapshotInput): String {
        require(input.appId.isNotBlank() && input.appVersion.isNotBlank()) { "App identity required" }
        require(input.backend in backends) { "Unknown backend" }
        require(input.scopeRoot.isNotBlank()) { "Scope required" }
        require(input.symlinks in symlinkModes) { "Invalid symlink policy" }
        require(input.directoriesVisited >= 0) { "Negative directory count" }
        require(listOfNotNull(input.filesSeen, input.directoriesSeen, input.matchingFilesSeen)
            .all { it >= 0 }) { "Negative file count" }
        require(input.status != AyaFilesystemScanStatus.COMPLETE || input.errors.isEmpty()) {
            "Cannot report a complete scan with errors"
        }
        require(!input.truncated || !input.truncationReason.isNullOrBlank()) {
            "Disclose why a listing was truncated"
        }
        require(input.entries.size <= 2500) { "Too many snapshot entries; use a summary" }
        for (entry in input.entries) {
            require(entry.path.isNotBlank() && entry.kind in kinds) { "Invalid entry" }
            require(entry.sizeBytes == null || entry.sizeBytes >= 0) { "Negative file size" }
        }
        for (error in input.errors) require(error.kind in errorKinds) { "Unknown scan error" }
        fun nullableCount(count: Long?): Any = count ?: JSONObject.NULL
        val document = JSONObject()
            .put("schema_version", "aya-filesystem-snapshot/v1")
            .put("app_id", input.appId)
            .put("app_version", input.appVersion)
            .put("generated_at_utc", input.generatedAtUtc)
            .put("scope", JSONObject()
                .put("backend", input.backend)
                .put("root", input.scopeRoot)
                .put("recursive", input.recursive)
                .put("symlinks", input.symlinks))
            .put("scan", JSONObject()
                .put("status", input.status.wireValue)
                .put("truncated", input.truncated)
                .put("directories_visited", input.directoriesVisited)
                .put("errors", JSONArray().apply {
                    input.errors.forEach { err ->
                        put(JSONObject().put("kind", err.kind).apply {
                            err.path?.let { put("path", it) }
                            err.detail?.let { put("detail", it) }
                        })
                    }
                }).apply {
                    input.truncationReason?.let { put("truncation_reason", it) }
                })
            .put("summary", JSONObject()
                .put("files_seen", nullableCount(input.filesSeen))
                .put("directories_seen", nullableCount(input.directoriesSeen))
                .put("matching_files_seen", nullableCount(input.matchingFilesSeen)))
            .put("entries", JSONArray().apply {
                input.entries.forEach { entry ->
                    put(JSONObject().put("path", entry.path).put("kind", entry.kind).apply {
                        entry.sizeBytes?.let { put("size_bytes", it) }
                        entry.reasonIncluded?.let { put("reason_included", it) }
                    })
                }
            })
            .put("disclosure", JSONObject()
                .put("redacted", input.redacted)
                .put("omitted_sensitive_paths", input.omittedSensitivePaths)
                .put("summary_only", input.entries.isEmpty()))
        val result = document.toString()
        require(result.toByteArray(Charsets.UTF_8).size <= 512 * 1024) {
            "Snapshot too large; explicitly summarize or redact before retrying"
        }
        when (val verdict = AyaFilesystemSnapshotVerifier.verify(
            result, input.appId, input.appVersion
        )) {
            is AyaFilesystemSnapshotCheck.Rejected -> throw IllegalArgumentException(verdict.reason)
            AyaFilesystemSnapshotCheck.Accepted -> return result
        }
    }
}
