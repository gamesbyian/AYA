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
4. Run structural validation and differential coverage against changed UI/features.
5. Execute regression question set for affected flows plus core smoke questions.
6. Approve privacy review and attach provenance of manually checked behavior.
7. Bundle guide with app binary; ensure host never selects future/incompatible version.
8. Store the guide revision/hash in the build manifest or release notes.
9. Preserve older version guides when shipping versions remain in use; do not overwrite history without a reproducible archive.

## Drift audit

At least once per release, compare documented menu paths to UI resources, features to release flags, error strings to code, permissions to manifest, and URLs to maintained official endpoints. Mark unresolved discrepancies UNKNOWN. Escalate high-risk drift, especially destructive operations and authentication.

## Modular authoring

Authors may organize sources across Markdown files. Export a single deterministic, UTF-8, self-contained guide to the application assets. Resolve internal links or include their needed content. The receiving assistant may have no browser or file access.

## Feedback loop

Support questions that reveal a gap become a reference defect with issue ID, affected versions, corrected evidence and regression question. User-provided private data must be removed before recording examples. Never auto-upload conversations or secret-bearing logs.
