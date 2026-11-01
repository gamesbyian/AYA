# Godot CI: authoritative real-engine APK gate

**Recorded:** 2026-10-31 local / 2026-11-01 UTC. This memo documents a concrete, verified change in job ownership. The [CI engineering standard](CI-ENGINEERING-STANDARD.md) remains normative.

## Baseline and why the extra job was redundant

Prior to this change, every Godot adapter or shared native AYA edit triggered both:

1. `godot.yml:godot-android`: compile both debug/release `aya` and `aya-godot` AARs, inspect staged addon scripts and run Godot 4.5.1's real headless editor parser/smoke.
2. `godot-export.yml:real-godot-export`: compile **the same** paired debug/release AARs, stage the identical addon and perform **the same** headless Godot smoke, then use the official, hash-verified Godot Android export templates to produce and inspect a real Godot-generated APK.

The first job supplied no independently different compiler, API-level or host contract. Its separate upload of the staged addon was useful, so that output is retained in the real-export gate.

Two historical successful `godot-android` job durations observed directly from GitHub Actions (wall time on an allocated runner):

| Run | Start (UTC) | End (UTC) | Runner wall |
| --- | --- | --- | --- |
| [41264756561](https://github.com/gamesbyian/AYA/actions/runs/41264756561) | 2026-11-01 02:21:07 | 02:22:32 | 1m25s |
| [41262708067](https://github.com/gamesbyian/AYA/actions/runs/41262708067) | 2026-11-01 01:50:15 | 01:51:39 | 1m24s |

The matching, successful actual exporter [41264756578](https://github.com/gamesbyian/AYA/actions/runs/41264756578) ran from 02:20:22 to 02:23:44 UTC (3m22s), including the complete original AAR stage, headless editor tests, Godot export and APK verification. The two jobs ran concurrently, so their elapsed times **must not be added** to estimate merge latency. Their runner allocations do add to consumed runner resources. These are historical samples, not a statistical or billed-money savings claim.

## Change

Remove the duplicate `godot.yml` workflow. Make `godot-export.yml` solely responsible for:

- Building `aya-godot:stageGodotAddon` once, confirming that **both debug and release AAR pairs**, `plugin.cfg`, `export_plugin.gd` and `aya_card.gd` are staged.
- Running headless Godot editor import, `aya_smoke.gd`, and `aya_export_preflight.gd` exactly as before.
- Exporting a **genuine Godot 4.5.1 Android Gradle APK** with the pinned official exporter and inspecting actual package identity, exact host guide bytes, merged sharing providers/receiver, v2 Android metadata and compiled DEX.
- Uploading **both** the full staged addon and the Godot-produced APK, each with finite retention and explicit missing-file failure.
- Dispatching on changes to `aya/**`, Godot code and scene, relevant verification tooling, Gradle root build/settings/properties, and its own workflow. Manual workflow dispatch remains available.

The deterministic `tools/test_godot_ci_ownership.py` checks workflow ownership, trigger coverage, artifact naming and that no old duplicate workflow returns. It cannot certify runtime behavior or installer portability by itself.

## Remaining limitations

The pass is still first-party synthetic **S2 engine-export packaging** evidence, not a genuinely independent host or real Android device. No TalkBack, gamepad, Android keyboard, provider attachment ingestion, output import or public extension-store installation is proven. Reference, device and recipient gates remain independent.

**Expected dispatch outcome:** one fewer Android/Gradle+Godot editor job for source changes, while maintaining the stronger actual-engine export evidence. Measure cumulative runner minutes, time to actionable failure and flake rate across representative subsequent PRs before claiming a numerical improvement.
