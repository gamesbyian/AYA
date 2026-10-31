# Structured Artifact Handoff · portable schema-driven output profile

**Shared authoring:** use the [Common Packet Authoring Standard](packet/AUTHORING_STANDARD.md), [Structured profile](packet/PROFILES.md#structured-artifact) and [Module Portability Standard](MODULE_PORTABILITY.md). The host supplies its own verified schema, field semantics, dependencies, actual import route and version constraints. AYA's profile does not know any host-specific recipe format.

**Implementation status:** this document specifies the portable handoff contract and a future generic Android typed entry point. The Android library **does not yet provide** a dedicated `AyaStructuredTask` launcher. Browser/PWA developers may implement the pattern using their platform's existing share/copy/save APIs; no particular browser integration is asserted or supported by this document. Neither route guarantees third-party assistant file ingestion.

## Purpose and suitable hosts

Any app that imports machine-readable files can give a user its verified file contract so a chosen agent can prepare a compatible artifact. Examples include procedural graphics presets, animation timelines, editor layouts, chart configurations, scene descriptions, audio-effect presets, and application configuration files. These are **feature categories**, not bundled products or adapters. Every host defines its own actual format and semantics.

A typical flow is: host feature → optional AYA card → editable brief and approved reference → user chooses their assistant or Copy → assistant proposes data → user saves file → user explicitly returns to the host importer → host validates, previews and applies with appropriate confirmation. AYA ends at the controlled handoff.

The host must have an operational, safe importer. If it cannot parse, validate or apply the requested output, it must not advertise that workflow merely because the agent could produce JSON. An AYA-generated packet is documentation, not an import implementation.

## Portable structured task contract (future SDK)

A future `AyaStructuredTask` could carry:
- `artifactRole`, file extension, exact MIME type and `schemaVersion`, taken from the shipped host importer;
- truthful `importInstructions` and expected apply/preview/undo behavior;
- a user-editable `prompt` and bounded, user-reviewed `hostContext`;
- a source-derived version-matched reference defining top-level shape, typed fields, defaults, bounds, conditional fields, interaction rules, expected output and negative examples;
- optionally the current artifact **only with a separate, unchecked-by-default user consent choice**.

Do not implement structured tasks by misusing image-generation requirements. Do not invent `AyaStructuredTask` calls in samples before the API actually exists. Enforce host/build identity, byte limits, user-approved final text consistency and truthful Copy/Save/manual-paste fallbacks.

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
- **Android:** review and Copy or `ACTION_SEND` with disclosed URI permissions. Core AYA's existing launcher types do not constitute a specialized structured-artifact API.
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

A reusable typed Android structured-artifact launcher, a fictional demonstration fixture, and associated compiler/parser/recipient QA may be added as independent changes. No host-specific branches, branded menus, format implementations or integration-status promises belong in this portable module.
