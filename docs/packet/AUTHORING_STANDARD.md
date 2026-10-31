# Common AYA Packet Authoring Standard v1

This document is normative for all AYA host integrations. It supplements the [12-section AYA-RAS Help Reference](../reference/AUTHORING_STANDARD.md), [Creative extension](../reference/CREATIVE_AUTHORING.md), [structured artifact profile](../STRUCTURED_ARTIFACT_HANDOFF.md), and [Translation Kit authoring](../translation/AUTHORING.md). Module-specific details cannot override its truth, privacy or disclosure boundaries. The [Module Portability Standard](../MODULE_PORTABILITY.md) also governs these profiles: generic AYA contract and tooling must not encode assumptions from any one adopting host. Source-derived app details belong in the host-authored packet, not the reusable module.

## Upstream prerequisite: understand the product

Before extracting facts for a packet, follow [AYA Application Understanding Framework](../understanding/README.md). Build a product thesis, domain ontology, goal-to-capability map, design principles and contradictions between intended, implemented, observed and expected behavior. Consult an authorized project director adaptively when material product interpretation is unresolved; record scoped decisions and deferrals. The AUF model informs shared facts but must not be treated as proof that intended features ship. See the [Director Consultation Protocol](../understanding/CONSULTATION.md).

## 1. Recover product reality before writing

Pin the **actual distributed app**: package, exact versionName/versionCode, variant, flavor, platform, feature flags and source commit. Never infer shipping behavior from open PRs, plans, tests that were not executed, or examples. Survey (a) navigational destinations/activities/Compose routes; (b) control callbacks, reducer actions, storage, remote calls; (c) strings and semantics; (d) permissions, lifecycle and accessibility; (e) service/provider variants and failures. Trace an action through observable UI, state persistence, and any remote consequences. Build a state matrix: absent/available/disabled, offline, permission denied, local/remote, concurrent changes, restart, retry, failure, rollback.

**Required developer milestones:** a build identity record; independently discovered fact inventory; source/evidence mapping; reviewed semantics and uncertainty; compiled packet; independent model/host test evidence; maintenance trigger. Mark UNKNOWN where evidence is missing. Do not fabricate a convenient account or provider capability.

## 2. Write atomic, typed claims in one source of truth

Maintain a JSON source conforming to [aya-packet-source/v1](schemas/aya-packet-source-v1.schema.json). One stable `FACT-###` describes one answer-relevant claim, with:

- `title`, concise `summary`, precise `details` and `applies_to` state/variant constraints.
- `status`: AVAILABLE, CONDITIONAL, EXPERIMENTAL, PLANNED, REMOVED, UNSUPPORTED or UNKNOWN.
- `impacts` including destructive, privacy, security, financial or accessibility where relevant.
- `profiles`: modules needing this fact. Allow reuse; avoid duplicating the same statement in competing module prose.
- `depends_on`: other fact IDs needed to interpret this claim correctly. A deletion action should depend on the fact identifying what is actually deleted.
- `evidence.kind`, `ref` and ISO 8601 `verified_at`; external assertions require `fresh_until`, with expiration causing compilation to fail closed. Distinguish observation, acceptance test, code, formal contract, external source and plan.

A fact claiming AVAILABLE cannot cite a plan or unknown source as its only evidence. The current validator checks that structural condition; it does not independently inspect the referenced commit or test. A second reviewer must audit the evidence and verify significant effects.

## 3. Build an independent discovery denominator

Produce [aya-packet-inventory/v1](schemas/aya-packet-inventory-v1.schema.json) from a separate pass over the host's shipped resources, source and observed behavior. Do not write the inventory by copying fact IDs from the authored packet. The inventory includes ID, applicable profiles, criticality and source ref. Reconcile the inventory to the authored fact source: discovered missing behavior becomes a blocking gap, not an invitation to prune the inventory.

The compiler enforces matching declared IDs, versions, profile memberships and basic evidence. **It cannot prove that the inventory itself is complete.** For a large app, independently challenge hidden controls, alternate states, error cases, negative capabilities and destructive side effects. Maintain source revision and a review history. Use held-out user questions to discover missing facts.

## 4. Design an agent-usable packet

A packet has seven consistent sections: Task brief, Host identity, Coverage manifest, Source-backed host facts, Task output contract, Valid and invalid examples, and Verification and limitations. The scope manifest declares exactly what was included and excluded. The assistant must never treat a scoped omission as proof that a feature is absent. The brief describes the desired user outcome and the host-owned manual return/verification boundary.

Make a **task-first quick reference** (short enough to fit a recipient's ordinary text channel when a text-only path is required), then full facts and examples. Prefer stable IDs, semantic definitions, specific conditions and reproducible cases over lengthy marketing language. If a task requires a parameter, constraint or destructive caveat, include it in the user-visible brief or guarantee that the relevant full packet is included. Never offer a short variant that silently loses a required constraint.

**Important implementation boundary:** the compiler can also produce a size-checked text-only brief using `--brief-output`, with all selected facts and dependencies (failure on >4000 Android UTF-16 code units). It does not automatically populate the Android `EXTRA_TEXT` channel, choose a model, or strip source content from a sent attachment. Host authors must independently test the actual Android final-review payload for each module and recipient. Do not claim that putting a reference in a ZIP or a repository URL means the assistant read it.

## 5. Preserve meaning, dependencies and limits

Compile a full profile or select stable IDs with `--select`; the compiler recursively includes dependencies plus each profile's `always_include` set. Fail on missing IDs, cycles, expired external facts, unidentifiable evidence or byte overflow. If a source claim changes, invalidate every dependent profile and held-out case. Keep the returned SHA-256 and source revision in QA records.

The default export budget is 2 MiB, matching AYA's existing one-file prototype ceiling, **not** a guarantee of recipient context capacity. Measure actual provider ingestion. If a packet exceeds budget, shrink scope explicitly and report omissions, rather than silently truncating, summarizing away a warning or assuming the assistant can fetch another file.

For an APK-bundled host, use `tools/build_reference.py --packet-source ... --packet-inventory ... --packet-profiles ... --packet-profile help` to assemble the typed, version-exact fragment into the 12-section AYA-RAS guide. The builder rejects app ID, exact-version or source-revision mismatches and checks assembled size and guide structure. For other modules, use their dedicated reviewed kit or verified task context as appropriate. AYA does not yet automatically select fact subsets at runtime. A host must not substitute an unvalidated newly generated packet for a known-good installed guide.

## 6. Examples and counterexamples

Each module profile must supply at least one valid and one invalid example with reasons and realistic edge cases. Help needs discriminating diagnoses, impossible feature traps and truthful uncertainty. Creative needs role-specific constraints and import outcomes. Structured outputs need the exact schema, coupled bounds, default values, valid/invalid fixtures through the real importer, and instructions to preserve unrequested fields. Translations need stable keys, terminology/Rosetta, placeholders, plurals, bidi and protected destructive actions.

An attractive example cannot establish real importer compatibility. The only authoritative output schema is the one generated or independently checked against the host's actual parser. Keep developer-approved semantics separate from inferred model commentary.

Use [controlled trial evaluation](EVALUATION.md) to record exact packet hashes, assistant versions, confirmed attachment ingestion, independently verified host results and failure severity. Treat models as external, changing dependencies.

## 7. Independent QA and release

1. Run structural checks on typed source, independent inventory, profile, compiled output and existing AYA-RAS guide.
2. Verify every high-risk fact on the actual distributed build, plus success/failure, status/authority/reversibility and data custody.
3. Use an independently authored held-out set: real user phrasings, novice/expert, negative capabilities, misleading labels, conditional states, privacy/security, byte-budget and failure scenarios.
4. Run the same approved packet bytes against representative assistants in controlled QA; separately record whether attachments were ingested, whether instructions were understood, and whether the output was valid.
5. Where the task returns a structured file, import it through the real host importer and verify resulting behavior. If no importer exists, label the path unimplemented.
6. Fail release for P0/P1 misdirection, false outcome claims, unsafe destructive guidance, incorrect schema, leaked secrets or unverified variant-dependent changes. Record and explain P2/unknowns instead of hiding them under a score.
7. Update packet sources, inventory, examples, evaluations and pinned app version **in the same PR** that changes relevant host behavior.

**No production telemetry:** all answer and artifact testing is separate, authorized QA with synthetic or consented material. AYA ends when the person shares/copies the packet. The receiving model is not granted control of the host app.

## Limits of the guarantees

Typed sources and schema validation reduce contradictions and omission risk; they do not certify claim truth, external provider freshness beyond declared expiry, the comprehensiveness of discovery, correct interpretation by any model, or the safety of returned data. The host's importer remains the final authority over any generated artifact.
