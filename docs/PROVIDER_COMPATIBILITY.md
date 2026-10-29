# Recipient-app compatibility ledger

**All recipient behavior remains UNVERIFIED on devices.** Prior public reports of Gemini's TXT Sharesheet support are useful [research](ANDROID_SHARING_RESEARCH.md), not a substitute for tested AYA end-to-end ingestion. AYA uses documented Android `ACTION_SEND` / `EXTRA_STREAM` and temporary content-URI grants. Whether ChatGPT, Claude or another receiver imports the attachment and creates a new conversation is controlled by that receiver.

| Target | Tested Android version | Tested target version | Attachment ingested | New conversation | Result |
| --- | --- | --- | --- | --- | --- |
| ChatGPT | Not tested | Not tested | Unknown | Unknown | UNVERIFIED |
| Claude | Not tested | Not tested | Unknown | Unknown | UNVERIFIED |
| Gemini | Not tested | Not tested | Unknown | Unknown | UNVERIFIED |
| Generic share targets | Not tested | Not tested | Unknown | N/A | UNVERIFIED |

## Manual test record template
Creative Handoff adds a distinctRecord request-only and attached-guide delivery **separately** for every recipient; they can differ even on the same app release. Neither format is automatically assumed compatible.

Creative Handoff adds a distinct **image-generation** acceptance axis; text/attachment support alone is insufficient. For each tested target and Android version, separately record: AYA's final approved prompt displayed in the destination, actual image-generation response (versus merely writing a prompt), requested ratio honored or nearest supported, the user's ability to save to device, and whether a saved file can be manually imported using the sample host's Android picker. Include negative cases (unsupported model, signed-out state, file ignored, text-only share, limited formats). These are developer-controlled trials only; AYA must never instrument production user conversations or outcomes. Until such tests exist, ChatGPT, Claude, Gemini and Grok creative compatibility is **UNVERIFIED**.


Record UTC timestamp, device/Android version, target app package and release version, target signed-in/out, AYA guide revision/size, whether Sharesheet offers target, whether file appears, whether the target reads document contents, whether a chat is new, whether user must press Send, whether the separate `EXTRA_TEXT` question appears correctly, what error is shown, test result, screenshots redacted and tester identifier.

Test at minimum fresh install, target logged out, target logged in, long guide, app backgrounded, repeated shares and no compatible receiver.

Do not change a row from UNVERIFIED until the real recipient was exercised, and document what was observed rather than extrapolating across versions.
