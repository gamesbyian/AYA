# Contributing to AYA

AYA is an experimental Android library. Start with the [specification](SPEC.md), [security model](SECURITY.md), and [test plan](TEST_PLAN.md).

## Engineering rules

- Preserve Android Sharesheet as the baseline. Never invent vendor deep-link contracts.
- Require informed user approval before sharing context.
- Keep context explicit, narrow and version-aware.
- Don't include personal information, secrets, torrent passkeys, network credentials, or private endpoint details in fixtures.
- Never claim a provider accepts attachments or creates conversations without dated, reproducible device evidence.
- Add tests for new serialization and privacy behavior.
- Keep the distinction between shipping features and proposed features explicit.

## Suggested implementation sequence

1. Confirm Gradle/Android build and fix integration errors.
2. Replace the long AlertDialog message with a full-screen accessible, editable preview that displays exactly what will be shared.
3. Add a demo host Activity and basic test guide.
4. Add filesystem retention cleanup that cannot invalidate live shares.
5. Run recipient validation and publish a compatibility matrix.
6. Offer optional contextual diagnostics with individual privacy toggles and explicit redaction.
