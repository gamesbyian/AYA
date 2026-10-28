# The AYA reference-document system

**AYA-RAS** is a documentation-as-product discipline for app-specific AI support. Authors first discover what truly ships, model the states that change behavior, and build a versioned guide. Independent inventories and held-out questions verify breadth and accuracy. A downstream assistant sees a self-contained reference, not an assertion of authority or permission to control the app.

## Core reading order

1. [Base authoring standard](AUTHORING_STANDARD.md): required envelope and 12-section structure.
2. [Advanced authoring](ADVANCED_AUTHORING.md): partial state model, conditional capability, high-information diagnoses, provenance, accessibility, context budgets and hallucination traps.
3. [Agent workflow](AGENT_WORKFLOW.md): reproducible instructions for taking an unfamiliar app repository through release-grade documentation.
4. [Template](TEMPLATE.md): copyable guide envelope and procedures.
5. [Independent traceability](TRACEABILITY.md): inventory denominator, evidence, ID cross-checks.
6. [Question-driven evaluation](EVALUATION_PROTOCOL.md) and [quality rubric](QA_RUBRIC.md): gold tests and explicit release blockers.
7. [Question bank](QUESTION_BANK.md): starting scenarios, not a substitute for app-specific held-out cases.
8. [90-question cross-category stress test](CROSS_CATEGORY_STRESS_TEST.md): real-world prompts that challenge cross-app journeys, upstream policy drift, negative capabilities and high-stakes answers (not verified facts about third-party apps).
9. [147-question second-batch stress test](CROSS_CATEGORY_BATCH2.md): 21 additional seven-question app inventories, with a [machine-readable prompt fixture](examples/cross_category_batch2_147.json) and transaction/authority/notification/hidden-state/recovery acceptance lenses (not verified third-party gold answers).
10. [Modular builds](MODULAR_BUILDS.md): deterministic, validated assembly of large guides.
11. [Maintenance](MAINTENANCE.md): release drift and ownership.
12. [Fictional sample](EXAMPLE_PARCELPAD.md): complete illustrative guide with [inventory](examples/parcelpad_inventory.json) and [gold cases](examples/parcelpad_questions.json). **Not evidence of a real app.**

## Automated contract

```sh
python3 tools/validate_guide.py --strict docs/reference/EXAMPLE_PARCELPAD.md
python3 tools/audit_reference.py docs/reference/EXAMPLE_PARCELPAD.md \
  --inventory docs/reference/examples/parcelpad_inventory.json \
  --questions docs/reference/examples/parcelpad_questions.json --strict
python3 -m unittest discover -s tools -p 'test_*.py'
```

The first check verifies syntax, the second checks independent declared coverage and references, and the last runs regression tests. **None proves the guide is truthful or the recipient assistant will behave correctly.** An independent release/binary audit and actual assistant question trials are release gates.

## Product contract

The host app ships **version-matched, non-personal, self-contained UTF-8 reference material** alongside the installed APK. AYA displays the export for user review before any third-party handoff. Do not assume the receiving assistant can browse, execute tools, access the app screen, or ingest a large attachment correctly.

A useful reference explains what features exist, where the user finds them, how actions behave across states, what outcomes prove success, how to diagnose failures, what harms and tradeoffs matter, and what remains unknown. **Version truth, safe uncertainty and practical recoverability outrank length.**
