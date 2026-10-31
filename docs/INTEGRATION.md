# Integrating AYA into an Android app

## Optional language and personality packs

AYA includes `Aya.launchTranslationBundled(activity, task, kitAsset?, guideAsset?, screenName?, direction?, askDirection?)`, which uses the regular installed-version-verified AYA-RAS guide **plus** an independently exact-version-verified `aya-translation-kit.md`. This second asset describes the host's *actual* supported pack format, closed output schema, source strings, Rosetta meanings, technical terms, sensitive action distinctions, worked examples and manual import steps. The request and kit appear in one editable, reviewed UTF-8 handoff attachment. This flow does not require any new receiving-assistant integration.

```kotlin
val result = Aya.launchTranslationBundled(
    activity = this,
    task = AyaTranslationTask(
        kind = AyaTranslationKind.LANGUAGE,
        target = "es-MX",
        importInstructions = "Settings > Language > Add language pack > choose the JSON file."
    ),
    direction = "Use contemporary Mexican Spanish.",
    askDirection = false
)
if (result is AyaBundledLaunchResult.Rejected) {
    // Inform the user; do not silently substitute an unverified kit.
}
```

The host must first implement normal language selection and a working, safe pack importer. Put a small optional AYA prompt below those ordinary controls. `askDirection=true` offers a local direction editor; `false` skips that screen when the host already supplied the preference. The user manually saves the output from their chosen AI and imports it into the host. AYA does not monitor the recipient, handle the returned file or activate a locale. Full production preparation is in the [Translation Kit authoring guide](translation/AUTHORING.md) and [module overview](translation/README.md); use the fictional example only as a format demonstration.

**Preferred path:** use a version-matched bundled guide and `Aya.launchBundled()`, not a hand-assembled request string. See [integration readiness](INTEGRATION_READINESS.md) and the [AYA-RAS authoring system](reference/INDEX.md).

## Optional file-manager automation recipes

For FTP, FTPS, SFTP, SAF, local, SMB, WebDAV and cloud storage hosts with an **existing safe recipe importer**, use the [Filesystem Automation module](filesystem/README.md). Bundle `aya-filesystem-kit.md` for the exact installed app, documenting the real recipe parser schema, backend semantics, intent clarification, protective conditions and manual import. When the user explicitly asks to provide filesystem context, the host may generate a sanitized [snapshot](filesystem/SNAPSHOTS.md) and offer it for review. AYA performs no crawling or scanning.

```kotlin
Aya.launchFilesystemBundled(
    activity = this,
    task = AyaFilesystemTask(
        importInstructions = "Automation > Import recipe > Review > Approve"
    ),
    direction = userApprovedRequest,
    askDirection = false,
    snapshotJson = optionalUserApprovedSnapshotJson
)
```

The user manually saves the assistant's recipe and returns to the host importer. AYA does not ingest the response, decide what to delete, run an operation or guarantee a file was generated. See the [authoring spec](filesystem/AUTHORING.md) and [safety acceptance](filesystem/TEST_PLAN.md) before enabling a card. This is a dedicated guarded API; `AyaCardView`'s built-in action is still standard Help.

## 1. Add the library

AYA currently distributes a **staging Maven AAR** through the GitHub Actions build artifact or as source. There is **no public Maven Central release**. The repository uses the [Unlicense](../UNLICENSE); third-party dependencies retain their own licenses. CI uses Gradle 8.9, Android Gradle Plugin 8.7.3, Kotlin 2.0.21, JDK 17, compileSdk 35 and minSdk 23.

**Source-module path:** place or include the `aya/` module as a module in your Android Gradle build. Example in the host `settings.gradle.kts` after checking out AYA alongside the host:

```kotlin
include(":aya")
project(":aya").projectDir = file("../AYA/aya")
```

The host build must resolve `com.android.library` and `org.jetbrains.kotlin.android` and have `google()`, `mavenCentral()` repositories. Then in the host app module:

```kotlin
dependencies { implementation(project(":aya")) }
```

**Maven-staging path:** Download the `aya-maven-staging-repository` artifact from a successful AYA GitHub Actions run and extract its **repository directory layout**, including AAR and POM. Add that local Maven repository to your host's `dependencyResolutionManagement.repositories`:

```kotlin
maven { url = uri(rootDir.resolve("libs/aya-maven")) }
```

Then add `implementation("dev.aya:aya-android:0.1.0-SNAPSHOT")`. This is an experimental snapshot, not a stable public release. The sample CI builds once against `:aya` and once against the staged POM/AAR to verify resolution. Review the Unlicense, third-party dependency obligations and the unstable snapshot API before external distribution.

Enable `android.useAndroidX=true` in the host's Gradle properties. AYA's manifest supplies the non-exported `FileProvider` authority `${applicationId}.aya.files`. Check the **merged manifest**, especially if your app defines other providers.

## 2. Ship exactly the guide for the installed build

Create `app/src/main/assets/aya-guide.md` using [the AYA-RAS template](reference/TEMPLATE.md). Pin the real package, installed `versionName`, variant and evidence. At minimum:

```yaml
schema_version: aya-reference/v1
app_id: dev.example.yourapp
app_name: Your App
app_version_min: 1.2.3
app_version_max: 1.2.3
platform: android
```

The full envelope also needs `locale`, `guide_revision`, `source_revision`, `last_verified_utc`, `owner` and all 12 required sections. Build and validate a source-derived inventory and held-out question set. The runtime guard checks **exact** version identity (no semantic range resolution). If shipping multiple variants with different behavior, bundle the corresponding variant-specific guide in each APK.

## Optional standardized host card

For a recognisable in-app AYA entry point, use the [AYA Card UI Standard v1](CARD_UI_STANDARD.md). `AyaCardView` uses host theme colours, a tinted vector icon, an outlined panel, a contextual explanation, attachment disclosure, an optional question field and an explicit handoff action. It does **not** add an AI provider or automatically transmit any data. Both `STANDARD` and `COMPACT` densities share the same safe local review.

```kotlin
val ayaCard = AyaCardView(
    context = this,
    activity = this,
    screenName = "Connections",
    description = "Ask your agent about connection settings or errors.",
    attachmentDisclosure = "A reference guide will be offered to your AI app; file acceptance varies.",
    densityMode = AyaCardDensity.COMPACT, // optional; defaults to STANDARD
    cornerRadiusDp = 0f // use square corners if the host design is square
)
ayaCard.id = R.id.your_aya_card
ayaCard.questionInput.id = R.id.your_aya_question // stable host-owned ID for draft restoration
container.addView(ayaCard)
```

Put the card inside a **host-managed scroll container** if the screen might exceed the viewport with large text or the keyboard. Do not embed another scrolling panel inside the card. This View API also works within Compose via `AndroidView`, without changing AYA's core dependency graph. The supplied card currently handles the **standard help reference** route only: creative, structured-artifact and translation tasks must retain their specific guarded launch APIs and disclose their actual attachment behaviour rather than reusing a help-specific promise.

## 3. Connect the help button and question editor

```kotlin
when (val result = Aya.launchBundled(
    activity = this,
    guideAsset = "aya-guide.md",
    screenName = "Connections", // optional, avoid sensitive/user-entered data
    question = "Help me configure a remote connection." // optional prefilled suggestion
)) {
    is AyaBundledLaunchResult.Rejected -> {
        Toast.makeText(this, "AYA help unavailable: ${result.reason}", Toast.LENGTH_LONG).show()
    }
    AyaBundledLaunchResult.QuestionOpened -> Unit // local question editor only
    AyaBundledLaunchResult.PreviewOpened -> Unit // local review only
}
```

No application name or version string is manually trusted: AYA reads the installed APK package/version and validates the asset. When the user chooses Share, AYA creates one UTF-8 text document with a read-only content URI grant; the destination controls ingestion, chat creation and its own privacy terms.

**Default:** the host action opens AYA's question composer. The user can type an issue or edit the host-supplied suggestion; AYA then shows a full preview, before sharing any data. For a host that already has its own question composer, use `question = hostQuestion, askQuestion = false` to skip AYA's duplicate question screen and go straight to preview.

**Share payload:** AYA includes the final user-approved question in the attachment and also as bounded `EXTRA_TEXT`; `EXTRA_STREAM` holds the complete reference document. Recipients may use one or both; no recipient-specific behavior is assumed. See [Android research](ANDROID_SHARING_RESEARCH.md) and [question UX](QUESTION_COMPOSER.md).

**Unsafe/legacy alternative:** `Aya.launch(this, AyaRequest(...))` takes arbitrary text and skips bundled-version checks. Keep that for intentional advanced workflows, not standard product help.

## 4. Test your host integration
### Evidence-based recipient interoperability (optional)

The `AyaRecipientCapabilityRegistry` is a read-only helper for developer-supplied observations. For instance:

```kotlin
val registry = AyaRecipientCapabilityRegistry(emptyList()) // truthful default
val evidence = registry.assess(
    packageName = "org.example.assistant",
    appVersionName = "1.2.3",
    androidSdk = 35,
    accountState = null, // unknown must not inherit signed-in evidence
    transport = AyaTransport.TEXT_ONLY
)
// evidence.confidence == AyaCapabilityConfidence.UNKNOWN
```

Do not hardcode assistant packages, guess app versions or override Android's chooser based on inferred intent filters. [Evidence and QA record contract](RECIPIENT_CAPABILITIES.md). The current SDK does **not** interrogate the selected target, learn outcomes, or choose a share path automatically.

A portable [`aya-handoff/v1` host-side JSON manifest](protocol/README.md) describes a future, independently testable interchange; the supported integration today remains the Kotlin `AyaRequest` and guarded `Aya.launchBundled()` / `Aya.launchCreativeBundled()` methods.

### Optional system assistant context

Hosts that explicitly want Android's **separate system assistant integration** can override `Activity.onProvideAssistContent()` and call `AyaAssistContext.populate(outContent, AyaPublicAssistContext(...))` with deliberate public text. This is **not** invoked by AYA, does not attach a reference, and does not guarantee an assistant consumes it. [Privacy and JSON-LD guide](ASSIST_CONTEXT.md).

## 3a. Integrate an artwork-picker creative panel
**Current API behavior:** creative launch presents an editable prompt-only review by default. **Share request** shares only the visible text with no file URI; **Copy request** copies it. **Full guide** opens the complete, still-editable version-matched AYA reference and offers either sharing mode. The optional expansion preserves the user's edits from the short view. The sample demo is in a separate, non-exported `ArtworkActivity` so existing help controls stay accessible.

Before adopting this into an actual artwork picker, implement the [host integration acceptance contract](CREATIVE_HOST_ACCEPTANCE.md), particularly restoration of the selected artwork slot, authoritative image validation and format-aware handling.

Creative Share and Copy now let the user send **just the approved image-generation request** (plain text, no attached guide), or include the full reference (.txt). The former rejects requests over 4000 characters instead of silently truncating them. Both routes are opt-in and use the final edited preview. No target is presumed to support either format until verified in real-device tests.


Place an optional “Create with your agent” panel below your **existing** recommended artwork options while preserving normal “Choose from device” access. Take the user's typed description in the host and call:

```kotlin
val result = Aya.launchCreativeBundled(
    activity = this,
    task = AyaCreativeTask(
        subject = seasonTitle, // deliberately selected, non-sensitive metadata
        assetRole = "Square season cover",
        image = AyaImageRequirements(
            aspectWidth = 1, aspectHeight = 1,
            preferredWidthPx = 2000, preferredHeightPx = 2000,
            acceptedMimeTypes = listOf("image/png", "image/jpeg"),
            safeMarginPercent = 8
        ),
        importInstructions = "Artwork > Choose from device > Crop > Save"
    ),
    screenName = "Artwork picker",
    direction = userArtworkDescription,
    askDirection = false
)
if (result is AyaBundledLaunchResult.Rejected) {
    // Show a truthful local error; no external handoff occurred.
}
```

The example's paths and limits are **illustrative**: obtain them from real shipped host code and tests. `askDirection=true` shows an editable AYA composer when the host has no text field. Both flows reach a concise creative review and require explicit Share or Copy; full-reference preview is available through Full guide. The host owns saving/importing the downloaded image through its standard picker; AYA never sees the result. The sample app includes a real `ACTION_OPEN_DOCUMENT` image chooser and a local image preview to demonstrate this return-by-user workflow. For validation/recipient limitations, consult [Creative Handoff](CREATIVE_HANDOFF.md), [creative reference authoring](reference/CREATIVE_AUTHORING.md) and [provider compatibility](PROVIDER_COMPATIBILITY.md).


- `python3 tools/validate_guide.py --strict app/src/main/assets/aya-guide.md`
- `python3 tools/audit_reference.py app/src/main/assets/aya-guide.md --inventory ... --questions ... --strict`
- Compile the host with AYA's module or staged published dependency. Ensure a valid AAR and POM resolve.
- Verify stale guide/package mismatch visibly rejects before exposing a Share action.
- Inspect Android Sharesheet, URI read permission, and actual receiving application with a **non-sensitive** fixture.
- Record device OS, recipient app version and whether the reference is **actually read** and a fresh chat started. Do not infer compatibility from its presence in the chooser.

The real `sample/` host now uses this guarded method and a guide about its own functionality. The separate [ParcelPad guide](reference/EXAMPLE_PARCELPAD.md) remains a *fictional authoring example*, never packaged as actual sample-app help.

## 5. Privacy and failure boundaries

AYA collects no runtime diagnostics automatically. Anything passed as `screenName` or `question` is host-controlled, visible in review, and possibly transmitted to the chosen assistant. Remove secrets before calling AYA. Copy exposes text through the clipboard. Files are in a private cache subtree, shared with temporary read access, and old AYA files are pruned opportunistically after seven days on subsequent shares. There is no instantaneous revoke of a recipient's downloaded copy.

The user may need to press Send or paste the package manually in their AI app; no verified new-conversation deep link exists.
