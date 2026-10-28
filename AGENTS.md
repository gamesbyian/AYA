# AGENTS.md — instructions for coding and documentation agents working in AYA

## Mission

AYA is an Android BYO-assistant help handoff. The user selects a third-party assistant. The host app supplies a precise, *installed-version-matched* reference and optionally a question/screen hint. AYA previews the exact payload and sends one file through Android's public Sharesheet. Do not introduce model hosting, hidden telemetry, proprietary assistant dependencies, or unsupported claims about what recipients do.

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

## Engineering constraints

- Public Android `ACTION_SEND`, one self-contained UTF-8 file, read-only content URI grant.
- Show exact editable payload before sending, with Cancel and Copy fallback.
- Do not silently collect/send runtime diagnostics, tokens, IPs, account IDs, private file paths or logs.
- Receiving apps determine attachment ingestion and new-chat behavior; do not promise one-tap completion.
- Respect FileProvider scope and file lifetime. Test keyboard, screen readers, repeated shares, large guides, no share targets and Activity lifecycle.
- Keep sample application fictional; never confuse its scenarios with real app features.

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
