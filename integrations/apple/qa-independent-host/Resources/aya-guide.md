---
schema_version: aya-reference/v1
app_id: org.example.aya.readerqa
app_name: Reading Queue QA
app_version_min: 0.1.0
app_version_max: 0.1.0
platform: ios
locale: en
guide_revision: 1
source_revision: readerqa-native-host-v1
last_verified_utc: 2026-11-04T00:00:00Z
owner: AYA independent fixture contributors
---

# Reading Queue QA reference

## Scope and version

This guide documents the fictional Reading Queue QA iOS host build 0.1.0, app ID org.example.aya.readerqa, with only the behavior visible in its source.

## Quick orientation

The sample displays a simple reading queue count and a button that adds one synthetic title. It runs locally with no accounts, backend or AI API.

## Navigation map

The only screen is Reading QA. Under its heading are the Saved titles count, Add sample title button and an Ask Your Agent help card.

## Task recipes

### TASK-001: Add a sample title [AVAILABLE]

Open the Reading QA home screen and tap Add sample title. The Saved titles count increases by one, without saving an actual book or contacting a service.

## Features and settings

### F-001: Temporary local counter [AVAILABLE]

Saved titles begins at zero when the app launches. Each tap on Add sample title increments the onscreen count; there is no persistence or deletion control.

## Troubleshooting

### ERR-001: Missing guidance [CONDITIONAL]

If the bundled guide is missing or does not match this installed bundle ID and version, Ask Your Agent rejects the review rather than passing an invented guide to another application.

## Limitations and unsupported behavior

This host has no file importer, recommendations engine, real book catalog, user account, persistent reading list or automatic assistant response processing.

## Privacy and data handling

This fictional host keeps the local count only in memory. AYA shows the full question and reference for editing before the user explicitly copies or shares them via iOS.

## Glossary and synonyms

Reading queue refers only to the on-screen synthetic count. A handoff means the user-approved text sent through the system Share Sheet or clipboard.

## Evidence and provenance

The exact source code for this independent QA host defines Add sample title, a local count, and an AYAHelpCard consuming the root SwiftPM AYAApple product.

## Unknowns and escalation

Real third-party AI ingestion, device screen readers, persistent storage and artifact import are unsupported or unverified. Developers must verify receiver behavior separately.

## Assistant answer policy

Answer based only on these version-matched controls. Do not promise account settings, actual stored books, invisible export actions, automatic AI output retrieval or data persistence.
