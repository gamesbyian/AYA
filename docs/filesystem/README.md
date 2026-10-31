# Filesystem Automation Handoff (optional AYA module)

**Audience:** developers of file managers, FTP/FTPS/SFTP clients, SAF/Android storage browsers, WebDAV/SMB/cloud file explorers and similar hosts. **No Expository-specific dependencies or assumptions.**

A host app offers a normal **Automation > Import recipe** workflow and optionally an **Ask Your Agent** card. The host creates a source-verified Filesystem Automation Kit and, with separate explicit user consent, may attach a minimized and dated filesystem snapshot. AYA opens a user-editable one-way handoff to the user's preferred Android assistant. The assistant clarifies consequential user intent and proposes a recipe **in the host's own documented schema**. The person saves that file and manually imports it. The host validates, enumerates, previews, revalidates and executes approved operations. AYA never scans files, executes commands, observes the response, or installs recipes.

## Start here

1. Follow [AYA-AUF](../understanding/README.md), [Director consultation](../understanding/CONSULTATION.md), [AYA-RAS](../reference/INDEX.md) and the [common packet authoring standard](../packet/AUTHORING_STANDARD.md). Confirm the installed build actually includes a safe recipe importer/executor. An intention or plan is insufficient.
2. Read [Host authoring standard](AUTHORING.md), including schema provenance, backend truth matrix, capability limits, conflict handling and operation-level safety.
3. Bundle an exact-version `aya-guide.md` and `aya-filesystem-kit.md`. Validate the kit offline and check the actual importer with independently constructed positive and negative tests.
4. If offering context, generate an on-device [Filesystem Snapshot](SNAPSHOTS.md) from the host's already authorized backend; ask the user before scanning or sharing. Do not include passwords or raw URLs with credentials.
5. Call the typed Android handoff below. It validates the guide, kit and optional bounded snapshot before opening review. The end user still selects a recipient or Copy.
6. Verify on real target devices and recipient versions, using [QA and failure gates](TEST_PLAN.md). The host importer is a separate safety release gate.

## Android host integration

```kotlin
val direction = automationTextField.text.toString() // user-edited in host
val context: String? = approvedFilesystemSnapshotJson // optional; host-generated and user-approved
when (val result = Aya.launchFilesystemBundled(
    activity = this,
    task = AyaFilesystemTask(
        recipePurpose = "file cleanup recipe",
        importInstructions = "Automation > Import recipe > Review > Approve"
    ),
    kitAsset = "aya-filesystem-kit.md",
    guideAsset = "aya-guide.md",
    screenName = "Automation",
    direction = direction,
    askDirection = false, // true opens the AYA local composer when no host editor exists
    snapshotJson = context
)) {
    is AyaBundledLaunchResult.Rejected -> showError(result.reason)
    AyaBundledLaunchResult.QuestionOpened -> Unit
    AyaBundledLaunchResult.PreviewOpened -> Unit
}
```

**This is an integration sketch.** `approvedFilesystemSnapshotJson`, `automationTextField` and `showError` belong to the host. They are intentionally not AYA scanner APIs. `QuestionOpened` and `PreviewOpened` describe only local UI. They do not signal that a third-party assistant opened a chat, read attachments or created a recipe.

Use the [AYA Card UI Standard](../CARD_UI_STANDARD.md) for a contextual, outlined host-themed card. A generic `AyaCardView` currently launches the ordinary Help route. A filesystem automation card must call `launchFilesystemBundled`, disclose the extra kit and optional snapshot and preserve the same full editable review. Do not overwrite a Help card's expectations.

## Contract boundaries

- **Build-time static:** the host-specific kit documents the exact released parser schema, supported operators, backend variants, exception policies and actual import steps. Structural AYA verification does not certify that documentation.
- **Optional runtime data:** a snapshot, at most 512 KiB, is a host-generated, time-stamped, user-reviewed description of a bounded scope. The host owns scanning, completeness accounting and redaction. Never gather it secretly.
- **Agent-authored:** a proposal, not authority or a verified list of files to change. Unknown intent must be clarified; unsupported actions must be refused.
- **Host-controlled:** import validation, identity/root authorization, bounded execution, dry-run and target review, user confirmation, revalidation and accurate outcomes. Do not trust the recipe's own claims of harmlessness.
- **AYA:** exact-build guard, local editable review, public Android text attachment sharing/Copy, and then stops. There is no polling, AI API, automatic result ingestion, or callback.

The [snapshot JSON Schema](schemas/aya-filesystem-snapshot-v1.schema.json) is shared guidance for context exchange; **AYA does not prescribe a universal executable recipe language**. Each host must document and enforce its own actual output schema. The [HarborFiles kit](examples/harborfiles-kit.md), [recipe schema](examples/harborfiles-recipe.schema.json), [recipe](examples/harborfiles-delete.recipe.json) and [snapshot](examples/harborfiles-snapshot.json) are deliberately fictional training fixtures, not production compatibility claims.

## Status

The Kotlin SDK includes a typed filesystem task and the guarded one-file reviewed handoff; snapshot scanning, UI selection/redaction, host recipe validators, executors, import screens and live-recipient acceptance are not part of AYA and are **not implemented by this module**. Version and JSON-shape checks do not prove filesystem safety. See [security](../SECURITY.md) and [test plan](TEST_PLAN.md).
