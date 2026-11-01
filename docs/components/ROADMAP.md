# Drop-in integration program: detailed build and release plan

**Owner intent:** reduce integration to an IDE dependency, visual component, logical node or one coding-agent instruction; preserve AYA as an Unlicensed convention rather than a compulsory service. Refer to [the status ledger](STATUS.md) for merged source, CI verification and remaining release gates; earlier phase descriptions are historical.

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
- Optional `aya-compose` artifact providing `AyaCard` and `rememberAyaLauncher` backed by the core SDK. Initial module and sample implemented; CI and cross-device accessibility acceptance are separate gates. Preserve a non-Compose core.
- XML-inflatable layout-editor View adapter merged in PR #24 (CI passed), with stable question view ID, required output instructions and fail-closed configuration.
- Configurable existing-button action and Standard/Compact card templates; optional menu icon, but **no intrusive overlay permission**.
- Android Studio installation examples for Gradle/Maven and source module; reusable project wizard snippet; package via tagged builds/artifact verification.
- Host-specific output-use/import guidance, honest attachment modes and explicit fallback. Reconcile the separately developed output-return PR before changes to shared UI.
- Correct local error states with accessibility announcements; instrument review + Copy/Share and version guard on supported Android SDKs.
- Portable manifest support for image and translation only after full operation-specific asset/task/schema checks and negative examples; structured artifact and filesystem automation only after their host contracts exist.

**P1 exit:** two independently authored real-app AYA-RAS guides, held-out questions, install/uninstall test, no duplicate prompts, support for 320x700/412x892, 200% font scale, TalkBack and IME; no broken changes to standard card or transport.

## Phase 2: Flutter and FlutterFlow (P1)

- Flutter Android plugin, typed Dart API, widget and headless call merged in PR #29; real Android APK compilation with staged AAR passed CI. Public distribution and physical-device acceptance remain outstanding. Map to `AyaComponentAction` and forward *local* status only.
- FlutterFlow Custom Widget and Action body templates merged in PR #32. Actual editor import/export, native artifact resolution, manifest merge and real Android device acceptance remain outstanding. If marketplace distribution is unavailable, publish a reproducible custom-code import path with that limitation stated.
- Use static asset build or an explicit native Android asset packaging step; validate guide identity against the **actual Android application ID and installed versionName**, not Flutter pubspec version guesses.
- Test lifecycle: rotation, multi-window, Flutter navigation, Android chooser cancellation, duplicate taps, process death.

**Exit:** end-to-end sample apps built by CI and manual editor import acceptance. No phantom plugin listing.

## Phase 3: React Native and Expo (P1)

- Expo CNG guide-asset helper, Android-only Expo Modules API bridge and React Native card are source previews. A first-party synthetic Expo Android APK with staged native SDK, exact audited guide, merged manifest and DEX definitions passed CI, as did an **out-of-tree npm-tarball synthetic consumer** under [PR #66](https://github.com/gamesbyian/AYA/pull/66). Independently authored adopting hosts and physical-device acceptance remain required for broad compatibility claims.
- A publishable npm package and tested integration with ordinary React Native hosts remain pending. Verify custom development builds, Activity lifecycle and exact native dependency resolution before announcing compatibility.
- Do not claim stock Expo Go can load arbitrary native modules; document precise support matrix and reject unsupported runtime environments with a helpful error.
- Validate user-typed prompt and JS lifecycle without promising provider reception. Confirm no source-scanning, automatic permission escalation or implicit file attachments.
- CI: example Android app build, TypeScript and native integration tests, manifest merge checks, local negative-control cases.

## Phase 4: visual scripting/game toolchains (P2)

- **Godot 4:** Android v2 plugin and host-configurable `AYACard` script with inspector fields, guarded `openHelp` and local status signals. Godot 4.5.1 has a **real engine-produced Android APK** ([CI 41264756578](https://github.com/gamesbyian/AYA/actions/runs/41264756578)) and a downstream **Android 35 emulator boot/native-singleton/card readiness smoke** ([CI 41266974910](https://github.com/gamesbyian/AYA/actions/runs/41266974910)). The editor preview is intentionally inert; there is no verified independent game adopter, real tap/Copy/Share, physical device or assistant receipt.
- **Unity:** source-preview UPM Inspector action, Android Kotlin bridge and a dedicated **optional** `AYA/Help` Visual Scripting Unit are checked in. Native Gradle/AAR and managed source C# compiler/flow smoke pass against test-only Unity/VisualScripting signatures. Still verify actual Unity Editor and graph import, Android export, IL2CPP/Mono boundaries, packaged host guide/manifest and device lifecycle before claiming broadly installable Unity compatibility.
- Document how UI controls and graph logic both connect to the same action. Never imply Godot/Unity desktop exports can use Android Sharesheet without a separate backend.
- CI smoke tests where headless toolchains allow; interactive editor import, android export and real Android device acceptance are distinct.

## Phase 5: beginner no-code + compatibility standard (P2)

- A **help-only MIT App Inventor v206 Rush 2.1.2 `.aix`** extension has compiled from the canonical AYA Android AAR and passed a real AIX descriptor/code archive audit ([CI 41267356990](https://github.com/gamesbyian/AYA/actions/runs/41267356990)). Its block API delegates to guarded `AyaComponentAction.Help` and reports only local UI state. Next: genuine App Inventor consuming project and built APK, correct native manifest/guide/provider assets, older bundled AndroidX compatibility, physical-device and user review acceptance. Kodular remains a separate unverified builder; never assume compatibility automatically.
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
