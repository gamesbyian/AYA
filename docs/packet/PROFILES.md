# Shared AYA Packet profiles

All five profiles consume the app-specific understanding developed with [AYA-AUF](../understanding/README.md). Recover purpose, user goals, concept distinctions and director-approved intent first; then verify runtime facts with the existing packet source and inventory. Do not regenerate conflicting semantic definitions independently for each module.

Every profile uses [the same authoring standard](AUTHORING_STANDARD.md) and typed fact source. Its `always_include` list names the app-specific facts required in every packet of that kind, while the dependency graph includes additional constraints for a selected action.

| Profile | Goal | Mandatory host context | QA target |
| --- | --- | --- | --- |
| **help** | Explain features, guide action, diagnose failures | Exact UI/state paths, effects, risks, error tests, unknowns | Supported answers from held-out questions, no invented controls |
| **creative** | Generate compatible image/assets | Asset role, dimensions/ratio, accepted formats, cropping/transparency, actual manual importer | Compatible outputs, honest size/format limitation, no installation claim |
| **structured** | Generate a valid machine-readable host file | Schema/parser contract, ranges, dependencies, inactive settings, defaults, examples, import/Undo | Host importer and semantic acceptance, preservation of unrequested fields |
| **translation** | Generate language, style and terminology packs | Source catalog, Rosetta, placeholders, locales, protected actions, genuine importer | Keys and placeholders preserved, accurate destructive semantics, grammatical tests |
| **filesystem** | Create a manually imported file automation recipe | Exact parser schema, backend matrix, scope, destructive safeguards, clarification policy, optional consented snapshot | Correct host-compatible recipe and explicit user safeguards; no presumed execution |

## Help

Use the existing [AYA-RAS 12-section document](../reference/INDEX.md) as the canonical app guide. A compiled packet is an optional verified supplement selected for a particular support journey, never a replacement that strips necessary troubleshooting or version truth. A short task request should reference the user's original question, while the full document supplies guidance for available/unknown/conditional cases. The host does not provide unauthorized diagnostic information.

## Creative

Preserve `AyaCreativeTask` typed fields and prompt-first UX. Ensure the essential ratio, format, transparency, cropping and manual import constraints appear in the actual short request, even where the full packet is not shared. Generate a role-specific supplement for complex cases (movie poster versus square cover). Do not assume a receiver can generate or download an image simply because it accepts a share.

## Structured Artifact

This profile has a documented [portable contract](../STRUCTURED_ARTIFACT_HANDOFF.md) and an **unpublished native Android source-preview** implementation: `AyaStructuredTask`, `Aya.launchStructuredBundled()` and `AyaComponentAction.Structured`. The host must bundle an exact-installed-version, seven-section `aya-structured-kit/v1`; the guard also checks that schema revision, extension and MIME match the typed task. A packet should document the real parser schema, field interactions, lock precedence, quantization and top-level shape, including valid, complex and invalid examples. The user returns through the ordinary **host-owned importer** after independently validating the file. No AYA file importer, recipient verification or publicly released SDK is implied.

## Filesystem Automation

Use [Filesystem Automation Kit authoring](../filesystem/AUTHORING.md) and [snapshot context specification](../filesystem/SNAPSHOTS.md). Compile source-backed capabilities, schema, exclusion rules, import and approval semantics with all destructive safeguards included as dependencies. The agent clarifies consequential ambiguity before creating a recipe. The snapshot is optional, redacted where appropriate, and can be partial or stale. The app must have a real safe recipe importer and executor; AYA does not provide either and never receives a generated file back. Verify outcome against an independently tested host parser and dry-run/approval flow.

## Translation Kit

Use the [Translation Kit developer authoring guide](../translation/AUTHORING.md) and the exact-version `aya-translation-kit.md`. Its output schema must be generated from the real pack importer, with a source catalog, Rosetta meanings and counterexamples. If there is no importer, the app must not display the AYA generation card. The typed packet compiler can supply reusable semantic facts, but does not replace the seven-section kit. Keep ordinary Language UI primary.

For all profiles, run a [controlled agent trial ledger](EVALUATION.md) on the exact compiled packet and separately verify import or action results, where applicable. Never infer correctness from a generated text file alone.

## Relationship to the Android SDK

The compiler can emit a bounded full-context `--brief-output` for request-only paths, but the host must explicitly use it and preserve final user edits. If this fails its length check, use full reviewed attachment and do not silently omit facts.

The current unpublished Android SDK accepts an installed-version AYA-RAS guide and uses a reviewed Android `ACTION_SEND`. Creative, Translation, Filesystem and Structured Artifact Handoffs have typed requests with guarded static kits where applicable. The packet compiler and optional `build_reference.py` fragment injection are developer-side tooling: **no runtime module-specific packet selection, multi-file attachment protocol, model API, reply observer or automatic result import is implemented**.

Do not claim recipient interoperability or release readiness without dated, independent QA.
