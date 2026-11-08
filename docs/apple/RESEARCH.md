# Apple platform prior art and engineering research (2026-11-03)

**Status:** verified API/documentation research, **not** empirical AI-recipient or device compatibility. Scope: iOS/iPadOS native host apps. AYA remains an optional, Unlicensed interaction convention, not an AI service. Platform-specific integration must not redefine or specialize the host-neutral modules in [Module Portability](../MODULE_PORTABILITY.md).

## Current Files-provider blocker research (2026-11-07)

See [evidence-based File Provider blocker review](FILES_PROVIDER_BLOCKER_RESEARCH_20261107.md) for the exact -1005 pre-callback failure boundary, the already-tried UIKit copy picker, published Apple guidance and independent incident precedents, the separate ShareLink recipient-representation differential, and the physical-device/Feedback Assistant decision path. The seven-file native picker gate [#147](https://github.com/gamesbyian/AYA/pull/147) remains red; this research is not itself acceptance evidence.

## Executive decision

Start with **reviewed handoff → system share / Copy fallback → manual import of a user-picked output**. Use an optional Swift Package; no runtime assistant API or automatic output watcher. App Intents and Shortcuts are separately gated enhancements rather than prerequisites. Align payload and identity semantics with the Android reference and portable packet authoring standards, while making native transport and importer details platform-specific. Do not assume that the iOS Share Sheet has identical behavior to Android's Intent chooser.

## Primary Apple APIs and prior art

| Need | Apple-supported option | Limits and implications |
| --- | --- | --- |
| Hand off complete reviewed text | SwiftUI `ShareLink` plus `Transferable`; UIKit `UIActivityViewController` / `NSItemProvider` / `UIActivityItemsConfiguration` | Share extensions advertise accepted types; a destination may accept text but not files, files but not text, or handle multiple items inconsistently. Offer **separate** text and .txt document modes and test each, not a presumed universal text+attachment delivery. |
| First-class native user review | Host-owned SwiftUI sheet / UIKit presented controller | Always display the exact content leaving the host, editable before Copy/Share. Selection of activity is not proof the AI read or used it. |
| Return generated file | SwiftUI `fileImporter` or `UIDocumentPickerViewController` with `UniformTypeIdentifiers` | Only user-selected files, never speculative scans of another app's storage. Use security-scoped access, coordinated reads and a bounded private byte snapshot. Host handles semantic validation, routing, dry-run and final confirmation. |
| Open the correct host screen | Universal Links with Associated Domains; optional explicit host document handling | Deep links do not grant filesystem permission, prove artifact provenance or authorize changes. Validate all parameters. Never auto-apply content merely because a link was opened. |
| Host capabilities in Shortcuts / Siri | App Intents, App Shortcuts, App Entities | These expose developer-declared actions and data to system experiences. They **do not** confer arbitrary access to every third-party LLM. Prefer read-only/prepare actions initially; destructive actions must require actual interactive host approval. |
| Share/input extension | Apple Share Extension (only if the host actually needs to RECEIVE shared content) | Not needed to **send** an AYA packet. Separate extension target, constrained lifecycle/UI; share common pure code rather than copy it. App Groups only if justified by a real interprocess data requirement. |
| First-party integration testing | SwiftPM unit tests; XCTest/XCUITest with iOS Simulator | Simulator cannot prove physical-device UI/accessibility or third-party provider ingestion. App Intents Testing exercises intent integration separately when added. |

## Published evidence and boundaries

- Apple: [Collaborating and sharing copies of your data](https://developer.apple.com/documentation/uikit/collaborating-and-sharing-copies-of-your-data) describes `UIActivityViewController`, item providers and activity item configuration.
- Apple: [SwiftUI ShareLink](https://developer.apple.com/documentation/swiftui/sharelink) specifically warns that some receiving apps advertise file types but not other types; `FileRepresentation` can make a destination appear. This is a **discovery**/representation fact, not proof that an assistant imported a guide.
- Apple: [Uniform Type Identifiers](https://developer.apple.com/documentation/uniformtypeidentifiers/) describes recognized, declared file types.
- Apple: [SwiftUI fileImporter](https://developer.apple.com/documentation/swiftui/view/fileimporter(isPresented:allowedContentTypes:onCompletion:)) requires a security-scoped resource start/stop for selected URLs. [UIDocumentPickerViewController](https://developer.apple.com/documentation/uikit/uidocumentpickerviewcontroller) calls for coordinated file access; [NSURL security-scoped access](https://developer.apple.com/documentation/foundation/nsurl) warns that unreleased scopes exhaust resources.
- Apple: [File system coordination](https://developer.apple.com/documentation/foundation/improving-performance-and-stability-when-accessing-the-file-system) explains why iCloud/File Provider reads must not block main-thread UI and why `NSFileCoordinator`/presenters matter.
- Apple: [Universal Links](https://developer.apple.com/documentation/xcode/supporting-universal-links-in-your-app) explicitly warns to validate parameters and avoid unsafe data-changing actions driven by links.
- Apple: [App Intents](https://developer.apple.com/documentation/appintents) and [Verifying your App Intents implementation](https://developer.apple.com/documentation/appintents/verifying-your-app-intents-implementation) distinguish unit integration, discovery in Shortcuts/Spotlight, and real usage. [App Intents Testing](https://developer.apple.com/documentation/appintentstesting) adds out-of-process integration tests.
- Apple: [Share extension guidance](https://developer.apple.com/library/archive/documentation/General/Conceptual/ExtensibilityPG/Share.html) and [Code structure for extensions](https://developer.apple.com/documentation/sirikit/structuring-your-code-to-support-app-extensions) argue against adding an extension merely to send content and for keeping extension back-end logic small/shared.
- Apple: [Sharing activity completion handler](https://developer.apple.com/documentation/uikit/uiactivityviewcontroller/completionwithitemshandler-swift.typealias) describes whether a system share activity was performed, **not** whether the recipient AI understood, retained or acted upon a document.
- Claude: [Use Claude App Intents and Shortcuts on iOS](https://support.claude.com/en/articles/10263469-use-claude-app-intents-shortcuts-and-widgets-on-ios) (published July 9, 2026) documents `Ask Claude` App Intent, Shortcuts and text shares on iOS 18+. This proves a provider-specific optional *possibility*, not AYA recipient compatibility for document files, text+file, new-chat creation, or every model/account.
- OpenAI: [Uploading files and audio to ChatGPT](https://help.openai.com/en/articles/8555545-uploading-files-and-audio-to-chatgpt) documents file attachments in supported mobile apps, **not** the ability to consume an AYA Share Sheet payload. Device-level AYA transport remains unverified.
- Apple: [Testing on simulated and physical devices](https://developer.apple.com/documentation/xcode/running-your-app-on-simulated-or-physical-devices) warns the simulator does not replicate every physical-device characteristic.
- GitHub: [Choosing runners](https://docs.github.com/en/actions/how-tos/write-workflows/choose-where-workflows-run/choose-the-runner-for-a-job) and [runner costs](https://docs.github.com/en/billing/reference/actions-runner-pricing). macOS compute is relatively expensive; qualify platform-neutral code on cheap runners and execute Xcode/simulator only on relevant changes, with measured gates.

## Architectural choices from the evidence

1. **No recipient allowlist or forced OpenAI/Claude link.** Apple's Share Sheet chooses from registered compatible receivers. Record real, dated per-provider and per-transport observations separately.
2. **Two explicit share representations, not a magic merged payload:** plain full-text Copy/Share, and a UTF-8 .txt file with the approved complete packet. On iOS, a separate file presentation may enable more destinations. Do not claim any receiver ingests both representations.
3. **No iOS directory guessing.** Sandboxed documents and File Providers require user selection. An observed previous destination or a share completion value never authorizes scanning its app container.
4. **The importer is host-owned and adversarial.** Snapshots are read with a bounded size, stable bytes, actual format recognition, ambiguous/wrong-card routing, semantic validation and an independent confirmation step. AYA must not execute recipes.
5. **No mandatory domain/server/account.** Universal Links require domain association and are optional; local picker remains the baseline. Avoid adding a backend to satisfy a handoff that works locally.
6. **No unnecessary Share Extension.** Start with native outgoing sharing and a host's existing file importer. Evaluate adding a Share Extension only after an actual inbound share use case demonstrates value.
7. **Strict evidence labels.** Swift source and Linux SwiftPM tests mean S0/S1 *core* only; macOS compile ≠ iOS UI build; iOS Simulator can validate local transitions, not physical-device behavior or recipient ingestion.

## Research questions requiring experiments

- On each supported iOS/iPadOS version, does each installed assistant appear as a receiver for **plain text**, **one UTF-8 file URL**, and (if ever attempted) **multiple items**? Record separate rows.
- On selecting the target, is the complete approved content visible? Is it imported as an attachment, quoted as text, truncated or ignored? Does the target open a compose view or require Send?
- Which specific provider/version/account states permit creating and saving a structured artifact or generated image? Can a host import it through Files without reaching inside the provider sandbox?
- Does an iPad popover have a stable visible anchor under rotation, multitasking and VoiceOver? Are text input/editing and the file picker usable at large Dynamic Type?
- Can a host's real File Provider/third-party iCloud documents be read with a single stable snapshot while remote sync, replacement or access revocation occurs?
- Are App Intents discoverable and correctly permissioned in Shortcuts across OS versions, including a negative test preventing import or destructive execution without consent?

All provider observations must record UTC date, iOS build, device, assistant name and version, signed-in state, consent/payload mode, visible result, evidence provenance and limits. **No production telemetry or outbound reply tracking.**
