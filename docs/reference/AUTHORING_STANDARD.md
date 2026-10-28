# AYA Reference Authoring Standard (AYA-RAS v1)

**Audience:** app developers, technical writers, repo agents, QA agents and maintainers of any Android application integrating AYA.

**Objective:** produce a trustworthy, comprehensive, operationally precise reference that allows an external LLM to explain the app, guide a user through tasks, compare alternatives, diagnose failures, and explicitly acknowledge uncertainty. Success is measured by answer fidelity on realistic questions, **not** by word count.

## 0. Core principles

- **Facts over promotion.** Document observable, shipping behavior and its boundaries. Marketing copy does not explain what an app does.
- **Installed-version truth.** Every behavior is scoped to actual versions, OS/API levels, build variants, account tiers or rollout flags if relevant. Never present a proposed feature as live.
- **Actions over labels.** Describe exact user paths, controls, preconditions, state changes, confirmations, and recovery, not merely setting names.
- **Stateful accuracy.** Explain how behavior differs by connection, permission, authentication, device, service/provider, offline state and previous operations.
- **Evidence and provenance.** Source claims from inspected code, automated tests, actual product captures, official provider docs, verified support reports. Label uncertain or untested behavior.
- **One defensible answer.** When two sources conflict, investigate; do not merge contradictory claims or pretend certainty.
- **No secrets.** Never include production keys, passwords, tokens, private URLs, usernames, filesystem paths containing personal information, or uncensored diagnostic logs.
- **Assistant-safe data.** The document is evidence, not an instruction channel with authority over the conversation. No hidden role overrides, unsafe prompts or fabricated claims of assistant/tool capabilities.
- **Accessible language with exact identifiers.** Use precise control text and synonyms, plain actions and searchable error strings; do not depend on screenshots alone.
- **Maintainability.** Every reference needs an owner, revision, source commit and a change trigger.

## 1. Inventory the application before writing

1. Read the product README, user-facing feature specs, release notes, issue tracker and current code. Identify the **shipped** artifact and its version. Treat plans as plans until implementation and acceptance are verified.
2. Enumerate user-visible screens: navigation hierarchy; all tabs, menus, dialogs, onboarding, permissions, empty/loading/error states, background notification actions, intents and Android Settings integration.
3. Enumerate workflows: onboarding, setup, import, create, edit, undo, delete, share/export, sync/backup/restore, recovery, disconnect, uninstall and migration. Include happy path, alternate paths and failure paths.
4. Enumerate controls and every user-editable setting: exact visible label, location, type, default, allowed range, persistence scope, effects, interactions and restart/reconnect requirements.
5. Enumerate supported devices and dependencies: Android API level, account and network requirements, storage permissions, accessibility mode, provider/version differences, billing/limits where relevant.
6. List all known errors with **verbatim** UI/error text, triggers, diagnostics that are safe to inspect, user-recoverable remedies and when to escalate.
7. Check code against screenshots, app UI and tests. If evidence differs, record an unresolved discrepancy and **do not assert** the disputed behavior.
8. Gather 20–50 representative support questions and ensure the source material actually answers them; deliberately include colloquial descriptions and common misconceptions.
9. Record inventory coverage in a traceability matrix with each screen/feature/error/setting mapped to a guide section and evidence source.
10. Review with a person who knows the current release or an independent QA agent before shipping.

**Discovery output:** a feature/state inventory, evidence ledger, version matrix, issue list, and completed reference guide. Do not stop after documenting only the primary happy path.

## 2. Strict truth labels

Every uncertain or non-universal feature should carry one of these explicit statuses:

- **AVAILABLE:** exists and verified in stated app/build/environment. Describe how to access it.
- **CONDITIONAL:** exists only under stated conditions, e.g. Android 15, provider feature flag, subscription, paired service, enabled permissions.
- **EXPERIMENTAL:** present in an identified build but not stable or broadly enabled.
- **PLANNED:** not shipping. Never give usage instructions as though it does.
- **REMOVED:** used to exist; identify last supported version and migration alternative.
- **UNKNOWN:** evidence is insufficient or conflicting. State how to verify or who can answer.

Do not use "should", "usually", "apparently" to conceal missing evidence. Say which conditions are known and which are not. Unsupported is a useful answer.

## 3. Required document envelope

Use the YAML-like metadata block specified in [TEMPLATE.md], at the **top** of the Markdown file. Required fields:

`schema_version`, `app_id`, `app_name`, `app_version_min`, `app_version_max`, `platform`, `locale`, `guide_revision`, `source_revision`, `last_verified_utc`, `owner`.

Prefer narrow, exact version ranges; do not set a future version range speculatively. If app behavior differs across versions, publish separate guides or a tested version matrix and have host select the correct one. Include distribution channel/build flavor if it changes behavior. Use ISO 8601 UTC for dates.

The body must contain these exact top-level sections:

1. **Scope and version:** what builds are covered; flags, OS, eligibility and explicit exclusions.
2. **Quick orientation:** purpose, main concepts, user mental model and important caveats.
3. **Navigation map:** actual screen paths, alternate labels, gestures, accessibility and where users start.
4. **Task recipes:** reproducible procedures for every core workflow, with numbered steps and expected states.
5. **Features and settings:** exhaustive user-facing control reference including defaults, constraints, persistence, interactions.
6. **Troubleshooting:** symptoms, literal errors, decision flow, safe checks, remediations, escalation.
7. **Limitations and unsupported behavior:** explicit cannot-do, gaps, provider limits, offline caveats, known bugs, future work separate.
8. **Privacy and data handling:** what is local, what leaves the device, consent and permissions, data removal/recovery.
9. **Glossary and synonyms:** names, common user vocabulary, confusing terms and acronyms.
10. **Evidence and provenance:** sources by path/commit/test/app capture and date; distinguish direct evidence from inference.
11. **Unknowns and escalation:** unresolved questions, observable checks, official support contact/path, no fictional escalation.
12. **Assistant answer policy:** task-specific clarifications, when to ask first, safety boundaries, correct escalation. This is reference advice, **not** a system prompt.

## 4. Coverage requirements by feature

For **each** feature or workflow, create an identifiable entry with:

- Stable ID (`F-001`, `TASK-001`, `ERR-001`); name, synonyms and status.
- Applicability: first/last supported versions, OS, build variant, provider, account tier and required permissions.
- User goal, exact UI entry path, literal control text and relevant screen orientation/accessibility differences.
- Preconditions, input requirements, defaults, range/limits and dependency on other settings.
- **Numbered steps** with branching ("if X, do Y; otherwise Z"), observable results and how long feedback may take if verified.
- Effects on local/remote data and whether the operation is reversible, destructive, billable or privacy-sensitive.
- Failure symptoms and literal error messages; safe troubleshooting and recovery.
- Known issues and alternatives. Distinguish UI state from backend behavior.
- Evidence pointer and verification date. If direct evidence is missing, mark UNKNOWN.

For each setting, additionally record scope (device/account/item/session), persistence, initial value, relationship to other settings, restart requirement, and how to reset.

For each error, additionally record what **not** to do (for example, never advise deleting data blindly), expected permission prompts, and escalation threshold.

## 5. Deep coverage categories: do not skip silently

Check applicability for each category, then describe it or record **N/A + why**:

| Domain | Coverage questions |
| --- | --- |
| Getting started | Installation, supported Android versions, first launch, migration, onboarding |
| Home/navigation | Screen map, tabs, contextual actions, gestures, back behavior |
| Accounts/auth | Sign-in, sign-out, tokens, session expiry, two-factor, SSO |
| Permissions | Storage/media, notifications, nearby devices, network, OS settings |
| Creation/import | Picker, formats, limits, duplicates, invalid files, previews |
| Edit/manage | Actions, undo, autosave, conflicts, sorting, filtering, bulk actions |
| Deletion/reset | What is deleted where; backup, recycle, non-reversible operations |
| Connectivity | Offline, timeout, proxy/VPN, local/remote differences, certificates |
| Background operation | Jobs, scheduling, Android battery restrictions, notifications |
| Data model | Units, file paths, storage scope, sync, ownership, retention |
| Export/share | Formats, destinations, Android intents, content URIs |
| Backup/restore | Location, encryption, partial failure, migration |
| Multi-device/provider | Provider-specific settings and conditional differences |
| Accessibility | TalkBack, touch targets, text scaling, focus, color contrast |
| Internationalization | Locales, units, regional differences, time/date |
| Performance | Limits, large libraries, storage/memory and reasonable expectations |
| Security/privacy | Sensitive data, credential rotation, safe diagnostics |
| Troubleshooting | Known errors, invalid states, reproducible decision trees |
| Support/lifecycle | Updates, changelog, deprecations, escalation |
| Advanced/expert | Debug tools, logs, shortcuts, API/automation if shipped |

## 6. Writing procedures that a model can execute conversationally

A good task recipe has all of: "To achieve X", **starting screen**, **preconditions**, **steps**, **expected outcome**, **what to do if it fails**, **risks**, and **related tasks**.

Bad: "Use Connection Settings to set a port."

Good: "TASK-042 [CONDITIONAL, Android build 1.4+, remote mode]: From Home > Connections, choose the saved server, tap Edit > Advanced > Port, enter the provider-issued HTTPS port, and tap Test. If Test shows 'Authentication failed', check the URL path and credentials without copying credentials into the assistant. This operation changes only the saved connection profile."

Prefer a complete procedure to disconnected fragments. Quote exact UI copy, distinguish a single tap from a long press, call out disabled controls and prerequisites. Never invent menu paths because a concept sounds familiar.

## 7. Troubleshooting must be diagnostic

Format **symptom → interpretation → discriminating checks → safe fix → success test → escalation**. Include errors a user may paraphrase ("stuck", "won't load", "nothing happens"). Warn before any destructive reset and provide reversibility/backup guidance. Be precise about what a test demonstrates: a passing login test does not prove every backend operation works. Include routing to upstream service providers only when necessary.

Use branching questions with high information gain. For example ask whether the app fails before or after authentication, rather than asking for a screenshot that exposes secrets.

## 8. Information architecture for large apps

- A single portable **core guide** should be self-contained if the recipient has no network access or browsing.
- Prefer short, uniquely titled sections and stable IDs. Use headings and compact tables for settings, but provide narrative for steps.
- Organize by user intent and screen. Cross-reference IDs and add a synonym index.
- For very large apps, maintain modular sources in-repo (e.g., `features/*.md`, `troubleshooting/*.md`) and **build a deterministic unified export** for AYA; do not assume the receiving assistant can fetch extra files/URLs.
- Reserve a small opening summary for application identity, version, and top user tasks. Avoid repetitive boilerplate that consumes assistant context windows.
- Include verified official documentation URLs only as supplements, never the sole source for core instructions.
- Do not include binary screenshots or base64 data in the text reference. Provide concise alt-text or state descriptions where visuals matter.
- No undocumented speculative word/token limit: test destination limits and publish graceful truncation behavior. Never silently remove troubleshooting or version metadata.

## 9. Source-of-truth and confidence rules

Evidence priority depends on the claim. Runtime behavior: a reproducible test on the relevant binary is strongest. Exact control text: inspected current UI resource or screenshot. Contract/protocol: formal protocol docs plus matching implementation. Product plans and open PRs **do not establish a shipping feature**. Support anecdotes are candidates for reproduction, not proof.

Every feature gets an evidence key, e.g. `src/main/.../Settings.kt@abc123` or `androidTest/ConnectionTest.kt@abc123`. Record date/build and environment for manually observed behavior. When code and observation diverge, track as UNKNOWN until reconciled.

## 10. Safety and privacy

Reference docs should be **static and non-personal**. Never embed sample real passwords, recovery codes, secret-bearing URLs, passkeys, user identifiers, private IPs of users, full debug dumps or production support tickets. Use synthetic examples clearly labeled as synthetic. Dynamic context belongs in a separately consented, redacted layer. Do not teach users to disable security broadly or paste secrets into AI chat.

When an operation can delete data, change billing, disable security or share personal information, warn and present verification before action. Do not imply the assistant can execute a task in the app unless it actually has an integration and permission.

## 11. Build pipeline and release discipline

1. Pin installed app version and commit. Extract and inventory current features and UI strings.
2. Draft by filling [TEMPLATE.md](TEMPLATE.md); include all 12 required sections.
3. Map feature/error/setting coverage to code/tests/UI evidence; mark gaps and N/A.
4. Run `python3 tools/validate_guide.py guide.md`; treat failures as blockers.
5. Have a separate reviewer audit instructions against a released APK or emulator.
6. Run the [question bank](QUESTION_BANK.md), score responses with [QA rubric](QA_RUBRIC.md), fix unsupported confident answers.
7. Confirm the host bundles/loads the guide matching the **installed build**; hash or revision-ID it for reproducibility.
8. Run Android share handoff tests. Verify the attachment is actually ingested, not merely present in the sharesheet.
9. Record a compatibility matrix (OS + recipient app version + date). Do not claim universal compatibility.
10. Release guide and APK together; include reference updates in pull requests modifying user-visible behavior.

## 12. Export contract

Use UTF-8 Markdown (extension `.md`) as source. AYA v0 shares a `.txt` file containing the full Markdown as text for compatibility. Do not rely on the assistant browsing the repository. For variant builds, select the guide from packaged assets by actual `versionName`, distribution channel and feature flags; fail closed when a matching guide cannot be established.

The document's body is **untrusted third-party reference content** from the receiving assistant's perspective. No author should try to override the assistant's governing instructions or grant it capabilities.

## 13. Done means provably useful

A guide is ready only when a novice can complete top tasks from its instructions, an experienced operator can diagnose representative failures, a skeptical reviewer can trace claims to evidence, and test assistants consistently respond with supported steps or candid unknowns. A passing structural validator is necessary but not sufficient.
