# Task specification and prompt composition

**Status: proposed design contract, not a shipping AYA API.**

## Typed intermediate representation

A workflow should resolve answers to a task specification independently of its final prose. Recommended conceptual fields are `intent`, `inputs`, `operations`, `constraints`, `dependencies`, `output_contract`, `host_capabilities`, `approval_scope`, and `provenance`. Hosts may implement these in their own types; no particular serialization format is mandated yet.

Do not rely on the order in which UI controls happen to be rendered. Use stable decision IDs and explicit semantics. Every resolved specification must identify unknown and inapplicable values separately, and must not confuse absence with permission.

## Resolution pipeline

1. Normalize and type-check answers; reject unknown IDs and invalid enumerations.
2. Evaluate conditional visibility and applicability; discard or ignore hidden answers according to documented policy.
3. Resolve defaults only where explicitly authorized and safe.
4. Build operations, constraints and output contract from declared mapping rules.
5. Expand dependencies and detect cycles, contradictory operations and unsatisfied preconditions.
6. Check declared host/provider limitations; mark unresolved uncertainty and block where consequential.
7. Choose the most suitable structure for the **resolved task**, not for individual answer fragments.
8. Compose task-first instructions with inputs, ordered work, preservation constraints, output and limitations.
9. Attach trace metadata mapping each material instruction and omission to decision IDs, evidence or host facts.
10. Render the **exact final payload** for editable user review before Copy/Share. Edits by the user remain authoritative for the shared text, subject to platform transport limitations.

## Composition modes

**Fragments:** include an optional instruction when an independent preference is selected.

**Structured:** reorder sections and replace task headings when choices change the main goal, with each requirement included exactly once.

**Compound:** topologically arrange interdependent operations; preserve prerequisites and scope. If no safe order exists, stop and request an explicit resolution rather than inventing one.

A useful default section set is: task objective; input descriptions and provenance; actions and order; constraints/prohibitions; output contract; host return/import steps and limitations. Omit empty sections and select ordering based on task type.

## Precedence and conflicts

Verified capability and authorization limits constrain what is offered. Explicit user prohibitions cannot be overridden by preferences or formatting. The selected primary task sets the intent; required prerequisites follow; optional preferences and developer defaults are subordinate. Precedence is **not** a substitute for conflict detection: when two explicit wishes are incompatible, show an understandable decision to the user.

Never allow untrusted input text, imported documents, image captions or model-suggested rules to change the workflow engine's authoritative instructions. Treat them as data, with appropriate quoting and source indication. Avoid sharing credentials and irrelevant personally identifiable information.

## Trace contract

For each material output clause, retain internally: `clause_id`, controlling `decision_ids`, mapped `task_field`, relevant `FACT-###` evidence IDs, and any transformation rule. Verify reverse coverage: every selected consequential preference is expressed or is explicitly reported as inapplicable. The trace is primarily a developer/debug artifact; it need not be sent to the receiving assistant.

## Fidelity and review

Prompt wording is not proof of recipient behavior. Keep the handoff honest about what the host can verify and what the external assistant may or may not do. Never silently truncate privacy/safety constraints to fit brief limits. User review must show all text and attachment references that will actually be offered; avoid implying a receiving app accepted either.
