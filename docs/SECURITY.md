# Security and privacy

## Trust boundary

Host app constructs text → AYA renders a reference package → user may **edit and approve** → AYA writes a unique UTF-8 cache file → Android grants a user-selected recipient temporary read access. AYA never performs network requests itself. The receiving app may upload/store the content under its own policies.

## Version identity and stale references

The preferred `Aya.launchBundled()` checks a packaged AYA-RAS guide against the **actual** app package and exact `versionName`, with required sections and metadata. It rejects a stale/cross-app guide before opening review. This validates only structure and identity, not the truth of the guide's claims. The legacy `Aya.launch(AyaRequest(...))` method permits advanced manually supplied text without this guard.

## Question-first disclosure and dual channel

AYA lets the user type a question locally (or edit a prefilled host suggestion). The question is merged into the reference, then shown in the full editable consent preview. On Share, the attachment contains the **current edited text**; Android may also pass the approved question as `EXTRA_TEXT` to the destination. `EXTRA_TEXT` is derived from that edited payload, not an old question, preventing accidental reinstatement of text removed by the user. These are two representations of the same approved data, not two independent disclosures.

A user choosing the recipient may still need to press Send inside the third-party application. Android grants only the required file URI read access; AYA cannot control recipient retention or any automatic imports.

## Data minimization

**Creative Handoff:** a typed `AyaCreativeTask` may include a media subject, intended cover role, image requirements and current manual import steps. These fields are supplied deliberately by the host, included in the editable preview, and treated as untrusted contextual data; they must never be populated by scraping private libraries, file paths, credentials or automatic diagnostics. `direction` is user authored. The full approved generation prompt is additionally sent as `EXTRA_TEXT`, so recipients that ignore attachments may still see it. Do not infer whether the recipient actually generates the image. **No reference images or binary user artwork leave the host through v1.** The user's later save/import happens outside AYA; there is no output callback, monitoring or post-handoff telemetry.


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
