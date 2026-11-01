# Protecting AYA's main branch with an always-running CI baseline

**Current observation (2026-10-31 UTC):** GitHub's public branch metadata reported `main.protected=false`, and no repository rulesets were returned. Reading the legacy branch-protection endpoint requires administration permission not available through this connection. **No branch-protection change has been made.**

## Required-check compatibility

AYA's existing native APK workflows deliberately use `paths:` filters to avoid expensive unrelated dispatches. **Do not make a path-filtered native job a universal required status check**: a PR outside those paths may never receive that check and become blocked, or an incorrectly interpreted skipped result might give false confidence.

`.github/workflows/reference-guide.yml` now dispatches its lightweight `docs` job on **every `pull_request`**, regardless of source paths. It validates core reference/packet contracts, security-related schemas, module portability, component manifests, director understanding data, and the full repository Python validator regression suite. Its existing `main` push filter remains targeted; native workflows retain their more expensive risk-based triggers.

The deterministic `tools/test_reference_gate_dispatch.py` check prevents accidental reintroduction of PR path filters and verifies the baseline still includes its essential tests. A failing baseline produces a structured, non-speculative diagnostic artifact through [CI failure index](CI-FAILURE-INDEX.md). This job does **not** prove a feature-specific native APK; the appropriate filtered Android/Flutter/Expo/Godot/Unity checks remain mandatory for affected code.

## Repository-admin steps still required

A maintainer with repository administration rights should open the GitHub repository Settings, Rules, Rulesets (or Branch protection rules where appropriate), and create a rule targeting `main`. Require a pull request before merging, disallow force-push and branch deletion, and require the **successful actual `docs` job under `Reference authoring checks`**, selected from the completed check context shown in GitHub. Use source/actor pinning to avoid naming a similarly titled untrusted external check.

Before enabling the requirement, verify a documentation-only PR **and** a code-only PR both receive the `Reference authoring checks` job. Test that a genuine failing validator blocks merging; do not silently change required checks based on skip status. Add review/approval requirements compatible with the project's contributor model, and preserve admin override/break-glass policy explicitly rather than assuming it. Verify permissions and ruleset behavior through GitHub's own UI.

**The repository remains unprotected until the administrator actually enables the rule.** AYA agents must never claim a CI workflow edit, an issue, or a successful test enforces branch protection by itself.
