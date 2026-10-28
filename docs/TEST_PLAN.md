# AYA verification and release gates

## Static and reference checks

- `python3 tools/validate_guide.py --strict docs/reference/EXAMPLE_PARCELPAD.md`
- `python3 -m unittest discover -s tools -p 'test_*.py'`
- For every integrating app, run validator and independent [AYA-RAS review](reference/AUTHORING_STANDARD.md); score against [QA rubric](reference/QA_RUBRIC.md) and [question bank](reference/QUESTION_BANK.md).
- Structural checks are necessary but cannot prove that an app guide matches shipping behavior.

## Android CI

Run `gradle :aya:testDebugUnitTest :aya:assembleDebug :sample:assembleDebug` with JDK 17, Gradle 8.9 and Android SDK 35. Preserve the debug sample APK artifact for tester installation.

## Android instrumentation and manual work remaining

- FileProvider URI is readable with grant, not without; grants never cover directories outside `cacheDir/aya`.
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
