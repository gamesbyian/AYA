# Security and privacy

## Trust boundary

Host app constructs text → AYA renders a reference package → user may **edit and approve** → AYA writes a unique UTF-8 cache file → Android grants a user-selected recipient temporary read access. AYA never performs network requests itself. The receiving app may upload/store the content under its own policies.

## Version identity and stale references

The preferred `Aya.launchBundled()` checks a packaged AYA-RAS guide against the **actual** app package and exact `versionName`, with required sections and metadata. It rejects a stale/cross-app guide before opening review. This validates only structure and identity, not the truth of the guide's claims. The legacy `Aya.launch(AyaRequest(...))` method permits advanced manually supplied text without this guard.

## Data minimization

No app settings, logs, screenshots, credentials, identifiers, tokens, URLs or personal information are automatically collected. The host developer is responsible for redacting all `AyaRequest` inputs before calling AYA. AYA has **no automatic redaction engine**. User edits can also contain sensitive details; review UI warns about downstream sharing.

Copy places the complete edited text on the Android clipboard, a separate disclosure surface. Treat clipboard as potentially accessible to other apps.

## Provider and cache

The non-exported FileProvider maps only `cacheDir/aya/`. URI grants are read-only. Filenames are unique, preventing overwrite between successive handoffs. AYA deletes only its own `aya-*.txt` cache files older than seven days when a later share occurs, avoiding premature removal during an active recipient read. Android may clear cache independently. No immediate post-share deletion guarantee exists.

## Threat model and unresolved risks

- **Host-supplied secrets:** guide authoring and host code must exclude sensitive data; v0 relies on user review.
- **Malicious content/prompt injection:** guide is reference material, never higher-priority assistant instructions. Receiving models are not guaranteed immune to attacks.
- **Recipient privacy:** AYA does not control selected destinations' retention, processing or policies.
- **Long content:** prototype enforces a 2 MiB UTF-8 share limit; recipient-specific limits remain unverified.
- **Accessibility/lifecycle:** preview keyboard, screen reader, rotation and process recreation require device testing.
- **No observation of outcomes:** AYA cannot tell whether a target ingested the document or created a new chat.

This is a prototype, not security-audited or certified for production use.
