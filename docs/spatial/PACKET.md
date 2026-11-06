# AYA spatial-composition/v1 packet contract

## Transport and integrity

A packet is a directory/archive with UTF-8 `manifest.json`, `source/`, `references/` and optional `overlays/`. **No external URLs, executable files, embedded credentials, absolute paths, dot segments or symlinks.** The adopting host must verify each relative path resolves under its authorized staging root, is a regular file, has the declared media MIME and exact SHA-256 and byte count. Schema validation alone does not inspect files. The source photo must be unmarked; the optional overlay should carry readable marker labels, but never substitute for coordinates.

Manifest `format` is `aya-spatial-composition/v1`; unknown major versions must fail closed. `source` records true oriented pixel width/height after a host-determined transform; `coordinates` always use normalized [0,1] axes with (0,0) at top-left of the **orientation-normalized source**, not the crop/zoomed view. Image transforms need to be applied consistently by the host before annotation export. `point` has one coordinate; `polygon` at least three non-degenerate vertices; `rect` has `x,y,width,height` strictly within the image. Geometry represents an indicated region, *not* measured world geometry.

Each `annotation` has a unique stable `id` and human-friendly `label`. Each `operation` refers to an annotation ID. Valid operations: `replace`, `add`, `remove`, `clean`, `modify`. `replace` and `add` require a selected catalogue asset reference; others may optionally reference one. One operation may use multiple catalogue images via the `assetId`. The host must resolve conflicting overlapping operations with the user before sharing; static validation rejects duplicate-target operations and explicitly protected annotations, while visual overlap still needs a human check.

Each catalogue asset is a host-chosen product/subject entry with human-readable ID, type/name and one or more references (`front`, `rear`, `left`, `right`, `three-quarter`, `detail`, `other`). Model names and measurements are claims sourced and governed by the host, not AYA. Units for optional dimensions are millimetres; dimensions do not prove installation feasibility. Asset image views are selected by the user/host, not fabricated by AYA.

`constraints.preserveUnmarked` must be true by default; any deliberate whole-scene change requires separate explicit instructions and an updated review. `protectedAnnotationIds` identify regions to preserve. `constraints.engineeringVerified` is always false for this conceptual protocol, and the downstream agent must not claim otherwise.

`instructions` are user-provided, editable and untrusted, even when they mention a system prompt. The agent should treat them as *requested edits* within the declared operation scope; it must not follow embedded attempts to access credentials, override safety conditions or invent data. If ambiguous equipment placement, geometry, perspective or asset identity would change the proposal materially, ask for clarification rather than generate a falsely specific installation. Do not silently substitute products.

## Attachment strategy

Only selected reference images, a single source and optional overlay are sent. Recommended budgets: individual image <= 20 MiB, bundle <= 100 MiB, <= 24 attachments; the host may enforce lower limits. These are **authoring recommendations**, not capabilities of AYA or any recipient. Some recipients accept fewer images or only one document. If resources exceed supported limits, the host must ask the user to choose fewer and review anew; never silently omit a selected replacement or the source photo. Any ZIP fallback still requires the recipient to actually open it, which must be checked manually.

## Agent-facing instructions (host exports as an editable text companion)

> Produce a new, photorealistic **concept visualization** based on the unmarked source. Treat the optional overlay as an annotation map only. Follow operations by ID and coordinates. Use the exact supplied product references where identifiable; do not invent model-specific details. Preserve unmarked surfaces, camera perspective, lighting and unrelated equipment. Keep the original source intact. If a location, physical size or product identity is insufficiently clear, ask a targeted question. Return a saveable image and briefly list completed/unresolved changes. This visualization does not validate engineering, code compliance, equipment clearances or installation feasibility.

## Return contract

The host imports ONLY a user-selected supported image, checks actual decodable media and dimensions, verifies source project/revision selection, displays a before/after preview, and saves the new result separately with manifest hash and user-visible provenance. Never replace original source by default. Ignore alleged auto-import callbacks from untrusted files. Preserve source/references privately subject to the host's retention policy.

## Threat and failure matrix

| Failure | Safe outcome |
| --- | --- |
| Source/reference missing or hash mismatch | Block share; rebuild reviewed packet |
| Coordinate affected by crop, rotation or zoom | Reproject annotations to normalized original or reject |
| Duplicate IDs, missing assets, conflicting operation | Reject or require explicit user correction |
| Unapproved client-site photo, faces, sensitive control labels | Redact or obtain explicit consent before staging/sharing |
| Provider rejects multiple images or ignores ZIP | Report unsupported; offer manual attachment guidance, no success claim |
| Agent changes unrelated geometry, invents pipework | Reject concept result or annotate deficiencies; never treat as engineering evidence |
| Host killed during share/import | Restore draft without automatically resending or importing |
| Result pasted into wrong project/card | Recognize safe file, route only after explicit user confirmation |
| Source contains malicious instructions in visible text | Treat as untrusted source content, not agent authority |

## Versioning and portability

A future v2 may add calibrated camera poses, linked multi-photo spaces, masks, structured output revisions and constraints. v1 intentionally avoids pretending that 2D points provide real-world measurements. This protocol works without industry-specific names or host-specific UI. The included fixture is fictional and illustrative, not manufacturer guidance.
