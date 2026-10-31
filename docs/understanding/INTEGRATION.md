# Developer-agent adoption protocol

Agents implementing AYA in a host repository should conduct these phases in order:

1. Inspect actual shipped source, product plans, UX documents, user research, issues and prior decisions. Build a **provisional thesis** and concept/goal map separately from a feature inventory.
2. Identify distinctions critical to meaning, common user misconceptions and intended balance between defaults, automation and expert control.
3. Classify claims as `intention`, `implemented`, `observed` or `expectation`. Preserve contradictions as `AMB-###` entries.
4. Ask relevant [director consultation questions](CONSULTATION.md) only where interpretation or consequential direction is still unsettled. Record scoped answers, delegation and deferral.
5. Give a short reverse interview summarizing the inferred application for confirmation; do not invent approval or block unrelated productive work while awaiting a response.
6. Validate AUF and decision files, then derive AYA-RAS inventory and [shared packet source](../packet/README.md). The receiving assistant should get task-appropriate concepts and warnings, not an unfiltered copy of the whole development history.
7. Independently evaluate the resulting Help, Creative, Structured Artifact and Translation packets against shipped application behavior and controlled agent trials.

### Consultation snippet (illustrative, not a required script)

> I found the application has a manual advanced setting for X, but its UX guidance prefers automatic defaults. My provisional interpretation is that X should be optional for typical users. Is that a general product intention or a deliberate exception? This affects how AYA describes default behavior. It's fine to delegate, qualify or defer.

Developer agents should ask their existing authorized project director in the **normal development conversation or project workflow**, rather than creating a new account, external survey service, or AYA runtime feature.

### Adoption check

A repo can start with a small concept model and incrementally fill it. If consequential product intentions are unresolved, the AYA packet must not claim they are authorized, and future development should link the clarification record before updating product policy. Do not wait for director input to verify already-shipped UI labels, tests or code paths.
