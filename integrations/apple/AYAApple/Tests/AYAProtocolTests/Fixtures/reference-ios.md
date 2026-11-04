---
schema_version: aya-reference/v1
app_id: org.example.aya-lantern
app_name: Lantern Demonstration
app_version_min: 1.0.0
app_version_max: 1.0.0
platform: ios
locale: en
guide_revision: 1
source_revision: cross-platform-fixture-v1
last_verified_utc: 2026-11-03T00:00:00Z
owner: AYA fixture contributors
---

# Lantern Demonstration reference: fictional iOS host

## Scope and version

This fixture describes a fictional layout helper at version 1.0.0. Its app identifier is org.example.aya-lantern. It is deliberately unconnected to any real user product or external repo.

## Quick orientation

The host displays two harmless controls and a small Ask Your Agent card. The guide is built with the host so the assistant can explain installed behavior without guessing future features.

## Navigation map

Home > Ask Your Agent > Review is the reviewed outgoing flow. Home > Import is a separate user-controlled file selection flow. Cancel leaves the host without sharing.

## Task recipes

### TASK-001: Ask about a setting [AVAILABLE]

Review the exact outgoing text before Copy or Share. Pick an external destination only after inspecting the packet. A recipient may not ingest attachments.

## Features and settings

### F-001: Local demo setting [AVAILABLE]

The user may toggle a fictional display layout in the host. The setting has no external side effects or background processing and no third-party service is called.

## Troubleshooting

### ERR-001: Missing reference [CONDITIONAL]

When source-derived guidance is absent or stale, stop before presenting review. Rebuild with a guide matching the exact installed bundle identifier and version.

## Limitations and unsupported behavior

This fixture does not connect to third-party models. No provider-specific promise, result watcher, automatic import or destructive recipe executor is available.

## Privacy and data handling

Outbound text is not transmitted until the user explicitly selects Copy or Share. The host does not collect model responses or inspect another app's private documents.

## Glossary and synonyms

A handoff is a human-reviewed outgoing request. A guide is version-matched reference text. An importer is a separately authorized host file reader.

## Evidence and provenance

All behavior here is synthetic and source-authored for parity tests. It cannot demonstrate correctness of another host, iOS device accessibility or recipient ingestion.

## Unknowns and escalation

If an assistant ignores a document, a user can choose a text-only copy route. Developer QA must record actual receiver behavior by version; unknown capabilities stay unknown.

## Assistant answer policy

Use only this fixture's documented controls. Never infer additional settings, request secrets or claim that a share attempt means a model consumed the material.
