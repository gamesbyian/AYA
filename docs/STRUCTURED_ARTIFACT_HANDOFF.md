# Structured Artifact Handoff · JSON recipe profile

**Shared authoring:** use the [Common Packet Authoring Standard](packet/AUTHORING_STANDARD.md) and [Structured profile](packet/PROFILES.md#structured-artifact) to derive schema, field semantics, dependencies and examples from actual importers. A compiled packet is build-time reference material, not a new implemented Android structured-task API.

**Status 2026-10-30:** browser/PWA implementation reference exists in the companion `gamesbyian/wallgen` branch `feature/aya-recipe-handoff-20261030`; AYA's Android library **does not yet expose a generic structured-artifact Kotlin entry point**. Do not claim native Android recipient compatibility. This document specifies the portable handoff profile and its future typed SDK extension.

## Purpose

Some hosts need a model to generate a structured file, **not** a bitmap. For example, ROYGBIV needs a canonical, importable `.json` design recipe based on a user brief and a version-aware description of controls, dependencies, ranges and effect interactions. AYA should provide the user's chosen agent with that reference plus the request, then stop.

Existing commitments remain immutable:
- user-supplied agent, no inference, billing, cloud account or new backend;
- explicit preview, consent and one-way transfer;
- no return callback, assistant output tracking, answer grading or automatic re-import;
- host owns final import validation, transaction, rendering and Undo;
- recipient attachment acceptance depends on the target app.

## Portable structured-artifact task contract (future Kotlin API)

A future `AyaStructuredTask` can hold:
- `artifactRole`, `extension`, exact `mimeType` and `schemaVersion`, verified against the receiving host's ordinary picker;
- `importInstructions` containing the real manual import flow;
- `prompt` (user editable) and bounded user-reviewed `hostContext`;
- `reference` (version-matched, source-derived guide), including a schema, defaults, preconditions, valid examples, coupled ranges, and documented unknowns;
- optional `currentArtifact` with an explicit, unchecked-by-default, user-controlled inclusion toggle.

Validate size and identity before sharing, keep the user's approved final text and attachment consistent, and expose Copy/Save fallbacks. Structured-artifact support must **not** be implemented by misusing `AyaImageRequirements` or claiming the assistant will create an image.

## PWA reference implementation: ROYGBIV

`More → Files & sharing → Ask Your Agent` launches a native browser dialog. A bundled generator reads the exact running app's canonical defaults and fields from `src/model.js` and `src/agent-api.js`, and combines them with source-informed conditional rendering notes. It includes a current full design **only with explicit opt-in**, then offers:
- **Share guide** as a single `text/plain` File via Web Share Level 2 file support where `navigator.canShare` allows it;
- **Copy guide** for paste into chat;
- **Save guide** for explicit manual attachment.

The recipient should return a JSON file with a canonical root recipe, required seed/structure, bounded enum/numeric values and no undocumented keys. The user saves the result and manually imports into ROYGBIV's existing JSON importer.

Browser file-share and Android `ACTION_SEND` have different compatibility surfaces. Do not extrapolate tested browser targets to the native Android SDK; verify each target independently.

## AYA authoring standard extension

For structured-result hosts, the reference author must include:
1. Authoritative machine-readable schema or a runtime-derived field list with a version identifier.
2. Types, defaults, full accepted numeric bounds and quantization; enum values from source, not paraphrases.
3. Activation prerequisites, disabled states and field applicability for every mode. Explain that an inactive field can be valid JSON but visually ineffective.
4. Interactions and ordering: where controls combine, override, mask or geometrically constrain one another.
5. Effect scale distinctions: numeric 0–100 is **not** necessarily linear perceptual response. Only claim calibrated response curves if reproduced on actual output fixtures; record source revision and measured uncertainty.
6. Minimum valid output example and top-level artifact shape; no envelope, fenced prose or explanatory fields inside the resulting `.json` file.
7. Modification guarantees: preserve all unrequested existing fields, locks and self-contained embedded assets.
8. Safe, reproducible import instructions with warnings that normalization may discard unknown/invalid fields.
9. Sample briefs, acceptable artifacts, invalid artifacts and independently tested expected visual properties.
10. Privacy boundary: omit current document/recipe unless the user opts in, never include secrets, credentials or private source assets by default.

Host-specific reference files remain the canonical holders of effects and schema details. AYA must not turn into a ROYGBIV-specific renderer, optimizer or schema registry.

## Implementation plan

1. **Completed in ROYGBIV feature branch:** PWA handoff generator, source-derived capability and semantics document, compact More composer, recolored AYA SVG, Share/Copy/Save actions and source-level tests.
2. **Next:** independently test real Android browser file-sharing and assistant ingestion, 320×700 / 412×892 single-screen geometry, focus/IME and host-side JSON imports.
3. **Later reusable SDK work:** add a typed structured-artifact entry point alongside `launchCreativeBundled`, not as an incompatible change; update template, Android sample and reference validators with genuine structured examples.
4. **Advanced:** source-driven calibration of visual effect interactions in hosts. These measurements are developer QA fixtures only; they must never introduce runtime monitoring of user conversations.

## Acceptance and non-goals

Passing a source/unit test does not guarantee recipient ingestion or artistic fidelity. AYA's success event ends at user-initiated transfer, not assistant reply or import. Every recipient capability must be labeled verified, conditional or unknown, and manual fallback remains available.
