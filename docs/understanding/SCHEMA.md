# AYA-AUF data contracts

The versioned [Host Concept Model schema](schemas/aya-understanding-v1.schema.json) defines a host's product thesis, concepts, user goals, design principles, truth-classified claims and unresolved ambiguities. The [Director Decision Record schema](schemas/aya-director-decisions-v1.schema.json) contains decision status, attribution, question, interpretation, response, source, scope and review trigger.

Both files use the same app ID and source revision. The concept model also identifies the exact shipped app version. For production models, use immutable and specific source references and separate product objectives from code observations. Never describe a hypothetical example as a verified release.

## Semantics

- `CONCEPT-###`: user-facing entity, relationship, synonyms, lifecycle and distinct identity.
- `GOAL-###`: user's intended outcome, relevant concepts and observable success criterion.
- `PRINCIPLE-###`: scoped policy, trade-off, design intention or guidance, sourced and truth-classified.
- `CLAIM-###`: statement about intention, implementation, observation or expectation, scoped to evidence.
- `AMB-###`: meaningful unsettled question; `consultation_needed` records whether director input is required.
- `DEC-###`: consultation event, with status confirmed/provisional/delegated/deferred/superseded.

A deferred record may document an **unanswered** question, as in the fictional fixture, but does not provide an affirmative director decision. Explicit director confirmation must be supported by actual communication evidence, not an LLM's plausible paraphrase.

## Integrating with AYA packet facts

This model sits upstream of [`aya-packet-source/v1`](../packet/schemas/aya-packet-source-v1.schema.json). Reference relevant concept and goal IDs in a separate crosswalk during authoring or in source evidence, then derive `FACT-###` records from verifiable behavior, approved product intent and scoped uncertainty. The existing packet compiler continues to validate and assemble fact records, not to infer product policy from the AUF model.

The model validator checks internal structure and referential integrity, not the depth of user research, real director approval, completeness of app discovery or strength of source evidence. Do not describe its output as an independent epistemic certification. Use independent scenario challenges and real-host trials.
