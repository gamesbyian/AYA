# Drop-in integration program: detailed build and release plan

**Owner intent:** reduce integration to an IDE dependency, visual component, logical node or one coding-agent instruction; preserve AYA as an Unlicensed convention rather than a compulsory service.

## Evidence/status legend
- **Existing:** verified in inspected main source, but any Android/recipient success still requires device acceptance.
- **In progress:** included in the initial integration branch; do not announce as a stable released artifact until merged and CI/device checks pass.
- **Planned:** specification only, not available to install.

## Phase 0: contracts, gap audit and core foundation (P0, this change)

Deliver:
1. Freeze help-only `aya-component/v1` static configuration JSON Schema and sample fixture; make invalid/extra keys rejectable.
2. Provide offline manifest validation plus deterministic multi-instance-safe Kotlin snippet generation, with injection-safe quoted string literals; clean command exit codes and negative tests. Explicitly document host-assigned stable View IDs for draft restoration.
3. Add Kotlin `AyaComponentAction` typed dispatcher for existing help/image/translation guarded entry points. Avoid changing core Share/Copy transport, output-return PR or card styles.
4. Document platform boundaries, host-side authoring model, director consultation, data minimization, truth categories, import separation and conformance invariants.
5. Link the developer entrypoint in README and AGENTS.md; keep release status accurate.
6. Verify existing Python tests; Gradle unit + Android/sample assemble + instrumented physical-device behaviour via CI/evidence where available. Never mark checks green by assumption.

**P0 exit:** schema/example/generator round-trip checks pass; generated Kotlin compiles in a compatible Android host; an exact-version guide opens review; invalid/stale guide and absent Activity fail safely; a reviewer verifies no new copy/share bypass. The snippet generator is not a certification stamp.

## Phase 1: mature Android drop-in UX (P0/P1)

Deliver:
- Optional `aya-compose` artifact providing `AyaCard` and `rememberAyaLauncher` backed by the core SDK. Verify Compose 2.x and activity lifecycle; preserve a non-Compose core.
- XML-inflatable layout-editor View adapter added in dependent PR #24 (CI pending), with stable question view ID, required output instructions and fail-closed configuration.
- Configurable existing-button action and Standard/Compact card templates; optional menu icon, but **no intrusive overlay permission**.
- Android Studio installation examples for Gradle/Maven and source module; reusable project wizard snippet; package via tagged builds/artifact verification.
- Host-specific output-use/import guidance, honest attachment modes and explicit fallback. Reconcile the separately developed output-return PR before changes to shared UI.
- Correct local error states with accessibility announcements; instrument review + Copy/Share and version guard on supported Android SDKs.
- Portable manifest support for image and translation only after full operation-specific asset/task/schema checks and negative examples; structured artifact and filesystem automation only after their host contracts exist.

**P1 exit:** two independently authored real-app AYA-RAS guides, held-out questions, install/uninstall test, no duplicate prompts, support for 320x700/412x892, 200% font scale, TalkBack and IME; no broken changes to standard card or transport.

## Phase 2: Flutter and FlutterFlow (P1)

- Build a first-party Flutter Android plugin, strong-typed Dart API, Dart widget and headless call. Map to `AyaComponentAction` and forward *local* status only.
- FlutterFlow-specific custom widget and custom action templates; prove plugin import, tree shaking, Android manifest merge, minSdk, rebuild and review UX on exported builds. If marketplace distribution is unavailable, publish a reproducible custom-code import path with that limitation stated.
- Use static asset build or an explicit native Android asset packaging step; validate guide identity against the **actual Android application ID and installed versionName**, not Flutter pubspec version guesses.
- Test lifecycle: rotation, multi-window, Flutter navigation, Android chooser cancellation, duplicate taps, process death.

**Exit:** end-to-end sample apps built by CI and manual editor import acceptance. No phantom plugin listing.

## Phase 3: React Native and Expo (P1)

- Build npm package with TypeScript types, `AskYourAgentCard` and `askYourAgent()`, a Kotlin module bridge and config plugin for Android assets/provider. Support ordinary React Native and prebuild/custom development clients for Expo where applicable.
- Do not claim stock Expo Go can load arbitrary native modules; document precise support matrix and reject unsupported runtime environments with a helpful error.
- Validate user-typed prompt and JS lifecycle without promising provider reception. Confirm no source-scanning, automatic permission escalation or implicit file attachments.
- CI: example Android app build, TypeScript and native integration tests, manifest merge checks, local negative-control cases.

## Phase 4: visual scripting/game toolchains (P2)

- **Godot 4:** Android v2 plugin, editor addon, `AyaHandoff` node, inspector fields from schema, `open_help(question)` method, `review_opened`/`rejected(reason)` signals. Android export-only; editor preview is a mock and must be labelled.
- **Unity:** UPM package with custom inspector + visual-scripting unit wrapping Android plugin. Verify Unity Android Activity access, export manifest, IL2CPP/Mono boundaries and Editor placeholder handling.
- Document how UI controls and graph logic both connect to the same action. Never imply Godot/Unity desktop exports can use Android Sharesheet without a separate backend.
- CI smoke tests where headless toolchains allow; interactive editor import, android export and real Android device acceptance are distinct.

## Phase 5: beginner no-code + compatibility standard (P2)

- Test MIT App Inventor and Kodular extension SDK feasibility, `.aix` output, assets packaging and tool version. If an editor cannot bundle verified guide assets or expose review, do not ship a broken partial adapter.
- Publish reusable editor screenshots/tutorials, self-implementation guide and behaviour-based conformance suite.
- Establish simple non-proprietary compatibility claims and self-test output; voluntary public compatibility registry only with explicit evidence and expiration, not telemetry.

## Shared engineering tasks, all phases

**Truth:** Each adapter must run AYA-AUF consultation/modeling, real-version inventory and provenance, AYA-RAS strict validation, Packet Compiler where applicable, independent held-out question evaluation, and cross-module card guidance audit. Builder UI cannot derive semantic truth from control names alone.

**Data/consent:** Use only explicitly declared host values, never auto-collect private state. Permissionless app-specific help remains useful; optional files need separate gates. Copy fallback available without compatible assistant; no output watcher/agent response tracking. Host import is local and uses independent validation/confirmation, with no trust assigned to output-origin token.

**Release:** pin exact dependency/version, signed tags, checksums, reproducible samples, supported platform/SDK matrix, migration notes and deprecation plan. Review API compatibility across adapters on each change. Schema major revisions for breaking changes; additive optional fields must have conservative defaults and tests. Reserve `aya-handoff/v1` as a separate protocol, never serialize `aya-component/v1` to recipients.

**Conformance cases (must be independently executed):**
1. Correct version and guide: question editor or preview opens; user can edit every shared text field.
2. Mismatched/removed/malformed/too-large guide: refuse with actionable local error, no share.
3. Long/empty/multiline/Unicode question: final `EXTRA_TEXT` comes from final approved payload.
4. No compatible share target or rejected attachment: honest Copy/manual path, no success assertion.
5. User cancels, rotates, backgrounds, repeats: no silent send, stale dialog or cached unauthorized payload.
6. TalkBack, keyboard, IME, 200% text and narrow phones: complete access to actions without clipped buttons.
7. Unknown operation/property/asset traversal: manifest or runtime rejects; no invisible fallback to weaker unguarded API.
8. Creative text-only versus full attachment: never claim attached reference when text-only, no silent truncation.
9. Translation or structured return: host import proof separate from AYA handoff; wrong-feature files and unrecognized types fail safely.
10. Source-of-truth test: deliberately falsify a sample feature claim; compiler/traceability or human audit must detect it before ship.

## Parallelizable work packages

| Package | Dependencies | Independent result |
|---|---|---|
| Static manifest + codegen | Phase 0 contracts | Validated configuration and deterministic snippet |
| Native typed action | Existing guarded Kotlin API | Callable surface for nodes/bridges |
| Compose module | Native action + UI standard | AAR and host sample |
| Flutter package | Native action and platform asset strategy | pub.dev-ready sources, tests |
| FlutterFlow examples | Flutter plugin available | Editor-imported widget/action |
| RN/Expo package | Native action + bridge design | npm-ready sources, tests |
| Godot addon | Native action + Android v2 export contract | Node, signals, APK evidence |
| Unity package | Native action + Android plugin contract | Inspector/unit, Android APK evidence |
| No-code extension | Platform feasibility | Reproducible extension or documented blocker |
| Conformance suite | All contracts | Independent behaviour and truth tests |

## Explicitly deferred decisions

- Whether to ship a standalone Compose package or a tiny sample-only wrapper first: choose based on consumer binary compatibility tests.
- A component marketplace badge/certification program: defer until independent conformance tests exist.
- Any native import-result helper: coordinate with the separate output-return work and host security contracts; never make agent reply tracking part of AYA.
- A platform-neutral serialized run request for advanced modules: not necessary for help v1, design only after real adapter needs are measured.

**Current cut:** build the minimal truthful Android/configurable foundation rather than publishing placeholder plugins. Expand distribution surfaces only after core acceptance.
