# Reference lifecycle and release operations

Treat an AYA guide like a compiled release asset. The user should not have to know the difference between the current app and last quarter's documentation.

## Ownership

Each application names one guide owner and backup, defines the shipping-guide file path, and sets a review cadence. The guide envelope records app version min/max, guide revision, source code revision and last verification UTC.

## Changes that must trigger review

Any user-visible screen or label change, setting/default/range change, new/removed feature, altered import/export format, permission change, new error state, provider protocol change, migration, altered privacy/data retention, newly confirmed limitation or fixed defect.

A UI PR should answer: "Which guide sections and acceptance questions does this change affect?" If none, record N/A with reason. PR reviewers must block new public features lacking guide updates.

## Release procedure

1. Identify exact binary build and source revision.
2. Update relevant task/feature/error IDs and cross-references; record status transitions (PLANNED → AVAILABLE only after acceptance).
3. Review all version and provider constraints; update explicit deprecations.
4. Update the **independently discovered inventory** (not just guide headings), confirm changes to public UI/permissions/flags/errors/providers, and run structural and cross-document traceability audits.
5. Update the **held-out gold question set** for affected state variants and execute regression cases plus high-risk smoke questions; independently review answers against the released app.
6. Approve privacy review and attach provenance of manually checked behavior.
7. Bundle guide with app binary; ensure host never selects future/incompatible version.
8. Store the guide revision/hash in the build manifest or release notes.
9. Preserve older version guides when shipping versions remain in use; do not overwrite history without a reproducible archive.

## Change impact ledger

For each PR note the changed screens, settings, task/error IDs, condition flags, data effects, provider dependencies and associated test cases. If behavior is unchanged, record that conclusion with evidence. A changed `source_revision` must be tied to a verified build; merely incrementing `last_verified_utc` does not constitute re-verification.

Review **unsupported**, **unknown** and **planned** capability entries whenever a release implements, removes or gates a feature. Preserve old identifiers; do not recycle an ID because the label changed.

## Drift audit

At least once per release, compare documented menu paths to UI resources, features to release flags, error strings to code, permissions to manifest, and URLs to maintained official endpoints. Mark unresolved discrepancies UNKNOWN. Escalate high-risk drift, especially destructive operations and authentication.

## Volatile upstream policy and entitlement claims

An APK release can remain unchanged while service-side subscription benefits, refund windows, account enforcement, provider rules, region availability, payment issuer requirements and workplace administration change. Track applicable statements at the **claim level**, recording authority, official source/document identifier, region/tier, verification date, risk, review trigger and a fallback when current confirmation is unavailable. Recheck high-risk payment, data-recovery and security assertions at a documented cadence **independent of app releases**. Expired/unverified assertions cannot be treated as confirmed merely because `app_version_min/max` still match the installed app. Where no reliable recheck channel exists, narrow the claim and instruct the agent to acknowledge uncertainty.

A real reported cancellation/booking dispute, notification pipeline failure, lost local-only draft, account recovery or unrecoverable cloud deletion should trigger a regression question with transaction stage, authority, OS/device conditions and data topology. See the [second cross-category challenge](CROSS_CATEGORY_BATCH2.md).

## Modular authoring

Authors may organize sources across Markdown files. Export a single deterministic, UTF-8, self-contained guide to the application assets. Resolve internal links or include their needed content. The receiving assistant may have no browser or file access.

## Feedback loop

Support questions that reveal a gap become a reference defect with issue ID, affected versions, corrected evidence and regression question. User-provided private data must be removed before recording examples. Never auto-upload conversations or secret-bearing logs.
