# Integrating AYA

1. Include the `:aya` Android library and AndroidX Core dependency. The library's merged manifest declares a non-exported FileProvider with authority `${applicationId}.aya.files` and maps `cacheDir/aya/`. Avoid duplicate provider declarations.
2. Create the **version-matched static reference guide** using [AYA Reference Authoring Standard](reference/AUTHORING_STANDARD.md). Fill the [template](reference/TEMPLATE.md), perform coverage and evidence review, then run `python3 tools/validate_guide.py guide.md`.
3. Bundle the completed Markdown file as an APK asset. The receiving assistant cannot be assumed to browse the repo or load external links.
4. Offer a clearly labeled user-initiated "Ask your agent" action. Pass only the explicit context appropriate for sharing. Do **not** automatically include logs, tokens, tracker URLs, credentials, private endpoint paths, or device identifiers.
5. Test the selected guide against the **actual installed app build**, including feature flags. Test the handoff separately against each recipient and record results in [compatibility ledger](PROVIDER_COMPATIBILITY.md).

```kotlin
val guide = assets.open("aya-guide.md").bufferedReader(Charsets.UTF_8).use { it.readText() }
Aya.launch(this, AyaRequest(
    appName = getString(R.string.app_name),
    appVersion = "1.0.0", // replace with actual installed version
    guide = guide,
    screenName = "Connections", // only if user is currently on this screen
    question = "How can I configure this connection?"
))
```

AYA creates an **editable** review dialog, with Cancel, Copy, and Share controls. Share sends exactly the current editor contents as one UTF-8 plain-text attachment. Copy is a manual fallback if the target ignores the attachment. The receiving app may require an additional Send tap and may upload content to its service.

For an executable integration example, run `sample`. It uses a **fictional** ParcelPad reference; it is not an actual ParcelPad app. Never ship the fictional guide as a reference for a real application.

## Privacy and lifecycle

Shared files are unique, under the host's cache directory, and only older AYA files are pruned on later shares (seven-day threshold). Android may clear cache independently. There is no guaranteed immediate deletion after recipient handoff. AYA does not make network requests itself; recipient policies govern downstream handling. When implementing runtime diagnostics, add explicit previewable opt-in and redaction.
