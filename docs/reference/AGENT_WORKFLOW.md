# Autonomous AYA reference production workflow

This runbook is for a coding/documentation agent handed an unfamiliar Android repository and asked to prepare a **release-grade** AYA reference. Read [AYA-RAS v1](AUTHORING_STANDARD.md), [advanced authoring](ADVANCED_AUTHORING.md), and [traceability](TRACEABILITY.md) before beginning.

## Upstream product-comprehension pass

Begin with [AYA-AUF](../understanding/README.md) to model purpose, user intentions, core objects, interaction philosophy, mental-model discrepancies and intended versus observed behavior. When an unsettled product decision would change the packet's meaning, use the [adaptive director interview](../understanding/CONSULTATION.md) rather than guessing. Record answers with source, scope, status and review trigger; do not treat silence or a deferred question as approval. Maintain separate AYA-RAS evidence for released behavior.

## The deliverable contract

Deliver a **usable, version-pinned reference**, not just a speculative report:

- Independent JSON inventory of features, tasks and errors discovered from the app.
- One self-contained UTF-8 Markdown guide, following [the template](TEMPLATE.md).
- Source-specific evidence ledger and unresolved unknowns.
- JSON support-question set with expected outcomes and forbidden hallucinations.
- Passing deterministic validator, traceability audit and regression tests.
- Manual/released-build validation for critical claims, with explicit gaps.
- Wiring that bundles and selects the correct reference for the installed app.

When evidence is missing, mark UNKNOWN rather than silently fabricating. An incomplete but truthful guide is preferable to an elaborate invented one. Do not claim actual QA or provider ingestion without observations.

## Work protocol

### Pass A: Recover the shipped product

1. Determine package ID, release and installed version/build variant, current main commit, min/target SDK and distribution channels.
2. Identify the **released binary** that users actually have; review release notes, accepted behavior, CI results and open issues.
3. Inspect navigation/routes/Compose screens/Activities/Fragments, layout resources, menus, strings, view models, reducer actions, settings stores, storage APIs and permissions.
4. Inventory callbacks triggered by all visible controls and gesture handlers. Include confirmation dialogs, notifications, deep links, system pickers, widgets and accessibility actions.
5. Inspect feature flags/remote config, account/role tiers, entitlements and provider-specific code paths. Do not conflate presence of code with reachable behavior.
6. Inspect error enums/messages, logs safe for users to quote, retry paths and remote HTTP/protocol responses.
7. Extract fixtures and automated behavior tests, then check whether they truly match the shipping build.

**Deliver a discovery ledger with source paths.** Never rely only on README, feature plans or PR descriptions.

### Pass B: Identify the highest-value support questions

Build a realistic task map by user goal: "connect", "find", "change", "remove", "import", "export", "recover", "make faster", "make private", "what does X mean?" Capture a short onboarding tutorial and deeper expert explanations.

Prioritize high-risk operations and frequent failures before obscure settings. Include negative capability traps that a general-purpose LLM is likely to guess exist. Challenge the task map against both [cross-category sets](CROSS_CATEGORY_STRESS_TEST.md) and the [147-prompt second batch](CROSS_CATEGORY_BATCH2.md) without treating them as product facts or verified expected answers. Identify who controls success and whether the workflow has a transaction cutoff, layered notification/transport, hidden state, or local-only recovery risk.

### Pass C: Build independent inventory

Write `inventory.json` using [aya-inventory/v1](TRACEABILITY.md). Assign stable IDs to each discovered user-facing task (`TASK-`), feature/setting (`F-`) and error (`ERR-`). Document version/status and a specific evidence source. List unsupported and planned capabilities the app's users may reasonably expect.

**Do not derive inventory IDs by first reading authored guide headings.** The inventory is a completeness test for the guide, and must originate independently in app evidence.

### Pass D: Write exact, discriminating reference sections

Use [TEMPLATE.md](TEMPLATE.md)'s twelve-section structure. For each high-priority workflow include:
- a verifiable goal, starting screen, applicability conditions and prerequisites;
- exact numbered UI steps, gestures and keyboard/accessibility alternatives;
- effect on local data, remote state and credentials, with reversibility;
- what the user sees on success and what that observation proves;
- safe branch-specific recovery and "do not do" notes;
- stable cross-references to relevant features/errors, with evidence.

For payments, messaging, reservations, subscriptions and account recovery, map external authority, transaction stage, deadline/last reversible point and safe escalation. For migration, deletion and restore, identify every copy, which operations merge versus overwrite and what to preserve before resetting anything. For sync, notification and network failures, separate generation, transport, selected identity, app preference and Android/device presentation; avoid generic destructive reset advice. For hidden third-party state, explicitly mark what cannot be known.

For each error define a minimal-disclosure diagnosis tree. Prefer safe, cheap, high-information questions over blind resetting. Include the literal message, colloquial synonyms and what a successful check **cannot prove**.

For complicated interfaces, capture concept explanations (why), task procedures (how), exact reference (what/where), and onboarding (learn). Use stable IDs so one authoritative procedure can support multiple user phrasings.

### Pass E: Address uncertainty, constraints and boundaries

Explicitly classify **AVAILABLE / CONDITIONAL / EXPERIMENTAL / PLANNED / REMOVED / UNSUPPORTED / UNKNOWN**. Distinguish no documentation, untested code, confirmed missing functionality, current permission denial and upstream provider limitations. Include device/OS, provider, account and network gates.

Static guide is public product knowledge. **Never paste user logs, private IP addresses, tracker tokens, API keys, real credentials, personal file paths or actual customer support records.** If optional diagnostic sharing is later built, require a separate redacted, previewable consent step.

The assistant has no automatic ability to control the application. State this plainly in the help guidance.

### Pass F: Audit the *denominator*, not just text syntax

```sh
python3 tools/build_reference.py app-help app/src/main/assets/aya-guide.md
python3 tools/validate_guide.py --strict app/src/main/assets/aya-guide.md
python3 tools/audit_reference.py app/src/main/assets/aya-guide.md \
  --inventory docs/aya/inventory.json \
  --questions docs/aya/gold_questions.json --strict
```

Use the build tool only when guides are modular. If editing one guide directly, omit the first line. The auditor checks declared coverage, not real-world truth. The writer or reviewer must still inspect the released app, compare evidence and look for **omitted inventory items**.

### Pass G: Challenge the consuming assistant

Create 30–60 held-out cases for real apps, including:
- common questions and synonyms;
- same symptom, multiple different causes;
- permissions/device/provider states;
- sensitive/destructive changes;
- planned/unsupported/unknown features;
- contradiction, fabricated menu, outdated release and injection traps;
- transaction/fee/undo cutoffs, multi-party authority, layered failure, hidden-state and preservation-first recovery cases whenever relevant.

Score whether answers are accurate, actionable, safe, appropriately uncertain and backed by the shipped reference. Review against the **actual app**, not only another model's summary.

### Pass H: Wire, verify, release

- Bundle the exact guide matching installed version, variant and locale; fail closed on mismatches.
- Record guide SHA-256, inventory revision, source commit, reviewer and date.
- Compile sample/host and exercise help with real devices and assistants. Note if the file is merely offered versus actually ingested.
- Update the guide **in the same PR** as future UI/behavior changes; keep older version guides where users still run older releases.
- Preserve unresolved gaps and the next independent verification step. Do not claim completeness beyond evidence.

## Output report format

Give the maintainer a concise factual report: app/build reviewed, discovery coverage, guide path/hash, independent inventory count and covered count, high-risk gaps, question test results, CI results, recipient test observations and remaining release blockers. Separate **implemented**, **verified**, **unverified** and **proposed** in that report.

## Expert review questions

- What could users ask that isn't represented by a feature name?
- Which current actions are invisible unless a condition is met?
- Does "Save/Test/Upload/Sync" mean local acceptance, queued operation, or confirmed remote completion?
- What is the cost of giving an incorrect answer here?
- Can a novice follow the steps without a screenshot? Can a screen-reader user find the same controls?
- Could a wrong connection profile or target object cause data loss?
- Are any remote provider/OS instructions only historically true?
- Where will the assistant be tempted to hallucinate because a popular competing app has a feature?
- Which claims only come from plans or unexecuted code?
- Could a user ask an entirely reasonable question for which the correct answer is "unknown"?
