# Security and privacy

Host app constructs data → AYA renders text → user reviews → AYA writes cache file → Android temporarily grants a selected destination read access. AYA never sends data to a server itself; chosen assistants may upload/store it under their own policies.

No settings, logs, screenshots, secrets, URLs or personal identifiers are automatically collected. The host app is responsible for redacting all input supplied to AYA. AYA's FileProvider is non-exported and maps only to `cacheDir/aya/`. Files have unique names but currently lack scheduled cleanup.

**Before production:** make preview scrollable and editable; carefully design file expiration without racing share recipients; test temporary URI grants; redact host context; audit clipboard copy and accessibility. This prototype is not security-audited.
