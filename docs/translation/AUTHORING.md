# Translation Kit v1: host developer authoring guide

**Shared authoring:** follow the [Common Packet Authoring Standard](../packet/AUTHORING_STANDARD.md) and [Translation profile](../packet/PROFILES.md#translation-kit). Use a single source-backed fact registry and independently inventoried host semantics to inform both Help and Translation Kit, rather than keeping contradictory descriptions of destructive actions.

This is the normative procedure for an **app-specific, exact-version** AI-facing translation kit. It extends, but never replaces, the mandatory [AYA reference authoring standard](../reference/INDEX.md). AYA-RAS explains the actual app; this kit describes how an agent may generate a **data file** that its own importer will understand. The kit's existence does not establish that an app supports import.

## 1. Inventory shipped localizable text

Inspect the exact released build variant and source revision. Inventory all strings from Compose/resources, notifications, dialogs, errors, onboarding, widgets, screen-reader labels, empty states and conditional operations, including non-happy-path screens. Each stable semantic key needs:

| Field | Why |
| --- | --- |
| `id` / `source` / `source_locale` | Stable identity, exact shipped text and BCP 47 locale |
| `screen`, `state`, `description` | Where and when it appears, and the actual action/result |
| `placeholders` | Names, types, ICU/plural/select requirements |
| `safety` | ordinary, technical, accessibility, permission, security or destructive |
| `layout` | Context/length guidance and actual wrapping behaviour |
| `evidence` | Source path, tests and revision |
| `notes` | Ambiguity, grammatical requirements and forbidden meanings |

Never identify a string by English text or array index. Exclude user data, logs, private library content, URLs containing credentials, account details and settings dumps. Generate a **static, public-safe** kit, not a live session snapshot.

## 2. Derive the output schema from the host importer

Create a machine-readable JSON Schema (or an equivalent formal grammar for a non-JSON format) matching the **actual** importer. Record format revision separately from catalog revision, allowed keys, top-level shape, kinds (`language` / `personality` / `terminology` / `combined` if supported), BCP 47 locale or declared style ID, base/fallback, dependencies, unknown-key policy, partial-pack semantics and maximum sizes. Ideally generate a closed set of per-key properties from the source catalog.

Do not substitute the fictional example schema for the app's own schema. Compile fixtures showing accepted and rejected packs through the real importer. JSON Schema alone cannot prove message-format syntax or preserved meaning. Validate UTF-8, Unicode, locale tags, placeholder parity/types, plural/select patterns, dependencies, bidi isolation, archive traversal/size if ZIP is supported, and transactional rollback. Every missing key needs documented per-string fallback. A catalog revision mismatch should be explicit, not silently accepted.

## 3. Make a Rosetta/reference, not merely a word list

For each ambiguous, technical or sensitive term, document its exact meaning, contrasting meanings it must **not** acquire, synonyms for beginners and experts, and at least one contextual usage. Include key distinctions such as **Remove item vs Delete actual data**, Pause vs Cancel, Local vs Remote, and permission/safety scope. Show approved translations and counterexamples with reasoning. Cite source code or tested behaviour; never let a speculative LLM annotation silently change developer-approved semantics.

## 4. Handle natural and invented voices

Treat **language/locale**, **personality/style** and **terminology** as distinct axes. A style pack can be Pirate, Cajun-flavoured, Yoda-esque space sage or film noir without masquerading as a conventional locale. Define layering and conflicts, such as personal override → style/terminology overlay → regional locale → parent locale → source fallback. Only advertise composition where the host actually implements it. A partial pack is valid if the host's fallback can supply all missing keys.

Preserve functional meaning under theatrical phrasing. A joke may appear in descriptions, but data deletion, permission changes, security warnings, file paths, safety instructions and accessibility labels must remain unambiguous. Avoid presenting playful cultural imitations as authentic language evidence. Specify invariant terminology, approved register, voice examples and surfaces where jokes are not permitted.

## 5. Export one self-contained, structured kit

Bundle UTF-8 `app/src/main/assets/aya-translation-kit.md`. Its mandatory frontmatter is:

```yaml
---
schema_version: aya-translation-kit/v1
app_id: dev.example.host
app_version: 1.2.3
catalog_revision: catalog-2026-10-30
source_revision: audited-build-commit
source_locale: en
owner: App localization team
---
```

Include exactly one of each H2 in this order:

1. `## Output schema`: complete machine-readable schema in a JSON code fence, file extension, pack/catalog versions, dependencies and valid root.
2. `## Source catalog`: structured stable IDs, source text, placeholders, screen/state, risk labels and evidence.
3. `## Rosetta and glossary`: domain meaning, forbidden readings, technical and plain terms, contextual examples.
4. `## Style and meaning constraints`: locale grammar and scripts, voice, protected messages, safety/accessibility, technical constraints.
5. `## Worked examples`: valid regular, personality, partial and risky/plural cases; invalid counterexamples and why.
6. `## Agent instructions`: expected output file, only documented keys, preserve parameters/plurals, self-audit, report uncertainties and never claim import.
7. `## Host import instructions`: actual user-facing path to save/import, fallback, version checks and known limitations.

The user-supplied desired locale or personality belongs in the launch request, not a fixed kit. AYA structurally verifies the frontmatter, app ID, exact installed version and headings; it **cannot certify** schema truth, formatting correctness or agent compliance. The kit is limited to **1 MiB**, with combined reviewed handoff at **2 MiB**. For large apps, deterministically export subsets/deltas or versioned partial packs, rather than silently omitting strings. Multiple separate attachments are not supported in the current AYA Share path.

## 6. Android handoff and host UX

```kotlin
val result = Aya.launchTranslationBundled(
    activity = this,
    task = AyaTranslationTask(
        kind = AyaTranslationKind.LANGUAGE,
        target = "fr-CA",
        importInstructions = "Settings > Language > Add language pack > choose saved JSON."
    ),
    direction = "Use Canadian French with familiar technical vocabulary.",
    askDirection = false
)
if (result is AyaBundledLaunchResult.Rejected) showError(result.reason)
```

Use a small optional **Make a language pack** AYA panel *beneath* a conventional language selector and Import action. Do not demand AI for switching languages or importing community files. If user input is already captured by the host, set `askDirection=false`; otherwise set it `true` for the AYA direction editor. AYA's editable review is the only authority over what it shares. Android message text is derived from the final edited request, not a stale host prompt. Users manually save an output file, then import with the host picker; AYA never monitors the assistant.

## 7. Maintenance and acceptance

Rebuild catalog and schema when shipped strings or behavior change. Separate pack-format from catalog revisions; mark changed **meaning** for translation review. Export missing/changed string deltas for incremental translation. Synchronize kit and AYA-RAS app versions with the actual APK and retain source evidence. Test the complete host importer, not just an external schema validator.

Before release, test: language switching without AI, imported partial packs, bad encoding/JSON, unknown keys, missing/extra placeholders, plural/select patterns, RTL, Unicode, large fonts, TalkBack, truncation, unsafe archives/dependencies, changed catalog, destructive warnings, rollback, valid output from multiple LLMs, ignored recipient attachment, user cancellations, editing and no response tracking. Review 320×700 and 412×892 UI snapshots. Keep provider claims tied to dated device evidence.

**Teaching material:** [fictional ParcelPad kit](examples/parcelpad-translation-kit.md), [example output schema](examples/parcelpad-output.schema.json) and [sample Pirate pack](examples/parcelpad-pirate.pack.json). Do not treat them as production integration evidence.
