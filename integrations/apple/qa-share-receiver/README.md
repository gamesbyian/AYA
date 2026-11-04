# AYA foreign iOS Share Sheet QA receiver

**Status:** experimental first-party *disposable* test application and Share Extension. Its source is deliberately independent of both the AYA Swift Package and the actual host app. In [PR #133 / CI 41781406186](https://github.com/gamesbyian/AYA/actions/runs/41781406186), it also demonstrated real **iPhone Simulator OS-mediated synthetic recipient input** in both modes with exact foreign-receiver SHA-256 and byte count. It is not an AI provider or production AYA module.

This fixture implements the narrow [byte-level Apple receiver acceptance plan](../../../docs/apple/RECEIVER_QA.md). It will receive an explicitly shared single plain-text item or one text file, read its actual NSItemProvider representation (including Apple's callback-scoped temporary file lifetime), and show **only** receipt type, byte count, SHA-256 and status. It never prints, uploads, saves or echoes the document body; the host and extension make no network calls.

Build on a Mac with Xcode and XcodeGen:

    cd integrations/apple/qa-share-receiver
    xcodegen generate
    xcodebuild -project AYAShareQA.xcodeproj -scheme AYAShareQAHost \
      -sdk iphonesimulator -destination 'generic/platform=iOS Simulator' \
      CODE_SIGNING_ALLOWED=NO build

The app bundle must contain `PlugIns/AYAShareQAExtension.appex` with `com.apple.share-services`, strict text/file activation keys and a resolved Swift principal class. These are **packaging** checks, not proof that a foreign receiver was offered, ran or obtained bytes. Do not claim compatibility with ChatGPT or any LLM from this synthetic fixture.

**Accepted native baseline:** [run 41781406186](https://github.com/gamesbyian/AYA/actions/runs/41781406186) installed this app alongside the sample, selected the QA extension through the actual iOS Share Sheet, and verified the independently received SHA-256 and byte counts for both plain text and full .txt. Next acceptance includes edited review bytes, repeated shares/cancellation, real assistant recipients and physical devices. Missing extension or mismatched bytes must fail rather than be skipped.

Do not add this to published AYA products, app IDs, user data, permanent files, system-wide URL handlers, third-party provider assumptions or production telemetry. Delete the disposable QA app when no longer needed.
