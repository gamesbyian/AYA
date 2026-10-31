# Build one reference from modular source documents

Complex apps can maintain guides in small, independently reviewed Markdown files rather than editing one enormous text file. AYA still needs a **single, self-contained reference** at share time. The standard library-only `tools/build_reference.py` creates a deterministic unified guide.

## Suggested layout in an integrating app

```text
app-help/
  00-header.md          # AYA-RAS frontmatter and # App guide title
  10-scope.md           # ## Scope and version / ## Quick orientation
  20-navigation.md      # ## Navigation map
  30-workflows.md       # ## Task recipes
  40-settings.md        # ## Features and settings
  50-errors.md          # ## Troubleshooting
  60-limits-privacy.md  # ## Limitations... / ## Privacy and data handling
  70-reference.md       # ## Glossary... / ## Evidence... / ## Unknowns...
  80-assistant.md       # ## Assistant answer policy
```

These file names are examples; the numeric prefixes establish stable order. Preserve required heading names exactly as in the template. Keep the AYA-RAS metadata envelope exclusively in `00-header.md`.

Run:

```sh
python3 tools/build_reference.py app-help app/src/main/assets/aya-guide.md
python3 tools/validate_guide.py --strict app/src/main/assets/aya-guide.md
```

## Optional source-backed packet fragment

For hosts with a [typed Packet Source](../packet/README.md), compile one of the four module profiles as a nested Markdown reference fragment during guide assembly. The builder verifies that the fact source shares the **same app ID, exact installed version and source revision** as the AYA-RAS guide. It preserves the 12 canonical sections and rejects an oversized combined export.

```sh
python3 tools/build_reference.py app-help app/src/main/assets/aya-guide.md \
  --packet-source host-docs/aya-facts.json \
  --packet-inventory host-docs/aya-independent-inventory.json \
  --packet-profiles host-docs/aya-profiles.json \
  --packet-profile help
```

Use `--packet-select FACT-012` repeatedly for explicit task-scoped builds. The compiler includes dependencies and required safety facts; omitted facts are reported as **not included**, never assumed unsupported. This is a **build-time** operation: the Android library does not currently select fact subsets or inspect host state dynamically. Keep the final guide included in the APK and verify it matches the actual released build.

The assembler rejects symlink inputs and files larger than the prototype's 2 MiB share limit, validates the combined document, writes UTF-8 with stable line endings, and prints a reproducible SHA-256. Verify the hash belongs to the APK or release record. Do not silently truncate or omit sections to fit.

Build **one guide per actually supported app release/variant**. Never mix released functionality with unreleased PRs or copy private log snippets into sources. If two source files contradict each other, resolve the discrepancy at the source and re-run the question bank.
