# Modelling the host before documenting it

## Pass 1: Reconstruct purpose

Write a short product thesis answering: whose problem the app addresses; the outcome users want; what makes success observable; how this app differs in approach; what is deliberately automated; what remains user-controlled; and what it explicitly declines to do. Cite source evidence for declared intentions. README copy alone is insufficient.

Identify user **situations and literacy**, rather than asserting demographic stereotypes. Record novice/expert expectations, accessibility, offline/remote context, and what normal users would call each activity.

## Pass 2: Recover the domain ontology

Inventory user-facing **concepts, not only implementation classes**. For each core object, record:

- Stable concept ID, preferred user term, technical term, synonyms and near-miss terms.
- What makes it a distinct thing; owner and authority; relationships to other concepts.
- Creation, mutation, state and deletion lifecycle.
- Persistent/temporary, local/remote/external and privacy consequences.
- Familiar user misconceptions and forbidden conflations.
- Evidence for implementation semantics versus product intention.

Draw a relationship graph or provide `related_concept_ids`, especially where operations involve two different objects (a transfer definition versus its downloaded files). Avoid collapsing distinct concepts for convenient prose.

## Pass 3: Understand goals before controls

Build a goal → capability → constraint → outcome map. Describe user intent without assuming the user knows app terminology. Identify supported, conditional, planned and impossible goals, potential fallbacks, and external decision-makers. For every major goal, state which observation actually verifies success and which UI signal merely means an attempt was accepted.

## Pass 4: Reconstruct interaction philosophy

Recover the hierarchy of automation, control, simplicity, expert detail, recoverability, privacy, accessibility, and speed. Identify **principles**, with their applicability and exceptions, then explicit **design tensions**: what wins when speed conflicts with correctness, automation with confirmation, or convenience with durable data preservation? Reference actual decisions and product specifications, never infer universal priorities from one implementation.

## Pass 5: Investigate the user's mental model

For each important workflow, ask how a user might naturally phrase the goal, which assumptions a competing app might foster, which states are hidden, and which apparently similar controls have different consequences. Include mistakes, novice terms, likely missing features, and what users do *not* know to ask. Source actual research separately from predicted misunderstandings.

## Pass 6: Separate truth categories

Every consequential claim must have a declared `truth_kind`:

- `intention`: director-approved or clearly attributed product goal; not proof of shipping behavior.
- `implemented`: behavior supported by code for a specified build and applicability; not proof of success.
- `observed`: recorded execution, screenshot fixture or accepted test run with scope.
- `expectation`: actual user research or explicitly labelled hypothesis about user understanding.

A disagreement requires an ambiguity record. Never synthesize "the app does X" from "the director wants X" or from a UI resource string alone. External/provider claims need freshness and controlling-authority boundaries.

## Pass 7: Test model coherence

Challenge the model with **unseen composite situations**, not just feature names. A good model should help the developer agent identify the facts needed to investigate an unfamiliar request, while refusing to invent steps or guarantees.

Examples to adapt: a user targets the wrong remote environment; an asynchronous operation appears complete before server acknowledgement; importing an older file changes only some settings; resetting one workflow might destroy unrelated local data; a style translation would change a destructive button's meaning. Ask "what evidence would resolve this?" rather than filling in an assumption.

## Reverse interview

After discovery, summarize the inferred product thesis, key concepts and contested distinctions, top user goals, design principles, unsupported expectations and unresolved ambiguities for the director. Ask for correction **only where approval or clarification changes a consequential conclusion**. Label the model provisional until the relevant scope is confirmed. Do not equate silence with approval.

## Outputs and maintenance

Create a versioned Host Concept Model conforming to [SCHEMA.md](SCHEMA.md). Link real `FACT-###` records from the [packet source](../packet/README.md) using explicit concept/goal relationships. Reevaluate affected entries whenever product intentions, shipped behavior, importer semantics, UI labels or upstream authorities change. Keep superseded director decisions for provenance; never silently rewrite an earlier answer.

**Scope scaling:** tiny apps may use a few concepts and goals; complex applications should split reviewed sources while exporting one coherent model. Complexity of user meanings, not line count, determines required detail.
