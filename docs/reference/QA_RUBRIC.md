# AYA reference quality rubric

Quality is measured on the **actual installed app and realistic support questions**. Structural validation checks headings/metadata; human or agent review checks truth and usefulness.

## Scoring

Score each criterion 0–4: 0 absent; 1 mostly absent/wrong; 2 partial; 3 sound with small gaps; 4 precise, evidence-backed, tested. Total /40.

| Criterion | What full score requires |
| --- | --- |
| Version truth | Exact release/variant/OS scope, AVAILABLE vs PLANNED vs CONDITIONAL accurate |
| Navigation | Every relevant screen and control path, exact UI text, states, accessibility variants |
| Core workflows | All top tasks include prerequisites, numbered steps, outcomes, recovery |
| Settings/features | Defaults, constraints, interactions, persistence, version applicability |
| Diagnostics | Symptom/real error strings, discriminating questions, safe fixes, verification |
| Data safety | Explains destructive actions, backup/undo, local/remote side effects |
| Permissions/privacy | Clear data flow, permission rationale, no credentials or private data |
| Unsupported/unknown | Honest limits, explicit uncertainties, no fictitious capabilities |
| Provenance | Claims trace to current code/release/tests; evidence ledger maintained |
| Assistant answer trials | Correct on sampled questions and appropriately refuses unsupported details |

### Gates

- **Mandatory:** validator exits 0; no secrets/PII; installed version and guide scope match; no unsupported feature presented as shipped; no fabricated UI paths.
- **Release-ready target:** 34/40 or higher, **no criterion below 3**, with zero critical factual or privacy errors.
- **Critical failure:** wrong destructive advice, false promise of remote data safety, fake credentials/authorization paths, false version availability, fabricated unsupported controls, or leaked secrets. Block release regardless of total.
- **Conditional coverage:** if a category is N/A, the guide must explain why. Do not silently skip authentication, offline operation or deletion.
- **Traceability:** top tasks, screens, settings and errors must each map to a specific reference section and evidence. A validator alone cannot verify this.

## Evaluation protocol

1. Construct a held-out list of 30–60 actual support questions with expected outcomes. Include novice, power-user, edge cases, adverse states and unanswerable questions.
2. For each, ask an assistant using *only* the shipped reference document, and record answer, factual errors, hallucinated controls, omissions and whether it requested sensitive data.
3. Independent reviewer checks steps against the installed build. Verify recoverability, not just wording.
4. Report task-completion rate, supported-answer precision, unsupported-answer calibration, and critical errors separately.
5. Fix reference sources or coverage, regenerate the shipped artifact, re-run all affected tests. Do not edit assistant answers to inflate scores.
6. Keep the results and guide revision linked in the release record.

### Severity

P0: privacy breach, destructive wrong advice, authentication bypass, false safety promise.
P1: wrong version/feature, nonexistent UI path, failed high-frequency workflow.
P2: omissions, unclear condition or incomplete troubleshooting.
P3: phrasing, synonyms, formatting.

P0/P1 block shipping; P2 requires documented disposition.
