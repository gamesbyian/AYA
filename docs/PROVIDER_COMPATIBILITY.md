# Recipient-app compatibility ledger

**All recipient behavior remains UNVERIFIED on devices.** The local capability registry therefore has no verified real-provider entries. Prior public reports of Gemini's TXT Sharesheet support are useful [research](ANDROID_SHARING_RESEARCH.md), not a substitute for tested AYA end-to-end ingestion. AYA uses documented Android `ACTION_SEND` / `EXTRA_STREAM` and temporary content-URI grants. Whether ChatGPT, Claude or another receiver imports the attachment and creates a new conversation is controlled by that receiver.

| Target | Tested Android version | Tested target version | Attachment ingested | New conversation | Result |
| --- | --- | --- | --- | --- | --- |
| ChatGPT | Not tested | Not tested | Unknown | Unknown | UNVERIFIED |
| Claude | Not tested | Not tested | Unknown | Unknown | UNVERIFIED |
| Gemini | Not tested | Not tested | Unknown | Unknown | UNVERIFIED |
| Generic share targets | Not tested | Not tested | Unknown | N/A | UNVERIFIED |

## Published image generation capabilities (research, not AYA compatibility tests)

Snapshot as of **2026-10-29**. These sources establish *some product capability* but do **not** establish that a given Android app version accepts `ACTION_SEND`, consumes an AYA request, opens a new conversation, generates from that entry point, or saves a compatible file.

| Assistant | Official documented image creation | Relevance / limitation |
| --- | --- | --- |
| ChatGPT | [Images in ChatGPT](https://help.openai.com/en/articles/11084440-images-in-chatgpt) describes generating, editing and saving images on mobile | Image generation is documented; **AYA outbound handoff unverified** |
| Gemini | [Gemini Apps image generation](https://support.google.com/gemini/answer/14286560?co=GENIE.Platform%3DAndroid&hl=en) documents generating images and saving them from Android | Feature/age/region/account restrictions may apply; **AYA outbound handoff unverified** |
| Grok | [xAI Imagine Image 2.0 announcement](https://x.ai/news/grok-imagine-image-2) describes image generation on Android and iOS | Feature support in Grok does not prove sharesheet integration; **AYA outbound handoff unverified** |
| Claude | [Can Claude produce images?](https://support.claude.com/en/articles/9002504-can-claude-produce-images) says Claude does **not** generate photos or illustrations the way image-generation tools do | Claude may produce SVG/HTML diagrams, charts, designs or artifacts, but these are not equivalent to raster key-art generation. **Do not claim direct photographic/illustrative key-art capability** |

**Compatibility policy:** Never block or force a recipient based on an AYA hardcoded provider list. People may have other models or tools available within those apps, and capabilities evolve. Only describe observed, dated compatibility in the tested matrix. If the chosen assistant cannot generate the requested image, it should say so, and the user can choose another target or manually use a generation tool. No AYA runtime monitoring, auto-switching or provider-account introspection.

Record request-only and attached-guide delivery **separately** for every recipient; they can differ even on the same app release. Neither format is automatically assumed compatible.

Creative Handoff adds a distinct **image-generation** acceptance axis; text/attachment support alone is insufficient. For each tested target and Android version, separately record: AYA's final approved prompt displayed in the destination, actual image-generation response (versus merely writing a prompt), requested ratio honored or nearest supported, the user's ability to save to device, and whether a saved file can be manually imported using the sample host's Android picker. Include negative cases (unsupported model, signed-out state, file ignored, text-only share, limited formats). These are developer-controlled trials only; AYA must never instrument production user conversations or outcomes. Until such tests exist, ChatGPT, Claude, Gemini and Grok creative compatibility is **UNVERIFIED**.


Record UTC timestamp, device/Android version, target app package and release version, target signed-in/out, AYA guide revision/size, whether Sharesheet offers target, whether file appears, whether the target reads document contents, whether a chat is new, whether user must press Send, whether the separate `EXTRA_TEXT` question appears correctly, what error is shown, test result, screenshots redacted and tester identifier.

Test at minimum fresh install, target logged out, target logged in, long guide, app backgrounded, repeated shares and no compatible receiver.

Do not change a row from UNVERIFIED until the real recipient was exercised, and document what was observed rather than extrapolating across versions.

## Machine-readable developer QA evidence contract

The SDK includes `AyaRecipientEvidence` and `AyaRecipientCapabilityRegistry`. The initial registry has **no verified providers**. A support claim is `VERIFIED_SUPPORTED` only if it comes from `DEVICE_QA` evidence for the **exact receiver package name, installed app version name, Android API level, recipient account state, and transport**. `DECLARED_INTENT_FILTER` and `PUBLISHED_DOCUMENTATION` records are helpful context but remain `UNKNOWN` for successful ingestion. Contradictory QA reports produce `CONFLICTING`, not automatic selection. An unknown signed-in state matches nothing. See [complete model](RECIPIENT_CAPABILITIES.md). No production user analytics populate this registry.

## Manual test record template

Record a reproducible QA fixture ID, UTC date, exact package name and `versionName`, Android API level, whether signed in/out or no account needed, and **one exact transport mode**, plus the assistant's observed behavior. Note whether text was received, attachment bytes were accessible, the user had to press Send, and image generation and saving were independently verified. Retest on each update rather than transferring a claim to newer app versions.
