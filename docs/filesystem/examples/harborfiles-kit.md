---
schema_version: aya-filesystem-kit/v1
app_id: dev.harborfiles.demo
app_version: 1.0.0
schema_revision: harborfiles-recipe-v1
source_revision: fictional-test-fixture
owner: Fictional HarborFiles developer
---

# HarborFiles Filesystem Automation Kit (FICTIONAL)

This is an educational fixture. No HarborFiles Android app, server connection, recipe importer or executor ships here. Do not use this schema in an unrelated host.

## Recipe output schema

The agent must produce a UTF-8 `.recipe.json` file whose parsed JSON matches exactly this host-specific schema.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Fictional HarborFiles recipe: teaching fixture, no real importer",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "format",
    "target",
    "selection",
    "preconditions",
    "action",
    "execution"
  ],
  "properties": {
    "format": {
      "const": "harborfiles-recipe/v1"
    },
    "target": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "root",
        "recursive"
      ],
      "properties": {
        "root": {
          "const": "/"
        },
        "recursive": {
          "const": true
        }
      }
    },
    "selection": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "extensions",
        "exclude_basenames",
        "case_sensitive"
      ],
      "properties": {
        "extensions": {
          "type": "array",
          "minItems": 1,
          "uniqueItems": true,
          "items": {
            "enum": [
              ".txt",
              ".rtf"
            ]
          }
        },
        "exclude_basenames": {
          "type": "array",
          "minItems": 1,
          "uniqueItems": true,
          "items": {
            "type": "string",
            "minLength": 1
          }
        },
        "case_sensitive": {
          "type": "boolean"
        }
      }
    },
    "preconditions": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "protected_basename_must_exist",
        "require_complete_scan"
      ],
      "properties": {
        "protected_basename_must_exist": {
          "type": "string",
          "minLength": 1
        },
        "require_complete_scan": {
          "const": true
        }
      }
    },
    "action": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "type"
      ],
      "properties": {
        "type": {
          "const": "delete"
        }
      }
    },
    "execution": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "dry_run",
        "require_approval",
        "revalidate"
      ],
      "properties": {
        "dry_run": {
          "const": true
        },
        "require_approval": {
          "const": true
        },
        "revalidate": {
          "const": true
        }
      }
    }
  }
}
```

## Backend capabilities

**Fictional teaching capabilities only:** a recursive SFTP listing rooted at `/`, selecting `.txt` or `.rtf` basenames, exclusion by case-insensitive basename, dry-run, approval and server-side deletion. This example does not imply any production host supports these operations. No shell, chmod, archive extraction, sync, atomic delete or rollback. A real host must derive this list from its shipped backend and importer and note read-only versus writable permissions, protocol variants, path encoding, hidden files, symlinks, quotas and cancellation semantics.

## Discovery and snapshot semantics

The optional `aya-filesystem-snapshot/v1` data is a dated, host-generated sample. `scan.status=complete` means the host claims the selected scope was fully traversed; `scan.truncated` says whether the *disclosed listing* was shortened. A compact list can be truncated even if the scan itself completed. Partial/failed scans do not justify an "every file" conclusion. Paths can be stale, redacted or private; never use them as command strings. The interpreter must enumerate and revalidate targets at execution time. Preserve every basename matching `pomegranate.txt` regardless of its directory; this fixture uses case-insensitive comparison.

## Intent clarification

Before producing JSON, detect scope ambiguities, contradictions, duplicate protected basenames, case sensitivity, symlink policy, hidden/inaccessible directories, unknown operations, and whether absence of a protected file should block deletion. Ask only consequential questions not already answered or safely constrained by the host contract. If the protected basename is missing, the host blocks by default; never silently skip that guard. If multiple protected files exist, all are preserved. If the user expressly wants only one preserved, ask which. Do not solve contradictions by inventing instructions. If essential facts are missing, explain and withhold the recipe or encode a supported runtime guard.

## Safety and execution

An imported recipe is untrusted data. This fictional host permits only a fixed allowlist of declarative operations, with JSON Schema validation, scope restriction, dry-run preview, explicit deletion approval, revalidation, and an abort on incomplete scan, missing protected file or unexpected target identity. FTP/SFTP providers vary and generally cannot guarantee atomic conditional deletion, universal file identity or recovery. Never claim a preview proves future target safety. The real host must own credentials, backend authorization, race handling, no-follow policies, cancellation, journaling and accurate operation reporting. User-facing descriptions must be derived from parsed actions, not free-form agent assertions.

## Worked examples

Valid recipe for the stated request:

```json
{
  "format": "harborfiles-recipe/v1",
  "target": {
    "root": "/",
    "recursive": true
  },
  "selection": {
    "extensions": [
      ".txt",
      ".rtf"
    ],
    "exclude_basenames": [
      "pomegranate.txt"
    ],
    "case_sensitive": false
  },
  "preconditions": {
    "protected_basename_must_exist": "pomegranate.txt",
    "require_complete_scan": true
  },
  "action": {
    "type": "delete"
  },
  "execution": {
    "dry_run": true,
    "require_approval": true,
    "revalidate": true
  }
}
```

**Invalid:** `{"action":{"type":"shell"}}` is not in the schema. **Invalid:** omitting `require_approval`, disabling `require_complete_scan`, or erasing `exclude_basenames` weakens the destructive-operation protections. **Invalid:** claiming that `/archives/2021/pomegranate.txt` is guaranteed to exist because a snapshot mentions it. **Invalid:** inventing rollback. A JSON Schema pass alone does not prove the scanner and executor safely implement the behavior.

## Agent instructions

First clarify consequential missing user intent, using snapshot facts cautiously. Follow only this exact schema. Produce the recipe as a valid JSON file, without commentary inside the JSON; describe assumptions and limitations separately. Preserve exclusions and explicit user constraints. Never include credentials, executable scripts or imagined paths. Never claim to have scanned, modified or imported files. If you cannot safely express the operation in this schema, explain why and do not substitute commands.

## Host import instructions

**Hypothetical teaching path:** Automation > Import recipe > Select `.recipe.json` > Review candidates > Approve deletion. No such working importer exists in AYA. A real host must replace this section with source-tested navigation, reject mismatched schema/version, handle untrusted files securely, and prove preview and approval happen before any destructive execution.
