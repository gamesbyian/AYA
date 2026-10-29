# AYA Handoff Protocol v1: portable host-to-AYA contract

**Version:** `aya-handoff/v1`. **Status:** descriptive interoperability contract for application developers; schema and fixture are checked in. The existing Android library's `AyaRequest`, `AyaCreativeTask` and `AyaImageRequirements` remain the shipped typed entry points. The JSON interchange defined here is **not yet a runtime parser** and is **not sent to assistants automatically**. No receiving AI app is known to understand this manifest.

## Goal

Define a stable, vendor-neutral *input model* for a host to prepare one AYA request, its known installed-version reference, non-sensitive current context, optional media metadata and output constraints. The host only submits details it intentionally selects. AYA asks the user to review/edit what will actually be sent; the standard Android Sharesheet/clipboard remain the wire protocol. This manifest is useful for future adapters and independent tooling without adding accounts, tokens or callback infrastructure.

- [JSON Schema](aya-handoff-v1.schema.json) (draft 2020-12) and [illustrative image request](examples/image-request.json).
- `operation`: `help` or `generate_image`.
- `host`: package ID, display name, exact installed version and optional screen name.
- `reference`: required AYA-RAS v1 asset, always exact installed version validated by AYA's guarded entry points.
- `request.text`: user intent, or a user-editable suggestion. No automatic reading of existing private app state.
- `context`: intentionally supplied public feature/subject labels only. A missing field means not known, not permission to scrape it.
- `outputRequirements.image`: actual host image-import preferences and instructions (see [host acceptance contract](../CREATIVE_HOST_ACCEPTANCE.md)). Ratio/pixel consistency must also be checked at runtime.
- `attachments`: **metadata descriptions only**, not payload bytes or source URIs. They are design reservations for later user-approved attachment support. Current AYA v1 only attaches its bundled UTF-8 AYA-RAS guide when explicitly chosen. It does not send optional reference images or multiple arbitrary files.
- `transportPreferences`: *possible*, not promised transports. Unsupported transports are reserved for future documented work; v1 currently implements text-only request and text + TXT reference.
- `privacy`: normative invariants: explicit user Share/Copy action, no assistant-response collection, no automatic return.

## Security and lifecycle invariants

1. The host must sanitize and minimize data before constructing this model; version-checked guide plus editable, user-controlled review are still required.
2. The manifest does **not** authorize execution, agent calls, screenshots, media access, URL fetches or post-share monitoring.
3. No receiver is implied by an intent-filter match. `ACTION_SEND` is best-effort; the target's ingestion behavior is unverified until observed with a controlled test.
4. Only the user's **final approved text** may be sent in a text-only share; recipients may ignore a file stream even when Android offers it.
5. Optional attachments require a *separate* feature and consent gate: MIME negotiation, immutable source selection, bounded stream-copy policy, URI grant scope, binary disclosure and per-recipient device compatibility. Merely listing an attachment in a manifest is not implementation.
6. Schema errors fail closed in any future importer. Do not silently coerce future incompatible major versions.

## Example

See the full fixture. A typical host-side implementation today is simply:

```kotlin
Aya.launchCreativeBundled(
    activity = this,
    task = AyaCreativeTask(
        subject = "Aurora Station, Season 4",
        assetRole = "Square season key art",
        image = AyaImageRequirements(
            aspectWidth = 1, aspectHeight = 1,
            preferredWidthPx = 2000, preferredHeightPx = 2000,
            acceptedMimeTypes = listOf("image/png", "image/jpeg")
        ),
        importInstructions = "Return to the artwork screen and choose Import saved image."
    ),
    direction = userTypedText,
    askDirection = false
)
```

This retains the shipped guard and prompt-first review. No JSON file needs to be generated in the production app. A separate adapter may consume JSON input in a future version only after its security and compatibility contract has been tested.

## Changes

- Additive minor schema fields may be introduced only with safe defaults and tests.
- Unknown top-level keys are invalid; a new incompatible operation or receiving intent requires a new major version.
- Never treat claims in `transportPreferences` as real provider support. See [local evidence registry](../RECIPIENT_CAPABILITIES.md).
