# Physical iPhone/iPad Files-return qualification (independent QA provider)

**Purpose.** Decide whether the persistent simulator LocalStorage `NSFileProviderErrorNonExistentItemIdentifier` failures reproduce on a genuine device. This is an acceptance procedure, **not** a claim that any device run has already passed.

## Prepare two separate installed applications

1. Use a macOS host with Xcode and `xcodegen`, a connected unlocked iPhone/iPad, and a signing team that can install development builds. Record the exact Xcode and iOS versions.
2. Generate the QA project from `integrations/apple/qa-share-receiver` using `xcodegen generate`. Open the project, set **CODE_SIGNING_ALLOWED=YES**, choose a signing team for both the containing app and its embedded Share Extension, and use valid unique bundle identifiers if the default example IDs cannot be provisioned. Install **AYA Share QA** on the physical device.
3. Generate the sample from `integrations/apple/sample` using `xcodegen generate`. Enable device signing and install the separate **AYA Lantern** sample. It must remain a different application/sandbox from the QA app. Do not add an App Group or private path shortcut to bridge them.
4. Record the exact source SHAs for both applications. For strict numeric-type, visible rejection and oversized-return assertions, build the importing sample from the acceptance implementation in [draft #147](https://github.com/gamesbyian/AYA/pull/147) or a later qualified integrated successor. The generic `main` sample alone does **not** currently establish every negative case in that branch.

## User-triggered fixture preparation

1. Open **AYA Share QA** on the physical device.
2. Tap **Prepare seven Files test documents**. Require the exact success text `Prepared: seven verified JSON files in this QA app's Documents folder`. A failure is a failed setup, not a test skip.
3. Open the system Files app and confirm **On My iPhone/iPad → AYA Share QA** contains seven `aya-layout-*.json` files. If the provider is absent or files cannot be selected, record that independently before testing the importing sample.
4. Preparing twice must verify existing bytes without replacing them. To reset, remove this disposable QA app and reinstall it. Do not erase or overwrite any unrelated files.

These files are entirely synthetic; one is an otherwise valid JSON object padded with whitespace to **4 MiB + 1 byte**. Do not submit user documents, secrets or real agent replies to this QA app.

## Strict manual acceptance

| Selection and action in **AYA Lantern** | Expected host state |
| --- | --- |
| User taps **Import saved agent output** then selects `aya-layout-valid.json` | A separate host semantic preview/Apply appears; current layout remains one column / warm until Apply |
| User taps **Cancel**, selects the same file again, then **Apply to demo** | Cancel preserves old state; explicit Apply changes to three columns / cool |
| `aya-layout-invalid.json` | Visible error, no Apply, unchanged state |
| `aya-layout-boolean.json` | Reject Boolean `columns`, no Apply |
| `aya-layout-float.json` | Reject floating `columns`, no Apply |
| `aya-layout-oversized.json` | Specific configured size-limit error, no Apply, unchanged state |
| Dismiss the Files picker without choosing a file | No preview, no mutation or fabricated selection |
| Select, then rapidly dismiss/reselect or background the app | No stale Apply; note whether any active read was interrupted or merely a pending picker was cancelled |

For each row capture the UI result **and** whether the OS picker actually called the host's selection completion. A test stuck at the Files screen or `picker-opened` does not qualify the host's reader/validator. Do not rely on a direct QA app container URL or a synthetic callback for any real Files-return row.

## Record evidence and escalation

Record: date/time, device model, exact iOS build, Xcode version, both app source SHAs and bundle IDs, active File Provider (local QA provider versus iCloud/other), fixture name, first/second attempt, host before/after state, any error, and evidence link. Exercise VoiceOver, largest Dynamic Type, keyboard and rotation separately; these are not implied by successful file transfer.

If a genuine device succeeds while simulator runs fail, preserve the simulator failures and classify the local provider as a **simulator acceptance blocker**, not a production-verified fix. If the physical device also fails at selection, collect its diagnostic logs with user consent and prepare a reduced Apple Feedback Assistant report referencing the LocalStorage `-1005` signature. If selection succeeds but reading/rejection fails, diagnose the now-reachable AYA snapshot/semantic boundary separately.

**Release rule:** device checks, external assistant ingestion, full in-flight provider cancellation and signed distributable SDK remain separate acceptance gates. Never close #147 or #120 solely because the fixture setup screen compiles.
