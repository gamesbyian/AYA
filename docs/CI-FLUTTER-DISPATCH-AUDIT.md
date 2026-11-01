# Flutter CI dispatch audit: avoid a redundant APK without dropping migration evidence

**Evidence:** 2026-10-31 UTC. Read alongside [CI engineering standard](CI-ENGINEERING-STANDARD.md) and [adapter release evidence](components/RELEASE-EVIDENCE.md).

## Existing native evidence

AYA currently runs three Flutter workflows when a native Flutter source file changes:

1. `flutter.yml`: Dart analysis, widget/bridge tests and an **in-tree** Flutter 3.47.9 AGP 9 debug APK build.
2. `flutter-external.yml`: **out-of-tree** source-package consumer using the same promoted Flutter 0.2 source and AGP 9 target, followed by final APK guide/manifest/DEX inspection. This is the stronger S2+ packaged-consumer contract, not an independently authored app.
3. `flutter-builtin-kotlin.yml`: the legacy-to-built-in-Kotlin migration toolchain, generating the modern candidate independently, checking migration-specific negative cases and building an APK. This protects a distinct compatibility/migration boundary and is retained.

Successful historical in-tree native Flutter jobs used the following runner-wall time:

| GitHub Actions run | Job start UTC | Job finish UTC | Runner-wall time |
| --- | --- | --- | --- |
| [41249286150](https://github.com/gamesbyian/AYA/actions/runs/41249286150) | 2026-10-31 22:41:10 | 22:45:43 | 4m33s |
| [41250574613](https://github.com/gamesbyian/AYA/actions/runs/41250574613) | 2026-10-31 22:59:28 | 23:03:11 | 3m43s |

These are two observations, not a forecast of billed minutes or a statistically reliable speed-up. The latter run also built an external host separately ([41250574535](https://github.com/gamesbyian/AYA/actions/runs/41250574535)), confirming overlapping native evidence.

## Change and preserved coverage

The in-tree `flutter.yml` now performs **Dart analyzer, widget/native-channel tests, deterministic component snippet compilation, host guide lint and independent reference audit** only. Java/Gradle setup, AAR staging and APK compilation are removed from this fast source job.

The canonical current-source **real APK** gate remains `flutter-external.yml`, which copies the actual promoted source package outside the monorepo and inspects the final Android APK and DEX. The **separate migration experiment** `flutter-builtin-kotlin.yml` still exercises conversion and a compiled APK under its specific toolchain. No stale/invalid guide, Activity, AYA share transport, or recipient acceptance test is being replaced by a mock.

`tools/test_flutter_ci_gate_ownership.py` verifies that the cheap source lane retains its relevant tests, both native lanes remain in place, and shared code/workflow changes continue to trigger their required checks.

## Expected impact and limits

One full in-tree Flutter Android APK job and its Java/Gradle setup are eliminated per relevant source/AYA-core change. Preserve measured baseline, run fresh native CI, and compare real dispatch/job duration after merge before making numerical savings claims.

This remains **first-party synthetic integration evidence**, not FlutterFlow Editor export, publicly installable pub.dev/native Maven distribution, physical device accessibility or proof that a receiving AI reads attachments.
