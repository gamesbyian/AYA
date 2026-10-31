# AYA Card UI Standard v1

**Status:** implementation profile for Android host-app embeds. AYA is a reusable convention, not a mandatory branded product or hosted service. An independent implementation is welcome.

## Invariants

1. An AYA card belongs visually to its host. Thin outline (1 dp by default), host background, typography, active text colour and outline tokens. Corners inherit host design: squared (0 dp) or rounded. No forced black tile.
2. The official AYA mark occupies the left of the explanatory header. Use the monochrome vector derived from `assets/ask-your-agent-icon.svg` with host foreground tint, never a baked-in dark-background logo.
3. The title, honest task-specific explanation, attachment status, and a **brief host-specific return/use instruction** come before an optional multiline question input and an explicit **Ask Your Agent** action. Input spans the available card width.
4. **Blank questions are allowed.** AYA's existing review supplies the generic help fallback. Never disable the action solely because the input is blank.
5. Action opens **local, editable privacy review**, not automatic transmission to an agent. A second deliberate Share or Copy step remains. Host provides the verified bundled guide and calls `Aya.launchBundled(..., question=typedText, askQuestion=false)`.
6. Disclose **actual** proposed materials, not imagined capabilities. An included reference is an *offered attachment*, subject to recipient acceptance. The host must avoid promising a new conversation, file ingestion, agent output, or return/import. If content can vary, the disclosure must vary too.
7. No diagnostics, screen scraping, tokens, private metadata, or implicit user files. Only explicit host-verified context and user-approved text. Preserve the one-way boundary.
8. Never place an independently scrollable viewport inside the card. Text wraps, input grows within sensible limits, all touch controls >=48 dp, Android keyboard and TalkBack work. At 320 dp portrait width and 200% font scaling, preserve reading order and usable actions. A host may scroll its containing screen.
9. Card submission errors (missing/mismatched guide, missing capabilities) must be exposed locally without attempting an unverified fallback.
10. **Every card explains what to do after the agent replies.** This is a visible, short, host-authored instruction: how to save and import a generated artifact using a real host control, where to paste/apply a result, or how to follow advice manually when there is no importable output. Say explicitly when nothing is imported or applied automatically. Never invent a menu path or imply AYA watches the recipient. A card whose host-specific return path is unknown must use a truthful manual-use explanation rather than claiming an import mechanism. Include the same verified path in the agent packet so its answer can guide the user.
11. Keep context semantics explicit: the host chooses screen hint and factual descriptive text from its evidence-backed app model. No assumptions that future/planned capabilities work.

## Output import action (optional, functional)

Cards expected to produce host-importable files should include a secondary **Import agent output** action, 48 dp minimum target, in both densities. It is available as `AyaCardView(onImportRequested = { ... })`, and must open a real host-controlled Android document picker/importer. Help-only cards or modules without an actual importer omit this action. Do not display a dead link.

Upon user file selection, use the [Output Return & Import module](OUTPUT_RETURN_IMPORT.md): bounded read, content-based artifact registry, schema validation and preview. Wrong-card results should offer routing to the correct host importer. Unknown/incompatible files receive explanations and a safe choose-another-file fallback. Any destructive change requires domain-specific dry-run, user confirmation and safe transaction controls; AYA itself performs no import.

The return instruction should explicitly mention the import action where it exists, while still explaining that users must save their agent's result first. Provider-choice hints are optional local-only opt-in; never scan storage or claim AYA saw the agent's output.

## Conforming densities

**Standard:** 64 dp mark on the left of title and multi-line explainer; an attachment disclosure and a concise 'After your agent replies' instruction; full-width multiline editor; full-width 48 dp action. Recommended for dedicated panels.

**Compact:** same information and behaviour in a shorter header (e.g. 48 dp mark and shorter task copy); attachment disclosure and return/use instructions remain visible and truthful. May position button alongside input only if both remain fully accessible, keyboard-safe and readable at narrow widths and large fonts. Prefer full-width button below input on phones.

A compact layout is not an excuse to omit consent or hide what is being shared.

## Android implementation

`dev.aya.android.AyaCardView` is the SDK's dependency-light **Standard** reference implementation, using ordinary platform Views. Hosts may embed it in Activity/Fragment, or use Compose `AndroidView` to adopt it without an SDK-level Compose dependency.

```kotlin
val card = AyaCardView(
    context = this,
    activity = this,
    guideAsset = "aya-guide.md",
    screenName = "Connections",
    title = "Ask Your Agent",
    description = "Ask about connections, errors or configuration.",
    attachmentDisclosure = "App reference offered for sharing; your AI app may not accept files.",
    outputInstructions = "After your agent replies, return to Connections and apply any recommended changes yourself.",
    cornerRadiusDp = 0f, // square host styling; use host's shape token
    densityMode = AyaCardDensity.COMPACT // or STANDARD (default)
)
container.addView(card)
```

`outputInstructions` is required in the reusable card constructor and may be updated with `setOutputInstructions()` when the task context changes. Describe only verified actions. `questionInput` is available for draft restoration; host should assign a stable view ID when saving a view hierarchy. The SDK invokes existing version guarding and final preview. `onRejected` may replace the default Toast. The custom View does not add a dependency on a specific receiving assistant.

**Current implementation:** standard View card + icon vector + local bundled review. Both Standard and Compact are implemented by `AyaCardView` through `densityMode = AyaCardDensity.STANDARD` (default) or `AyaCardDensity.COMPACT`. Compact reduces the mark, padding and initial field height but retains the full-width accessible action and disclosure. Compose hosts can wrap either variant with `AndroidView`; a dedicated Compose component is not shipped. UI measurements, TalkBack and recipient transport require device testing; they are acceptance criteria, not verified claims.

## Acceptance checks

- Square/rounded, light/dark and custom high-contrast host themes: outline, logo tint and typography remain visible.
- 320x700 / 412x892 and larger, landscape, font scaling 100–200%, IME open: no clipped controls or internal scrollbars.
- Keyboard, TalkBack, focus traversal, rotation/recreation: question survives when stable ID and host state restoration are provided.
- Blank, edited, very long and multi-line question; verify final review and final EXTRA_TEXT use same approved data.
- Missing/stale guide blocks share; no recipient falsely marked successful.
- When a file importer is supported, confirm an actionable import button opens SAF, can handle wrong-card selection and fails safely without automatic commits.
- Confirm the visible output-use path is correct for help/advice, creative image import, structured recipes, and translation packs; do not invent or promise automatic import.
- Show attachment status accurately for each module, including text-only creative routes and optional file handoffs.
- Verify using a dated Android/receiver version; actual ingestion and fresh-chat semantics are independent external QA.

## Authoring

The developer's agent must first apply the [application understanding framework](understanding/README.md), consult an authorized director for consequential unclear intent, and source-verify shipped capabilities. Then produce card title, short task description, one honest attachment disclosure, one concise verified output-use/import instruction, and optional suggested question. Keep packet authoring separate from UI wording; the compact card summarizes the task, not the full reference. See [packet standard](packet/AUTHORING_STANDARD.md).
