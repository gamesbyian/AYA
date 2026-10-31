# AGENTS.md — instructions for coding and documentation agents working in AYA

## Mission

AYA is an Android BYO-assistant, one-way help and creative handoff. The user selects a third-party assistant. The host app supplies a precise, *installed-version-matched* reference and optionally a question/screen hint. AYA previews the exact payload and sends one file through Android's public Sharesheet. Do not introduce model hosting, hidden telemetry, proprietary assistant dependencies, or unsupported claims about what recipients do.

## Application understanding before packet authoring

Read [AYA-AUF](docs/understanding/README.md), [concept modelling](docs/understanding/MODEL.md) and [Director Consultation Protocol](docs/understanding/CONSULTATION.md) before drafting host packet content. Recover purpose, user goals, ontology, intended automation/control, misconceptions, disputed semantics and four distinct truth categories. Investigate evidence before asking the director; request only consequential missing direction through context-rich questions, and preserve deferral/delegation/unknowns. Validate AUF models and decisions with `tools/validate_understanding.py`. A director statement proves only scoped **intention**, never shipping or successful behavior. The protocol operates in the developer workflow, not in AYA's user-facing handoff.

## Cross-module packet authoring

Read [Common Packet Authoring Standard](docs/packet/AUTHORING_STANDARD.md), [module profiles](docs/packet/PROFILES.md) and [compiler usage](docs/packet/README.md) when changing or adding any host-to-agent information packet. Keep independent source-derived inventory, atomic host facts with source evidence and profile dependencies, actual output contracts, contextual examples/negative examples and source freshness. Run the compiler and regression tests, verify high-risk facts against the installed binary, and reject silent truncation or missing protective dependencies. A structural green check does not establish truth or provider ingestion. Never infer receiver success or monitor production agent responses.

## Documentation is a release-critical feature

**Read [docs/reference/INDEX.md](docs/reference/INDEX.md) and [docs/reference/AUTHORING_STANDARD.md](docs/reference/AUTHORING_STANDARD.md) before working on references.** For release-bound integrations **also follow** [ADVANCED_AUTHORING.md](docs/reference/ADVANCED_AUTHORING.md), [AGENT_WORKFLOW.md](docs/reference/AGENT_WORKFLOW.md), [TRACEABILITY.md](docs/reference/TRACEABILITY.md) and [EVALUATION_PROTOCOL.md](docs/reference/EVALUATION_PROTOCOL.md). Follow [TEMPLATE.md](docs/reference/TEMPLATE.md), [QA_RUBRIC.md](docs/reference/QA_RUBRIC.md), [QUESTION_BANK.md](docs/reference/QUESTION_BANK.md), and [MAINTENANCE.md](docs/reference/MAINTENANCE.md). The fictional ParcelPad reference illustrates structure but **never** provides real-app evidence.

When integrating AYA into another app:

1. Recover its actual code, latest released binary/build variant, shipped features, UI strings, release notes, tests and real errors. Do not treat plans, prototypes or open PRs as shipping behavior.
2. Make a full inventory of UI, tasks, settings, state-dependent behavior, permissions, provider variations, destructive effects, errors, accessibility and lifecycle.
3. Produce a UTF-8 guide with AYA-RAS v1 envelope and all twelve required sections. Each important feature/task/error must have a stable ID, version/status, exact steps, real evidence and user-safe troubleshooting.
4. Differentiate UNSUPPORTED (confirmed absent), UNKNOWN (not established), PLANNED (future intention), and conditionally unavailable features. No invented controls, support URLs, provider guarantees, external assistant powers or secrets.
5. Create a **separate, source-derived JSON inventory and held-out gold question set**; run `python3 tools/validate_guide.py --strict path/to/guide.md` plus `python3 tools/audit_reference.py path/to/guide.md --inventory path/to/inventory.json --questions path/to/questions.json --strict`; complete a manual behavior/evidence audit and held-out question-bank evaluation.
6. For large apps, use [modular reference builds](docs/reference/MODULAR_BUILDS.md) so the exported reference is deterministic and self-contained. Ship the guide with the exact installed version and keep it updated in the same PRs that modify user-facing product behavior.
7. Verify Android recipient behavior on **dated app and OS versions**; keep [compatibility ledger](docs/PROVIDER_COMPATIBILITY.md) factual.

## Optional Translation Kit integration

- Read [Translation Kit module](docs/translation/README.md) and [developer authoring standard](docs/translation/AUTHORING.md) before introducing localization handoffs. Host language selection, import, validation, rollback, fallback and live UI updates remain host-owned. The AYA prompt card must be subordinate to normal language settings.
- Source-derive every stable key, shipped source string, meaning, placeholder/plural type, risk label, technical glossary and Rosetta counterexample from the *exact installed* app build. Never substitute the fictional ParcelPad kit as evidence for a real app or invent a language importer.
- Use `Aya.launchTranslationBundled()` and an exact-version `aya-guide.md` plus `aya-translation-kit.md`. AYA verifies identity/shape but not semantic correctness or valid returned packs. Keep model-produced notes distinct from developer-approved constraints; use explicit no-data-loss ambiguity rules.
- Preserve the one-file reviewed UTF-8 Share path and derived final `EXTRA_TEXT`, 1 MiB kit and 2 MiB combined limits, no provider-specific API, no background response tracking and no automatic return/import. Do not promise a language pack was created simply because the Sharesheet opened.
- Run `python3 tools/validate_translation_kit.py docs/translation/examples/parcelpad-translation-kit.md --schema docs/translation/examples/parcelpad-output.schema.json --example docs/translation/examples/parcelpad-pirate.pack.json` plus unit/reference checks. Test bad placeholders, wrong versions, missing headings and high-risk copy.

## Host card integration

Follow [AYA Card UI Standard v1](docs/CARD_UI_STANDARD.md). Prefer `AyaCardView` as the host-native Standard layout or implement an equivalent custom card with the same content and two-stage review semantics. Logo tint follows host foreground; outline/corners follow host theme; question is optional. Always disclose the actual intended attachment without promising receiver ingestion. Do not introduce a Compose dependency in the core Android SDK merely to render the card. Validate layout and TalkBack on narrow/mobile screens.

## Engineering constraints
- AYA's evidence registry is **read-only** and initially empty. Device QA must match recipient package, app version, Android SDK, account state and exact transport. Published claims or intent filters are NOT verified ingestion. Do not introduce package sweeps, telemetry, success monitoring or automatic recipient selection.
- The optional `AyaAssistContext` adapter is Android's separate system-assistant request surface, and must only be wired into a host after explicit host approval of the exact public context. Do not enable it implicitly, send private identifiers, or misrepresent Android JSON-LD as the AYA handoff format.
- `aya-handoff/v1` JSON Schema documents host-to-AYA exchange for future adapters; the active Android SDK still uses typed Kotlin and reviewed `ACTION_SEND`, and **does not parse or send this JSON automatically**.
- AppFunctions, ACTION_PROCESS_TEXT, and reference images remain separate opt-in design candidates, not dependencies of core AYA. Never add delegated actions or agent callbacks without their own security design.
- Creative UX is **prompt-first**: Share request and Copy request transmit only the edited visible generation prompt; Full guide explicitly opens the complete editable reference and optional attachment path. Guide identity is still validated at launch. Never regenerate an old direction when expanding a modified prompt.

- Creative Handoff uses `Aya.launchCreativeBundled()` with `AyaCreativeTask` and `AyaImageRequirements`. Preserve the same guarded AYA-RAS reference, editable preview, final-review-derived message text, and no-return boundary as help. Consult [creative contract](docs/CREATIVE_HANDOFF.md) and [creative authoring extension](docs/reference/CREATIVE_AUTHORING.md).
- Creative requests may use text-only or full-reference sharing. Text-only must never silently truncate or refer to a nonexistent attachment; test final edited request extraction and the absence of file/URI grants. Preserve the same one-way user-controlled boundary.
- For image generation, include a standalone explicit generation instruction in approved `EXTRA_TEXT`, not just an attachment, and never promise that a recipient will generate or save an image. Image import remains the host app's responsibility; AYA never watches or handles an assistant's output.
- Do not autoattach artwork, images, metadata with secrets, paths or account IDs; optional reference-image support is **not implemented**. Guard typed image requirements and verify host import truth independently.

- Prefer `Aya.launchBundled()` and an exact-version, real-package APK guide over manually assembled help context. The code must reject mismatched/missing guides before review; never silently fall back to stale data.
- Public Android `ACTION_SEND`, one self-contained UTF-8 file, read-only content URI grant.
- Default to AYA's question-first composer, allowing the user to type in the host app; when a host already captures the question, pass `askQuestion=false` to avoid duplicate prompts.
- Share exact approved question as `EXTRA_TEXT` alongside `EXTRA_STREAM` to improve interoperability, but derive it from **final edited preview** (no hidden/stale original data).
- Show exact editable payload before sending, with Cancel and Copy fallback.
- Do not silently collect/send runtime diagnostics, tokens, IPs, account IDs, private file paths or logs.
- Receiving apps determine attachment ingestion and new-chat behavior; do not promise one-tap completion. See `docs/ANDROID_SHARING_RESEARCH.md` for platform evidence and source links.
- Respect FileProvider scope and file lifetime. Test keyboard, screen readers, repeated shares, large guides, no share targets and Activity lifecycle.
- The Android sample is a real app (`dev.aya.sample`) with its own validated guide. ParcelPad is a separate, intentionally fictional documentation example; never conflate them.

## Required checks

```sh
python3 tools/validate_guide.py --strict docs/reference/EXAMPLE_PARCELPAD.md
python3 tools/audit_reference.py docs/reference/EXAMPLE_PARCELPAD.md --inventory docs/reference/examples/parcelpad_inventory.json --questions docs/reference/examples/parcelpad_questions.json --strict
python3 -m unittest discover -s tools -p 'test_*.py'
gradle :aya:testDebugUnitTest :aya:assembleDebug :sample:assembleDebug
```

On GitHub, use the provided Actions workflows. Do not claim tests were run without actual evidence. If CI is blocked or failing, identify failure precisely and leave it documented. Do not merge a product change while required checks are red.

## Prioritization

Prefer an integrated working handoff, truthful app-specific docs and real-device acceptance over additional speculative features or untested compatibility layers. Treat hallucinated user instructions and accidental sensitive disclosures as release-blocking defects.
