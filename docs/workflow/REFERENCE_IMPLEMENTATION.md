# Workflow Composer reference implementation (experimental)

The small Python prototype at [tools/workflow_composer.py](../../tools/workflow_composer.py) uses only the standard library. It demonstrates deterministic multiple-choice decisions, conditional applicability, basic defaults, conflict rejection, prompt sections, and a local rule-to-answer trace. A [draft 2020-12 JSON Schema](schema/aya-workflow-v0.schema.json) now documents this deliberately limited input format. The Python runtime independently checks relevant shape and semantic constraints without requiring a JSON Schema library. This is **not** a production engine, a complete formal schema-validation implementation, a Kotlin/Swift SDK API, or a recipient compatibility guarantee.

## Run from the repository root

```sh
python3 tools/workflow_composer.py \
  docs/workflow/examples/fictional-image-workflow.json \
  docs/workflow/examples/fictional-image-answers.json --trace
python3 -m unittest tools.test_workflow_composer -v
```

The CLI prints composed text for **developer inspection**, not an automatic transmission. The optional trace is a local diagnostic, never an assertion that the recipient acted on the request.

## Minimal v0 format

A workflow JSON object includes `schema: "aya-workflow/v0"`, a nonempty `title`, `questions`, `rules`, and optional `conflicts`.

Each question has unique `id`, `prompt`, nonempty string `options`, optional `required`, optional `default`, and optional `when`: a map from question ID to exact option value. All conditions in a `when` map must match. A hidden question's old answer is ignored. Optional questions without a default or answer are absent, and their dependents are resolved as inapplicable rather than deadlocking. Unknown specification fields are rejected to reduce silent misconfiguration.

Each rule has unique `id`, optional `when`, a `section` of `objective`, `operations`, `constraints`, or `output`, and nonempty `text`. Rules are applied in definition order to their section; sections use fixed task-first order. A conflict has a nonempty `when` and explanatory `message`.

The reference implementation validates referenced IDs and condition values, rejects cyclic visibility dependencies, rejects invalid and unknown answer values, and requires a resolved objective. Rules are deterministic, but they cannot infer whether the resulting task is feasible or safe. A host integrating this as production code must add its own capability authorization, semantic conflict analysis, attachment consent, output contract validation, accessibility, localization, and final user review.

## Intentional limitations

- Only single-select string questions; no true booleans, free text, multiselect, numeric ranges, arbitrary predicates, or multi-stage dependency graphs.
- JSON Schema is provided for independent tooling, but CI currently checks fixture JSON syntax and Python runtime validation rather than running an external JSON Schema implementation. Shape checks and semantic reference validation are not exhaustive production assurance.
- There is no guaranteed protection against conflicting prompt text outside explicitly declared conflicts.
- The user-facing questions are host-authored; the CLI does not render UI or save user state.
- Output cannot be sent automatically to an agent, nor can agent output be observed or imported by this tool.
- No provider-specific prompt claims or performance evaluation have been made.

A dedicated [GitHub Actions workflow](../../.github/workflows/workflow-composer.yml) runs the unit suite and both fictional CLI examples when relevant files change. Small finite decision spaces are enumerated in unit tests; CI success does not prove semantic prompt quality.

The implementation's deliberate smallness makes a useful starting point for a future independent schema and platform-portable conformance suite. Expansion should be guided by actual host use cases and test invariants, not by speculative configurability.
