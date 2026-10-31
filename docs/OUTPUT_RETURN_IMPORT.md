# AYA Output Return & Import · host-side module v1

**Status:** implemented Android helper primitives and optional card action. The host remains responsible for defining, validating, previewing, applying and rolling back each artifact format. Provider-neutral, no AYA service, no reply monitoring, no generated-output access until the user chooses a file.

## Why the return action exists

For tasks that yield a reusable file, an AYA card may show **Import agent output** underneath **Ask Your Agent**. The first action creates a reviewed, one-way request; the second opens a host-controlled import path *later, after the user has saved the file*. AYA never receives the agent's conversation, solicits a callback from an AI provider, or searches arbitrary storage. Help-only cards without importable artifacts should have no import action, but still show brief manual-use instructions.

### What the library actually supplies

- `AyaCardView(onImportRequested = { ... })`: optional accessible 48 dp action, available in Standard and Compact. A host must provide a real action; no inert decoration is shown without a callback.
- `AyaImportPicker.openDocumentIntent(mimeTypes, initialUri)`: Android Storage Access Framework (`ACTION_OPEN_DOCUMENT`); initial URI is optional and only a previously user-authorized content URI. Host owns lifecycle and Activity Result registration.
- `AyaImportPicker.readSelected(context, uri, maxBytes)`: bounded snapshot from a user-picked `content:` URI; default 4 MiB, absolute library cap 16 MiB. Refuses `file:` and unsupported schemes, unreadable data, and oversized inputs. **Call from a worker thread** to avoid ANRs. A host can choose a smaller cap; images larger than 16 MiB require a separate purpose-built host importer and must not be forced through this helper.
- `AyaImportFile`: private byte snapshot with copy-on-read, optional UTF-8 decoding and SHA-256 fingerprint. The document cannot silently change between inspection and downstream host use if the host passes these snapshotted bytes to its importer. This is not a cryptographic provenance guarantee.
- `AyaImportRegistry`: routes only after registered host format probes recognize the *content* and the chosen route validates its semantics. Untrusted filenames, MIME hints and optional AYA envelope do not authorize import. Registry never executes a recipe.
- `AyaImportDecision`: `Ready`, `Unusable`, `Ambiguous`, `Unrecognized`. `Ready.wrongCard` flags another registered AYA destination; `Ready.declaredTargetAppMismatch` flags a conflicting untrusted claim.
- `AyaImportDialogs.show(...)`: optional preview, wrong-card guidance, unknown-file recovery, ambiguous-route selection. **Continue to importer** is a handoff to the host's *own further review*, not apply or execute.

The registry is app-wide: each host module registers a stable route ID, user-visible title, `recognizes(file)` probe and `validate(file)` routine. Card IDs are contextual **entry points**, never exclusive import directories. The same file selected from a different card should resolve to its proper route. When two probes match, the user chooses which importer to inspect; `inspectAs` re-runs recognition and validation.

## Host implementation model

Use a host-managed Activity Result launcher. The following outline targets an AndroidX `ComponentActivity`:

```kotlin
val registry = AyaImportRegistry(packageName, listOf(languageRoute, wallpaperRoute))
// Host-created routes implement AyaImportRoute. Their validators are read-only.
val pickOutput = registerForActivityResult(ActivityResultContracts.StartActivityForResult()) { result ->
    val uri = result.data?.data ?: return@registerForActivityResult
    executor.execute {
        val read = AyaImportPicker.readSelected(this, uri)
        runOnUiThread {
            when (read) {
                is AyaImportRead.Rejected -> showImportError(read.explanation)
                is AyaImportRead.Loaded -> {
                    val decision = registry.inspect(read.artifact, cardRouteId = "wallpaper")
                    AyaImportDialogs.show(
                        this, decision,
                        onContinueToHostImporter = { ready ->
                            // DO NOT apply here directly.
                            // Present the real importer, using ready.artifact.bytes()
                            // and ready.route.id. Validate downstream dependencies,
                            // show impact/diff/dry-run, confirm, then commit atomically.
                            openHostImporter(ready)
                        },
                        onChooseAnotherFile = { pickOutput.launch(
                            AyaImportPicker.openDocumentIntent(listOf("application/json"))
                        ) },
                        onChooseAmbiguousRoute = { route ->
                            val chosen = registry.inspectAs(read.artifact, route.id, "wallpaper")
                            showRoutingDecision(chosen)
                        }
                    )
                }
            }
        }
    }
}
val card = AyaCardView(
    context = this,
    activity = this,
    outputInstructions = "Save the JSON recipe, then choose Import agent output here.",
    onImportRequested = {
        pickOutput.launch(AyaImportPicker.openDocumentIntent(listOf("application/json")))
    }
)
```

In production, wire the helper callbacks to actual host methods and close any Activity/lifecycle/executor resources appropriately. Compose hosts can use an `AndroidView` wrapper and Compose's Activity Result contract. For a simple in-app image picker with no structured schema, prefer the host's existing image-import pipeline.

## AYA identification hints, compatibility, and request matching

The optional JSON marker below is useful **only** when the actual artifact schema allows an envelope:

```json
{
  "aya_artifact": "v1",
  "target_app": "com.example.host",
  "artifact_type": "language-pack",
  "schema_version": "2",
  "request_id": "nonsecret-session-marker",
  "payload": {}
}
```

All fields are *claims supplied by an untrusted file*. The app's real parser and versioned schema remain authoritative. A `request_id` can improve explanations but must never grant permission or act as an authentication token. Users may import a valid file from another device, another agent, or a manual editor without an AYA marker.

**Do not wrap formats that require an exact root object.** ROYGBIV's canonical JSON recipe, for example, should remain in its native format. For legacy formats, identify through source-derived content probes or accept a separate opt-in sidecar with no authority over the artifact. Do not strip unknown keys or normalize a recipe merely to make it appear valid.

### Wrong AYA card

1. Inspect *all registered* source-backed import routes without modifications.
2. For a single valid route different from the initiating card, explain: "This looks like a language pack. Open the Language Pack importer instead?" Explicitly surface any declared target-app mismatch.
3. Preserve the exact chosen bytes, proceed only after user confirmation, and open the actual host importer (not a fake destination).
4. For multiple plausible formats, offer a short list; user choice must be revalidated. For invalid, unsupported or foreign files, show the reason and allow another file.
5. Do not claim to know which agent produced the file. Do not import solely because extension or metadata matches.
6. If the selected file is a nested collection with multiple artifact types, a host may expand into a separate, bounded batch-review workflow. Never execute embedded scripts as a recognition shortcut.

## Import safety policy

**Mandatory gates:** user selection; bounded read; confident content recognition; actual schema/version validation; preview; any dependency/side-effect analysis; explicit authorization appropriate to the operation; atomic host-side commit with rollback/recovery. Every host importer independently checks app identity, permissions, schema, referenced assets and side effects. Keep the original file unchanged on failure.

Low-risk imports (previewing a wallpaper recipe or proposing a language pack) may use a single confirmation after validation. Destructive or remote actions (delete files, reorganize trees, changing a server) require a dry-run manifest, target scope proof, collision/ownership checks, separate risk confirmation and reversible or recoverable transaction where possible. No generic AYA handler may grant arbitrary filesystem authority.

Revalidate any external dependencies at commit, even with an immutable artifact snapshot: current app version, user account/environment, target paths/objects, storage ownership, schema migration and permissions can change. Do not use a file's claimed origin to bypass confirmation.

## Handling unknown or unusable output

- **Unknown:** preserve file, explain supported artifact families, offer "Choose another file", and optionally provide source-backed instructions to ask the agent for the correct format.
- **Malformed/unsupported version:** explain which version the app accepts; never silently coerce, discard data, or replace active state.
- **Wrong host-app claim:** show mismatch; require the actual importer to establish whether it is valid and applicable.
- **Wrong card:** route via registry and explicit destination confirmation; do not make the user search for the right AYA panel manually.
- **Ambiguous:** let the user pick a likely destination, then validate that route independently.
- **Oversized/unreadable:** report exact limitation without loading the full file or retrying insecure paths; offer host-supported larger-file workflows if available.

## Optional Sharesheet selection hints

Android `Intent.createChooser(target, title, IntentSender)` can report a selected `ComponentName` through `Intent.EXTRA_CHOSEN_COMPONENT` (API 22+). **Selection is not proof of recipient ingestion, successful message send, result generation, or download path.** Callbacks can be absent when the chooser is abandoned. Android 15 (API 35) offers a newer `ChooserResult`, but it does not reveal where a later result was saved.

AYA exposes `AyaShareTargetHints.setEnabled(context, true)` as an **explicit user-opt-in, local-only** feature (off by default). The library records only the last selected receiver package in the host's private preferences; `lastChosenPackage()`, `clear()`, and `setEnabled(false)` allow local hints and deletion. Disabling clears the value. Hosts must explain the setting and must not use it for marketing or surveillance.

The value can improve "Return from your AI app" wording if the host has independently verified that provider's export conventions for that Android version. It cannot identify a saved document, a folder or app-private storage. Use a user-selected SAF URI, and optionally `DocumentsContract.EXTRA_INITIAL_URI` only with a previously granted document location (API 26+). Avoid arbitrary Downloads sweeps, broad storage permission requests, hardcoded guessed folders and provider-specific scraping.

Android source references: [Intent chooser callback](https://developer.android.com/reference/android/content/Intent#createChooser(android.content.Intent,%20java.lang.CharSequence,%20android.content.IntentSender)), [Storage Access Framework document selection](https://developer.android.com/training/data-storage/shared/documents-files), [DocumentsContract initial URI](https://developer.android.com/reference/android/provider/DocumentsContract#EXTRA_INITIAL_URI).

## Acceptance and limitations

Test document picker cancel/denial, multi-format routes, wrong card, spoofed metadata, malformed JSON, huge files, 320 dp / 200% font, TalkBack, lifecycle re-entry, host preview, rollback and no unsolicited file access. Use non-diagnostic snapshots for tests. Provider/agent exports must be validated against specific app versions. Neither the library nor the demo claims to have applied arbitrary host artifacts; integrating host developers must provide functional importers and final domain-specific confirmation.

This module leaves the AYA one-way handoff boundary intact. The human initiates a *separate host-local file selection* later; AYA never watches an AI reply.
