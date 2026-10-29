# Android-to-assistant handoff research and decision record

**Creative handoff note (2026-10-29):** standard `ACTION_SEND` can carry AYA's generation request as `EXTRA_TEXT` and its guide as `EXTRA_STREAM`; a target may read only one of these. Android offers no generic intent meaning "start a new AI image-generation conversation and return generated artwork." Saving a generated image and importing it via the host's ordinary document/image picker are separate user-controlled actions. This is documented in [Creative Handoff](CREATIVE_HANDOFF.md) and must be verified per recipient on-device. Android's public [sharing guide](https://developer.android.com/develop/ui/compose/sharing/send) documents text/binary sharing and recommends its photo picker for selecting media; this is platform guidance, not a test of any specific assistant.

**Reviewed:** 2026-10-28. **Scope:** Android applications sharing user questions and versioned reference documents with ChatGPT, Claude, Gemini or another app. Research establishes platform contracts and published examples; it does **not** replace tests on installed receiver versions.

## Established Android mechanisms

1. **Android Sharesheet**: `Intent.ACTION_SEND` plus `Intent.createChooser()`, as recommended by [Android Developers: Send data to other apps](https://developer.android.com/develop/ui/compose/sharing/send). The platform selects target apps based on MIME type and installed receivers. Don't rebuild Sharesheet or rely on private intents.
2. **Text content**: `Intent.EXTRA_TEXT` with MIME `text/plain`. This supports receivers interested in text-only sharing.
3. **File attachment**: `Intent.EXTRA_STREAM` containing a `content://` URI, permission via `FLAG_GRANT_READ_URI_PERMISSION` and `ClipData`. Use a narrow non-exported [FileProvider](https://developer.android.com/training/secure-file-sharing), not a raw file path, `file://`, world-readable file or public storage.
4. **Combined text and attachment**: Android's receiver guidance explicitly shows reading both `EXTRA_STREAM` and `EXTRA_TEXT` from a single incoming share. [Android Developers: Receive data from other apps](https://developer.android.com/develop/ui/compose/sharing/receive). This is a *permitted data shape*, not a guarantee that any particular third-party receiver consumes both fields.
5. **MIME type matters**: Use `text/plain` for the self-contained UTF-8 `.txt` attachment. Don't indiscriminately switch to `*/*` or make multiple mixed-type attachments; the list of offered targets and receiving behavior may change.
6. **Conversation creation is recipient-controlled**: A sender cannot require an unrelated app to open a *new* conversation, prepopulate a specific field, attach successfully, or automatically Send unless the recipient documents such an integration. The Android chooser returning is not evidence of successful ingestion.

## Provider evidence (do not overclaim)

| Recipient | Publicly corroborated capability | Not established by current evidence |
| --- | --- | --- |
| Gemini Android | Android share-target import of TXT/docs and other files was reported in version 1.0.686588308; later multi-image/video share improvements reported in 1.0.869192867. Sources: [Android Authority file sharing](https://www.androidauthority.com/google-gemini-android-share-sheet-3502006/), [media sharing update](https://www.androidauthority.com/gemini-image-video-import-3645222/). | Guarantee of simultaneously ingesting `EXTRA_TEXT` and `EXTRA_STREAM`, present-day file limits or automatic new-chat creation. |
| Claude Android | Anthropic documents chat file uploads and Android system-app/intent integrations. Sources: [Upload files to Claude](https://support.claude.com/en/articles/8241126-upload-files-to-claude), [Use Claude with Android apps](https://support.claude.com/en/articles/11869629-use-claude-with-android-apps). | Those docs do **not** guarantee an inbound Sharesheet TXT+question handoff or new conversation; outbound Claude-to-other-app actions are a different direction. |
| ChatGPT Android | OpenAI documents Android app file/attachment support and mobile composer updates: [ChatGPT release notes](https://help.openai.com/en/articles/6825453-chatgpt-release-notes). | A documented incoming `ACTION_SEND` contract for TXT + prompt that guarantees document ingestion, a new conversation or automatic Send. |
| Generic Android receiver | Standard intent contracts allow receiving both `EXTRA_TEXT` and `EXTRA_STREAM`; correct behavior is up to each implementation. | No universal receiver behavior, supported file size, account eligibility, or prompt propagation. |

**Evidence levels:** platform-supported is not provider-tested; historical third-party coverage is not current compatibility. Provider app versions and account states must be recorded in [PROVIDER_COMPATIBILITY.md](PROVIDER_COMPATIBILITY.md). Do not claim success from a Sharesheet icon alone.

## AYA's baseline strategy

**One self-contained text document + one short message text.**

- The **attachment** contains the user's final edited question and all relevant app/version information, guidance and reference text. It remains usable when the receiver discards `EXTRA_TEXT`.
- `EXTRA_TEXT` contains the question extracted from the **final approved preview** so an app that handles both can put it in the composer, and an app that ignores the file still sees the question. A deleted/modified original question must not leak through a stale extra.
- A very long question stays **in full** within the attachment; the separate message text explains that the full question is attached. Do not put megabytes of guide text into the binder extra.
- `EXTRA_STREAM` and `ClipData` point to the same narrow read-granted content URI; Android's system UI chooses the destination.
- If a recipient ignores shared files, users can manually Copy the full help document and paste it into their preferred assistant. Never describe that clipboard action as private or automatic ingestion.

## Future option hierarchy, driven by measured compatibility

1. **Combined text and TXT file** (AYA default): good for targets that honor both, safely self-contained for file-only targets.
2. **TXT attachment only**: A/B test if receivers reject mixed extras. No assumed improvement.
3. **Text-only sharing**: optional explicit fallback for applications that cannot ingest files. Must respect Android IPC limits; avoid silently truncating the guide. Manual Copy remains the default unambiguous fallback.
4. **Alternative formats** (PDF, Markdown, content provider virtual documents): add only when app-version-specific evidence shows a real gain, and weigh larger size/accessibility against compatibility.
5. **Recipient-specific documented APIs/intents**: only after independent verification and maintenance ownership. Do not reverse-engineer hardcoded internal deep links as if they were stable contracts.
6. **Android App Functions or platform agent protocols**: separate investigation for assistants that might *act on* an app. AYA's present mission is informed help, not delegated device control.

## Reproducible acceptance matrix

For each target, Android OS version, app version and signed-in state, run with a **non-private** sample question and guide:

| Variant | Attachment | Text | Verify |
| --- | --- | --- | --- |
| A: combined | TXT URI | exact user question | Target shown; receiver opens; attachment exists; content is parsed; new/old chat; Send required |
| B: file only | TXT URI | none | Same observations; compare whether `EXTRA_TEXT` caused rejection or duplication |
| C: question only | none | exact user question | Does text enter composer, new/old chat, Send required? Note missing reference |
| D: manual paste | manually pasted full package | same | Confirm fallback is understandable and complete |

Additional tests: missing target, old recipient version, logged-out recipient, no network, large reference, emoji/multiline question, quoted text, repeated shares, two devices, TalkBack and keyboard focus, canceled share, permission denial, and prompt that was edited/removed in privacy review.

For every test, record **the actual visible composer content and whether the agent can quote facts from the reference**. Do not use undocumented proprietary automation or send real user data through test harnesses.

## Known architectural limits

A smart Android intent cannot force another company's app to accept an attachment. Intent priority, activity selection, share previews, size constraints and target apps can change. AYA must support graceful fallback and offer the user a chance to inspect all text before it leaves the host.
