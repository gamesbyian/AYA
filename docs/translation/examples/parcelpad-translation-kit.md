---
schema_version: aya-translation-kit/v1
app_id: dev.parcelpad.example
app_version: 1.0.0
catalog_revision: fictional-catalog-v1
source_revision: fictional-fixture-no-release
source_locale: en
owner: Fictional ParcelPad example maintainers
---

# ParcelPad Translation Kit (FICTIONAL EXAMPLE)

This is a teaching fixture. It does not describe a shipped app, working importer or verified UI.

## Output schema

Output is a UTF-8 .json file. This schema is specific to the fictional ParcelPad example, not a universal AYA language pack.
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Fictional ParcelPad language pack v1",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "format",
    "app_id",
    "catalog_revision",
    "kind",
    "target",
    "base_locale",
    "entries"
  ],
  "properties": {
    "format": {
      "const": "parcelpad-pack/v1"
    },
    "app_id": {
      "const": "dev.parcelpad.example"
    },
    "catalog_revision": {
      "const": "fictional-catalog-v1"
    },
    "kind": {
      "enum": [
        "language",
        "personality",
        "terminology"
      ]
    },
    "target": {
      "type": "string",
      "minLength": 2,
      "maxLength": 48
    },
    "base_locale": {
      "const": "en"
    },
    "entries": {
      "type": "object",
      "minProperties": 1,
      "additionalProperties": false,
      "properties": {
        "parcel.status.ready": {
          "type": "string",
          "minLength": 1,
          "maxLength": 800
        },
        "parcel.action.remove": {
          "type": "string",
          "minLength": 1,
          "maxLength": 800
        },
        "parcel.action.delete_files": {
          "type": "string",
          "minLength": 1,
          "maxLength": 800
        },
        "parcel.files.count": {
          "type": "string",
          "minLength": 1,
          "maxLength": 800
        },
        "parcel.a11y.delete_files": {
          "type": "string",
          "minLength": 1,
          "maxLength": 800
        }
      }
    }
  }
}
```

## Source catalog

Stable semantic keys with operational meaning:
```json
{
  "source_locale": "en",
  "catalog_revision": "fictional-catalog-v1",
  "strings": [
    {
      "id": "parcel.status.ready",
      "source": "Ready",
      "screen": "Parcel list",
      "state": "idle",
      "description": "Status only: parcel is ready, not transmitted.",
      "safety": "ordinary",
      "placeholders": [],
      "evidence": "fictional design fixture"
    },
    {
      "id": "parcel.action.remove",
      "source": "Remove from list",
      "screen": "Parcel actions",
      "state": "confirmed",
      "description": "Removes list item but keeps downloaded files.",
      "safety": "technical",
      "placeholders": [],
      "evidence": "fictional design fixture"
    },
    {
      "id": "parcel.action.delete_files",
      "source": "Delete local parcel files",
      "screen": "Parcel confirmation",
      "state": "destructive",
      "description": "Permanently deletes local saved parcel files.",
      "safety": "destructive",
      "placeholders": [],
      "evidence": "fictional design fixture"
    },
    {
      "id": "parcel.files.count",
      "source": "{count, plural, one {# parcel} other {# parcels}}",
      "screen": "Parcel list",
      "description": "Count of parcels; ICU plural syntax.",
      "safety": "ordinary",
      "placeholders": [
        {
          "name": "count",
          "type": "number",
          "format": "plural"
        }
      ],
      "evidence": "fictional design fixture"
    },
    {
      "id": "parcel.a11y.delete_files",
      "source": "Delete downloaded parcel files from this device",
      "screen": "Parcel confirmation",
      "description": "Accessibility label for irreversible file deletion.",
      "safety": "accessibility",
      "placeholders": [],
      "evidence": "fictional design fixture"
    }
  ]
}
```

## Rosetta and glossary

Explicit contrasts for terse UI terms:
```json
{
  "terms": [
    {
      "term": "Remove",
      "meaning": "Remove the parcel from the UI list, keep stored files",
      "forbidden": "delete downloaded files",
      "keys": [
        "parcel.action.remove"
      ]
    },
    {
      "term": "Delete",
      "meaning": "Permanently erase stored parcel files on this device",
      "forbidden": "merely hide the item",
      "keys": [
        "parcel.action.delete_files",
        "parcel.a11y.delete_files"
      ]
    },
    {
      "term": "Ready",
      "meaning": "Ready for a later action; no transfer has occurred",
      "forbidden": "already delivered",
      "keys": [
        "parcel.status.ready"
      ]
    }
  ]
}
```

## Style and meaning constraints

A Pirate style may embellish ordinary statuses but may not obscure Remove versus Delete, imply a transfer that never happened, or make an accessibility description vague. Preserve ICU placeholders and plural branches. Do not claim Cajun-flavoured or invented voices represent authentic linguistic translations. Keep permission, security and destructive language plain and accurate.

## Worked examples

Valid partial Pirate pack:
```json
{
  "format": "parcelpad-pack/v1",
  "app_id": "dev.parcelpad.example",
  "catalog_revision": "fictional-catalog-v1",
  "kind": "personality",
  "target": "pirate-en",
  "base_locale": "en",
  "entries": {
    "parcel.status.ready": "Ready to sail",
    "parcel.action.remove": "Remove from the list",
    "parcel.action.delete_files": "Delete local parcel files",
    "parcel.files.count": "{count, plural, one {# parcel aboard} other {# parcels aboard}}",
    "parcel.a11y.delete_files": "Delete downloaded parcel files from this device"
  }
}
```

**Invalid:** translating `parcel.action.remove` to `Delete files` changes behavior. **Invalid:** `parcel.files.count` = `A lot of parcels` drops the count placeholder. **Invalid:** adding `parcel.action.launch` invents an unknown key. **Invalid:** a successful JSON Schema match alone does not prove ICU message syntax is valid.

## Agent instructions

Use the schema and catalog above to produce a valid, importable .json file matching the requested language or personality. Keep exact keys, preserve all named placeholders, and respect distinctions about real data loss. A partial pack is permitted: omit any untranslated entries rather than inventing meaning. Report uncertainty outside the JSON file. Do not claim to have installed anything in ParcelPad.

## Host import instructions

**Hypothetical only:** A ParcelPad host implementing this spec would expose Settings > Language > Add language pack > Choose JSON, preview a pack and activate it. Such an importer does not exist in this repository; real hosts must replace this with the verified UI steps. AYA only shares the kit and task; the assistant must let the user save the generated file, which they manually import.
