# Controlled AYA packet evaluation

The [packet source compiler](README.md) verifies structure, provenance declarations, required dependencies, and size. It does **not** prove that an LLM read the packet, understood it, or produced an acceptable result. Use the existing [help evaluation protocol](../reference/EVALUATION_PROTOCOL.md) and this cross-module procedure for real-world acceptance.

## Trial procedure

1. Compile a byte-identical packet from the exact host release and save its SHA-256 in the build report.
2. Assemble held-out user goals **independently** of the packet writer. Include hard negative cases, fragile state distinctions, invalid schemas, privacy and destructive ambiguity. Do not reuse examples as validation questions.
3. Deliver the actual approved text and attachment in controlled sessions to each assistant/Android combination. Record provider app and version, Android version, exact tested packet, and whether the attachment was **actually ingested** (not merely offered in the Sharesheet).
4. Have an independent reviewer check actual answers against current host code and binary; for artifacts, import them using the real host validation path and test the resulting behavior.
5. Record results in a manually authored JSON `aya-packet-trials/v1` ledger. Preserve local test artifacts and an evidence reference; avoid private conversation uploads or credentials. For each case record ID, user goal, expected outcome, recipient, recipient version, Android version, UTC timestamp, ingestion confirmed, host outcome independently verified, reviewer, evidence ref, verdict (pass/fail/unknown), severity (P0-P3), and forbidden claims.
6. Run `python3 tools/validate_packet_trials.py trials.json --packet exact-packet.md`. It refuses packet-hash drift, duplicate IDs, false pass claims without ingestion and review, or any failed/unknown cases in strict mode. `--allow-unverified` emits an explicit incomplete report for development; it never labels an incomplete report ready.
7. Fix packet **source evidence** or host implementation, regenerate and retest. Never massage the recorded answer or use runtime AYA conversations as QA telemetry.

## Limits

The validator establishes the completeness/consistency of the *recorded* trials only. A dishonest or mistaken reviewer could record a fictitious pass; model capability and source truth require independent observation. The unit tests are **synthetic**, not AI-app compatibility evidence. One successful target does not verify other models, accounts, Android versions, or future application builds.

The AYA product still ends at the user's Share or Copy action. All trials are separate, explicitly authorized development QA.
