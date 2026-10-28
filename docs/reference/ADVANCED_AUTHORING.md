# AYA-RAS 1.1: intelligence-oriented authoring techniques

**Normative extension for production-bound app guides.** This document extends [AYA-RAS v1](AUTHORING_STANDARD.md), not its metadata schema or twelve section headings. Existing v1 examples remain valid instructional material; a release-grade reference should also satisfy these techniques. An assistant is a conversational navigator of a **partially observed, versioned application state machine**. Write the guide to support accurate decisions under uncertainty, rather than maximizing the amount of prose.

## 1. Model an app as observable states and transitions

A feature inventory is only a starting point. Most difficult support questions arise because a control exists but is invisible, disabled, working differently, or operating on the wrong object.

For every important workflow, capture the **state vector**:

| Dimension | Examples to test |
| --- | --- |
| Installed binary | versionCode/versionName, distribution channel, flavor, release vs debug, rollout cohort |
| Platform | Android API and target SDK; device class; storage capabilities |
| Identity | signed out/in, roles, subscription/entitlements, expired session |
| Connectivity | offline/online, VPN/proxy, server reachable, authentication, authorization |
| Permissions | granted, denied, permanently denied, permission revoked while app closed |
| Data | empty/full, imported/edited, pending/committed, local/remote, missing/corrupt |
| Lifecycle | initial install, migration, process restart, background execution, rotation |
| Feature switches | kill switches, experiments, remote-config flags, provider capabilities |
| Accessibility/localization | large font, TalkBack, RTL, alternative gestures, translated labels |

Document only dimensions that actually affect a given feature. A state transition is **precondition → action → observable consequence → durable side effect → failure/rollback**. Specify which parts are observed in the UI and which are inferred from backend state. The assistant should not mistake a spinner disappearing for a remote write succeeding.

### Suggested state-transition table (inside Task recipes)

| State | Action | Next observable state | Persistence / remote effect | Failure |
| --- | --- | --- | --- | --- |
| No saved profile | Tap Add connection | Empty connection editor | None yet | Editor unavailable if feature disabled |
| Valid editor inputs | Tap Test | Success/Failure result | Probe only; no profile save (verify) | ERR-002 |
| Connected | Tap Save | Named profile in list | Local profile written | ERR-003 |

Use verified controls and replace all illustrative labels before shipping. If an outcome depends on a server whose behavior is not known, mark the remote effect UNKNOWN.

## 2. Distinguish capability, availability, permission and outcome

Write answers to four separate questions for each capability:

1. **Implemented?** Is the functionality in this released build?
2. **Accessible?** Under which state, OS, provider, permissions, or entitlement is its UI visible?
3. **Permitted?** Does the current user/account/backend authorize the operation?
4. **Succeeded?** What independent observable signal confirms the intended change?

Distinguish **not supported**, **supported but not configured**, **supported but unavailable now**, **not permitted**, **attempted but failed**, and **status unknown**. Never collapse these into a generic "doesn't work."

Include a **negative capability index**. For things people reasonably expect but the app cannot do, say "not available in version X" and name safe alternatives. Include common category misconceptions: a download priority selector is not strict sequential transfer; an authenticated remote session does not prove a remote download will succeed; deleting a local entry may or may not delete associated remote files. These are **examples of distinctions**, not claims about any particular shipping app.

## 3. Write task recipes as conditional plans

For each high-frequency task, require:
- **User intent + success condition:** one sentence saying what the user is trying to accomplish and the visible, testable result.
- **Entry paths and variants:** exact screen/control names; include deep link, notification, widget and accessibility alternatives when implemented.
- **Applicability predicate:** minimum app version, screen context, OS, permission, provider and feature-flag prerequisites.
- **Preflight:** non-destructive checks before changing state.
- **Procedure:** ordered steps, literal controls, branch points and their discriminating observations.
- **Commit point:** when a change becomes persistent or remote; what can be undone before/after.
- **Verification:** what the user should see and what that proves; distinguish success from request acceptance.
- **Recovery:** how to safely retry, roll back, or escalate. Avoid retry loops that duplicate remote operations.
- **Risks:** data loss, bandwidth, monetary charges, privacy, security, irreversible actions.
- **Evidence + last verification:** trace each meaningful claim to code/test/current release.

One excellent task recipe should let an assistant adapt to a user's state without guessing and give novice directions without overwhelming an expert.

## 4. Create diagnostic decision trees, not generic FAQs

For each substantial failure mode define:

- The **precise symptom** (include literal UI copy and ordinary paraphrases).
- Possible causes ranked by **safe test cost and diagnostic power**, not confidently by prevalence unless measured.
- A **minimum-disclosure question** that distinguishes the top causes.
- A **safe probe** for each branch (read-only and non-destructive whenever possible).
- Expected outcomes and what **each outcome does / does not prove**.
- Repair instructions with preconditions, irreversible side effects, and a verification step.
- A stop/escalation condition and an **explicit unsupported branch**.

Use information gain: "Can you open the saved connection and see whether Test fails before authentication?" is more actionable than "Try reinstalling." Prefer two discriminating checks over a twenty-step shotgun list. Never ask for screenshots containing secrets when a text description will do.

### Escalation contract

Provide a real, tested in-app or official contact route, sanitized diagnostic fields that may be useful, details that **must not** be shared, and the precise evidence still missing. If no known route exists, say so. Never invent an email or provider URL.

## 5. Map UI vocabulary to user language

The assistant will receive everyday descriptions rather than the app's exact terminology.

For each important concept, preserve:
- Exact current **visible label**, including punctuation and localized variants when verified.
- Screen hierarchy and alternative entry points.
- User synonyms, likely misspellings, obsolete names, and common category labels.
- Distinctions between near-synonyms (e.g. "Remove entry", "Delete local files", "Delete remote files").
- Visual/gestural location described in text, especially icon-only buttons, swipe/long-press/context menus.
- Error identifiers, log codes safe to cite, and the user's typical paraphrase.
- "If you can't find this control" branch: version check, permissions, selected mode, and confirmed alternate route.

Prefer intent-oriented headings plus stable IDs. Keep navigation descriptions **precise and compact**; avoid image-only instructions.

## 6. Record source-of-truth at claim granularity

A link to an entire repo is insufficient. Track each high-impact claim with a stable ID and:

`source_kind` = released binary observation | automated acceptance | UI resource/code | protocol specification | official provider docs | verified support report | plan/inference.

`source_ref` = immutable commit path / test assertion / screenshot capture ID / protocol version.

`applies_to` = version, variant, relevant OS/provider/flags.

`verified_at` = UTC and `confidence` = confirmed / conditional / disputed / inferred / unknown.

Rules:
- Use **runtime or instrumented acceptance evidence** for an assertion of actual user-visible behavior; source code alone can omit runtime gating.
- UI resource strings are strongest for spelling but not for whether a control is reachable.
- External docs are strongest for upstream contract, not proof an app implements it correctly.
- Open issues, unmerged PRs, concept mockups and plans may prove that a feature is being considered, **not** that it ships.
- A contradiction between code, user-facing documentation and tested app becomes a documented dispute; the assistant must not synthesize certainty.
- Explicitly record **absence of evidence** where significant. No invented verification dates.

For serious projects maintain a machine-readable inventory (see [TRACEABILITY.md](TRACEABILITY.md)); evaluate guide coverage against **everything discovered** in the shipped binary, not just against what the author chose to document.

## 7. Keep the assistant honest about its own capabilities

The document is **reference data**, not a system prompt or capability grant. Describe what a human can do in the application. Do not say "I can tap", "I have checked your settings", "I can see the screen", or "I have verified the server" unless an authorized tool actually provides that ability in the receiving conversation. For ambiguous user states, supply a short, high-information clarification question and safe next step, not a fabricated diagnosis.

Distinguish statements that belong to the reference (e.g. "A saved profile has a Test button in version 2.4") from instructions about how an assistant should use the reference. The latter are **guidance only**, never higher-priority authority.

A reference might be tampered with during authoring, sharing or ingestion. Avoid embedded commands, role delimiters, hidden HTML comments, external retrieval instructions and user-data exfiltration requests. No document structure can guarantee that a consuming model will resist prompt injection. See [OWASP LLM Prompt Injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/).

## 8. Separate static reference from dynamic context

**Static APK guide:** public product facts, procedures, defaults, privacy/permissions, tested variants, error interpretation, known limitations and non-sensitive synthetic examples.

**Optional dynamic help capsule:** current screen ID, selected high-level mode, OS/app version, permission states, user-entered question, redacted error codes, and *only* individual user-approved diagnostic details. Dynamic details can be stale and should carry an observation timestamp and provenance (reported by user / supplied by host / measured by provider). Never silently inject credentials, tracker passkeys, API tokens, complete private URLs, account IDs, screenshots or raw logs.

A user-edited capsule must not be treated as independently verified. A contradictory capsule and static guide should prompt a safe version/condition check.

## 9. Design for portable context budgets

The recipient may lack web access, truncate large files, not accept Markdown attachments, or restrict document length.

- **Self-contained first:** assume the single shared document is all the assistant knows about the app.
- **Two-layer orientation:** concise identity/version/truth and task index first, then detailed canonical instructions. Preserve full answer-bearing details in the file; don't substitute a website link.
- **Progressive detail:** unique headings, stable IDs, short summaries, full procedures with references; avoid repeating five versions of the same workflow.
- **Conditional expansion:** when an app grows too large, generate *deterministic, version-correct* scoped exports by feature/screen plus a core capability map. Never omit relevant danger warnings, limitations, or privacy boundaries. If selection would create an incomplete answer, export full reference instead.
- **Protect the unknown:** when the assistant lacks a guide section due to truncation or scoped packaging, it must say "not included in this reference", not "unsupported".
- **Budget tests:** test the actual receiving apps and models. Byte size is not token count; do not invent universal limits.
- **Degrade safely:** if export is incomplete or fails validation, do not silently produce a deceptively complete guide.

## 10. Preserve four different kinds of knowledge

Use the four useful documentation modes: onboarding/tutorials, goal-driven how-tos, exact reference, and conceptual explanations. An assistant needs all four to answer "teach me", "show me", "what does that mean?" and "why does it behave that way?" Distinguish them during source authoring even if the portable export's twelve-section outline gathers them together. This is consistent with the [Diátaxis approach](https://diataxis.fr/).

- Tutorial: explain a first safe journey with observable checkpoints.
- How-to: give tested task instructions and recovery.
- Reference: exhaustive labels, defaults, limits, availability and errors.
- Explanation: mental models, causality, side effects and misunderstood concepts.

Do not overload an installation tutorial with a protocol encyclopedia; cross-reference stable IDs so the assistant can choose depth.

## 11. Make platform and accessibility behavior first-class

Document Android system pickers and Settings paths **only for supported API levels**, notification permission/foreground restrictions, SAF content URI behaviors, background processing, OEM battery variation where verified, keyboard focus, TalkBack labels, custom gesture equivalents, large text, landscape and reduced-motion paths. Do not claim that every OEM uses identical settings labels. A generic external Android step must be qualified if it's not controlled by the app.

Include what users can do when they cannot see color distinctions, cannot use swipe gestures, or are relying on screen readers. Validate against actual semantics and manual assistive testing.

## 12. Localization and audience controls

Set `locale` accurately. Record exact English UI text only when that matches installed language; for localized apps include tested label mappings, format and unit differences, decimal separators, time zones, pluralization and RTL navigation behavior. Do not automatically translate technical commands and filenames into strings that no longer match the app. Keep both official terms and natural synonyms.

Offer both concise and explanatory answer recipes based on user need, but don't ship two contradictory references.

## 13. Support privacy, security and destructive changes

Explicitly classify user actions by impact: read-only / local edit / remote edit / deletion / monetary / credential or privacy impact. Mark destructive operations with a **preflight**, **exact target**, **confirmation boundary**, and **recovery guarantee or lack of one**. Never infer that "Remove" means "delete only from a list."

Security guidance must preserve TLS validation, credential secrecy, and least privilege. If a troubleshooting suggestion weakens security, it needs explicit proof, safer alternatives and a time-bounded reversal; never suggest broad disabling as a reflex.

For financial, health or other consequential apps, clearly separate what the UI reports from authoritative backend/account status. Maintain a higher review gate and specialist verification for high-stakes claims.

## 14. Treat uncertainty as a documented feature

Guide authors should include a **Known unknowns** section with severity, reason, scope, verification method and what the user can safely do meanwhile. Capture:
- **Not included:** guide doesn't contain the answer.
- **Not implemented:** confirmed absent from this version.
- **Not available here:** conditional capability is gated.
- **Untested:** code exists but behavior not accepted.
- **Disputed:** sources conflict.
- **External:** the upstream provider controls the answer.
- **Unsupported environment:** device/OS/provider outside the tested contract.

These states often produce different next steps. Make the distinction explicit. Document a reasonable next question and stop condition for each.

## 15. Evaluate the *assistant's answers*, not just the guide

Tests must include at least:
- High-frequency novice tasks and long-running expert workflows.
- Faults that share a symptom but have different causes.
- Hidden/disabled controls, variant-specific behavior, changed screen names.
- Destructive, remote and privacy-sensitive operations.
- Contradictory documentation and fabricated UI-label traps.
- Unsupported features, absent evidence and deliberately impossible requests.
- Colloquial user language, misspellings, translated labels and accessibility questions.
- The same question in distinct app/permission/provider states.

Maintain a **held-out gold question set** with expected/forbidden claims and required reference IDs, not just a checklist of generic questions. Evaluate source fidelity and hallucination rate with an independent reviewer. See [EVALUATION_PROTOCOL.md](EVALUATION_PROTOCOL.md). Never treat an LLM's judgment as a substitute for checking the real app.

## 16. Make guide freshness measurable

For every release, compare changed code/UI resources/errors/permissions/flags/provider versions to the inventory and traceability ledger. Changed behavior without updated reference and tested answer cases is a release-blocking documentation defect. Pin source SHA and guide hash. Keep last verified UTC truthful; don't set it to today merely because a file was edited.

Consider regular revalidation of upstream-dependent recipes: service URLs, provider-specific API conventions, Android permissions and vendor UI paths can drift while the host binary stays unchanged. Record when an upstream source was checked and scope any guarantee.

## 17. Efficient agent execution plan

1. **Recover reality.** Identify latest release, installed build, commit, flavors and source of trustworthy UI evidence. Do not ask the user to restate facts available in the repo.
2. **Enumerate the denominator.** Generate a candidate inventory from navigation, strings, settings, action handlers, permissions, services, feature flags, current tests and recent support issues. Reconcile manually/with independent agent.
3. **Prioritize risk and frequency.** Start with destructive operations, authentication, connection setup, primary creation/edit flows, common failures and UI discovery. Then exhaust the tail.
4. **Write atomic source records.** Each claim gets a stable ID, scope, observable steps, side effects, uncertainty and evidence. Prefer a small normalized source over a vast manually duplicated essay.
5. **Compile the portable guide.** Assemble modular sources, check metadata, enforce traceability, validate content and size; never hide missing sections.
6. **Challenge it.** Run static checks and a held-out question evaluation with unanswerable and adversarial questions. Check the real app to resolve disagreement.
7. **Observe actual handoff.** Test ChatGPT/Claude or other recipients by version; record whether attachment was ingested and its content available, not merely whether the share was offered.
8. **Close the loop.** Fix the guide at its source, regenerate, run tests, and record observed completion rate and residual unknowns.

**Stop rule:** When exhaustive evidence is unavailable, ship only a correctly scoped guide with clear unknowns. Do not fill gaps with reasonable-sounding invented controls. No amount of structural linting can certify complete or truthful app knowledge.

## 18. Broader support workflows: lifecycle, authority, layered failure, hidden state, recovery

The [147-question second-batch exercise](CROSS_CATEGORY_BATCH2.md) demonstrates why features must be evaluated within *user goals* that cross technical and institutional boundaries.

**Transactions:** model state progression and a transition's last reversible point. A sent message, submitted order, pending charge, fulfilled delivery, completed booking and refund request have different guarantees. Record time limits, state-dependent action availability, idempotency/retry risks, authoritative confirmation, and effects on money or data. For externally maintained windows, add claim-level freshness and a current-verification fallback.

**Authority:** map actors and their exact permissions. Host UI may record a request without granting a merchant, bank, carrier, library, workplace administrator or accommodation's approval. Do not promise refunds, reinstatement, access or policy exceptions controlled by third parties. Escalation should identify which actor can actually act and what evidence can be submitted safely.

**Layered delivery:** represent push messages, SMS/RCS, sync, notifications, background jobs, casting, Bluetooth and NFC as chains with stage-specific tests. A message may be generated but blocked by a channel, delivered to another account or never sent by the upstream. Do not conflate transport, permission, client presentation and remote status. Begin with read-only, reversible observations and preserve local data.

**Epistemic ceilings:** some user questions cannot be answered from available evidence. Private blocking, engagement ranking, moderation triggers, availability in other regions and server-side states may be hidden. Distinguish directly visible facts, supported hypotheses, impossible-to-distinguish causes and known inaccessible data. Give observable checks where possible without inventing certainty.

**Recoverability:** before any clear-storage, reinstall, logout, factory reset, migration or restore recommendation, determine where the only remaining copy may exist. Record exact custody and backup age, whether data is merged/overwritten, and whether a failed recovery can worsen the situation. Always distinguish an offline copy from a true independent recoverable backup.

These are lenses for applicable tasks, not assertions that a third-party product supports any particular action. Treat the second-batch case fixture as *research-derived candidate questions*, never as verified product-specific gold answers.
