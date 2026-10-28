# AYA verification and release gates

## Static and reference checks

- `python3 tools/validate_guide.py --strict docs/reference/EXAMPLE_PARCELPAD.md`
- `python3 tools/validate_guide.py --strict sample/src/main/assets/aya-guide.md`
- `python3 tools/audit_reference.py sample/src/main/assets/aya-guide.md --inventory docs/reference/examples/aya_sample_inventory.json --questions docs/reference/examples/aya_sample_questions.json --strict`
- `python3 -m unittest discover -s tools -p 'test_*.py'`
- For every integrating app, run validator and independent [AYA-RAS review](reference/AUTHORING_STANDARD.md); score against [QA rubric](reference/QA_RUBRIC.md) and [question bank](reference/QUESTION_BANK.md).
- Structural checks are necessary but cannot prove that an app guide matches shipping behavior.

## Android CI

Run `gradle :aya:testDebugUnitTest :aya:assembleDebug :aya:assembleDebugAndroidTest :sample:assembleDebug` with JDK 17, Gradle 8.9 and Android SDK 35. Next publish via `gradle :aya:publishReleasePublicationToStagingRepository` and build sample with `gradle :sample:assembleDebug -Paya.consumePublished=true`. CI preserves the sample APK and local Maven AAR/POM repository artifacts.

`AyaReferenceVerifierTest` exercises mismatched app IDs, old/new/ranged versions, duplicate metadata, missing sections and placeholders. `AyaShareIntentsTest` is a device/emulator instrumentation suite that tests UTF-8 bytes, scope, unique URIs and permissions; compiling tests **does not mean running them**.

## Android instrumentation and manual work remaining

- Run `gradle :aya:connectedDebugAndroidTest` on a configured emulator/device; verify the FileProvider URI reads with grant and **from an independent foreign package** cannot be read without grant. Existing tests cover local URI contents, flags, and scope; external-package denial remains a separate test case.
- Cancelling or editing the preview changes exactly what is copied/shared, including multiline and Unicode content.
- Empty content and over-2MiB content do not launch a share.
- Repeated shares create unique filenames; old cache cleanup never deletes active handoffs.
- Missing target, denied chooser, bad FileProvider setup, cache failures and Activity recreation fail gracefully.
- TalkBack, full-size font, keyboard focus, touch reachability, landscape and 320x700/412x892 screen snapshots.
- Confirm no unexpected internet permission, credential collection, analytics, or background network calls.

## Recipient matrix

Run Android 10, 13, 15, 16+ where devices are available, and current installed ChatGPT/Claude clients in logged-in/out states. Record tested versions and dates in [compatibility ledger](PROVIDER_COMPATIBILITY.md), including whether file was actually ingested, new chat creation, and required extra user action. Do not advertise provider behavior until verified.

## Stable release gate

Passing static/Gradle checks; tested sample APK; true reference coverage for at least one real app; security/privacy review; assistant answer evaluation and P0/P1-free behavior; physical-device provider matrix; accessibility acceptance.
