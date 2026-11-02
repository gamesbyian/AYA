# Controlled AYA packet evaluation

The [packet source compiler](README.md) verifies structure, provenance declarations, required dependencies, and size. It does **not** prove that an LLM read the packet, understood it, or produced an acceptable result. The trial ledger supports all five compiled profiles: `help`, `creative`, `structured`, `translation` and `filesystem`. Filesystem trials additionally require checking the host's real recipe parser, user approval and refusal of unsafe destructive proposals; a simulated deletion or model answer alone cannot establish execution safety.

Use the existing [help evaluation protocol](../reference/EVALUATION_PROTOCOL.md) and this cross-module procedure for real-world acceptance.

## Trial procedure

1. Compile a byte-identical packet from the exact host release and save its SHA-256 in the build report.
2. Assemble held-out user goals **independently** of the packet writer. Include hard negative cases, fragile state distinctions, invalid schemas, privacy and destructive ambiguity. Do not reuse examples as validation questions.
3. Deliver the actual approved text and attachment in controlled sessions to each assistant/Android combination. Record provider app and version, Android version, exact tested packet, and whether the attachment was **actually ingested** (not merely offered in the Sharesheet).
4. Have an independent reviewer check actual answers against current host code and binary; for artifacts, import them using the real host validation path and test the resulting behavior.
5. Record results in a manually authored JSON **`aya-packet-trials/v2`** ledger. Preserve local test artifacts and an evidence reference; avoid private conversation uploads or credentials. For each case record ID, user goal, expected outcome, recipient, recipient version, Android version, UTC timestamp, evidence kind, transport, actual recipient-input receipt, attachment ingestion (when applicable), host outcome independently verified, reviewer, evidence ref, verdict (pass/fail/unknown), severity (P0-P3), and forbidden claims. Actual recipient QA also records tested receiver package, Android API, device/emulator classification and the SHA-256 of the host APK used.
6. Run `python3 tools/validate_packet_trials.py trials.json --packet exact-packet.md`. It refuses packet-hash drift, duplicate IDs, false pass claims without appropriate real input receipt and host review, or any failed/unknown/non-real cases in strict mode. `--allow-unverified` emits an explicit incomplete report for development; it never labels an incomplete report ready.
7. Fix packet **source evidence** or host implementation, regenerate and retest. Never massage the recorded answer or use runtime AYA conversations as QA telemetry.

## v2 evidence classification and v1 compatibility

The v1 validator could report `release_gate_pass=true` for a **synthetic fixture** if the author marked the ingestion and outcome booleans true. That overstates what the ledger demonstrates. **v1 ledgers remain parseable** and retain their per-case outcomes, but now return `release_gate_pass=false` with `unqualified_trial_ids`; they cannot satisfy the strict release gate. Do not simply relabel a fixture as real. Re-test real recipient/host behaviour before creating a v2 record.

In v2, each case includes:

- `evidence_kind`: `real_recipient`, `synthetic_fixture`, or `documentation_only`. **Only real recipient cases can qualify for release**; combining even one non-real case into the same ledger blocks that ledger's release pass.
- `transport`: `text_only`, `text_and_txt_reference`, `txt_reference_only`, `image_attachment`, `multiple_attachments`, or `process_text`. This identifies which actual delivery mode was tested, not the assistant's general capabilities.
- `recipient_input_verified`: boolean confirming that the destination actually received and displayed/read the intended material, independently of Sharesheet discovery. `attachment_ingested` is separately required for modes carrying files; `text_only` and `process_text` must not falsely require an attachment.
- For `real_recipient`: `recipient_package` (actual Android package ID), `android_api_level` (integer), `device_kind` (`physical_android` or `android_emulator`) and `host_artifact_sha256` (64-digit actual host APK SHA-256). The existing recipient version, UTC timestamp, reviewer and evidence reference remain mandatory.

A minimal *synthetic example* of the extra fields for a real-recipient-shaped record is shown below. **It is not QA evidence** and must never be copied as if a device was actually tested:

```json
{
  "evidence_kind": "real_recipient",
  "transport": "text_and_txt_reference",
  "recipient_input_verified": true,
  "attachment_ingested": true,
  "host_outcome_verified": true,
  "recipient_package": "org.example.testassistant",
  "android_api_level": 35,
  "device_kind": "android_emulator",
  "host_artifact_sha256": "0000000000000000000000000000000000000000000000000000000000000000"
}
```

The report distinguishes `attachments_reported_ingested` (all declared records, including fixtures and legacy v1) from `attachments_confirmed_ingested` (the older field name, now counted **only** from explicitly classified v2 real-recipient cases). Neither count automatically verifies the truth of the underlying observation, and a record claiming success still requires independent review. The validator checks **self-reported structure**, not the external truth of observations, existence of the referenced APK, assistant versions, or reviewer independence. Even a well-formed real-recipient declaration requires an actual independently reviewable observation. An emulator real-recipient trial does not automatically establish physical-device S4 or general S5 compatibility. Scope every conclusion to the exact versions, account state and transport tested.

## Limits

The validator establishes the completeness/consistency of the *recorded* trials only. A dishonest or mistaken reviewer could record a fictitious pass; model capability and source truth require independent observation. The unit tests are **synthetic**, not AI-app compatibility evidence. One successful target does not verify other models, accounts, Android versions, or future application builds.

The AYA product still ends at the user's Share or Copy action. All trials are separate, explicitly authorized development QA.
