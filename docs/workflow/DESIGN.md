# Human-centered workflow design

## Goal first, questions second

Before adding a question, record the user's goal, observable successful result, host capabilities and the intended recipient's role. Derive the smallest set of decisions that can affect instructions or required context. A question that produces no meaningful difference in the task should be removed, inferred from verified host state, or made an optional explanatory preference.

For each decision record:
- Stable ID, user-facing phrase, plain-language alternatives and choice type (binary, single choice, multi-select, bounded input, or free text).
- Meaning and effect of each answer in the domain ontology; do not make a human interpret model jargon.
- Applicability and visibility predicate; prerequisites and incompatible choices.
- Default and source of default (host evidence, explicit user preference, safe fallback); whether omission means unknown, false, not applicable or deliberately skipped.
- Which task-specification fields it controls; side effects, risk and privacy classification.
- Accessibility requirements and how the person can revisit or edit the answer.

## Interaction rules

Prefer one coherent decision at a time where sequencing clarifies dependencies, but do not force a wizard when a compact form communicates better. Present consequential choices before cosmetic refinements. Reveal dependent questions progressively and explain why newly presented questions matter. Preserve navigation flexibility, keyboard and screen reader access, labelled states, touch targets, state restoration and an accessible review step.

A hidden question must have a documented state policy: **clear**, **retain but ignore**, or **revalidate when shown**. Hidden stale answers must never silently modify the task. Distinguish unset from false, and avoid auto-answering a risky question solely because a switch defaults to off.

Explain tensions and conflicts to users in terms of outcomes. For mutually exclusive settings, consider a single-choice control instead of multiple toggles. Do not silently override a prohibition when some other requested feature requires breaking it.

## Question necessity checklist

For each question ask:
1. What genuinely different instructions, inputs or permissions result?
2. Can reliable existing host state supply the answer instead?
3. Is the distinction intelligible without explaining the agent implementation?
4. Can the user predict the main consequence of each choice?
5. Does it require product-director approval because semantics are not yet established?
6. Will an omitted answer be treated correctly?
7. Does it expose sensitive information or create a destructive, financial or irreversible result?

## Example (fictional)

A fictional image editor offers task = restore / reinterpret. A separate preservation choice might apply in both modes, but selecting restore plus unrestricted geometry changes could be contradictory. The designer may replace two conflicting toggles with a more coherent single selection, or the resolver may ask for an explicit conflict resolution.

This fixture is illustrative, not evidence of any host's editing capability or a guarantee of assistant results.

## Consultation and evidence

Follow the [Director Consultation Protocol](../understanding/CONSULTATION.md) when a decision changes product meaning, authorization, or safety. A director-approved intention does not demonstrate implementation. Every selectable action requiring a real importer or host control must be corroborated against the installed version before authoring a claim about it.
