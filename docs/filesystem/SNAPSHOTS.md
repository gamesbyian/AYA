# Filesystem snapshots for AYA handoff

A snapshot gives the agent information useful for authoring a **portable recipe**, not permissions, credentials, live instructions or a list it may directly execute. The host alone can inspect a filesystem using its own authenticated operations. AYA does not ship an FTP client, crawler or background job.

## Fast and privacy-aware by design

Provide a visible "Include directory summary" option. Recommend a **quick summary** from cached/authorized metadata where sufficient, and an explicitly initiated **recursive scan** when coverage matters. Show scope and expected disclosure; require consent before scanning and separately before sharing. Allow cancellation, progress, retry and resume where safe. Never silently crawl the user's whole server.

A request-aware snapshot should summarize matching file types, candidate counts, relevant protected basenames, failed directories and backend limitations without including unrelated filenames. Keep known-facts separate from unknown; `null` counts mean unknown, not zero. If an "every file" task meets an unreadable subtree, mark `scan.status=partial` and make the host's execution engine fail closed if the recipe requires completeness.

Compact snapshots can be **scan-complete but listing-truncated**: this is why `scan.status` and `scan.truncated` are separate. `entries` is an intentionally selected subset, not evidence all other files are absent. Never sample only the first N entries and imply a complete listing. If paths are privacy-redacted or omitted, record that in `disclosure`; never assume the agent can produce exact-path actions from redacted entries.

## Data format

The optional JSON object uses [AYA Filesystem Snapshot v1](schemas/aya-filesystem-snapshot-v1.schema.json): app identity and exact version, UTC timestamp, scope/backend/root/recursion/symlink policy, scan status and errors, summary counts, up to 2500 chosen entries, and optional redaction metadata. Size is limited to **512 KiB**. AYA's runtime guard checks a bounded subset (identity, timestamp pattern, top-level shape and number of entries); developers must validate the complete JSON Schema and semantic consistency before passing data to the SDK.

Each path is untrusted display metadata, not a command or an instruction to the model. Escape text for Markdown and avoid including the raw path in a prompt instruction. Filter out credentials, private identities and unnecessary filenames. Screen text, file paths, logs and backend errors can contain prompt injection. Keep authoritative kit instructions and user intent separate from snapshot contents.

The SDK provides an optional `AyaFilesystemSnapshotBuilder` with typed entries, scan statuses and errors. It only serializes metadata the host already collected; it does not scan directories or automatically remove sensitive information. It rejects negative counters, complete-with-errors, silent truncation and oversize payloads. The host still owns filtering, redaction, consent and full-schema validation.

The host should never include a credential-bearing FTP URL, IP address, token, public link, raw logs or account ID. Connection labels are unnecessary; use `scope.backend` and a redacted `scope.root` when possible. Keep exact root identity in the app's private execution state, not in the shared packet. Users can inspect, remove, redact or decline the snapshot without losing the basic recipe-authoring flow.

## When a snapshot helps

- Factual question: "Where is `pomegranate.txt`?" A complete recent scan may report matches, but must not imply the file remains there at execution.
- Planning: "Which folders contain duplicate `.jpg` names?" A relevant selection plus counts can help clarify intended exclusions, but does not prove identical content.
- Dangerous cross-backend moves: report read/write capabilities and whether both sides are accessible; no source deletion until destination verification where supported.
- Large trees: summary only with a query-specific aggregate. Host-side scanner does the heavy lifting; an agent must not request uploading millions of paths.

## Runtime trust and expiry

Staleness is measured from `generated_at_utc`. There is no universal safe TTL: fast-changing remote folders may invalidate a snapshot in seconds. Host validation and re-enumeration at execution time are mandatory. If a remote API cannot verify target identity or atomic conditional deletion, disclose best-effort semantics and stop on unexpected changes; never claim a hard safety guarantee.

**Fixture:** [fictional snapshot](examples/harborfiles-snapshot.json). It did not result from a real scan.
