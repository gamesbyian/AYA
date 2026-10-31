package dev.aya.sample

import android.content.Intent
import android.net.Uri
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import dev.aya.android.AyaImportDecision
import dev.aya.android.AyaImportFile
import dev.aya.android.AyaImportPicker
import dev.aya.android.AyaImportRead
import dev.aya.android.AyaImportRegistry
import dev.aya.android.AyaImportRoute
import dev.aya.android.AyaImportValidation
import dev.aya.android.AyaShareTargetHints
import org.junit.Assert.*
import org.junit.Test
import org.junit.runner.RunWith

/** Independent format probes intentionally ignore the optional AYA hint. */
@RunWith(AndroidJUnit4::class)
class AyaOutputImportTest {
    private fun route(routeId: String, marker: String, valid: Boolean = true) = object : AyaImportRoute {
        override val id: String = routeId
        override val title: String = routeId
        override fun recognizes(file: AyaImportFile): Boolean =
            file.utf8Text()?.contains(marker) == true
        override fun validate(file: AyaImportFile): AyaImportValidation =
            if (valid) AyaImportValidation.Valid("Ready for preview: $routeId")
            else AyaImportValidation.Invalid("Wrong schema version")
    }

    @Test fun correctCardCanPreviewWithoutApplying() {
        val file = AyaImportFile.fromBytes("{\"kind\":\"language-pack\"}".toByteArray())
        val result = AyaImportRegistry("dev.aya.sample", listOf(route("language", "language-pack")))
            .inspect(file, "language")
        assertTrue(result is AyaImportDecision.Ready)
        assertFalse((result as AyaImportDecision.Ready).wrongCard)
        assertEquals("language", result.route.id)
    }

    @Test fun wrongCardSuggestsCorrectImporter() {
        val file = AyaImportFile.fromBytes("{\"kind\":\"language-pack\"}".toByteArray())
        val registry = AyaImportRegistry("dev.aya.sample", listOf(
            route("wallpaper", "wallpaper-recipe"),
            route("language", "language-pack")
        ))
        val result = registry.inspect(file, "wallpaper") as AyaImportDecision.Ready
        assertEquals("language", result.route.id)
        assertTrue(result.wrongCard)
    }

    @Test fun falseMetadataCannotOverrideContentValidation() {
        val file = AyaImportFile.fromBytes(
            """{"aya_artifact":"v1","target_app":"some.other.app",
               "artifact_type":"language-pack","schema_version":"4",
               "payload":{"kind":"wallpaper-recipe"}}""".toByteArray()
        )
        val registry = AyaImportRegistry("dev.aya.sample", listOf(
            route("wallpaper", "wallpaper-recipe")
        ))
        val result = registry.inspect(file, "wallpaper") as AyaImportDecision.Ready
        assertEquals("wallpaper", result.route.id)
        assertTrue(result.declaredTargetAppMismatch)
    }

    @Test fun invalidAndUnrecognizedFilesNeverBecomeReady() {
        val registry = AyaImportRegistry("dev.aya.sample", listOf(route("language", "language-pack", valid = false)))
        assertTrue(registry.inspect(AyaImportFile.fromBytes("language-pack".toByteArray())) is AyaImportDecision.Unusable)
        assertTrue(registry.inspect(AyaImportFile.fromBytes("unrelated".toByteArray())) is AyaImportDecision.Unrecognized)
    }

    @Test fun ambiguousContentRequiresExplicitChoiceAndRevalidation() {
        val routes = listOf(route("language", "shared"), route("wallpaper", "shared"))
        val file = AyaImportFile.fromBytes("shared".toByteArray())
        val registry = AyaImportRegistry("dev.aya.sample", routes)
        assertTrue(registry.inspect(file) is AyaImportDecision.Ambiguous)
        val chosen = registry.inspectAs(file, "language") as AyaImportDecision.Ready
        assertEquals("language", chosen.route.id)
        assertTrue(registry.inspectAs(file, "unknown") is AyaImportDecision.Unrecognized)
    }

    @Test fun snapshotCannotBeMutatedFromCaller() {
        val original = "language-pack".toByteArray()
        val file = AyaImportFile.fromBytes(original)
        val digest = file.sha256
        original[0] = 'x'.code.toByte()
        file.bytes()[0] = 'y'.code.toByte()
        assertEquals("language-pack", file.utf8Text())
        assertEquals(digest, file.sha256)
    }

    @Test fun pickerUsesSafAndRejectsUnselectedFilePaths() {
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        val intent = AyaImportPicker.openDocumentIntent(listOf("application/json", "text/plain"))
        assertEquals(Intent.ACTION_OPEN_DOCUMENT, intent.action)
        assertTrue(intent.hasCategory(Intent.CATEGORY_OPENABLE))
        assertEquals("*/*", intent.type)
        assertTrue(AyaImportPicker.readSelected(context, Uri.parse("file:///sdcard/Download/test.json"))
            is AyaImportRead.Rejected)
    }

    @Test fun chooserHintsAreDisabledAndClearableByDefault() {
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        AyaShareTargetHints.setEnabled(context, false)
        assertFalse(AyaShareTargetHints.isEnabled(context))
        assertNull(AyaShareTargetHints.lastChosenPackage(context))
        AyaShareTargetHints.setEnabled(context, true)
        assertTrue(AyaShareTargetHints.isEnabled(context))
        AyaShareTargetHints.clear(context)
        AyaShareTargetHints.setEnabled(context, false)
        assertNull(AyaShareTargetHints.lastChosenPackage(context))
    }
}
