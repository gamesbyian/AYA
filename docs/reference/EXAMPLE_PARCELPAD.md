---
schema_version: aya-reference/v1
app_id: dev.example.parcelpad
app_name: ParcelPad
app_version_min: 1.0.0
app_version_max: 1.0.0
platform: android
locale: en
guide_revision: 1
source_revision: fictional-example-1
last_verified_utc: 2026-10-28T00:00:00Z
owner: AYA examples
---

# ParcelPad: fictional example reference

**This entire guide describes a fictional training app, NOT a real Android product.** Behaviors are synthetic and only demonstrate reference-writing technique.

## Scope and version

ParcelPad 1.0.0 Android fictional demonstration. No real installation, account or provider exists. No Android version restriction is represented. All feature claims below are illustrative. Future or non-fictional product claims are UNKNOWN.

## Quick orientation

ParcelPad is a fictional offline inventory of packages. A *parcel* has a title, note and delivered checkbox. A *collection* groups parcels. It never automatically tracks shipments. Main tasks: add a collection, add a parcel, mark delivered, export a local JSON backup.

## Navigation map

- Home > Collections: list of collections, including an empty-state Add collection button.
- Collections > [collection] > Add parcel: opens parcel editor.
- Parcel editor > Save: writes a parcel to local storage.
- Home > Settings > Export backup: creates a JSON document through Android's document picker.
- Back from unsaved editor: fictional confirmation "Discard changes?"

## Task recipes

### TASK-001: Add a parcel [AVAILABLE]

- Applies to: fictional ParcelPad 1.0.0 only.
- Start: Home > Collections.
- Prerequisites: a collection exists; if none, tap Add collection first.
1. Open the intended collection.
2. Tap Add parcel.
3. Enter a title; optionally enter a note.
4. Tap Save.
- Expect: parcel appears in the selected collection.
- If it fails: see ERR-001.
- Side effects/undo: saved locally; can later edit or delete the parcel.
- Evidence: fictional training scenario, not a shipped app.

### TASK-002: Export backup [AVAILABLE]

- Applies to: fictional ParcelPad 1.0.0 only.
- Start: Home > Settings.
- Prerequisites: device has an Android DocumentsUI provider.
1. Tap Export backup.
2. Select a folder in Android document picker.
3. Confirm file creation.
- Expect: a JSON backup document in selected location.
- If it fails: ensure destination permits writing; choose another directory.
- Side effects/undo: export does not delete local parcels. The backup may contain user-entered notes; do not share it publicly.
- Evidence: fictional training scenario.

## Features and settings

### F-001: Delivered checkbox [AVAILABLE]

- What it does: locally marks parcel as delivered; it does not query a carrier.
- Location: Home > Collections > [collection] > [parcel] > Delivered.
- Default: unchecked.
- Constraints: one Boolean per parcel, editable anytime.
- Persistence: local device storage.
- Status/version: AVAILABLE in fictional v1.0.0.
- Evidence: fictional training scenario.

### F-002: Carrier tracking [PLANNED]

No live tracking endpoint or notification exists in this fictional release. Do not instruct the user to enable it.

## Troubleshooting

### ERR-001: "Title required"

- Context: displayed when saving a parcel with a blank title.
- Meaning: no new parcel was saved.
- Check: ensure Title is not empty.
- Fix: enter a nonblank title and tap Save again.
- Verify: the parcel appears in its collection.
- Escalate: no official support contact exists for this fictional app.
- Evidence: fictional training scenario.

## Limitations and unsupported behavior

The app has no carrier APIs, accounts, sync, background jobs, location tracking or server. Carrier tracking is PLANNED, not available. Import from JSON, automatic updates, and multi-device sync are UNKNOWN (not defined in this training scenario).

## Privacy and data handling

All parcel fields in this fictional example are stored locally; a backup explicitly exported by the user leaves the app. No account, remote service or background network use is modeled. An exported backup can contain private notes; avoid sharing it in AI help.

## Glossary and synonyms

- Parcel: package, shipment entry, item; does not mean a live carrier-tracked shipment.
- Collection: folder, group.
- Delivered: manually toggled status, not confirmed delivery by a carrier.

## Evidence and provenance

Synthetic example authored solely to demonstrate AYA-RAS v1, last revised 2026-10-28. There is no implementation, release binary, test result or real product claim.

## Unknowns and escalation

UNKNOWN: behaviors outside the explicitly described synthetic functions. Safe verification for any real app would require its code/test or installed build. Support: not provided (fictional product).

## Assistant answer policy

First establish whether the user is asking about this fictional example or an actual app. Never claim it exists on Google Play. For fictional tasks give the exact synthetic paths above. Do not ask for backups containing private notes. No app-control integration is implied.
