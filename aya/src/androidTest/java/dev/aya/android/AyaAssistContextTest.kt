package dev.aya.android

import android.app.assist.AssistContent
import androidx.test.ext.junit.runners.AndroidJUnit4
import org.json.JSONObject
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class AyaAssistContextTest {
    @Test fun optInContextIsSchemaOrgJsonLdAndContainsNoGrantOrAttachment() {
        val target = AssistContent()
        AyaAssistContext.populate(target, AyaPublicAssistContext(
            applicationName = "AYA Sample",
            applicationVersion = "1.0.0",
            visibleTitle = "Fictional artwork selector",
            visibleDescription = "Square artwork picker"
        ))
        val json = JSONObject(target.structuredData!!)
        assertEquals("https://schema.org", json.getString("@context"))
        assertEquals("SoftwareApplication", json.getString("@type"))
        assertEquals("Fictional artwork selector", json.getJSONObject("about").getString("name"))
        assertNull(target.clipData)
        assertNull(target.webUri)
    }

    @Test fun hostTextIsJsonEscaped() {
        val value = AyaAssistContext.toJsonLd(AyaPublicAssistContext(
            "AYA Sample", "1", "Cover \"Blue\" / 🌈"
        ))
        assertEquals("Cover \"Blue\" / 🌈", JSONObject(value).getJSONObject("about").getString("name"))
    }
}
