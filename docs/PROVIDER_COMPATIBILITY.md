# Recipient-app compatibility ledger

**All recipient behavior remains UNVERIFIED on devices.** AYA uses documented Android `ACTION_SEND` / `EXTRA_STREAM` and temporary content-URI grants. Whether ChatGPT, Claude or another receiver imports the attachment and creates a new conversation is controlled by that receiver.

| Target | Tested Android version | Tested target version | Attachment ingested | New conversation | Result |
| --- | --- | --- | --- | --- | --- |
| ChatGPT | Not tested | Not tested | Unknown | Unknown | UNVERIFIED |
| Claude | Not tested | Not tested | Unknown | Unknown | UNVERIFIED |
| Generic share targets | Not tested | Not tested | Unknown | N/A | UNVERIFIED |

## Manual test record template

Record UTC timestamp, device/Android version, target app package and release version, target signed-in/out, AYA guide revision/size, whether Sharesheet offers target, whether file appears, whether the target reads document contents, whether a chat is new, whether user must press Send, what error is shown, test result, screenshots redacted and tester identifier.

Test at minimum fresh install, target logged out, target logged in, long guide, app backgrounded, repeated shares and no compatible receiver.

Do not change a row from UNVERIFIED until the real recipient was exercised, and document what was observed rather than extrapolating across versions.
