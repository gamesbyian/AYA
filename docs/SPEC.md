# AYA product/engineering specification (draft 1)

## Goal and operating principle

AYA is a reusable Android **bring-your-own-AI help and creative handoff**. An app provides version-matched, operationally rich documentation and optionally a user question/screen context. AYA previews the exact package and lets the user share it through the Android Sharesheet with a compatible assistant, without running or paying for an AI model.

## Key product component: trustworthy references

**The quality of the app guide determines the help quality.** Every integration must follow [AYA Reference Authoring Standard](reference/AUTHORING_STANDARD.md), with full feature inventory, exact UI paths, task recipes, state and provider variations, troubleshooting, source evidence, unsupported functionality, privacy and upgrade guidance. Guides must match the installed app version. Maintain a quality rubric and held-out question trials. The full static reference is embedded in one plain-text package, not fetched by the recipient.

## Prototype API

**Creative Handoff v1:** `Aya.launchCreativeBundled(activity, task, guideAsset?, screenName?, direction?, askDirection=true)` uses the **same installed-version guard**, editable consent and one-way Android sharing flow. A typed `AyaCreativeTask` carries subject, intended artwork role, manual import instructions, and an `AyaImageRequirements` object with a positive aspect ratio, optional consistent preferred pixel dimensions, accepted PNG/JPEG/WEBP MIME types, optional transparency and safe-margin rules. The host must verify the truth of these constraints. An optional user direction is entered in AYA or in the host, then previewed. AYA requests **actual image generation**, not merely advice, and uses a self-contained final-review-derived request as Android `EXTRA_TEXT` as well as the complete reference in its UTF-8 attachment. The person saves the output in the chosen AI app and imports it through the existing host picker. See [normative creative specification and plan](CREATIVE_HANDOFF.md).


**Preferred host API:** `Aya.launchBundled(activity, guideAsset?, screenName?, question?, askQuestion=true)` loads an APK asset, verifies its app ID and exact installed `versionName`, and refuses stale or malformed references before opening review. `AyaBundledLaunchResult.QuestionOpened` means the question editor is on screen; `PreviewOpened` means the complete review dialog is on screen. Neither is an external handoff result. `Rejected(reason)` requires truthful host error handling. The legacy `Aya.launch(activity, AyaRequest(...))` remains for advanced/manual unverified input. Source-only import and staging Maven AAR/POM consumption are both tested by CI.

No data is collected by AYA itself. Android library includes a non-exported FileProvider limited to `cacheDir/aya/`. AYA creates a unique text file with the edited payload and sends it using `ACTION_SEND`, `EXTRA_STREAM`, `ClipData`, and `FLAG_GRANT_READ_URI_PERMISSION`.

## User experience

1. Tap "Ask your agent" within a host app.
2. AYA asks "What do you need help with?" in a multiline input, optionally prefilled by the host. If the host already has its own question field, `askQuestion=false` skips this extra screen.
3. User selects Review details and inspects or edits the entire shared document.
4. User can Cancel, Copy to clipboard, or Share using Android Sharesheet.
5. AYA sends an attachment containing the complete question and reference, plus the **final edited** question as `EXTRA_TEXT`. Each receiving app decides which fields it consumes and whether to start a new chat.
6. If recipient does not ingest the file, paste copied text manually.

See [question-first UX](QUESTION_COMPOSER.md) and [Android-to-agent prior art](ANDROID_SHARING_RESEARCH.md).

No guarantee of new-chat creation, auto-send, or assistant adherence. Destination processing is outside AYA's control. Sharing limit: 2 MiB in the prototype. Old unique cache files pruned on a later share after seven days.

## Strict handoff boundary

AYA's job ends when the user invokes Share or Copy and control passes to the selected destination or clipboard. Android and the receiving assistant own everything afterward. AYA does not request a return channel, receive agent replies, monitor conversations, solicit success ratings, collect outcomes, track resolution, or trigger follow-up reminders. No callback, analytics event, or background job may be added to observe what an agent says or what a user does with its advice.

Quality evaluation of reference material belongs exclusively to **separate developer/QA fixtures or explicitly run testing**, not to runtime monitoring of real AYA users or their conversations. Developer testing may measure documentation usefulness in controlled samples; it must never be phrased as a requirement to observe production outcomes.

## Non-goals

In Creative Handoff specifically: in-AYA image creation, reading AI output, automatic image return, automatically replacing host artwork, fetching private current artwork, assuming a model supports image generation, or silently adding images to the outgoing attachment.


Bundled chatbot, vendor lock-in, inference billing, automatically reading installed accounts, reading assistant responses, screen scraping, silently exporting diagnostics, editing the recipient conversation, unofficial deep links or pretending assistant can operate the host app.

## Acceptance gates and roadmap

**Prototype:** library, documentation/authoring standard, validator, real sample host, exact-version guide guard, module and staged AAR consumer tests, Android URI instrumentation tests (execution separately tracked).
**Beta:** physical-device and instrumentation verification, accessible preview acceptance, host version-guard, redaction controls, explicit diagnostic opt-in, recipient compatibility ledger.
**Stable:** real integrating app's released guide plus QA rubric, compatibility contract, maintenance ownership, artifact publication, security and accessibility review.

Evidence belongs in [test plan](TEST_PLAN.md) and [compatibility ledger](PROVIDER_COMPATIBILITY.md).
