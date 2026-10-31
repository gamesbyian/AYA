# AYA verification and release gates

The [cross-module trial ledger](packet/EVALUATION.md) must bind results to the exact compiled packet, record actual attachment ingestion and independently checked host outcomes. The offline tool `tools/validate_packet_trials.py` rejects fabricated-incomplete *metadata* claims, but human proof is still necessary. Unit tests use explicitly synthetic fixtures only.

## Application Understanding and director consultation checks

Run `python3 tools/validate_understanding.py docs/understanding/examples/parcelpad-understanding.json --decisions docs/understanding/examples/parcelpad-decisions.json` and the associated unit tests. For real hosts independently confirm the conceptual model with relevant source/QA and, where necessary, a scoped director interview. Reject unknown references, unsupported approval claims, interpretation drift, and any confusion of intentions with implemented or observed states. No project director was consulted for the fictional fixture.

## Shared Packet Authoring checks

Run the [Packet compiler](packet/README.md) on the fictional four-profile fixture, then independently test against real host builds before release:

```sh
python3 tools/packet_compiler.py --source docs/packet/examples/parcelpad-facts.json \
  --inventory docs/packet/examples/parcelpad-inventory.json \
  --profiles docs/packet/examples/parcelpad-profiles.json \
  --profile help --as-of 2026-10-30T00:00:00Z \
  --output /tmp/aya-help-packet.md --report /tmp/aya-help-packet.json
python3 -m unittest discover -s tools -p 'test_*.py'
```

For each actual adopting app independently verify inventory coverage, live UI and effects, dependency closure, text-only essential constraints, precise import semantics, token/byte limits, actual assistant attachment ingestion and generated-output acceptance. Refuse stale upstream claims and unreviewed high-risk facts. No production response monitoring is allowed.

## Static and reference checks

- `python3 tools/validate_guide.py --strict docs/reference/EXAMPLE_PARCELPAD.md`
- `python3 tools/validate_guide.py --strict sample/src/main/assets/aya-guide.md`
- `python3 tools/audit_reference.py sample/src/main/assets/aya-guide.md --inventory docs/reference/examples/aya_sample_inventory.json --questions docs/reference/examples/aya_sample_questions.json --strict`
- `python3 -m unittest discover -s tools -p 'test_*.py'`
- For every integrating app, run validator and independent [AYA-RAS review](reference/AUTHORING_STANDARD.md); score against [QA rubric](reference/QA_RUBRIC.md) and [question bank](reference/QUESTION_BANK.md).
- Structural checks are necessary but cannot prove that an app guide matches shipping behavior.

## Optional Translation Kit checks

- Run `python3 tools/validate_translation_kit.py docs/translation/examples/parcelpad-translation-kit.md --schema docs/translation/examples/parcelpad-output.schema.json --example docs/translation/examples/parcelpad-pirate.pack.json` and `tools/test_validate_translation_kit.py` through Python discovery.
- Kotlin `AyaTranslationKitTest` checks version/app rejection, required sections, duplicate metadata, invalid task values, preserved meaning and final-review prompt edits. Verify these through Android unit-test CI; fixture consistency is not proof of a real host's importer.
- In an actual adopting host: verify kit content matches released string catalog, exact-version AYA-RAS guide, imported pack parser and user-visible manual import route. Test protected/destructive/permission/accessibility texts, invalid ICU placeholders/plurals, locale variants, RTL, size/UTF-8, unknown keys, incomplete overlays, fallback and rollback.
- Device tests: ordinary Language settings do not require an assistant; the AYA card remains secondary; Copy/Cancel/Share correctly distinguish approved text and the single attachment; the chosen recipient may ignore attachments; user imports returned output manually. No background observation or inferred generation success.

## Android CI

Run `gradle :aya:testDebugUnitTest :aya:assembleDebug :aya:assembleDebugAndroidTest :sample:assembleDebug` with JDK 17, Gradle 8.9 and Android SDK 35. Next publish via `gradle :aya:publishReleasePublicationToStagingRepository` and build sample with `gradle :sample:assembleDebug -Paya.consumePublished=true`. CI preserves the sample APK and local Maven AAR/POM repository artifacts.

`AyaReferenceVerifierTest` exercises mismatched app IDs, old/new/ranged versions, duplicate metadata, missing sections and placeholders. `AyaShareIntentsTest` is a device/emulator instrumentation suite that tests UTF-8 bytes, scope, unique URIs and permissions; compiling tests **does not mean running them**.

## Android instrumentation and manual work remaining
- Prompt-first creative review: user can edit the generation request without scrolling the full reference, Copy and Share request reflect edits exactly, no stream/URI grant is included, Cancel/Back never sends, and opening Full guide preserves edited prompt rather than regenerating stale direction.
- Sample Android UI: Home controls remain visible without scrolling after adding the separate artwork screen; the new non-exported `ArtworkActivity` opens from Home, keeps its host-owned draft and accepts manual import. Verify the return journey with rotation/process recreation as feasible.
- Apply the host acceptance contract in [CREATIVE_HOST_ACCEPTANCE.md](CREATIVE_HOST_ACCEPTANCE.md) to any production importer, including URI grants, MIME/magic mismatch, EXIF, cropping, dimensions, alpha/format handling, save/apply outcomes and undo.
- Creative share-mode checks: choose request-only (no `EXTRA_STREAM`, `ClipData` or URI grants), versus complete guide (.txt read-only URI), and test both Copy choices, cancellation, edited prompts, missing headings and >4000-character requests. No silent truncation or stale pre-edit text.
- Sample importer rejects unsupported MIME types/undecodable images and downscales oversized PNG/JPEG previews without saving permanent media artwork.
- Creative pure Kotlin tests: required image-spec validation, consistent aspect/dimensions, accepted MIME type limits, multiline direction, real generation instruction, host manual-import steps in the text fallback, and final-review edit/delete invariants.
- Creative UI: host direction via `askDirection=false`, built-in direction editor, confirm/cancel, 320×700 and 412×892 screenshots, keyboard, rotation and Share/Copy. Test that the sample's `ACTION_OPEN_DOCUMENT` picker can import a PNG/JPEG **after** manually returning from an AI app, independently of AYA.
- Real target trials: distinguish target offered, text seen, guide read, **image actually generated**, image saved, and manual import; no automatic success callback exists. Record findings only in controlled QA, never user-runtime analytics.


- Run `gradle :aya:connectedDebugAndroidTest` on a configured emulator/device; verify the FileProvider URI reads with grant and **from an independent foreign package** cannot be read without grant. Existing tests cover local URI contents, flags, and scope; external-package denial remains a separate test case.
- Question-first composer: blank/general question, editable host-suggested question, multiline text, keyboard/focus, back/cancel, host `askQuestion=false` path.
- Cancelling or editing the preview changes exactly what is copied/shared, including multiline and Unicode content.
- AYA sends the final question both in the attachment and in bounded `EXTRA_TEXT`, never restoring a question removed in review.
- Empty content and over-2MiB content do not launch a share.
- Repeated shares create unique filenames; old cache cleanup never deletes active handoffs.
- Missing target, denied chooser, bad FileProvider setup, cache failures and Activity recreation fail gracefully.
- TalkBack, full-size font, keyboard focus, touch reachability, landscape and 320x700/412x892 screen snapshots.
- Confirm no unexpected internet permission, credential collection, analytics, or background network calls.

## Recipient matrix
In addition to recipient interoperability trials, test `AyaRecipientCapabilityRegistry`: unverified intent filters, published documentation, exact QA match, account state unknown, app/Android version mismatch, contradicting test observations and absence of entries. Do not let published feature claims become verified ingestion. Test `AyaAssistContext.populate()` in Android instrumentation for JSON-LD and absence of URI grants, and its conservative size limits in unit/device tests. Document real image-generation capability separately from ingestion.

Check image creation ability **separately** from Android `ACTION_SEND` ingestion and account eligibility, because a recipient can support the Sharesheet but not image creation (or vice versa). Include a documented non-image-generating recipient as a negative-case test; confirm that AYA never claims generation happened and that selecting the recipient remains the user's decision.


Run Android 10, 13, 15, 16+ where devices are available, and current installed ChatGPT/Claude/Gemini clients in logged-in/out states. Record tested versions and dates in [compatibility ledger](PROVIDER_COMPATIBILITY.md), including whether file was actually ingested, new chat creation, and required extra user action. Do not advertise provider behavior until verified.

## Stable release gate

Passing static/Gradle checks; tested sample APK; true reference coverage for at least one real app; security/privacy review; assistant answer evaluation and P0/P1-free behavior; physical-device provider matrix; accessibility acceptance.
