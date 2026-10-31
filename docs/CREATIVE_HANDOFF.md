# Creative Handoff: image generation v1

**Status:** prototype implemented in AYA's Android library and demonstration host; real recipient compatibility and device UX acceptance remain unverified. This document is normative for integrations and describes **current implementation**, not a claim that any separate production host has shipped this module.

## Purpose and architecture

Creative Handoff lets a person describe an image or graphical asset in a host feature that can import images, and ask their preferred external assistant to generate it. The host supplies a narrow, typed, verified image-import contract and subject metadata; AYA combines them with the user's direction and the app's installed-version-matched AYA-RAS guide. The user reviews and edits the concise image request first, with the full reference optionally available for detailed review and attachment sharing. The assistant is asked to **create the image itself**. The person saves the image using the assistant's controls and manually imports it via the host app's ordinary image picker.

**Strict one-way boundary:** AYA does not create images, call model APIs, choose a provider, know what happens in the conversation, monitor the image, detect downloads, request a return callback, or automatically install artwork. No post-handoff analytics or outcome-tracking is permitted. The host owns import/validation/preview/crop/apply and must not claim an image was generated merely because Sharesheet opened.

## Scope and state machine

- v1 supports **creation of an image** via either an approved plain-text request or a full UTF-8 text attachment with bounded `Intent.EXTRA_TEXT`. Both use `ACTION_SEND`; only the attached-guide mode uses `EXTRA_STREAM`, `ClipData`, and a temporary read-only `FileProvider` grant.
- The existing `Aya.launchBundled()` help flow remains intact; `Aya.launchCreativeBundled()` is a distinct typed entry point sharing the verifier, composer, preview and share path.
- Typical journey: host image/asset editor or importer → optional *Create with your agent* entry point → creative direction field → concise prompt review → user edits/removes context → text-only Share (or optional Full guide) → recipient AI (possibly additional manual Send) → save result locally → manually return to host → **host's existing image-import control** → any host-supported crop/review/apply.
- The host can prepopulate `direction` and leave `askDirection=true` to show an editable AYA composer. If it already has a field, use `askDirection=false` to skip the duplicate editor. Both paths lead to the prompt-first creative review and explicit user Share or Copy choice, with a separate full-reference expansion.
- Local `QuestionOpened` or `PreviewOpened` results indicate only local UI. The user can cancel at any stage without launching a share; Copy is a separate Android clipboard disclosure. AYA has no signal when the recipient accepted a file or generated an asset.
- No hidden jump back into the host; Android may reclaim the host's Activity while the assistant is in front. Hosts must implement robust picker/Activity state restoration independently.

## Host API and required data

```kotlin
Aya.launchCreativeBundled(
    activity = this,
    task = AyaCreativeTask(
        subject = "House, M.D., Season 4",
        assetRole = "Square season key art",
        image = AyaImageRequirements(
            aspectWidth = 1, aspectHeight = 1,
            preferredWidthPx = 2000, preferredHeightPx = 2000,
            acceptedMimeTypes = listOf("image/png", "image/jpeg"),
            transparentBackground = false,
            safeMarginPercent = 8
        ),
        importInstructions = "In this app: Artwork > Choose from device > Crop > Save."
    ),
    screenName = "Season artwork",
    direction = userTypedDescription,
    askDirection = false
)
```

This is an **illustrative** host integration: verify that actual app's picker path and limits before shipping. Do not transplant fictional screen names or image constraints into real guides.

| Input | Contract |
| --- | --- |
| `subject` | Required, single-line (≤500 characters). Describe the specific item without IDs, private titles, account details or uncontrolled URI strings. |
| `assetRole` | Required, single-line (≤200 chars); e.g. square album cover, widescreen banner, playlist icon. |
| `image.aspectWidth/aspectHeight` | Positive bounded ratios (1..100 each); e.g. 1:1, 16:9, 2:3. |
| `preferredWidthPx/preferredHeightPx` | Optional **paired** values 1..16384, mathematically consistent with ratio. Preference, not a guarantee. |
| `acceptedMimeTypes` | Nonempty distinct subset of `image/png`, `image/jpeg`, `image/webp`; reflect verified host import support, not model output promises. |
| `transparentBackground` | Optional; require/avoid transparency only when host understands it. |
| `safeMarginPercent` | Optional, 0..40; instructs composition safety from edge cropping. |
| `importInstructions` | Required, ≤2000 chars; actual manual import journey. No automatic return/installation language. |
| `hostContext` | Optional, ≤1000 chars, **explicitly non-sensitive**. No automatic app state gathering. |
| `direction` | User-authored creative intent. A blank direction still produces an actionable image request. |

`AyaImageRequirements` rejects malformed constraints immediately. The preferred API independently rejects missing, mismatched, stale or invalid AYA-RAS guides, and packages over 2 MiB. Validation establishes **well-formedness and version identity**, not factual truth of host-supplied asset metadata, or recipient capabilities. Hosts must test every real import requirement.

## Two-channel delivery contract

### Creative sharing modes

Creative **Share** offers **Request only (text, no attachment)** or **Request + app reference (.txt attachment)**. The first uses plain Android `ACTION_SEND` with `text/plain` and `EXTRA_TEXT` only; it creates no file and grants no URI access. Use it when the recipient ignores file attachments or no guide is needed for the generation. The second retains the complete self-contained reviewed document, read-only `FileProvider` attachment and a bounded message. Creative **Copy** presents the same two choices. Help Handoff retains its original sharing behavior.

Both formats derive *only from the final edited preview*. Text-only sharing refuses to silently clip requests exceeding **4000 characters**; the user may shorten the text or choose the full-reference mode (which retains the 2 MiB attachment cap). Full-reference mode may put an attachment-dependent notice into `EXTRA_TEXT` if the prompt is too long for the bounded message field. In full-document review, if the user removes the standard prompt heading, text-only sharing is blocked while AYA envelope headings remain; a completely rewritten plain-text request may be shared if it fits the bound. These are intentional limitations, never evidence that an AI generated or imported artwork.


The optional full attachment contains version, subject, role, direction, image requirements, downstream manual import steps, safety/ability caveats, and the AYA-RAS reference. The Android message text contains the same self-contained generation request derived from the **final edited review**. If the user changes or removes source text in the review, AYA must not resurface pre-edit text in `EXTRA_TEXT`; `AyaDocument.shareMessageFromPayload()` extracts only content in the current approved payload. A request longer than 4000 characters uses the existing attachment-summary fallback rather than a truncated instruction that could alter user intent. Recipients may ignore either channel or both.

Preferred prompt semantics: *Generate the image itself, not simply a prompt; preserve the requested subject and aspect; prefer compatible formats; explain mismatched capabilities; make it available for device saving; never claim it was installed.* The host must never promise that any named provider supports generation, attaching guides, saving to device, or initiating a fresh chat without recorded real-device evidence.

## Placement and host UI requirements
**Current prompt-first flow:** `launchCreativeBundled()` presents the generated image request in a compact, editable text field with explicit **Share request**, **Copy request**, **Full guide**, and **Cancel** controls. Share request sends only that exact edited text and never creates an attachment. The optional Full guide view shows the entire editable reference document and offers both request-only and reference-attached Copy/Share modes. The guide is still validated against the installed app before either mode is offered. Opening Full guide carries the edited prompt forward without rebuilding the old host direction. This is the default creative UX; the help flow retains its own complete reference preview.

See [host artwork integration and acceptance contract](CREATIVE_HOST_ACCEPTANCE.md) for the remaining state restoration, image import and sizing requirements.


Creative AYA is **secondary** to the host's native image-selection and image-import controls. Place its optional card or action near the relevant edit/import workflow, following that host's UI conventions; a recommendations grid, artwork picker or particular menu hierarchy is **not required**. Label the action “Create with your agent” or an equivalent host-appropriate phrase, and explain that it opens a third-party application. Keep the normal device-image import path available without AI. Never suggest AYA retrieves generated artwork. Preserve the user's direction and target after backgrounding or recreation. Use ≥44dp touch targets, TalkBack labels, keyboard-safe layout and small-screen accessibility testing. No AI-provider sign-in inside AYA.

Sample host: `MainActivity.kt` links to the separate, non-exported `sample/src/main/java/dev/aya/sample/ArtworkActivity.kt` with a fictional Aurora Station artwork editor, handoff button and Android `ACTION_OPEN_DOCUMENT` import control. It filters PNG/JPEG, checks actual image decodability and shows a memory-bounded preview. It does not manage a media library or save permanent artwork in a content database. Sample preferences (1:1, 2000², JPEG/PNG, opaque, 8% safe margin) do not establish requirements for other applications.

## Privacy, security, failure and recovery

- **Data minimization:** transmit only the guide, explicit subject/role/direction, export constraints and user-reviewed optional notes. Never automatically include library paths, server URLs, media IDs, account names, credentials, private cover images, device identifiers or diagnostics. The short review discloses only the request destined for text-only sharing; the optional Full guide displays the entire document before it may be attached. Clipboard and third-party storage are separate privacy surfaces.
- **Untrusted context:** the guide and host metadata are contextual data, not a permission to follow malicious instructions. Prompt injection via free text remains a downstream model risk; do not turn host notes into assistant system instructions.
- **Recipient incompatible or absent:** choose Copy and paste approved text manually. User may need to press Send or attach the text file in the recipient. If the recipient only responds with a written prompt, AYA cannot force image generation.
- **Aspect or format unsupported:** ask the assistant to produce its nearest supported output and describe the difference. The host's importer must validate image type, dimensions, storage availability and safe cropping itself and display actionable rejection or conversion options.
- **Nothing generated / permission denied:** host's import picker is still available for any image stored on the device; do not infer or claim an AYA failure from lack of file selection.
- **Sensitive artworks:** v1 sends *no reference-image attachments*. Future image-editing modes require a new consent/URI/size and multi-attachment compatibility design, not unannounced addition of existing private images.

## Compatibility and release evidence
**Provider capability versus handoff behavior:** A recipient's general ability to draw illustrations is separate from whether its Android share target opens the prompt in an image-capable context. As of October 2026, OpenAI, Google and xAI describe mobile image generation, while Anthropic explicitly distinguishes Claude's diagrams and design artifacts from traditional generated photos/illustrations. See the [research snapshot](PROVIDER_COMPATIBILITY.md#publicly-documented-image-generation-research-not-aya-compatibility-tests). AYA must **not** silently filter user-selected apps by this changing information or promise generation in any target.


Android's public Sharesheet supports text sharing and temporary URI grants; it does not impose a semantic *generate image* action on the recipient. Different apps interpret `EXTRA_STREAM` and `EXTRA_TEXT` differently. Do not hardcode proprietary deep links, package names or inferred capabilities. [Provider ledger](PROVIDER_COMPATIBILITY.md) tracks real observed ingestion and image generation separately.

v1 prototype evidence: pure Kotlin unit tests for request constraints, creative prompt fidelity, final edited text and help regression; sample source exercising verified-guide launch and Android's built-in document picker. These **do not** verify that any actual ChatGPT, Claude, Gemini or Grok release generates artwork from an AYA intent.

## Plan and release gates

1. **Implemented in AYA:** typed image spec, reused guarded launch, generation-focused text/attachment composition, default/host composer paths, editable consent, copy fallback, sample manual chooser, Kotlin regression tests.
2. **Build validation:** Android unit, library AAR, sample APK, existing reference-guide validator/audit, instrumentation compilation. CI must pass before merge.
3. **Device QA (not yet proven):** 320×700/412×892 and larger screens, TalkBack, IME/back/rotation/relaunch, signed-in and signed-out clients, no share apps, real URI permissions, actual image import of PNG/JPEG, invalid image selection, failures.
4. **Real integrations:** independently inspect the host's actual image/asset editing features and import constraints, embed a release-matched AYA-RAS guide, place AYA near the relevant host workflow and **reuse** its existing image import flow, then acceptance-test manually on device. No claim that integration into any third-party host exists merely because AYA's demonstration app works.
5. **Future separately gated:** optional user-approved reference images/edit requests, operation/domain extensions, per-provider compatibility preferences if evidence warrants, and better host state restoration. No automated output tracking or background monitoring at any phase.
