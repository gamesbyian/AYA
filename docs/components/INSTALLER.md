# Safe AYA host integration scaffolder (initial Android support)

**Status:** build-time helper, not a full SDK installer or editor marketplace plugin. It emits a real Kotlin wrapper or Android XML layout into an existing Android module, plus the exact validated JSON configuration under `.aya/components/`. It does not fabricate app-specific documentation or install a dependency automatically.

## Why

Coding agents and casual developers can generate consistent, uniquely named drop-in components without editing a project's existing files. This complements the [component architecture](README.md), [XML layout adapter](XML.md), and the merged [Compose adapter](COMPOSE.md). For now it handles **Android Views/Kotlin, Compose (when the optional `aya-compose` library is installed), and Android XML**, since a Compose source generator requires the optional Compose SDK to be merged and tested first.

## Use

From an AYA checkout, with an existing Android project at `/path/to/project`:

~~~sh
python3 tools/component_scaffold.py \
  --project-dir /path/to/project \
  --module app \
  --manifest docs/components/examples/sample-help-card.json \
  --mode android-xml
~~~

This is a **dry run**: it prints a machine-readable plan with exact destinations and remaining requirements. Nothing is written until `--apply` is specified. For Kotlin code use `--mode kotlin --package com.example.hostapp`.

~~~sh
python3 tools/component_scaffold.py \
  --project-dir /path/to/project \
  --module app \
  --manifest /path/to/host-specific-aya-component.json \
  --mode kotlin \
  --package com.example.hostapp \
  --apply
~~~

The generated file belongs to the developer's project, which must already have a valid `app/src/main` directory. The generator will not create a fake app, mutate Gradle, add permissions, add SDK binary blobs, scan an app, or bundle misleading sample documentation. It refuses unknown configuration keys, unsafe paths, accidental replacements, existing modified files, and symlink escapes. Re-running an identical applied configuration leaves existing content unchanged.

**The sample manifest is an example only.** Before applying, derive real scope, description, disclosure, and output-use instructions from the exact host build using [AYA-AUF](../understanding/README.md), [AYA-RAS](../reference/INDEX.md) and [Packet Authoring](../packet/README.md). The host must include an exact-version `aya-guide.md` asset and a compatible SDK dependency, then place the generated XML in its screen layout or call the generated Kotlin wrapper.

The generated configuration record is a reproducibility aid, never automatically included in any user-to-assistant packet. Copy, sharing, output import, and any destructive actions remain independently user-controlled. Do not present a generated file as evidence of recipient ingestion or a working Flutter/Godot plugin.

## Safety guarantees / limitations

- Structural generation only: no semantic verification or release acceptance.
- A missing guide fails at runtime in the guarded SDK; the scaffolder intentionally refuses to invent one.
- It never overwrites a pre-existing file with different contents. On interrupted multi-file creation, newly created files are rolled back where possible; an OS crash can still leave partial output and should be inspected.
- A Kotlin namespace is explicitly supplied for Kotlin or Compose source. XML output is card-only; headless actions require the Kotlin entry point.
- Android module directories and generated paths are constrained, with symlinks rejected on output paths.
- The tool does not automatically wire the generated element into a UI screen; host agent/developer must integrate, test, and keep it accurate.
- Build/dev QA requires real Android emulator/device testing; cross-toolchain adoption remains separately tracked in [#21](https://github.com/gamesbyian/AYA/issues/21).
