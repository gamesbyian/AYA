# Second cross-category challenge: 147 questions across 21 apps

**Recorded:** 2026-10-28. **Source:** user-supplied research-informed candidate question inventory; external research claims, search-volume ordering, app feature availability and documentation links are **not independently verified** here. This is a taxonomy/authoring stress test, not a factual product FAQ, a benchmark with known correct answers, or a claim that one app is the biggest in its category.

The original inventory describes **30 categories × 7 questions = 210 questions**, but the material actually provided in this review ends at **category 21, Microsoft Teams**. Thus this repository records exactly **21 × 7 = 147 questions**. Do not imply the remaining nine categories or 63 questions were reviewed.

## Canonical fixture and integrity check

- **Structured complete question bank:** [cross_category_batch2_147.json](examples/cross_category_batch2_147.json), preserving every received question's intent in close paraphrase, a stable ID `B2-01-01` through `B2-21-07`, its named app and category, and annotated challenge boundaries.
- **Coverage guard:** `python3 -m unittest tools.test_cross_category_fixtures`, also covered by the normal `python3 -m unittest discover -s tools -p 'test_*.py'` command.
- **Round-one taxonomy:** [90-question cross-category challenge](CROSS_CATEGORY_STRESS_TEST.md).

The JSON is intentionally **not `aya-questions/v1`**. No independently verified app version, gold answer, permitted/forbidden assertions or runtime conditions have been established. Using it directly as a release qualification would be misleading. Convert selected prompts into verified, version-specific `aya-questions/v1` tests before scoring a real integration.

## What's genuinely new relative to the first 90 prompts?

The previous challenge already covered app navigation, permission/version gates, negative capabilities, secrets, cloud copies, Android/OEM dependence and volatile policies. These 147 questions put considerably more weight on five **additional** failure classes.

### T: Time-sensitive, partially committed transactions

**Examples:** Gmail's Undo Send window; Uber cancellation fees; Amazon post-order address edits; Uber Eats cancel/refund eligibility; Booking.com refund terms; paid subscriptions and duplicate card authorizations.

A feature guide must describe a *transaction lifecycle* at a useful level. Document observed stages such as **draft → submitted → pending acceptance → accepted/processing → committed → fulfilled/cancelled/disputed/reversed**, adjusting to the *real service*, and map each permissible action to a state. Include:

- Who can still cancel/change what at **each stage**, any verified time window, policy/region/tier variation and where to check the current status.
- Whether the action creates a **pending authorization** versus a settled charge; refund request acceptance versus refund paid; queued send cancellation versus recall of already delivered content.
- The expected result, confirmation and whether a retry can create a **duplicate booking, order, message, refund claim or payment**.
- Timezone effects for booking and scheduled-message tasks, and whether scheduling guarantees availability/courier assignment.
- When service discretion or a human decision supersedes the app control.

Never invent fees, windows, refund entitlements or price guarantees. If the state/policy cannot be verified, guide the user to a safe check and distinguish what is still reversible from what is already committed.

### A: An explicit authority and adjudication graph

**Examples:** Booking.com versus hotel versus bank; Google Wallet versus issuing bank and terminal; Uber Eats versus courier versus merchant; Microsoft Teams versus workplace/tenant admin; Google Messages versus carrier and device OEM.

Document each participant's **responsibility**, **authority to change state**, **evidence visible to the user**, **escalation route**, and **limits on what the host can observe**. The correct answer may be different depending on which party charged, denied access, delivered a service, or set a workspace policy.

Support journeys should give an escalation ladder grounded in *real official channels*, with safe evidence (transaction IDs entered in official channels, timestamps, screenshots redacted as needed) and a clear distinction between **request filed**, **request accepted**, **request resolved**, and **money/data actually returned**. Do not request payment credentials in an agent chat or promise the third party will grant relief.

### L: Diagnose multi-layer delivery and media pipelines

**Examples:** Google Messages RCS provisioning/verification; WhatsApp codes/notifications; Gmail sync; Teams Android message/call alerts; Calendar reminders; Chrome site notices; Google Wallet NFC; Spotify Bluetooth/Android Auto.

A useful diagnosis tree models a chain, not a single toggle. Where applicable:
1. Did the remote service/carrier/publisher produce the event or approve the operation?
2. Did the network or device transport receive it (carrier SMS, RCS registration, push delivery, local network, Bluetooth)?
3. Is the intended account, device, chat, profile or endpoint selected?
4. Do app preferences/channels and Android notification permissions permit presentation?
5. Are DND/Focus, device battery restrictions, background-data rules or OEM differences interfering?
6. Can the user distinguish **event never sent**, **sent but not received**, **received but not surfaced**, and **surfaced on another device/account**?

These are hypotheses and checks to adapt to the actual app, not a blanket recommendation to disable battery optimization or reset data. Document the *least destructive test first*. RCS/SMS/MMS are distinct transports; don't equate a successful general internet connection with carrier verification. State which evidence is inaccessible without service-side diagnostics.

### E: Hidden states and unprovable inferences

**Examples:** "Who viewed my Instagram profile?"; "Was I blocked?"; "Am I shadowbanned?"; why a title or song disappeared; whether marketplace moderation targeted a user; inexplicably low engagement; Teams showing Away.

Separate:
- **Observable:** current UI labels, official account/status notifications, content availability in a documented region, logged errors.
- **Probable hypothesis:** a causal explanation backed by repeated measurements and stated conditions, not proof.
- **Private or inaccessible:** another person's account relationship, proprietary ranking signals, moderation logic, unpublished enforcement, server-side state unavailable to the assistant.
- **Unidentifiable:** multiple causes produce exactly the same symptom; no available observation can disambiguate them.

Write what cannot be concluded, and reject fake "profile viewer", "shadowban detector", scam-recovery or algorithm-certainty instructions. Where the service provides official account status or appeal controls, describe only the verified route. A confident diagnosis from engagement numbers alone is not a pass.

### R: Recoverability and custody of data

**Examples:** WhatsApp restore without overwriting new conversations; TikTok drafts after reinstall; Chrome crashed tab restoration; Google Maps device-stored Timeline; Google Photos Locked Folder and cloud deletion; CapCut unsynced projects; Drive file history; Gmail deleted items.

For each data class, document an **inventory of copies and custody**: app-local database/cache, visible device media, cloud account, export, third-party device, backup (encrypted/unencrypted), trash and retention rules. Specify:
- Which versions/data are in each copy and how the user can inspect them **before** restoring or wiping.
- The preservation sequence, including read-only diagnostics and backups before reinstalling, clearing app data, resetting accounts, replacing devices, revoking credentials or recovering deletions.
- Whether a restore merges, replaces, duplicates or conflicts with newly created data; how to confirm restored content safely.
- Known retention limits, irreversible deletion, third-party support limits and potential costs.
- Difference between a missing item, unsynced item, locally cached item, removed cloud copy and permanently deleted item.

No agent should casually recommend reinstalling an app whose only remaining copies may live in its private local storage.

## Additional acceptance traps to include

| User request | A bad answer | What a passing answer requires |
| --- | --- | --- |
| Gmail "recall" | Claims delivery can always be reversed | Distinguishes verified Undo Send cancellation from post-delivery retrieval |
| Facebook "who blocked me" | Suggests a definitive detector | Explains which private states cannot be established |
| Google Messages RCS stuck verifying | Says "clear all messages" | Tests configuration, carrier/account/device and keeps history intact |
| Uber pending vs duplicate charge | Guarantees a chargeback or refund | Distinguishes authorization holds, captured charges and official dispute processes |
| Google Photos "delete cloud only" | Recommends Delete without copy analysis | Checks data topology and keeps local/cloud effects explicit |
| CapCut project disappeared | Recommends reinstall as first action | Attempts preservation of local-only drafts first |
| Google Drive "any Android folder automatically backed up" | Invents a built-in folder-watch setting | Separates native capabilities from another app/provider integration, scoped to version |
| Teams notifications | Assumes the app controls all delivery | Diagnoses tenant/account, service, Android permission/channels and device conditions |
| Netflix title missing | Blames a subscription without evidence | Explains eligibility/region/licensing and known vs unknown states |
| Booking.com "pay at property" | Claims payment cannot occur beforehand | Distinguishes confirmed booking terms, preauthorization, property charges and disputes |

## How this affects AYA-RAS

Treat **T/A/L/E/R as additional *lens tags*** to use where relevant, not five new mandatory top-level sections. The AYA-RAS metadata contract and 12-section export structure remain unchanged. Any high-value workflow tagged with one or more of these must have the matching evidence and branch logic in its existing task, diagnostic or limitation entry. The [extended authoring standard](AUTHORING_STANDARD.md), [advanced techniques](ADVANCED_AUTHORING.md) and [evaluation protocol](EVALUATION_PROTOCOL.md) spell out the release expectations.

For each new integrating app, select a representative group from **both** stress sets and add current *real help desk* questions, error strings and source-derived feature inventories. Test a model with the resulting guide in a fresh receiving chat. Score **truthfulness, safety, executable help and calibration** separately from whether an external account/bank/merchant actually granted the outcome. When a claim is remote-controlled and volatile, use current authoritative evidence or explicitly state what remains unknown.

**Important:** Neither of the two cross-category question banks is itself proof that a top Android app has a named feature or that the question is among its most frequently searched. They are prompts intended to reveal documentation and response failures.
