# AYA Translation Kit: optional localization handoff

**Status (2026-10-30):** A guarded Android SDK entry point, a kit verifier and task builder are implemented. AYA does **not** implement a language runtime, pack importer, editing UI or automatic result collection. The sample has no real localization importer, and recipient compatibility is unverified.

## Experience

The app should lead with **ordinary language settings**: Follow device language, installed languages and Add language pack. An unobtrusive AYA card underneath may say: **"Want something different? Make a language or personality pack with your favourite AI."** Avoid AI-first navigation, mandatory accounts and an "AI languages" category.

The host owns source keys, import, validation, fallback, active locale, UI updates and sharing of completed packs. AYA prepares and shares the host's version-matched catalog/schema/terminology/context with an agent; the user's assistant may generate a file, which the user saves and imports manually. The host must support pack imports before advertising this card.

## Integration

Bundle `aya-guide.md` (standard exact-version AYA-RAS reference) and `aya-translation-kit.md` (seven-section Translation Kit v1). See [the detailed authoring instructions](AUTHORING.md) and [the fictional worked example](examples/parcelpad-translation-kit.md).

```kotlin
val outcome = Aya.launchTranslationBundled(
    activity = this,
    task = AyaTranslationTask(
        kind = AyaTranslationKind.PERSONALITY,
        target = "Pirate English, playful but precise",
        importInstructions = "Settings > Language > Add language pack > select saved JSON."
    ),
    kitAsset = "aya-translation-kit.md",
    guideAsset = "aya-guide.md",
    screenName = "Language",
    askDirection = false
)
if (outcome is AyaBundledLaunchResult.Rejected) {
    showError(outcome.reason)
}
```

`askDirection=true` opens AYA's optional direction composer; `false` proceeds to review, suitable when a host already captured a request. Both assets must match the installed application ID and exact version. The verified kit is appended inside one reviewed UTF-8 text attachment alongside the AYA-RAS guide. The final edited request is additionally available as bounded Android `EXTRA_TEXT`. A recipient may ignore the attachment or need another Send. `QuestionOpened` and `PreviewOpened` do not mean successful AI ingestion.

The resulting **pack** is host-specific JSON (or another explicitly documented importer format). It is separate from the **kit** (an agent-facing export). Personality and terminology overlays should be independent of ordinary locale resources, where supported, with explicit fallback and merge precedence. The developer must independently verify any output before accepting it as runnable data.

AYA still ends at Share/Copy, never queries an agent, watches responses, imports files, or modifies host localization state. See [privacy](../SECURITY.md), [test plan](../TEST_PLAN.md), and [authoring guide](AUTHORING.md).
