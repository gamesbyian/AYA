# The AYA reference-document system

This is the **authoritative playbook for authors, maintainers and coding agents** preparing app-specific help for AYA. AYA's handoff quality is limited by the quality and freshness of the app reference. Treat the document as a tested product artifact, not a marketing brochure.

Start in this order:

1. [Authoring standard](AUTHORING_STANDARD.md): discovery, required coverage, truth model, writing rules and export strategy.
2. [Copyable template](TEMPLATE.md): structure and metadata accepted by the validator.
3. [QA rubric](QA_RUBRIC.md): measurable completeness criteria and release gates.
4. [Question bank](QUESTION_BANK.md): adversarial and ordinary questions to test with and without an assistant.
5. [Maintenance lifecycle](MAINTENANCE.md): update and ownership rules.
6. [Modular builds](MODULAR_BUILDS.md): deterministic, validated assembly of large references from maintained source modules.\n7. [Example fictional application](EXAMPLE_PARCELPAD.md): a fully populated guide, not a claim about a real product.

Validate a candidate: `python3 tools/validate_guide.py path/to/aya-guide.md`. Run `python3 -m unittest discover -s tools -p 'test_*.py'` for validator tests.

## Contract

An app ships a **version-matched, UTF-8 Markdown or text guide**, which AYA includes verbatim within a separate help package identifying the installed app/version and user's starting question. AYA intentionally **does not invent documentation** or infer app internals from a screen name.

A complete guide must allow an assistant to answer both "what can this app do?" and "how exactly do I perform/recover from this operation?" without fabricated controls. It needs task-level instructions, state-dependent behavior, real error strings, permissions, and version-qualified limitations.

Use a *safe, generic* static core guide for v0. Contextual runtime data requires separate opt-in disclosure and redaction before share.
