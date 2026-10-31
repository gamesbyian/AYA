# Director Consultation Protocol (AYA-DCP v1)

This protocol governs **developer-agent consultation with the project's authorized human or designated director** during Host Concept Model construction. It neither modifies the app's runtime handoff nor asks the end user to act as the project director.

## Default: investigate first

Inspect source, shipped behavior, specifications, issues and prior director decisions before interrupting anyone. A question qualifies for consultation when:

1. It changes a consequential product principle, user-facing meaning, priority, safety boundary, or packet guidance.
2. No reliable, current authorized decision resolves it.
3. The agent cannot safely establish the intention by technical inspection alone.

Do **not** ask a director to find a class name, explain an existing build flag, reproduce a readily runnable test, or repeat a documented decision. Do not ask for credentials or private records.

## Adaptive interview

Select from [QUESTIONS.md](QUESTIONS.md) or adapt one to the observed uncertainty. Use this concise structure:

- **Observed evidence:** what is actually known, with version and source.
- **Provisional interpretation:** what the agent currently thinks, labelled as inference.
- **Question:** one meaningful decision or distinction.
- **Consequences:** which product model, UX, specifications or AYA packet facts would change depending on the answer.
- **Options when useful:** plausible non-leading choices, including "depends", "delegate", "defer", and a freeform response.

Batch closely connected issues only when the director can make decisions in one coherent exchange. Use the smallest number of questions required. Critical ambiguities may be blocking; minor uncertainties should not interrupt productive work. Record questions already asked to avoid repetitive consultation.

## Director answers and states

A director may confirm, correct, qualify, explicitly delegate a scoped choice, defer an unsettled decision, or say the available evidence is insufficient. Respect that result.

Use a **Director Decision Record** with question ID, referenced ambiguity, original observation and interpretation, verbatim or faithful paraphrase of the response, decision status, scope, authorized actor/role, date and source reference, affected concepts/principles/goals, and next review trigger.

Statuses:
- `confirmed`: explicit applicable direction.
- `provisional`: an interim direction whose applicability/review trigger is recorded.
- `delegated`: an explicit delegation of judgement with boundaries, not invented consent.
- `deferred`: no decision yet; preserve ambiguity.
- `superseded`: replaced by another cited decision; retain historical record.

Do not call a hypothetical example a director-approved decision. Missing responses stay unresolved. A developer agent may independently choose implementation details within established delegation, but may not convert that into proof of observed app behavior.

## Escalation priority

Ask sooner when ambiguity affects destructive operations, permissions, ownership, financial outcomes, critical accessibility or fundamental product identity. For less consequential uncertainties, document an assumption and continue reversible work. A required unanswered product choice blocks only the dependent packet claim or implementation, not unrelated tasks.

## Reverse interview and final director review

Present a brief concept-model synthesis: product thesis, intended users and goals, core domain distinctions, automation/control principles, trade-offs, mismatches between declared direction and shipping implementation, and the highest-impact unresolved questions. Invite corrections, not a ceremonial sign-off. Record explicit scoped approval if given. Silence does not count.

## QA

An independent reviewer checks that:
- No question was already answered in existing authorized records.
- Questions were non-leading and exposed meaningful alternative interpretations.
- Responses are attributed without fabricated authority, with status, scope and source.
- An unresolved question is not silently treated as confirmation.
- Model/packet claims based on decisions are labelled `intention`, while runtime claims require implementation/observation evidence.
- Superseded or delegated decisions are not applied beyond their legitimate scope.

The validator checks linkage and structural completeness; it cannot verify that a director actually spoke or that the response is authentic.
