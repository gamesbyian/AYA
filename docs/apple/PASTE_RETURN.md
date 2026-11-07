# User-mediated text return on iOS

The reusable `AYAImportPasteButton` is a text-only escape route for an agent-produced artifact when the user has raw text but cannot select a saved file through iOS Files. It complements `AYAImportPickerButton` and the native Files import acceptance in #147; it does not substitute for a passing OS File Provider callback.

## SDK contract

`AYAImportPasteButton(title:maximumBytes:onSelected:)` is available on iOS 16+. The user explicitly opens an ordinary text editor, uses iOS's own paste/edit controls, and taps **Review pasted output**. The control never reads the clipboard API, scans storage, performs a background import or writes pasted content to disk. Cancel and host disappearance discard any pending snapshot without invoking the callback.

An empty submission, invalid limit or input over the configured UTF-8 byte cap remains in the editor with visible error feedback. The default cap is 4 MiB, and callers cannot request a cap over 16 MiB. On Review, the component copies immutable bytes into an `AYAImportFile` and calculates a SHA-256 content fingerprint. It invokes `onSelected` only after dismissing its editor, allowing the host to present independent semantic review. The display name is an untrusted hint; no file provenance or model identity is claimed.

**Host obligation:** recognize and validate bytes with `AYAImportRegistry` or equivalent host-owned logic; resolve ambiguous/wrong-card matches; show an impact preview; require a separate, explicit Apply confirmation. The AYA component has no permission to mutate host state or execute content. All format-specific schemas must remain in the adopting host, never in the SDK.

The fictional Lantern sample exposes a **Paste JSON output** control below the handoff card and sends returned text through the very same `inspectSelectedFile` path used by its Files importer. Malformed or unsupported JSON cannot reach Apply. No automatic clipboard monitoring or assumption of compatibility with arbitrary assistant-app formats.

## Qualification

`AYAAppleHostPasteImportUITests` runs against the installed native host: human-style text entry to Review, Cancel before Review, valid preview then Cancel, valid preview then Apply, and invalid bytes rejected without Apply. A passing run proves the text route only. It must not count toward #147's real Files-provider selection gate, third-party app capability, cloud files, physical-device accessibility or actual AI-app ingestion.

Keep the genuine, foreign-app Files tests strict even when this fallback works. For actual iPhone/iPad Files comparisons, use [PHYSICAL_FILES_QA.md](PHYSICAL_FILES_QA.md).