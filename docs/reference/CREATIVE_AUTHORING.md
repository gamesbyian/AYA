# AYA Creative Handoff: app-specific authoring extension

**Shared rule:** follow the [Common Packet Authoring Standard](../packet/AUTHORING_STANDARD.md) and [Creative profile](../packet/PROFILES.md#creative) for evidence, dependencies, scoped context, examples and independent QA. A request-only Share must contain every essential generation/import constraint even without a full reference attachment; test the exact visible approved text.

**Status:** v1 image generation. This extends, but does not replace, the [AYA-RAS v1 12-section guide](AUTHORING_STANDARD.md) and the version guard. The core reference remains a standalone, source-backed explanation of the actual installed app. The dynamic creative request supplies the currently selected asset, task and user direction; **do not generate a separate user-specific AYA guide for each item**.

## Two distinct contracts
**User-facing review:** a short, editable image-generation request is shared by default. The complete app-specific reference is offered only after the user explicitly chooses Full guide. Even when not transmitted, that reference remains mandatory, version-checked, comprehensive and accurate. Do not document default creative sharing as attaching the guide automatically.


1. **Static installed-version guide:** document the app's real image/asset editing or import entry point, supported asset types and import behavior as verified in shipping code and tests. Include feature, task and error IDs, navigation, failure recovery, privacy, evidence/unknowns and exact build applicability in the usual 12 sections.
2. **Dynamic per-handoff creative task:** `AyaCreativeTask(subject, assetRole, image, importInstructions, hostContext?)` plus user-authored `direction`, all visible in the review. Fields must represent the *actual active item and host import route* and must be tested independently. Dynamic request data is not evidence of what the app supports.

The user chooses their AI provider. The author cannot guarantee the recipient creates an image, understands the guide, recognizes copyrighted fictional characters, satisfies exact pixels, preserves lettering, or installs artwork. The assistant must be asked to **generate an actual image**, while being truthful about absent capabilities.

## Research checklist for an integrating app

- Identify actual image/asset destinations separately: for example profile avatars, UI icons, document illustrations, game textures, media tiles, vertical posters or landscape banners **only where the host supports them**. Record actual ratios, accepted import dimensions (hard bounds versus recommendations), accepted MIME/file formats and alpha handling **per slot**. Do not generalize one destination's constraints to another.
- Distinguish recommended artwork, search results, local import, external URLs, custom image capture, crop/edit, cancel/undo and persistence. Follow each to the real underlying implementation, even when it differs between app modes or versions.
- Record storage authority, device media picker, Android permissions, remote/cloud provider state, offline cases, thumbnails/previews, overwrite behavior, automatic resizes/compression, rejection messages, crop bounds, file-size limits, and where edits appear.
- Document host manual import flow from the **same screen the user left**, including if Android recreates the Activity, whether it retains the draft selection, and whether the file picker persists access. Distinguish local selection from actual saved/applied artwork.
- Describe privacy: what details host supplies to AYA; nothing auto-scraped or exported; recipient may store/upload text. If art includes personal photos, private library titles or account information, default to omission and explicit user review.
- Record exact source revision, binary version, screenshots/UX state, independent coverage inventory, and held-out questions. Distinguish AVAILABLE/CONDITIONAL/UNKNOWN/UNSUPPORTED, especially for recipient and generator behavior.
- Identify accessibility: touch target, TalkBack, label of creative panel, keyboard overlap, editable direction and privacy preview, custom image picker, return and focus restoration.

## Required item-level fields and rules

Use the library's types (see [Creative Handoff contract](../CREATIVE_HANDOFF.md)) rather than inventing ad-hoc JSON. The following are **host-side design rules**:

- `subject`: concise public-facing title of the selected work; don't export server addresses, file locations, tracking IDs or authentication data. If the title itself is sensitive, give the user control to edit before sharing.
- `assetRole`: unambiguous noun phrase, e.g. "square Season 4 key art", not "an image". Record actual target slot.
- `image`: ratio and optional preferred pixel dimensions that mathematically match; only formats supported by **the host importer**. Distinguish pixel preferences from strict minimum/maximum constraints in the host guide. Model transparency/margins only when applicable.
- `importInstructions`: navigation starting from the host's real retained image/asset editor or importer, actual picker actions and save/apply controls. No fabricated one-tap back or deep-link instructions.
- `hostContext`: compact, public, necessary facts only. Never automatically include current private image, local filesystem paths, URLs containing tokens, logs, installed app accounts, or extracted metadata from a sensitive library.
- `direction`: preserve user text; do not quietly prepend aesthetic judgments, strip names or rewrite their intent. The assistant may need to honor its own image policies, which AYA does not override.

**Request quality target:** Distinguish a recipient-friendly text-only creative request (4000-character bound, no attachment) from the complete AYA reference. The person selects between them after reviewing the payload, and AYA never tracks which produced artwork.

**Request quality target:** a receiving assistant with only `EXTRA_TEXT` can understand what to generate, for which subject and target, intended composition/ratio, preferred resolution and supported import formats, and the manual save/import relationship. The full guide is supplemental. A receiver that only ingests the file receives all of it. The final approved preview must control both channels.

## AYA-RAS authoring examples (illustrative only)

The examples below use a fictional media artwork editor for concreteness, **not** as the canonical Creative host category. A profile-image importer, illustration editor or game-asset tool must substitute its own actual UI, schema and tested constraints.

`TASK-ART-001` [AVAILABLE, verified host version]: "From Library > Season > Artwork, tap Change > Choose from device, select an image/jpeg or image/png, crop and tap Save. If Save is disabled, see ERR-ART-002. This updates the local season artwork only; any remote server propagation is UNKNOWN."

`F-ART-002` [CONDITIONAL]: "Create with your agent appears beneath recommended choices when that feature flag is enabled; pressing it opens local AYA review. AYA shares a text request; there is **no automatic replacement**."

`ERR-ART-002` [AVAILABLE]: "Unsupported image format. Choose one of the confirmed importer types or convert **outside AYA**. Verify the preview and metadata after saving."

Every assertion in an actual app guide needs a real source pointer. These are fictional templates, **not verified behavior for any production host**.

## Independent QA cases

Maintain held-out questions independent of the reference writer, including host-relevant cases such as: "I want a new avatar/illustration/icon"; "The AI just wrote a prompt"; "My provider doesn't appear in Share"; "It generated dimensions different from the host's requirement"; "I can save PNG but the importer rejects it"; "I returned and lost my target selection"; "Does AYA automatically install my art?"; "Will this overwrite the current asset?"; "Are private source images sent?"; and "What changes between available host modes?". Score exact steps, truthful uncertainty, formatting requirements, no hidden data and safe manual import. Never use production user conversations as automated QA telemetry.

## Release checklist

- [ ] Static AYA-RAS guide covers the actual picker/import states and matches the installed APK version.
- [ ] Independent inventory and held-out question set identify art features/errors; strict validation and audit pass.
- [ ] Typed dynamic creative requirements are sourced from **verified host constraints** and user intent survives intact.
- [ ] The app gives a normal import option without AYA; opt-in creative panel is clearly separate and accessible.
- [ ] Full review and text-only fallback preserve **final edited** instructions, with no prior hidden question.
- [ ] Native importer tests success, bad format, malformed image, crop, cancel, activity recreation and state retention.
- [ ] Recipient trials on actual Android/provider versions demonstrate where possible actual generation and saving, not merely chat opening. Unknowns remain UNKNOWN.
- [ ] No return channel, output monitoring, telemetry or silent binary attachments were added.
