# AYA Creative Handoff: host artwork integration acceptance

**Audience:** implementers of real Android artwork pickers. This contract is mandatory for production integrations; the AYA module itself is deliberately a one-way prompt/reference handoff and must not receive or track generated output.

## Objective and boundaries

A user viewing a particular artwork slot in Chunks, a music application, or another host may decide to generate their own artwork in an external AI application. The host remains fully responsible for its *existing* Import from device pathway. AYA neither downloads the result nor observes the user's AI conversation. The host may remember the selected artwork target locally while the user switches apps, because this is normal host state restoration, **not** AYA response monitoring.

The integrator must distinguish:
1. **Preferred generator output:** target composition, aspect ratio, optional nominal resolution, preferred format and safe margins, provided to the agent as practical guidance.
2. **Acceptable importer input:** verified supported MIME/bitstream types, dimensions, encoded file size, alpha/orientation handling and decoding limits, enforced by the host after manual user selection.
3. **Final stored artwork:** whether the host crops/resizes/transcodes/compresses, where it saves the image, what it overwrites, when a remote server updates, and how the user can undo or replace it.

Never promise that an external image generator can deliver an exact pixel count, file format or attached reference. Do not claim an imported image has been applied simply because a picker returned a URI.

## Host-owned state and lifecycle

The host captures the selected media item and artwork slot in its own scoped, stable state before the AYA handoff. It must persist at least the item identifier or a safe local navigation reference, slot type (poster/banner/season tile/etc.), original artwork or applicable undo metadata, edit draft, and the intended action. For multiple simultaneous artwork edits, ensure each screen instance is unambiguous and a returned picker result cannot target the wrong item. Avoid passing or sharing those private identifiers to AYA unless explicitly necessary and user-approved.

When Android backgrounds, rotates, kills or recreates the host Activity, restore the editor and scroll position where practical. Revalidate current item existence and editability on return. If the underlying media item or server-side state changed, ask for confirmation rather than silently applying to a different target. The host may provide **Import saved image** as a persistent control on the same artwork screen. No automatic deep-link back, recipient polling, clipboard scraping, content observer, or background scanning for generated images may be used to reconstruct an AYA result.

Acceptance: start a creative request, switch to another app, rotate/recreate the host, return manually and choose an image. The image must still be associated with the originally selected artwork slot or require explicit reselection. Cancelled import must not disturb previous artwork.

## Safe manual import pipeline

Use the host's existing, tested photo/document picker or a permission-scoped equivalent. Prefer Android's Activity Result APIs in new integrations. Do not request broad storage access merely to support AYA. A content URI is a capability with a defined permission lifetime; take persistable permissions only when the picker/provider offers them, and only when persistence is needed. Do not assume that URI implies a local filesystem path.

After user selection, verify actual image content rather than trusting a filename extension or self-declared MIME type alone. Enforce reasonable encoded-byte limits, source pixel and decompressed memory budgets, and timeout/error handling on remote document providers. Read dimensions from a bounded metadata pass where available; decode a bounded preview rather than the full-resolution image on the UI thread. Handle EXIF orientation consistently, and do not destructively modify the original downloaded file. On decoding errors, security exceptions or missing permissions, show a localized actionable message and keep the prior artwork intact.

Support the formats actually present in the host pipeline. If the host can crop or convert JPEG/PNG/WEBP, distinguish them by documented state; never infer support from Android `image/*`. Transparency handling is slot-specific: conversion from PNG to JPEG must not turn transparency into unintended dark/black backgrounds without preview. Check color-space/ICC/HDR handling if the host offers it.

## Aspect, crop, resize and final save

Make clear whether a value is **required**, **recommended**, or **preferred**. If the output has the wrong ratio, preview safe center crop/letterboxing or allow manual repositioning where the host supports it. Never silently crop faces or lettering. If minimum dimensions are required, report the actual failure; do not claim the generator can meet them. Source aspect and final stored dimensions may legitimately differ after cropping/transcoding.

The actual Apply/Save operation must use the host's existing persistence code and report success only after that code has completed or its asynchronous confirmation is observed *by the host*. For local and remote media environments, clearly label destination/scope, eventual propagation, cancellation, replacement and undo. This is normal artwork management, not an AYA success metric or post-handoff observation.

## Accessibility and simplicity

Place an optional AYA panel beneath existing recommendations, while preserving a normal import button that never requires AI. The creative direction field and its final prompt-first AYA review must be accessible with TalkBack, keyboard navigation, font scaling, orientation changes and at least 44dp touch targets. Validate a small screen and a large screen with keyboard visible; avoid making the host's usual help controls inaccessible merely by adding the creative panel.

Avoid duplicating the question composer when the host already has a text field (`askDirection=false`). Do not preselect recipients, scrape installed AI app accounts, claim a new chat will open automatically, or hide provider limitations. If sharing fails, offer the copy/manual-paste path. Returning after generating an image should not require the user to re-enter the original media selection.

## Integration checklist and release gate

- [ ] Actual shipped artwork slots, supported formats, hard limits and preferred aspect/dimensions are source-verified and recorded in AYA-RAS with stable IDs.
- [ ] Host owner supplies truthful `AyaCreativeTask` and `AyaImageRequirements`, and a real current manual import procedure.
- [ ] The default brief image prompt is editable; text-only Share/Copy includes the final edited text and no attachment. Full guide remains an explicit, editable opt-in.
- [ ] Selected item, slot and draft remain correct after rotation, backgrounding, process recreation and canceled import.
- [ ] Existing import path validates URI permissions, bytes, decoding, orientation, alpha, size and crop, preserving original on failure.
- [ ] Save/Apply uses native persistence, identifies local/remote scope and never assumes a receiver generated an image.
- [ ] Accessibility and small-screen acceptance, old Help workflow and no-AI import flow pass independent tests.
- [ ] Real recipient-specific trials record offer/ingestion/generation/save separately; AYA runtime retains no results, logs or telemetry.

**Implementation status:** the sample demonstrates a separate artwork screen, a source-format-constrained document picker and downsampled preview. It does not implement a production art database, crop tools, EXIF handling or every above condition. These requirements become enforced as each actual host integrates AYA.
