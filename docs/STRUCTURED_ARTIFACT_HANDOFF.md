# Structured Artifact Handoff · portable schema-driven output profile

**Shared authoring:** use the [Common Packet Authoring Standard](packet/AUTHORING_STANDARD.md), [Structured profile](packet/PROFILES.md#structured-artifact) and [Module Portability Standard](MODULE_PORTABILITY.md). The host supplies its own verified schema, field semantics, dependencies, actual import route and version constraints. AYA's profile does not know any host-specific recipe format.

**Implementation status:** the **unpublished Android source SDK** now provides `AyaStructuredTask`, `AyaStructuredKitVerifier`, `Aya.launchStructuredBundled()` and `AyaComponentAction.Structured`. The launcher uses the canonical installed-version AYA-RAS guard, a second exact-version kit check, editable local review, and deliberate Copy/Share; no host importer, automatic reply retrieval, browser/PWA adapter, third-party assistant attachment acceptance, physical-device or publicly distributed library is implied. Browser/PWA developers may independently implement the one-way convention using their platform's APIs.

## Purpose and suitable hosts

Any app that imports machine-readable files can give a user its verified file contract so a chosen agent can prepare a compatible artifact. Examples include procedural graphics presets, animation timelines, editor layouts, chart configurations, scene descriptions, audio-effect presets, and application configuration files. These are **feature categories**, not bundled products or adapters. Every host defines its own actual format and semantics.

A typical flow is: host feature → optional AYA card → editable brief and approved reference → user chooses their assistant or Copy → assistant proposes data → user saves file → user explicitly returns to the host importer → host validates, previews and applies with appropriate confirmation. AYA ends at the controlled handoff.

The host must have an operational, safe importer. If it cannot parse, validate or apply the requested output, it must not advertise that workflow merely because the agent could produce JSON. An AYA-generated packet is documentation, not an import implementation.

## Portable structured task contract (unpublished Android SDK)

`AyaStructuredTask` carries the host-verified `artifactRole`, lower-case `fileExtension`, `mimeType`, `schemaVersion` and true `importInstructions`. The runtime receives an editable direction, an exact-version AYA-RAS guide, and a separate developer-authored `aya-structured-kit/v1` asset. It reads at most 1 MiB of kit, caps the combined reviewed package at 2 MiB, checks installed package/version, rejects unsafe kit paths and malformed UTF-8, then opens the normal local question or review dialog. The structural verifier additionally checks that kit schema revision, extension and MIME type **exactly match the typed task**, preventing two different host output contracts from being silently shared. The host creates, validates, previews and applies any returned file; AYA does not receive or import it.

An optional **current artifact** is intentionally **not** accepted by this API yet. Any future attachment must use a separate unchecked-by-default user approval and a bounded, auditable payload. Do not misuse image-generation requirements to describe structured files.

## Source-preview Android usage

```kotlin
val task = AyaStructuredTask(
    artifactRole = "chart configuration",
    fileExtension = ".json",
    mimeType = "application/json",
    schemaVersion = "chart-3",
    importInstructions = "File > Import > Preview > Apply"
)
val result = Aya.launchStructuredBundled(
    activity = activity,
    task = task,
    kitAsset = "aya-structured-kit.md",
    guideAsset = "aya-guide.md",
    direction = "Create a horizontal categorical chart"
)
// This result describes opening local UI, never agent receipt or import.
```

The sample values above belong to a **fictional feature**, not an AYA output format. The integrating host bundles its independently audited asset with this exact seven-section format:

```markdown
---
schema_version: aya-structured-kit/v1
app_id: dev.example.chart
app_version: 1.0
schema_revision: chart-3
artifact_extension: .json
artifact_mime: application/json
source_revision: example-build
owner: example developer
---
## Artifact output contract
## Field semantics and bounds
## Interactions and precedence
## State preservation and migration
## Worked valid and invalid examples
## Agent clarification and safety
## Host import and recovery
```

These headings and metadata are **structural** requirements; empty headings, invented schema descriptions or untested examples are not evidence that an actual host importer can accept any generated file. Use the host's real verified format, not the fixture.

## Offline authoring validation

Before bundling a structured kit, the developer can run the stdlib-only checker against a source-derived asset and independently verified installed package/version, extension, MIME and importer revision:

```sh
python3 tools/validate_structured_kit.py path/to/actual-host-kit.md \
  --app-id dev.example.chart --app-version 1.0 \
  --schema-revision chart-3 --extension .json \
  --mime-type application/json
```

These arguments and the included [fictional chart kit](structured/examples/chart-kit.md) are examples, **not** claims that a real chart importer is implemented in AYA. This offline check rejects stale/foreign metadata, missing/empty sections, duplicates, unsafe file contracts, unresolved placeholders, symlink paths and oversized/malformed UTF-8 kits. It neither validates JSON Schema nor parses generated artifacts; actual importer compatibility, field semantics, examples, privacy and recipient ingestion must be verified separately.

## Required developer-authored schema and semantics

The host integration must document:
1. The authoritative real importer/parser revision, extension, MIME and accepted top-level shape. Include a JSON Schema where applicable; XML, YAML and other formats retain their *actual* native contracts.
2. Required and optional fields, types, enums, defaults, exact numeric bounds, quantization, units, normalization, unknown-field and duplicate-field policy.
3. Activation conditions and unsupported combinations. A syntactically valid field may be ignored when its feature or mode is inactive.
4. Interactions and precedence: controls that compose, override, mask, inherit, lock, interpolate or constrain other controls, including order-sensitive behavior.
5. Effect scale and meaning, not merely numeric slider ranges. Do not claim linear or calibrated perceptual behavior without repeatable evidence.
6. Minimal valid and realistic complex examples accepted by the *shipped* importer, plus intentionally invalid examples and the expected rejection reason.
7. Preservation rules for existing unknown/unchanged fields, embedded assets, IDs, external references and version migration. No automatic dropping of state.
8. Save/import instructions, preview, rejection messaging, transactional application, recovery and undo limitations.
9. Independently tested sample user briefs, expected artifact semantics and parser/renderer results.
10. Explicit privacy consent for any current document, design, media, asset metadata or user-specific context. No hidden source assets, tokens or private data.

A strict-root native format must be returned unchanged: do **not** wrap it in an AYA envelope or append explanation fields unless the verified importer specifically permits that. Any agent-side caveats belong outside the import file. The host must treat all generated content as untrusted and must never execute arbitrary generated code or destructive operations solely because a schema accepts the file.

## Transport-agnostic authoring and delivery

Use a platform-appropriate, user-approved path:
- **Android:** `Aya.launchStructuredBundled()` provides the version-checked, typed source-preview path through review/Copy/`ACTION_SEND` with disclosed temporary URI permissions. The host still owns output/import behavior; no general marketplace component is published.
- **Browser/PWA:** user-initiated Share with `navigator.canShare` checks where supported, or Copy/Save for manual attachment. Browser file-sharing availability does not imply Android Sharesheet compatibility.
- **Other integrations:** preserve the same editable preview, version consistency, consent and manual return boundary, without claiming unimplemented platform support.

The receiving agent might reply in prose, include code fences, omit the attachment, or generate invalid data. The host's own parser and import preview are authoritative; the user must not be told a file is compatible before validation.

## Required acceptance gates

- Independently derive a feature inventory and schema from a *real* host build. Never copy a hypothetical fixture into a shipping packet.
- Test minimal, maximal, nested, conditional, inactive and interdependent fields; unsupported ranges; migrations; malformed, oversized, stale and foreign files; and unchanged-property preservation.
- Verify the reviewed packet includes all essential semantic constraints and the exact user-approved optional current artifact.
- Verify host import is user-invoked and separately validates content, permissions, side effects and recoverability.
- Test each OS/browser/assistant transport combination directly. Record unknowns; do not infer that share success means recipient ingestion or artifact production.
- Confirm the module's vocabulary and operations remain applicable to at least two unrelated classes of structured-file hosts, without carrying an external project's UI, repository paths, naming conventions or schema.

## Future work

The typed Android launcher and Kotlin negative tests now exist as unpublished source. Remaining work includes independent consuming-host APK/device acceptance, real validated output parser/importer round trips, optional current-artifact consent design, visual-builder adapter wiring, dated recipient trials and public distribution. No host-specific branches, branded menus or proprietary formats belong in this portable module.
