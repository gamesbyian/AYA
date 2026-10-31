# AYA Application Understanding Framework (AYA-AUF)

**Status:** normative developer-agent authoring method and optional build-time validation. It precedes [AYA-RAS](../reference/AUTHORING_STANDARD.md) and the [Packet Authoring Standard](../packet/AUTHORING_STANDARD.md). It does not alter AYA's one-way Android handoff, grant an agent access to the host, or solicit the host app's users.

A developer agent must understand **why the app exists, for whom, what concepts it contains, which user goals its capabilities serve, what the director intends, and what the shipped build actually does** before authoring a reliable packet. An exhaustive repository feature inventory alone cannot establish those relationships.

## Start here

1. [Conceptual discovery and modelling](MODEL.md): investigate purpose, user intentions, domain ontology, mental-model mismatches, automation philosophy, operating boundaries, design tensions, and observed behavior.
2. [Director Consultation Protocol](CONSULTATION.md): derive contextual questions from actual ambiguities; record decisions and delegated judgment without interrupting routine work.
3. [Adaptive question bank](QUESTIONS.md): a reusable repertoire, never a mandatory long form.
4. [Machine-readable model format](SCHEMA.md): concepts, user goals, principles, ambiguities, evidence, and director decision references.
5. [Fictional example](examples/parcelpad-understanding.json) and [illustrative decision record](examples/parcelpad-decisions.json). These are teaching fixtures, not assertions about a real application.

## Expected workflow

```text
Released app + product plans + research + decisions
                     |
                     v
Independent concept discovery and provisional understanding
                     |
            Significant ambiguity?
             /              \
           yes               no
            |                 |
Contextual director question  |
            |                 |
Versioned decision record     |
             \               /
              v             v
    Evidence-scoped Host Concept Model
                     |
        AYA-RAS / shared FACT source
                     |
        Profile-specific AYA packets
                     |
     Independent host/assistant trials
```

### Scope and truth

Maintain **four independent propositions**: product intention (approved direction), implemented behavior (code and released build), observed result (executed test), and user expectation (research/inference). Their disagreements are discoveries, not errors to smooth over. A director can authorize intended behavior, but cannot retroactively prove a shipping feature. A reviewer should reject unexplained conflation.

Consultation is expected where it affects product interpretation, but **not mandatory interruption**. Research first, ask only consequential unresolved questions, and continue safe independent tasks when the director is unavailable. An answer of "you decide" is a scope-limited *delegation*, not an implicit product-wide policy.

A director's answer must be attributable and accurately transcribed, with scope and date. Do not invent quotes, decisions, approvals, or verification. Never solicit credentials or personally sensitive information.

## Local validation

```sh
python3 tools/validate_understanding.py \
  docs/understanding/examples/parcelpad-understanding.json \
  --decisions docs/understanding/examples/parcelpad-decisions.json
python3 -m unittest discover -s tools -p 'test_*.py'
```

For packet compilation, pass `--understanding <model.json> --director-decisions <decisions.json>` together to `tools/packet_compiler.py`. It validates the consultation records and refuses to compile from an AUF model whose app ID, exact version or source revision conflicts with the fact source. The flags are optional for existing consumers; any adoption claiming AUF coverage should use them in CI.

This validator checks provenance, identities, relationships, unresolved ambiguities and decision references, not the truth or completeness of a model. A separate reviewer must check the actual app, confirm director responses, and challenge the model with novel user scenarios.

## Output contract

An AUF-complete integration provides a versioned concept model, a separately sourced independent capability inventory, an uncertainty/consultation queue, and any authorized decision records. The developer agent presents a short **reverse interview**, summarizing its understanding and assumptions, before claiming director approval. Packets must inherit source-backed semantics and applicable decisions while retaining version-specific evidence. When consultation is unavailable, tag unknown intentions and prohibit automatic promotion of assumptions to product policy.
