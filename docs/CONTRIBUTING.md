# Contributing to AYA

AYA is an experimental Android library. Start with [specification](SPEC.md), [security model](SECURITY.md), and [integration guide](INTEGRATION.md).

**The reference documents are product behavior.** Any PR modifying public behavior must assess impact on [AYA-RAS](reference/AUTHORING_STANDARD.md), update affected guide sections or document N/A, and add regression questions. Do not describe work in plans or unfinished PRs as released.

Engineering rules:

- Preserve Android Sharesheet as provider-neutral baseline; no undocumented app-specific deep links.
- Require explicit preview and approval before sharing; do not gather private diagnostics silently.
- Never include passwords, BitTorrent passkeys, tokens, private endpoint URLs, or production support logs in test fixtures.
- Never assert ChatGPT/Claude ingestion or new-chat creation without reproducible version-stamped observations.
- Write tests for output formatting, privacy behavior, file grants and compatibility changes.
- Do not merge failing CI or claim unsupported behaviors are accepted.

Recommended next tasks: Android device acceptance, instrumented URI-grant tests, screen-reader and preview-state tests, packaging a real application guide, and provider compatibility trials. The current sample's ParcelPad is intentionally fictional.
