# AYA behaviour compatibility and review evidence (v1)

This is an optional, non-proprietary **behavioural** compatibility standard. Developers do not need AYA code or permission to implement the concept. An SDK integration and a self-implemented handoff may both be assessed with the same criteria.

This is **not** certification or proof that a third-party assistant will read the attachment. A parsed JSON record proves only that somebody filled in a form. Every pass still requires attributable, release-specific independent technical evidence. Do not advertise a passing schema as approval by AYA maintainers.

## Mandatory cases

- `installed_version_identity`: Guide and host version match actual installed build.
- `source_backed_scope`: Guide facts are traceable to shipped behavior and current host evidence.
- `explicit_user_initiation`: Only a deliberate user action opens the handoff.
- `editable_review`: Full outgoing content can be inspected and edited before sharing.
- `cancel_without_share`: Cancel leaves app open and transfers nothing.
- `manual_copy_fallback`: Copy/manual path remains available when share targets fail.
- `reject_missing_stale_guide`: Missing or stale guide refuses without unguarded fallback.
- `read_only_attachment`: When using attachments, only scoped content URI read grants are given.
- `provider_neutrality`: No forced AI provider, required login or backend inference.
- `truthful_return_use`: Host explains how output is actually used or manually followed.
- `no_answer_monitoring`: No recording, scraping or watching agent replies.
- `accessibility_lifecycle`: Screen reader, focus, narrow view and rotation tested.

Use [the JSON Schema](aya-compatibility-v1.schema.json) and [explicitly unverified fictional fixture](examples/unverified-fictional.json). The required 12 case IDs must appear exactly once. A case may be `pass`, `fail`, or `unverified`. `not_applicable` is allowed only for `read_only_attachment` when the host **never** sends a file and its evidence explains the text-only transport. Other bypasses are rejected.

A pass needs `test_method` other than `unverified`, a useful `notes` account and at least one independently reviewable `evidence_refs` identifier. The checker treats those references as opaque, because blindly opening arbitrary local paths/URLs would expose private or irrelevant data. A reviewer must investigate scope, freshness and authenticity separately. No raw conversation dumps, private IDs, secrets, cloud account details or actual agent responses belong in evidence records.

Examples of acceptable evidence include a committed Android instrumentation test result, manually recorded dated OS/app build and accessibility QA, an audited reference inventory with its source revision, or provider-neutral shared-URI contract tests. A screenshot of an Android chooser proves only the chooser was shown.

## CLI

```sh
python3 tools/check_component_compatibility.py docs/components/conformance/examples/unverified-fictional.json --allow-incomplete
python3 -m unittest discover -s tools -p 'test_*.py'
```

The default mode rejects incomplete or failed cases. `--allow-incomplete` is for developers' drafts and outputs an honest **incomplete** status, not a badge or certification. The checker can only decide whether the submitted record is structurally complete and all cases have declared supporting evidence; it cannot validate the truth of those claims or a receiving AI client's behaviour.

This supplements [AYA-AUF](../../understanding/README.md), [AYA-RAS](../../reference/INDEX.md), [Packet Authoring](../../packet/README.md) and the [Drop-in Components standard](../README.md). Different installed builds require different evidence records, not an unbounded "works everywhere" claim.
