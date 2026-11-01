# Structured reference-validation failure index

The `Reference authoring checks` workflow emits a small machine-readable `aya-reference-failure-index` artifact **when a validation step fails**. The producing step appends a concise summary to GitHub's job summary. This is a first implementation of the agent-readable diagnostics requirement in [the CI engineering standard](CI-ENGINEERING-STANDARD.md).

## Observed facts and boundaries

`tools/ci_failure_digest.py` accepts the GitHub Actions `steps.<id>.outcome` values for each source- and packet-validation stage, in their actual workflow order. The JSON (`aya-ci-failure/v1`) records immutable run identity and SHA when available, executed/skipped/cancelled outcomes, failed-stage IDs, the first **observed failing stage**, and a link to the exact run.

The tool **does not infer a root cause** from a failed stage. Its `root_error` is explicitly `null`; inspect that step's real logs and reproduce its command from `.github/workflows/reference-guide.yml` before forming a hypothesis. It never uploads private question payloads, credentials, entire logs or model-generated content. If checkout or Python setup fails, the script itself may be unavailable; GitHub's raw failure log is then the only authoritative evidence.

The artifact is produced on failure, retained for 14 days and not distributed or reused as an input to release tasks. It does not call GitHub APIs or require additional permissions. The normal suite stays mandatory and continues to fail when an underlying test fails.

## Developer-agent use

1. Open the failed `Reference authoring checks` run and read the short job summary.
2. Read `aya-ci-failure.json` to identify failing and skipped stages and the exact commit, rather than guessing from the last line of a large log.
3. Follow the link to the first failing step and investigate its bounded, relevant log excerpt. Reproduce the command recorded in the checked-in workflow, not an inferred command.
4. If multiple stages failed, keep each failure separate. A later skipped stage cannot be marked passing; test outcomes do not certify source truth or recipient ingestion.
5. Update code and tests, never mask failures or weaken guide identity/portability constraints.

Run the offline contract tests with `python3 -m unittest discover -s tools -p 'test_ci_failure_digest.py'`.
