# AYA Spatial Composition Handoff · v1

**Status: protocol, offline validator and Android multi-attachment source-preview adapter implemented. The sender and independent synthetic receiving-app tests require CI qualification. Real assistant ingestion, automatic output return and production host acceptance are NOT verified.**

This module lets a host with a photo/document canvas describe **localized visual changes** using geometries, catalogued replacement assets, preserved areas and an editable user brief. The host creates a bounded, explicitly approved bundle for a user-selected assistant to create a *proposed* edited composition. The user saves any result and independently imports it into the original host.

The normative contract is [PACKET.md](PACKET.md), with [JSON Schema](schema/aya-spatial-composition-v1.schema.json), [synthetic fixture](examples/mechanical-room.json) and offline [validator](../../tools/validate_spatial_composition.py). The mechanical-room example is fictional. The same mechanism applies to landscaping photographs, retail display alterations, building maintenance proposals and interior visualizations without AYA knowing host-specific catalogues.

## Boundaries

- Host-owned: image capture/import and orientation normalization; annotations, masks, catalogue, source inventory and permissions; asset export and hashes; project persistence; consent; recipient handoff UI; returned image validation, attribution and project import.
- AYA-owned: portable format, constraints and invariants, advisory agent brief, structural offline validation, explicit disclosure and compatibility guidance. AYA never scans a site, recognizes or measures equipment, uploads data itself, generates images, checks clearances, tracks the assistant or silently applies an output.
- Recipient-owned: whether multi-file inputs are accepted, actual generation, output file format and quality. Sending or opening a chooser is not proof of ingestion.
- Preserve separate *conceptual visualization* and *engineering feasibility* claims. Generated plumbing, dimensions, mounting or compliance are never accepted as verified engineering.

## Recommended flow

1. Host imports an original photograph and preserves unchanged source bytes. Establish EXIF orientation and display coordinates before committing annotations.
2. User taps points, sketches polygons/areas and selects references from the host's catalogue. The host stores stable annotation IDs, descriptive labels and explicit operation associations. User writes or edits directions.
3. Host assembles a manifest and ONLY the minimum authorized attachments, with original unannotated source plus optional labelled overlay; all image paths are relative to a private export staging root.
4. Present an intelligible review: exact image count, image previews, descriptions, marked regions, product identities, processing location/privacy warning, preservation rules and the user's editable instructions. Nothing is transmitted until the user approves.
5. Validate locally and negotiate *observed* recipient support. Share attachments using a platform adapter only after consent; offer explicit manual-file/ZIP fallback when multi-attachment receipt is unknown. If a recipient is text-only, disclose that the photo cannot be included and do not represent the text-only version as equivalent.
6. User separately saves the agent's result, returns to the host through its own picker, verifies an image preview and confirms insertion as a **new revision**. Keep originals and provenance intact.

## Developer integration requirements

Build host-specific facts using [AYA-AUF](../understanding/README.md), the [packet authoring standard](../packet/AUTHORING_STANDARD.md), and [module portability standard](../MODULE_PORTABILITY.md). Obtain actual catalogue data from the host, not from these examples. An adopting host must implement orientation-safe canvas mapping, source-file ownership, content URI read grants and expiry, byte quotas, cancellation and Activity recreation. Ensure source assets never leak through unreviewed embedded links or background uploads.

The Android source-preview adapter is `AyaSpatialHandoff.launch(activity, AyaSpatialShareTask(manifestJson, images))`. It opens a review dialog showing every file path, byte count, hash prefix and operation with an editable instructions field, and copies explicitly approved source/overlay/reference `content:` URIs to a private FileProvider cache. It checks the declared SHA-256 and exact lengths, image signatures and decoded dimensions before constructing `ACTION_SEND_MULTIPLE` with a manifest JSON and images, `ClipData`, and temporary read-only grants. Use the separate existing Creative Handoff launcher for text-only image creation. **Do not claim that multi-file receipt is supported by any particular AI app without recipient-specific evidence.** Prefer a full packet saved as an archive when the recipient doesn't reliably accept separate images. Always test actual target app versions and distinguish Share Sheet opened, attachment ingested, and result produced.

## Acceptance gates

- Schema validation (synthetic valid/invalid fixtures, path traversal, label collisions, bad references, out-of-bounds coordinates, preservation conflicts, hash mismatches and budget checks).
- Offline packet validation followed by a host-owned file-byte verifier and manual inspection of annotated overlay mapping.
- Real Android sender ↔ independent receiving app validation: approved content only, complete attachment counts/hashes, cancellation, recreation, permissions, no background capture; report OS/build/recipient versions.
- Real assistant trials: verifies each supplied image was used (not just selected), no unrequested edits, perspective retention, uncertainty disclosure, and manual image import. Real engineering accuracy requires separate professional verification.
- Verify portable behavior with a photo-based interior redesign host AND an outdoor grounds-planning host.

Run: `python3 tools/validate_spatial_composition.py docs/spatial/examples/mechanical-room.json` and `python3 -m unittest tools.test_spatial_composition tools.test_module_portability`.

## Kotlin Android integration (source preview)

```kotlin
AyaSpatialHandoff.launch(
    activity = this,
    task = AyaSpatialShareTask(
        manifestJson = hostGeneratedManifestJson,
        images = listOf(
            AyaSpatialImage("source/photo.jpg", hostApprovedSourceContentUri),
            AyaSpatialImage("references/replacement.png", hostApprovedReferenceContentUri)
        )
    )
)
```

The return value is `AyaBundledLaunchResult.PreviewOpened` (only the local dialog opened) or `Rejected(reason)`; callers must handle a rejection and must not equate preview or chooser opening with delivery. The default `guideAsset = "aya-guide.md"` must contain the exact installed-app/version AYA-RAS reference and is verified before showing review. It is not silently attached to the share. The example paths are placeholders: each must match an entry in the provided manifest. The host must author a complete v1 manifest, obtain consent for the photos, offer a way to edit/inspect all changes and restore its draft after recreation. The AYA dialog gives final user review of **file names, byte counts, hash prefixes, operation IDs and editable instructions**, plus a separate **Inspect complete manifest** control exposing every outgoing structured field. It does not render thumbnail previews. The host is responsible for visual preview, redaction and accurate orientation. Staging happens on a worker thread only after Share files is pressed. If bytes changed, AYA blocks the outgoing intent. The chooser may still show no compatible receiver because `*/*` mixes JSON and image types. No ZIP fallback or automatic return is provided yet.

The host can explicitly open its own image picker for returned output, using the [Output Return & Import](../OUTPUT_RETURN_IMPORT.md) primitives. Keep original and revision provenance intact. The current adapter is source preview, not a published SDK release.

## Remaining adapter slices

1. Add host-provided thumbnail review, resumable staging cancellation, independent no-copy-before-consent UI testing and accessibility acceptance.
2. Qualify Android multi-URI sharing with an independent synthetic receiving app; add optional ZIP export fallback and recipient format compatibility trials.
3. Explicit user-initiated return via [Output Return & Import](../OUTPUT_RETURN_IMPORT.md), with streamed, bounded image decode, EXIF handling and source revision checks.
4. Cross-platform adapters for Swift/Files sharing and web download, only after platform-specific acceptance.
