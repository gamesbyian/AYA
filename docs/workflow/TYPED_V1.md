# Typed Workflow Composer v1: experimental portability contract

This developer-side reference adds **typed questions**, **nested predicates** and **ordered instruction clauses**. It does not replace the existing v0 demonstration, change AYA's one-way handoff, or ship a production Android/Apple integration.

## Run

From the repository root:

    python3 -m unittest tools.test_workflow_composer tools.test_workflow_composer_v1 -v
    python3 tools/workflow_composer_v1.py docs/workflow/examples/fictional-visual-v1.json docs/workflow/examples/fictional-visual-v1-answers.json --trace

The typed implementation is [tools/workflow_composer_v1.py](../../tools/workflow_composer_v1.py), and its structural shape is described by [JSON Schema](schema/aya-workflow-v1.schema.json). Conformance cases are in [visual-v1-cases.json](conformance/visual-v1-cases.json). A future implementation in Swift, Kotlin or JavaScript should parse the same workflow, consume the same answer objects, and produce the same resolved sections, normalized answers and ignored-answer set. Tests are a *minimum*, not certification.

## Inputs and semantics

Questions have stable IDs, plain-language prompts, and a type:
- **boolean:** JSON true/false, not integers or strings; no options list.
- **choice:** exactly one string from declared options.
- **multi:** a list of unique declared option strings; canonical results follow option declaration order, regardless of the user's click order.

Questions can be required, optional or have typed defaults. A conditional question uses a \`when\` predicate. An answer to a hidden question is ignored, including when it was previously entered and retained by a UI. An unanswered visible optional question remains absent; its absence is neither false nor negative consent.

Predicates have exactly one of: \`{"question":"id","equals":value}\`, \`{"question":"id","contains":"option"}\` (multi only), \`{"all":[...]}\`, \`{"any":[...]}\`, or \`{"not":predicate}\`. The \`not\` operator does **not** treat a missing or hidden referenced answer as affirmative evidence for the inverse. Cross-question references are checked, and conditional question cycles fail validation.

Every rule has a stable ID, section, literal text, optional predicate, and optional list of \`after\` rule IDs. Dependencies must remain within the same section; active rules whose declared predecessors were not selected fail rather than silently changing meaning. A stable topological order controls text composition. The four output sections are Task, Operations, Constraints and Requested output.

Explicit conflicts use a predicate and human-readable explanation. Detecting undeclared semantic conflicts remains a host-author responsibility. No LLM is called at runtime. Source material and arbitrary free text are intentionally excluded from this small prototype.

## Conformance and security boundaries

The [test corpus](conformance/visual-v1-cases.json) covers expected results and explicit failure cases, including hidden stale answers, multi-select normalization, required dependent questions, and strict booleans. The [unit suite](../../tools/test_workflow_composer_v1.py) also covers cycles, malformed shapes, invalid references, navigation order independence and rule dependencies. The developer-side CLI writes inspectable text to stdout; it does not share it with any assistant.

A host remains responsible for disclosure of private selections, prompt/attachment inspection, authoring and verifying capabilities against the installed app, final editable review, Copy/Share, manual return/import, and output validation. A JSON Schema validating an input's shape cannot establish that its questions are intuitive, that the generated prompt is semantically correct, or that an external assistant supports the requested task.

**Versioning:** v0 and v1 are independent experimental formats. Do not silently reinterpret a v0 document as v1 or imply a stable public SDK API. Introducing richer rules should continue to be driven by demonstrable user workflows rather than adding an unrestricted expression language.
