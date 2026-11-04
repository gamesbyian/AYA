package dev.aya.android

import org.json.JSONObject
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.File

/**
 * The Android runtime consumes the *same* synthetic rejection matrix as the
 * Swift and Python guard tests. Only platform identity is inverted here.
 * No host-specific app settings or paths belong in the protocol itself.
 */
class AyaReferenceCrossPlatformParityTest {
    private fun fixtureDirectory(): File {
        val relative = "integrations/apple/AYAApple/Tests/AYAProtocolTests/Fixtures"
        val root = generateSequence(File(System.getProperty("user.dir")).canonicalFile) { it.parentFile }
            .firstOrNull { File(it, "$relative/cases.json").isFile }
            ?: error("Shared source-controlled AYA-RAS fixtures are absent")
        return File(root, relative)
    }

    @Test
    fun matchesSharedSwiftAndPythonRejectionMatrix() {
        val dir = fixtureDirectory()
        val source = File(dir, "reference-ios.md").readText(Charsets.UTF_8)
        assertTrue("Original baseline must be iOS", source.contains("platform: ios"))
        val androidGuide = source.replaceFirst("platform: ios", "platform: android")
        val matrix = JSONObject(File(dir, "cases.json").readText(Charsets.UTF_8))
        assertEquals("aya-reference-parity/v1", matrix.getString("schema"))
        val appID = matrix.getString("installedAppID")
        val version = matrix.getString("installedVersion")
        val cases = matrix.getJSONArray("cases")
        assertTrue(cases.length() >= 13)
        val seen = mutableSetOf<String>()
        for (index in 0 until cases.length()) {
            val test = cases.getJSONObject(index)
            val id = test.getString("id")
            assertTrue("Duplicate case: $id", seen.add(id))
            var candidate = androidGuide
            if (id == "android-guide-on-ios") {
                // This is the shared *wrong platform* case. Swift tests an
                // Android guide on iOS; Android tests the reverse.
                candidate = candidate.replaceFirst("platform: android", "platform: ios")
            } else if (test.has("find")) {
                val find = test.getString("find").replace("platform: ios", "platform: android")
                val replace = test.getString("replace")
                val first = candidate.indexOf(find)
                assertTrue("$id: source fixture mutation missing", first >= 0)
                assertEquals("$id: mutation text is not unique", -1,
                    candidate.indexOf(find, startIndex = first + find.length))
                candidate = candidate.replaceFirst(find, replace)
            }
            val actual = AyaReferenceVerifier.verify(candidate, appID, version) is AyaReferenceCheck.Accepted
            assertEquals("$id: Android must share the native reference acceptance contract",
                test.getBoolean("runtimeAccepts"), actual)
        }
    }

    @Test
    fun rejectsOversizedUnicodeReferenceByUtf8ByteCount() {
        val guide = File(fixtureDirectory(), "reference-ios.md").readText(Charsets.UTF_8)
            .replaceFirst("platform: ios", "platform: android")
        val extraUnicode = "é".repeat(1_050_000)
        val actual = AyaReferenceVerifier.verify(
            guide + extraUnicode, "org.example.aya-lantern", "1.0.0"
        )
        assertTrue("A >2 MiB UTF-8 guide cannot reach reviewed sharing",
            actual is AyaReferenceCheck.Rejected)
    }
}
