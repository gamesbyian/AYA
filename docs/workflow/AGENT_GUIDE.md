# Coding-agent playbook: design a pre-handoff workflow

Use this playbook only when the adopting host needs user decisions before an AYA handoff. Simple Ask Your Agent help cards do not require a workflow engine.

## Protocol

1. **Discover:** inspect the actual host, installed variant and existing settings. Read [AYA-AUF](../understanding/README.md), [Module Portability](../MODULE_PORTABILITY.md) and applicable packet profile. Separate evidence from aspirations.
2. **Model:** state the user's goal and what successful agent output would look like; identify the smallest set of genuinely consequential user decisions.
3. **Design:** write questions in user vocabulary, with appropriate types, default explanations, applicability rules, safe hidden-state policy and accessibility review.
4. **Resolve:** map answers to a typed intermediate task; specify conflicts, dependencies and prohibited combinations before generating text.
5. **Compose:** choose fragment, structured or compound mode; preserve all constraints and the original user's intent. Use deterministic runtime composition by default.
6. **Verify:** generate representative and adversarial combinations, inspect traces, test edit/reopen transitions, and verify host capability assertions against the installed app.
7. **Integrate:** add the resulting prompt to an existing AYA user-approved review/Copy/Share path, keeping attachment and import behavior host-owned.
8. **Maintain:** link rules to source evidence and version changes. When a host capability changes, revise associated questions, task mappings, references and tests together.

## Deliverables for the adopting host

- Decision inventory: IDs, user language, answer meanings, applicability, risk and controlling feature evidence.
- Question schema and conditional navigation.
- Resolver rules and typed task specification.
- Composer implementation and prompt-section design.
- Bidirectional trace of answer -> task field -> instruction.
- Exhaustive or risk-based combination tests, negative fixtures and manual review checklist.
- Explicit limits of what the host, AYA and selected assistant can actually verify.

## Autonomy and escalation

Investigate technical details independently. Ask the developer only for consequential unresolved product decisions; follow [DCP](../understanding/CONSULTATION.md) and preserve deferred decisions. Do not assume that a plausible control or output is supported by the host. Do not send private answers without user approval.

## Completion criteria

A generated workflow is eligible for host adoption only when questions are understandable, every reachable selection set is valid or clearly rejected, resulting prompts are coherent and traceable, host-specific claims are evidenced, and the user reviews the actual handoff payload. Never use structural validation alone as evidence of recipient interoperability.
