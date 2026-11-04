# Native iOS Share Sheet receiver QA: separate-app acceptance contract

**Status: real first-party synthetic foreign-receiver acceptance verified, 2026-11-04.** [PR #132](https://github.com/gamesbyian/AYA/pull/132) built the separate .app/.appex with constrained activation; [PR #133 / run 41781406186](https://github.com/gamesbyian/AYA/actions/runs/41781406186) then installed it alongside the AYA host, selected it through the actual iOS Share Sheet and verified both text and .txt delivered **identical approved bytes** by independently checked length and SHA-256. This is synthetic QA receiver ingestion only, not real AI app compatibility, physical-device accessibility, or return/import. This is a first-party, disposable *test fixture* for a generic AYA transport, not a runtime component, provider-specific bridge, or claimed assistant compatibility. It follows [Apple transport architecture](ARCHITECTURE.md), [Apple prior art](RESEARCH.md) and [release evidence levels](../components/RELEASE-EVIDENCE.md).

## What this test must establish

The host's `UIActivityViewController` can offer the **final edited, user-approved text** as (a) a plain string and (b) a single UTF-8 `.txt` file, and a *different installed application* can actually access the complete bytes that the operating system delivered. These are separate acceptance cases. Opening the Share Sheet, seeing a recipient icon, triggering an activity completion callback, or reading a temporary file from the original host process is insufficient.

A real assistant may not advertise the same UTTypes, may only accept one representation, or may ignore a document after receiving it. The synthetic receiver must never be recorded as ChatGPT/Claude/Gemini ingestion.

## Fixture architecture

1. Add a small **separate first-party QA application** with a Share Extension, independently installed in the iOS Simulator. Build it from a pinned XcodeGen or native Xcode project, not from AYA's shipped Swift Package runtime. Its distinct bundle identifier, target identity and embedded `.appex` must be verified from the final `.app`.
2. Use a narrow `NSExtensionActivationRule` declaring text and one file only. Do not ship `TRUEPREDICATE`; Apple's extension guidance reserves it for initial debugging, and indiscriminate activation would misrepresent compatibility. Document strict matching and activation dictionary version so text and file can be independently tested.
3. The extension inspects `NSExtensionItem.attachments` using `NSItemProvider.hasItemConformingToTypeIdentifier`. For a plain string, load a suitable text representation. For the file, use `loadFileRepresentation(forTypeIdentifier:completionHandler:)` or an appropriate typed equivalent, then **consume and hash the complete bytes inside its completion callback**. Apple may delete the temporary file when the callback returns. Do not save private document text or assume another app's file URL is permanently readable.
4. Calculate SHA-256 and byte count on the **received** bytes, and display a small test-only receipt in the extension's visible UI: transport/type, byte count, digest and success/error state. Never display or publish the document body. A reviewer/test can compare that receipt with a separately computed expected hash of the approved fixture.
5. Avoid App Groups, cloud storage, inbox directories and custom backend services unless proven necessary. Prefer an on-screen receipt that an XCUITest can observe in the foreign extension's own accessibility hierarchy. If XCUITest cannot access that receipt, investigate the actual system boundary rather than manufacturing a simulated receipt in the sending app.

## System acceptance scenarios

| Scenario | Required observation | Failure signal |
| --- | --- | --- |
| Plain-text Share | Review/edit AYA text; explicit **Share as text**; select the foreign QA extension; compare complete UTF-8 byte count and SHA-256 against the **last approved** string | App not offered, type wrong, truncated/stale text, absent receipt, digest mismatch |
| Full `.txt` Share | Distinct **Share full .txt file** action; receiver loads actual file representation and hashes its bytes | Only a filename/URL received, no read access, stale cache item, missing bytes, mismatch |
| Cancel before Share | Cancel review without invoking Share | Any foreign receiver invocation, clipboard change or side effect |
| Edit/remove content | Delete/replace an old question before consent; only final edited text passes | Old question reappears through a parallel text field, file item or implicit request reconstruction |
| Unavailable receiver | Destination not offered or cannot accept one transport | Honest fallback, no false green or inferred assistant support |
| Repeated sharing | Use different edits and repeat; receiver sees the corresponding distinct approved bytes each time | Cached first document, overwritten shared temp, stale text after navigation |
| iPad presentation | Explicitly verify Share Sheet appears anchored and is usable under rotation/multitasking; no clipped actions | Crash, wrong popover anchor or unreadable sheet |

For native acceptance, use the **same compiled first-party host** and source-derived guide verified by the earlier iOS `.app` packaging gate. Do not print the reviewed payload into CI logs, screenshot attachments or test reports; synthetic fixtures may be committed, but the test channel should emit only receipt metadata and deterministic error classifications.

## CI, cost and evidence policy

Reuse the existing path-scoped Apple macOS workflow and installed iOS Simulator, preferably with one small independent fixture app built once and reused across the text/file cases. Do not spawn a separate macOS matrix for every representation. Keep a bounded capture of the first failed fixture step and record exact Xcode, simulator, app and extension versions, AYA revision, approved packet digest, receiver-observed digest, type and result.

Require **real extension code to execute and report an independently computed digest** before declaring a pass. A visual share sheet alone can qualify only presentation; an activity completion callback cannot establish the receiving application's post-share behavior. An XCUITest that cannot locate the extension, or receives no output, must fail, not quietly skip.

**Out of scope:** production share extensions, automatic return from an assistant, hidden provider discovery, filesystem scanning, real-agent test accounts, physical-device VoiceOver evidence, new permissions or network services.

## Primary API and prior-art references

- Apple [NSItemProvider](https://developer.apple.com/documentation/foundation/nsitemprovider): recipient-specific typed representations, asynchronous loading from extension attachments.
- Apple [loadFileRepresentation](https://developer.apple.com/documentation/foundation/nsitemprovider/loadfilerepresentation%28fortypeidentifier%3Acompletionhandler%3A%29): temporary file is removed after the completion handler returns.
- Apple [Share extension programming guide](https://developer.apple.com/library/archive/documentation/General/Conceptual/ExtensibilityPG/Share.html) and [extension activation keys](https://developer.apple.com/library/archive/documentation/General/Reference/InfoPlistKeyReference/Articles/AppExtensionKeys.html): declared data types, activation policy and extension lifecycle.
- Apple [UIActivityViewController completion handler](https://developer.apple.com/documentation/uikit/uiactivityviewcontroller/completionwithitemshandler-swift.property): only local activity completion, not model ingestion.

**Work order:** finish the distinct first-party iPad/large-type UI acceptance first, implement this receiver in one scoped PR with exact-byte tests, then begin independently authored host integration and saved-file return through Files.
