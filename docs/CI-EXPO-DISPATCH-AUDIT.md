# Expo CI dispatch audit: source checks vs packed APK verification

**Evidence date:** 2026-10-31 UTC. The authoritative current workflow definitions are in `.github/workflows/`; this note records the decision and its limits, not a perpetual performance measurement.

## Prior redundancy

The previous `expo-module.yml` dispatched two jobs when Expo source, the native AYA core or the workflow changed:

- `types-and-contracts`: TypeScript API, React Native card and fail-closed local-result tests.
- `real-android-host-apk`: staged canonical AYA Maven artifact, Expo prebuild, Android APK compilation, source-specific guide identity, manifest and native DEX verification.

At the same time `expo-packed-host.yml` independently staged the same AYA native SDK, built a synthetic Android host from **npm tarballs** in a separate directory, and performed the same final APK identity/guide/manifest/DEX inspection. The latter is a stronger source-distribution boundary because it tests the files that adopters actually receive.

Two successful historical duplicate APK jobs consumed the following **observed runner-wall time**, including setup and compilation:

| Run | Job start UTC | Job finish UTC | Runner-wall time |
| --- | --- | --- | --- |
| [41247600931](https://github.com/gamesbyian/AYA/actions/runs/41247600931) | 2026-10-31 22:18:44 | 22:22:54 | 4m10s |
| [41245911246](https://github.com/gamesbyian/AYA/actions/runs/41245911246) | 2026-10-31 21:57:01 | 22:04:33 | 7m32s |

These are two historical observations, **not** a reliable estimate of billed savings or future duration distributions. Do not compare concurrent workflows' wall time with total runner minutes.

## Change

Keep the existing `expo-module.yml` TypeScript and mock-contract job, but remove its redundant APK compilation. The only automatically dispatched Expo **native APK acceptance job** is `expo-packed-host.yml:clean-packed-consumer`, with its real packed npm dependencies, host-versioned guide audit, compiled APK and DEX checks. Keep `expo-packed-js.yml` for the distinct Metro source-to-bundle contract.

`tools/test_expo_ci_gate_ownership.py` verifies that the native APK gate remains dispatched for Expo modules, shared AYA core, both verification scripts and workflow edits, while guarding against accidental reintroduction of a second native build. Path filters are not proof of branch-protection status; verify configured required checks before changing gate names or protection rules.

## Expected and verified impact

**Expected dispatch change:** one fewer full Android Gradle/APK job on a PR that changes Expo or the shared native AYA core while retaining the packed-host native APK gate. Native verification **coverage is retained**, not replaced with mocks. The fast typed-contract job continues independently.

**Measurement still required:** compare subsequent representative Expo/AYA core PRs against baseline, recording dispatch counts, total runner minutes, median/95th-percentile time-to-first-actionable failure and merge latency. No percentage speed-up is asserted from this structural improvement.

**Remaining separate evidence:** independent app authorship, actual Unity/FlutterFlow editor export, physical Android interaction/accessibility, recipient attachment ingestion and publicly resolvable native/npm artifacts.
