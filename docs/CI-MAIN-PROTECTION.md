# Protecting AYA's main branch with an always-running CI baseline

**Current observation (2026-11-01 UTC):** GitHub's public branch metadata now reports `main.protected=true`. The repository has an [active `Default` ruleset #26302570](https://github.com/gamesbyian/AYA/rules/26302570) with pull-request, no-deletion and non-fast-forward restrictions. **Its `required_status_checks` array is empty**, so the always-on `docs` CI job is **not yet mandatory**. The ruleset was subsequently narrowed to **only `~DEFAULT_BRANCH`**; the earlier `~ALL` feature-branch overreach and HTTP 409 write failures are historical. A fresh feature-branch write probe is still required before claiming recovered iteration. **The required `docs` check is still not enforced.** The legacy branch-protection details endpoint still requires administration permission unavailable through this connector.

## Required-check compatibility

AYA's existing native APK workflows deliberately use `paths:` filters to avoid expensive unrelated dispatches. **Do not make a path-filtered native job a universal required status check**: a PR outside those paths may never receive that check and become blocked, or an incorrectly interpreted skipped result might give false confidence.

`.github/workflows/reference-guide.yml` now dispatches its lightweight `docs` job on **every `pull_request`**, regardless of source paths. It validates core reference/packet contracts, security-related schemas, module portability, component manifests, director understanding data, and the full repository Python validator regression suite. Its existing `main` push filter remains targeted; native workflows retain their more expensive risk-based triggers.

The deterministic `tools/test_reference_gate_dispatch.py` check prevents accidental reintroduction of PR path filters and verifies the baseline still includes its essential tests. A failing baseline produces a structured, non-speculative diagnostic artifact through [CI failure index](CI-FAILURE-INDEX.md). This job does **not** prove a feature-specific native APK; the appropriate filtered Android/Flutter/Expo/Godot/Unity checks remain mandatory for affected code.

## Repository-admin steps still required

In GitHub repository **Settings → Rules → Rulesets**, edit the existing active [`Default` ruleset #26302570](https://github.com/gamesbyian/AYA/rules/26302570):

1. **Completed at ruleset level:** branch matching now includes only `~DEFAULT_BRANCH` (the current `main`) and excludes the prior all-branches `~ALL` target. Preserve pull-request, no-force-push and no-deletion protections on `main`.
2. Under required status checks, add the actual **`docs`** context from the `Reference authoring checks` workflow, with source/actor pinning where supported. GitHub currently reports an empty required list, which means a failing `docs` job does not yet block a merge.
3. Confirm both a docs-only and a native-code PR produce the always-on `docs` check; separately prove a deliberately failing `docs` check cannot merge. Native jobs remain path-filtered and must be reviewed when affected, not added as globally required skipped contexts.
4. Test that an ordinary contributor can update a feature-branch PR head without bypass, while no direct unreviewed change can reach `main`. Confirm available bypass actors, review requirements and administrator recovery procedures intentionally.

**Verified:** branch protection is active. **Still unverified:** an enforceable required-`docs` check, a successful normal PR-head write probe, and fail-closed merge negative controls. See [issue #73](https://github.com/gamesbyian/AYA/issues/73). The current GitHub connector can read the ruleset but cannot mutate GitHub administration settings.
