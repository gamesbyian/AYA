# AYA reference template

Copy from the next line onward into a new file, e.g. `app/src/main/assets/aya-guide.md`. Replace all angle-bracketed fields; remove comments; do not ship this page unchanged. Run the validator before bundling.

```markdown
---
schema_version: aya-reference/v1
app_id: com.example.yourapp
app_name: Your App
app_version_min: 1.0.0
app_version_max: 1.0.0
platform: android
locale: en
guide_revision: 1
source_revision: <git-commit-or-release-id>
last_verified_utc: 2026-10-28T00:00:00Z
owner: <team-or-maintainer>
---

# Your App: support reference

## Scope and version
- Covers: <release/build/channel/OS>
- Does not cover: <betas, unreleased features>
- Features conditional on: <permissions/accounts/providers>

## Quick orientation
- Purpose: <what this app does, in user language>
- Key concepts: <core objects and their relationships>
- Most common user tasks: <top five>

## Navigation map
- Home > <screen> > <exact control>: <result>
- <include all visible screens, menu entry points, gestures and empty states>

## Task recipes
### TASK-001: <achieve a user goal> [AVAILABLE]
- Applies to: <version/build/provider/OS>
- Start: <exact starting screen>
- Prerequisites: <permissions, files, account, network>
1. <tap exact control>
2. <enter/select something>
3. <confirm action>
- Expect: <observable result>
- If it fails: <ERR-001 and safe discriminating check>
- Verification: <what the outcome proves and does NOT prove>
- Side effects/undo: <local/remote scope, commit point, cost, reversibility>
- Condition branches: <visible/disabled under permission, provider, flag, OS>
- Evidence: <path/test/build and verified date>

## Features and settings
### F-001: <feature name> [AVAILABLE]
- What it does: <precise>
- Location: <exact UI path>
- Defaults: <value and unit>
- Constraints and interactions: <bounds, other settings>
- Visibility: <which state/permission/variant exposes this control>
- Persistence: <session/device/account>
- Status/version: <AVAILABLE/CONDITIONAL/etc., range>
- Evidence: <specific source>

## Troubleshooting
### ERR-001: <verbatim error or symptom>
- Context: <when/where>
- Meaning: <what this does and does not prove>
- Check: <non-sensitive question/test, possible outcomes, and what each proves>
- Fix: <safe remediation per observed outcome>
- Verify: <what successful recovery looks like>
- Escalate: <legitimate path, no invented contact>
- Evidence: <source>

## Limitations and unsupported behavior
- <confirmed absence UNSUPPORTED, announced future PLANNED, unverified UNKNOWN>
- <provider and OS differences>

## Privacy and data handling
- Device storage: <what and where at useful level>
- Shared/network data: <what leaves the device>
- Permissions: <what for and revocation effects>
- Deletion/export: <scope, permanence, backup>
- Safe help context: <never send passwords, tokens, secrets>

## Glossary and synonyms
- <official term>: <what users might call it>
- <confusable term>: <distinction>

## Evidence and provenance
- Build: <release/build and revision>
- UI sources: <path/revision>
- Tests: <path and result/date>
- Known gaps: <evidence limitations>

## Unknowns and escalation
- UNKNOWN: <specific unresolved behavior>
- Safe verification: <user-observable test>
- Support: <real in-app or official channel, or 'not provided'>

## Assistant answer policy
- First determine: <top branching questions with high information gain>
- Avoid: <likely but nonexistent controls, forbidden secrets, dangerous defaults>
- Distinguish: <unsupported vs unknown vs currently unavailable>
- When advising: <exact screen labels and non-destructive steps>
- If unsupported: state it explicitly; do not invent controls
- No direct app control is implied by possession of this guide.
```

The template intentionally contains placeholders and is **expected to fail** automated validation until completed.
