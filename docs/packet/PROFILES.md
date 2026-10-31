# Shared AYA Packet profiles

Every profile uses [the same authoring standard](AUTHORING_STANDARD.md) and typed fact source. Its `always_include` list names the app-specific facts required in every packet of that kind, while the dependency graph includes additional constraints for a selected action.

| Profile | Goal | Mandatory host context | QA target |
| --- | --- | --- | --- |
| **help** | Explain features, guide action, diagnose failures | Exact UI/state paths, effects, risks, error tests, unknowns | Supported answers from held-out questions, no invented controls |
| **creative** | Generate compatible image/assets | Asset role, dimensions/ratio, accepted formats, cropping/transparency, actual manual importer | Compatible outputs, honest size/format limitation, no installation claim |
| **structured** | Generate a valid machine-readable host file | Schema/parser contract, ranges, dependencies, inactive settings, defaults, examples, import/Undo | Host importer and semantic acceptance, preservation of unrequested fields |
| **translation** | Generate language, style and terminology packs | Source catalog, Rosetta, placeholders, locales, protected actions, genuine importer | Keys and placeholders preserved, accurate destructive semantics, grammatical tests |

## Help

Use the existing [AYA-RAS 12-section document](../reference/INDEX.md) as the canonical app guide. A compiled packet is an optional verified supplement selected for a particular support journey, never a replacement that strips necessary troubleshooting or version truth. A short task request should reference the user's original question, while the full document supplies guidance for available/unknown/conditional cases. The host does not provide unauthorized diagnostic information.

## Creative

Preserve `AyaCreativeTask` typed fields and prompt-first UX. Ensure the essential ratio, format, transparency, cropping and manual import constraints appear in the actual short request, even where the full packet is not shared. Generate a role-specific supplement for complex cases (movie poster versus square cover). Do not assume a receiver can generate or download an image simply because it accepts a share.

## Structured Artifact

This profile currently has a documented [portable contract](../STRUCTURED_ARTIFACT_HANDOFF.md), but the generic Android structured-artifact entry point is not implemented. A packet should document true parser schema, field interactions, lock precedence, quantization, accepted extension/MIME and expected top-level shape. Include one valid minimal example, one realistic complex example and destructive invalid examples. The user returns through the ordinary host importer. Never fake a new Android API by misusing image requirements.

## Translation Kit

Use the [Translation Kit developer authoring guide](../translation/AUTHORING.md) and the exact-version `aya-translation-kit.md`. Its output schema must be generated from the real pack importer, with a source catalog, Rosetta meanings and counterexamples. If there is no importer, the app must not display the AYA generation card. The typed packet compiler can supply reusable semantic facts, but does not replace the seven-section kit. Keep ordinary Language UI primary.

For all profiles, run a [controlled agent trial ledger](EVALUATION.md) on the exact compiled packet and separately verify import or action results, where applicable. Never infer correctness from a generated text file alone.

## Relationship to the Android SDK

The compiler can emit a bounded full-context `--brief-output` for request-only paths, but the host must explicitly use it and preserve final user edits. If this fails its length check, use full reviewed attachment and do not silently omit facts.

The currently shipped SDK accepts an installed-version AYA-RAS guide and uses a reviewed Android `ACTION_SEND`. Creative Handoff has its own typed task. Translation Kit's proposed/branch SDK adds a guarded, second kit asset. The packet compiler and optional `build_reference.py` fragment injection are developer-side tooling: **no runtime module-specific packet selection, multi-file attachment protocol, model API, reply observer or automatic result import is implemented**.

Do not claim recipient interoperability or release readiness without dated, independent QA.
