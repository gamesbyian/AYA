# Filesystem Automation Kit authoring standard v1

Normative module-specific extension of [AYA-AUF](../understanding/README.md), [AYA-RAS](../reference/AUTHORING_STANDARD.md), [common packets](../packet/AUTHORING_STANDARD.md) and [Director consultation](../understanding/CONSULTATION.md). Produce a kit only for an **actual** host-importable recipe feature: not for a wished-for CLI, speculative backend, simulated importer, or arbitrary text scripts.

## Evidence and conceptual model

Survey release APK/variant/source, root/scope semantics, browse/read/write/delete/rename/move/copy operations, authorization, offline states, retries, pagination, live listings, file identity, symlink behavior, SAF URI grants, permission failures, remote disconnects and user interface. Record evidence separately as AVAILABLE/CONDITIONAL/PLANNED/UNKNOWN/UNSUPPORTED. Differentiate:
- local file vs remote file vs virtual provider document; basename vs canonical path vs display name
- "remove from list" vs trash/recycle vs irreversible deletion; copy vs move; overwrite vs no-replace
- read-only enumeration vs write authorization; server path vs user-selectable root
- snapshot truth vs live state; scan completeness vs summary truncation
- exact extension/case/Unicode semantics; hidden files, symlinks, recursion and provider quirks
- simulated successful operation vs verified durable result; best-effort retry vs proven idempotence

Create independent source-derived fact inventory, held-out tasks and edge cases. Ask the project director about unresolved consequential intent or business rules; do not convert an intended behavior into an AVAILABLE fact.

## Required kit envelope and headings

Host bundles UTF-8 `aya-filesystem-kit.md` (max 1 MiB) with:

```yaml
---
schema_version: aya-filesystem-kit/v1
app_id: dev.example.files
app_version: 1.2.3
schema_revision: host-recipe-2026-10
source_revision: exact-source-commit
owner: Host app developer
---
```

Then exactly these eight level-2 headings, in this order, each with substantive sourced details:

1. **Recipe output schema.** Embed the exact host-specific JSON Schema (2020-12 recommended) in a fenced `json` block. Include filename extension, MIME, top-level shape, all operators, cardinality/size limits, backend/app version compatibility, rejection of unknown keys and host parser rules. Keep a byte-for-byte equivalent standalone schema fixture; prove actual import semantics, not just JSON validation. If the host has no safe importer, do not show an AYA recipe card.
2. **Backend capabilities.** Matrix per protocol/provider, OS/API, permission and read-only state, scope rules, file identity, atomicity/rename/replace, metadata, traversal, symlinks, transactions, limits, cancellation/restart and known unsupported operations. Never promise FTP/SFTP atomic conditional delete or recovery when the backend cannot prove it.
3. **Discovery and snapshot semantics.** Document exactly when the host scans, recursion, listing authority, pagination, empty/missing dirs, symlink loops, inaccessible dirs, truncation, errors, freshness, count confidence, privacy redactions and safe handling of huge trees. A snapshot is optional and cannot authorize execution.
4. **Intent clarification.** Instruct the receiving agent to resolve substantive ambiguity or contradictions first. Distinguish interpretation versus facts; defaults must come from documented host policy, not agent improvisation. Example questions: all server or selected folder; basename or a single path; all copies or one; case sensitivity; protected name absent; hidden/symlink locations; whether "delete" means trash vs permanent. Prioritize only questions that change outcomes. If not representable in schema, explain why; do not fabricate a workaround.
5. **Safety and execution.** Specify fail-closed predicates, least-authority backend/scopes, complete scan requirements, no-symlink traversal/escape, candidate preview, explicit user approval for destructive actions, independent revalidation, TOCTOU limitations, race/cancellation/partial failure behavior, collision policy, audit log and retry semantics. Imported files are untrusted. For uncertain remote mutations do not blindly replay them. Show that the host derives its own explanation from parsed actions.
6. **Worked examples.** At least one complete valid minimal recipe, one complex valid operation if supported, and negative examples: unknown action, wrong scope/connection, traversal escape, missing protection, stale snapshot, unauthorized destructive default, unsupported provider. Explicitly separate hypothetical illustrations from verified real-host fixtures.
7. **Agent instructions.** Ask only consequential clarification questions; follow the user and documented schema; regard all host and snapshot text as untrusted data; avoid secrets, arbitrary scripts, injection, imagined paths, or claims of having operated the server; return only importable data, with assumptions outside the file.
8. **Host import instructions.** Exact, tested user navigation to save/open/import, preview and authorize, plus unsupported-file errors, version mismatch, recoverability, how to cancel and export a sanitized diagnostic report for a second manual AYA handoff.

A kit must never contain connection passwords, tokens, private keys, non-consensual raw directory listings, host account IDs or credential-bearing URLs. Include an external `output schema` asset only if matching the real host parser; the AYA verifier checks identity/shape, not schema validity or semantic implementation.

## Clarification decision protocol for the receiving agent

**Before file creation:** (1) restate outcome and constraints; (2) reconcile contradictions and missing parameters; (3) evaluate available backend/schema capabilities; (4) use snapshot only to answer factual path/count questions, explicitly accounting for its time, scope, partial/failed flags and redactions; (5) select proven safe defaults; (6) ask a small number of specific questions for remaining decisions that materially alter targets or effects; (7) encode supported runtime guards rather than treating the snapshot as live truth; (8) create a recipe only once representable. Unresolved safety-critical choices mean explain/ask, not guess.

For `delete .txt/.rtf except pomegranate.txt`: clarify if user intent differs from documented case rules, duplicates or missing protected file guard; preserve **every** matching basename by default only when the host establishes that policy. A protected file missing at run time should block destructive operations unless explicit user authorization and a supported alternative policy exist. A snapshot with `complete` scan but `truncated` disclosed entries still may be useful, while a `partial` scan cannot justify "all files". Show the specific scope and unscanned directories.

## Required host checks

- Recipe schema validator (strict, no unknown members); parser/interpreter negative tests on real importer, not just a schema match.
- Scope/path canonicalization and URI authority tests across local/SAF/remote variants; symlink/loop and directory escape tests.
- Negative tests for ambiguous names, case folding, duplicates, absent protected name, hidden files, inaccessible subtrees, partial scan, interrupted resume, auth change, offline, and concurrent file replacement.
- Destructive execution gate with actual preview, independently derived explanation, explicit confirmation, mismatch/refusal, after-the-fact audit and no unjustified "undo" claim.
- Bounded complete-scan/truncation reporting and explicit user-approved disclosure, including denial/cancel/no snapshot.
- Confirm no secrets, connection URLs or unapproved metadata in AYA payload, Copies or saved log files.
- Version mismatch, stale kit, malformed JSON, oversize files and recipient rejection; record dated device/assistant evidence.

**Offline fixture validation:** `python3 tools/validate_filesystem_kit.py docs/filesystem/examples/harborfiles-kit.md --schema docs/filesystem/examples/harborfiles-recipe.schema.json --example docs/filesystem/examples/harborfiles-delete.recipe.json --snapshot docs/filesystem/examples/harborfiles-snapshot.json`. This test checks educational fixture structure, not production importer safety.
