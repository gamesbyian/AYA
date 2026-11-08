# AYA Workflow Composition: developer guidance (proposal v0)

**Status: design guidance only.** No Workflow Composer runtime, portable workflow schema validator, or cross-platform workflow adapter is claimed as implemented. AYA's existing user-reviewed one-way sharing remains the handoff boundary.

A host can ask goal-oriented questions, collect choices, and compile them into a coherent task for the user's preferred assistant. This optional capability is independent of the Help, Creative, Structured Artifact, Translation, Filesystem and Spatial handoff profiles.

## Begin here

1. Discover the host's actual user goals, supported capabilities and vocabulary using [Application Understanding](../understanding/README.md). Distinguish intended, implemented, observed and expected behavior.
2. Model consequential decisions **before** designing controls. Read [DESIGN.md](DESIGN.md).
3. Build a validated intermediate task intent from the answers, then compose an agent-facing brief. Read [COMPOSITION.md](COMPOSITION.md).
4. Apply [VALIDATION.md](VALIDATION.md) to questions, branching, combinations, resulting prompts and privacy.
5. Feed approved prompt and approved attachments into the existing AYA review/Copy/Share flow. Neither composition nor Share Sheet completion establishes recipient ingestion or output success.

## Conceptual layers

`Host evidence + user goal -> decision schema -> host-owned UI -> recorded selections -> intent resolver -> validated task specification -> deterministic composer -> exact user review -> platform share/copy`.

Host-specific questions, user-facing wording, defaults, actual features, output contracts and approval boundaries are defined by the adopting host. Reusable AYA guidance and future tooling must remain independent of real host product assumptions under [Module Portability Standard](../MODULE_PORTABILITY.md).

The same intent model may produce very different handoff narratives: a short additive instruction, a reordered set of constraints, or a multistage task with prerequisites. The composer must not reinterpret unselected answers as consent, or override explicit prohibitions to make a prompt prettier.

## Three adoption levels

- **Simple:** A few independent toggles safely append instructions. Preserve clear user review and test combinations.
- **Structured:** Branching questions resolve into a typed task specification, with dependencies, invariants, and contradiction handling.
- **Compound:** A validated graph of goals, operations, dependencies, constraints and output requirements is ordered into a coherent executable brief.

Do not build a dynamic orchestration engine when an ordinary form and a few deterministic rules are sufficient.

## Existing AYA boundaries remain unchanged

Host UI, permissions, persistence, import, output checking, provenance and capability verification are host-owned. The user must see and approve the exact content shared. Private answers and attachments require explicit disclosure; avoid silently bundling irrelevant answers. Never monitor assistant responses, assume an imported output exists, introduce a mandatory API key, or claim real-recipient acceptance based on synthetic tests.

## For coding agents

Read [AGENT_GUIDE.md](AGENT_GUIDE.md) before generating questionnaire code. For cross-module packets, also read the [Common Packet Authoring Standard](../packet/AUTHORING_STANDARD.md). Start with a fictional minimal fixture for any new reusable engine. No AYA default question should presume the behavior of a particular adopter.
