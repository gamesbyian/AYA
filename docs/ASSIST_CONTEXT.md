# Optional Android system-assistant context adapter

**Implementation:** `AyaPublicAssistContext` + `AyaAssistContext.toJsonLd()/populate()` in the AYA Android library, with Android instrumentation tests. **Disabled unless a host app explicitly invokes it**. The sample does not enable it by default.

Android API 23+ can invoke a foreground Activity's `onProvideAssistContent(outContent)` at the system's discretion when the user requests an assistant. `AssistContent.setStructuredData()` accepts **schema.org JSON-LD**, not arbitrary AYA request JSON. Source: [Android AssistContent reference](https://developer.android.com/reference/android/app/assist/AssistContent) and [Activity assistant context](https://developer.android.com/reference/android/app/Activity#onProvideAssistContent(android.app.assist.AssistContent)).

A host can opt in with publicly shareable screen labels only:

```kotlin
override fun onProvideAssistContent(outContent: AssistContent) {
    super.onProvideAssistContent(outContent)
    AyaAssistContext.populate(
        outContent,
        AyaPublicAssistContext(
            applicationName = "My App",
            applicationVersion = "1.0.0",
            visibleTitle = "Artwork picker",
            visibleDescription = "Square poster artwork can be imported as PNG or JPEG"
        )
    )
}
```

This constructs schema.org `SoftwareApplication` with `name`, `softwareVersion`, and a `Thing` in `about`. It intentionally does not publish file paths, media IDs, the actual artwork, screen captures, credentials, accounts, `ClipData`, share URI permissions or a return channel. Text is length-bounded and JSON-escaped; output is limited to 2048 UTF-8 bytes. Only the host knows whether a given item title is private, so the host must consciously choose public text, or **not call this adapter** on sensitive screens.

This is a **separate context surface** from a user pressing AYA's “Ask your agent” button. The standard AYA editable disclosure preview does not control Android's assistant-context request; the host must make an independent privacy decision. The system and chosen assistant determine whether context is requested and consumed. The adapter neither invokes the assistant nor detects whether it used the information.

Do **not** automatically attach the full AYA-RAS guide to AssistContent, use `setClipData()` for private files, create a non-public deep link, or turn this into a hidden content export. Real-system-assistant efficacy and privacy acceptance require device QA before a production host enables it.
