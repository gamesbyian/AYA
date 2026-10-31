# AYA Module Portability Standard

**Normative for modules, adapters, developer-agent instructions, documentation, code generation, example packets and tests.**

AYA is an optional interaction convention and host-neutral toolkit. Each module defines a **reusable capability class** and the handoff/interface contracts necessary to support it. It must not encode one actual adopting application, external repository, project identity, UI layout, preferences, file naming convention, particular schema, or implementation detail as a universal requirement.

## Layering boundary

| Layer | May contain | Must not contain |
| --- | --- | --- |
| AYA core/module | Typed tasks, validation, disclosure, version guards, handoff lifecycle, output roles, security requirements, failure/return conventions | Another app's name, repo/branch, project-specific file structure, proprietary recipe format, unique control values, host behavior assumed to be universal |
| Optional adapters | Framework/platform entry points, routing and lifecycle guards | Host-branded logic, silently bundled host-specific dependencies or provider-directed shortcuts |
| Fictional fixtures and sample | Clearly identified made-up host, invented benign schemas/assets and demonstrative values | Undocumented real-project claims or the suggestion that examples define defaults for other hosts |
| Adopting host's generated packet | Actual version-matched schema, import/export instructions, field interactions, navigation, capabilities and audited evidence | Unsourced guesses, secrets, unapproved context or blanket applicability to other hosts |
| Adopting host's implementation | Host-specific UI, importers, data model, rollback, validation, settings, consent and integration tests | Claims that AYA itself carries out those host-specific operations |

**The apparent tension is intentional:** AYA's *tooling* is host-neutral, while the *packet produced by an integrator* must be deeply specific to that host. The latter is supplied, owned and verified by the integrating developer. AYA must not ship a real application's implementation details as a built-in default.

## Module definitions by capability

- **Help/reference:** explaining actual host features and workflows, source-derived at build time.
- **Creative:** describing an image or asset that a host can actually import, with verified role, format and return instructions.
- **Structured artifact:** generating a machine-readable artifact according to the host's independently supplied schema and semantic contract.
- **Translation/localization:** producing a pack in an integrating host's real catalog/schema, with meaning, placeholders and safety preserved.
- **Filesystem automation:** requesting host-importable operation proposals for local/remote/cloud filesystem managers, with user clarification, scope and destructive-action safeguards.
- **Output return/import:** user-initiated bounded artifact selection, recognition, routing and host-side confirmation, independent of what assistant produced it.
- **Visual components and framework adapters:** reusable UI/action entry points, never branded host workflow implementations.

File format, backend, renderer, control names, paths, card placement, color palette and source-tree layout are supplied by each host when applicable. Android-specific platform contracts are allowed in Android adapters; product-specific Android-app assumptions are not.

## Authoring and review rules

1. Describe applicability by **host capability**, with prerequisites and exclusions. A game editor and a chart builder could both use structured-artifact handoff but do not necessarily share a schema.
2. Use role-based language, placeholders, and invented fixture names. Never embed a maintainer's other real app, branded menu hierarchy, repository link, pending branch, known preset, media/library setting or development status in normative module text.
3. Keep illustrative values explicitly non-normative; e.g. one fictional app's square-image import preference must not become Creative's universal preferred dimensions.
4. Keep real external integration notes, if any, in that external host's repository. AYA may document a *general mechanism* without treating that implementation as canonical.
5. Confirm the module would serve at least **two materially different plausible hosts** of its feature class without changing AYA's runtime logic. Host-authored schema/packet variation is expected and does not count as customizing AYA.
6. Keep the one-way handoff, human edit/consent, and host-owned import/validation boundaries unchanged. No hidden directory scanning, output monitoring, or automatic action is implied by a module.
7. Before merging, search all AYA docs, code, tests, templates and samples for references to unrelated real projects and repo URLs. Run the repository's portability regression check alongside module tests.

## Review checklist

A module change is portable when its public types have generic semantics, its documentation names prerequisites rather than one host's controls, its examples are fictional, all app-specific claims are supplied by the adopter and verifiable, and the same reusable implementation serves more than one host category. Do not label a host-integrated feature as implemented in AYA unless the generic SDK actually ships it.

## Automated coverage and limits

`python3 -m unittest tools.test_module_portability` scans first-party documentation, source code and component templates across Android, Flutter, React Native/Expo, Godot, Unity/C#, web and Gradle formats, excluding generated outputs and installed third-party dependencies. The check rejects known historical cross-project names and links. It is a narrow, deterministic guard, **not** proof that an innocuously named module is conceptually portable; reviewers must still apply the two-host reasoning test and inspect values, behavior and generated packets.
