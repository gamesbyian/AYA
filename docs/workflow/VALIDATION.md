# Workflow validation and evaluation plan

**Status: test design guidance.** This document does not claim an implemented validator or recipient acceptance.

## Static checks

- Unique stable question, answer and rule IDs; valid answer types and allowed values.
- All referenced IDs exist; no dependency or prerequisite cycles.
- Reachability for questions and branches; no impossible or permanently hidden required question.
- Defaults are typed and documented; missing/unset/false/inapplicable remain distinct.
- Every meaningful answer has a traceable effect or an explicit no-op rationale.
- Contradictions, prohibition violations and unsupported host capabilities are diagnosed rather than silently overwritten.
- Every generated operation has necessary inputs, permissions and validated output conditions.
- No private or nonconsented data is bundled and no high-risk constraint is dropped through compact rendering.

## Combination coverage

Exhaustive enumeration is desirable for a small finite decision space. For larger spaces use pairwise coverage, targeted higher-order conflict sets, boundary values, hidden-state transitions and property-based generation. Include reset/edit/reopen behavior and stale selections; test interaction order independence when questions are logically independent.

## Required invariants

1. Selecting strict preservation cannot generate authorization to change preserved properties.
2. An answer to a currently inapplicable question cannot affect the composed request.
3. Equivalent valid answer states produce equivalent structured intent irrespective of UI navigation order.
4. Contradictory explicit selections produce a conflict outcome, never quiet priority-based replacement.
5. Every required output field is supported by the chosen operation and the host's real importer or truthful manual-return path.
6. The complete reviewed payload is exactly the payload supplied to Copy/Share to the extent controlled by AYA; transport delivery and agent ingestion remain unverified.
7. Every consequential selected preference maps to a traceable clause or a disclosed exclusion.

## Evaluation layers

**Structural:** schema and rule validator. **Semantic:** expert review against user goals and host capability evidence. **User interaction:** usability and accessibility tests, including revised answers. **Agent usefulness:** held-out tasks comparing generated briefs for completeness, clarity, feasibility and faithfulness. **Recipient:** dated app/OS/provider trials, separately scoped from output quality. **Host return:** independently validated importer or manual instructions, never presumed from a Share Sheet action.

Maintain golden fixtures, negative fixtures, decision matrices and an evidence ledger. A test passing at one layer does not qualify the higher layers.
