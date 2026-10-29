# Receiver capability evidence and decision policy

**Status (October 29, 2026):** implemented read-only Kotlin evidence registry and tests; **no end-to-end provider-specific device QA** has been imported. Empty is the honest default. Do not advertise tested ChatGPT, Claude, Gemini, Grok or local-model support until documented.

## Why an evidence registry?

Android Sharesheet is not a feature-negotiation protocol. `ACTION_SEND` declarations determine which destinations might be offered, not whether a destination actually ingests `EXTRA_TEXT` or `EXTRA_STREAM`, opens a fresh chat, creates images or saves them. An inference app might use a cloud account, local models or both; none of those assumptions is established by the package name alone.

The registry supports *developer QA* and future user-visible compatibility guidance, while leaving selection with Android and the user. It must **never** be fed by runtime feedback, monitoring, background agent checks, accessibility scraping, automatic account inspection, or an opaque service.

## Kotlin API and guarantee

`AyaRecipientEvidence` stores one transport finding with:

- `packageName` and exact `appVersionName`
- Android SDK level and `AyaAccountState` (`SIGNED_IN`, `SIGNED_OUT` or `NOT_APPLICABLE`)
- `AyaTransport`: `TEXT_ONLY`, `TEXT_AND_TXT_REFERENCE`, `TXT_REFERENCE_ONLY`, `IMAGE_ATTACHMENT`, `MULTIPLE_ATTACHMENTS`, or `PROCESS_TEXT`
- `AyaCapabilityResult` (`SUPPORTED` / `UNSUPPORTED`)
- `AyaEvidenceLevel` (`DECLARED_INTENT_FILTER`, `PUBLISHED_DOCUMENTATION`, `DEVICE_QA`)
- `evidenceId` and mandatory UTC `testedDateUtc` for device QA

`registry.assess(packageName, appVersionName, androidSdk, accountState, transport)` returns `UNKNOWN`, `VERIFIED_SUPPORTED`, `VERIFIED_UNSUPPORTED` or `CONFLICTING`, plus exact QA evidence IDs. Only exact `DEVICE_QA` matches can produce verified support/unsupported; unknown account state always returns UNKNOWN. Conflicting observations must not be auto-resolved in favour of a provider.

### Limitations

This first model is a **developer-maintained research index**, not a runtime capability scanner. It does not know which recipient the user ultimately selects and does not change the Sharesheet or choose a share mode. `SUPPORTED` proves only that a controlled test found a specified *transport* working, not a particular generative task, account eligibility, future release behaviour, or response quality. There is no provider list embedded in code.

Even exact QA evidence can become stale due to server-side feature flags, geography, billing and model changes without a package update. Treat it as a narrow dated observation, not a guarantee. Include scenario details and screenshots (with secrets removed) in external QA records; a small registry entry isn't a replacement for that evidence.

## Evidence ladder and promotion gate

1. **Discovered:** Android intent resolver advertises candidate; mark `DECLARED_INTENT_FILTER`. Package visibility on Android 11+ can make enumerations incomplete. Never call `QUERY_ALL_PACKAGES` solely for AYA.
2. **Documented:** vendor or platform docs describe ability; mark `PUBLISHED_DOCUMENTATION`. Not evidence of AYA handoff ingestion.
3. **Verified:** controlled developer-run Android app version receives actual AYA text or file bytes. Record one exact transport, device/SDK, version, account state, time and reproduction steps.
4. **Separate outcome QA:** manually verify image-generation and file-saving capabilities in a controlled test, recorded in the compatibility ledger, *outside* production users. A text-share test by itself is insufficient.
5. **Regression:** recheck altered recipient releases, device versions and eligibility. The SDK never learns about the outcome after Share.

## User choice and fallback

AYA continues to present text-only/complete-guide modes and Android's system chooser. It must not hide a recipient because the registry has no evidence or because a published page is old. Copy/paste remains available. A future optional UX hint may cite exact QA evidence, but must say “tested under these conditions,” not “this app will definitely work.”

## Test examples

```kotlin
val registry = AyaRecipientCapabilityRegistry(emptyList())
val assessment = registry.assess(
    "org.example.assistant", "1.2.3", 35,
    AyaAccountState.SIGNED_IN,
    AyaTransport.TEXT_AND_TXT_REFERENCE
)
// UNKNOWN; the example package is fictional
```

The core JVM tests assert that intent filters and docs cannot establish support, QA matches must be exact, ambiguous account states do not match, and contradictory device trials stay CONFLICTING. [Provider ledger](PROVIDER_COMPATIBILITY.md) is the human-reviewed source of truth for field QA.
