# AYA specification (draft 0)

## Concept

A host Android app can provide structured application knowledge to a third-party AI assistant selected by the user. The developer supplies knowledge; the user supplies an existing AI account. AYA avoids embedding an inference service.

## MVP requirements

1. Receive application name, installed version, guide, and optional screen/question from host.
2. Preview the complete exact share payload, with Cancel/Copy/Share.
3. Generate one self-contained UTF-8 document and share via `ACTION_SEND`, `EXTRA_STREAM`, `ClipData`, and temporary URI read permission.
4. Never gather diagnostics, private settings, identifiers, credentials, or screenshots implicitly.
5. Avoid proprietary or undocumented intent contracts. No guaranteed new chat.
6. Preserve app usability on share failures; provide copy fallback.
7. Accurately disclose recipient privacy boundary and lack of guarantees.

## Product direction

An 'Ask your agent' entry point anywhere within an app. Intelligent contextual help without vendor lock-in. Version-matched documentation differentiates real, deprecated and planned features. Improve review into a dedicated, editable, accessible screen with opt-in diagnostic fields. Support dated provider capability testing.

## Non-goals

Automatic assistant account creation, answering inside AYA, LLM billing, screen scraping, silently sending telemetry, and reading assistant conversations.

## Release gates

Buildable host example, unit and instrumentation tests, privacy review, accessible full-length document review, and device-verification matrix for actual ChatGPT/Claude versions.
