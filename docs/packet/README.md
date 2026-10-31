# AYA Packet Authoring System

**Status:** build-time authoring tooling and module profiles, not a new AI protocol, a runtime host-state scraper or a replacement for AYA's existing Android Share path.

The [Packet Authoring Standard](AUTHORING_STANDARD.md) governs how every AYA module obtains real host facts, models the task, compiles a concise and semantically complete context packet, and proves its quality before release. Read it alongside [module profiles](PROFILES.md).

## Contract and architecture

AYA's **host developer** owns authoring and approval. The user's preferred assistant receives an explicitly reviewed packet and task. AYA does not access the app's secrets, scrape its UI, observe agent replies or import the result.

The build-time records are:

1. [Typed fact source](schemas/aya-packet-source-v1.schema.json), keyed by stable fact IDs and containing descriptions, applicability, status, risk, dependencies, immutable evidence and date.
2. [Independent inventory](schemas/aya-packet-inventory-v1.schema.json), discovered from the host's shipped UI/code/tests separately from the authored packet. It defines the completeness denominator.
3. [Module-specific profiles](schemas/aya-packet-profiles-v1.schema.json), defining purpose, agent task, output contract, examples and mandatory facts.

The compiler is `tools/packet_compiler.py`. It produces deterministic UTF-8 Markdown plus a machine-readable audit report: host identity, scope, included/omitted fact IDs, dependencies, evidence, source revision, size, digest and high-risk coverage. A scoped packet tells the assistant **"not included"** rather than conflating omissions with **"unsupported."**

## Example (fictional ParcelPad)

```sh
python3 tools/packet_compiler.py \
  --source docs/packet/examples/parcelpad-facts.json \
  --inventory docs/packet/examples/parcelpad-inventory.json \
  --profiles docs/packet/examples/parcelpad-profiles.json \
  --profile creative --select FACT-003 \
  --as-of 2026-10-30T00:00:00Z \
  --output build/aya-creative-packet.md --brief-output build/aya-creative-brief.txt --report build/aya-creative-report.json
python3 -m unittest discover -s tools -p 'test_*.py'
```

The optional `--brief-output` creates a **complete**, at-most-4000-UTF-16-unit text request containing selected facts, dependencies and constraints. It fails instead of truncating for larger tasks; attach the full reviewed packet in that case. Host integration must still use only the final user-approved text and independently test the receiving app.

Changing `--profile` to `help`, `structured`, or `translation` uses the same verified facts without competing hand-written descriptions. Omit `--select` to include the full profile. Specify more than one `--select` for multiple facts. The compiler walks transitive dependencies and mandatory facts; if a packet is too large it **fails**, instead of clipping the safety context. Set a smaller selection or revise the source. `--fragment` makes a Markdown fragment that can be incorporated into an existing APK-bundled AYA-RAS guide using its modular build process.

**APK guide integration:** The existing modular guide builder now accepts `--packet-source`, `--packet-inventory`, `--packet-profiles`, `--packet-profile`, and optional `--packet-select`. It compiles a nested Markdown fragment into the AYA-RAS document, and **rejects** a fact source whose app ID, exact version or source revision differs from the guide. This makes authoring-to-APK assembly a repeatable build step without adding a new Android runtime API.

```sh
python3 tools/build_reference.py host-reference-fragments/ app/src/main/assets/aya-guide.md \
  --packet-source host-docs/facts.json \
  --packet-inventory host-docs/independent-inventory.json \
  --packet-profiles host-docs/profiles.json \
  --packet-profile help
```

**Important limitation:** A compiled AYA packet does not automatically get attached to a conversation. The host must deliberately package it into its version-matched guide, translation kit, or task-specific export. AYA still shares one approved TXT attachment; the normal app importer handles returned files. The current SDK has no general-purpose runtime parser of the `aya-packet/v1` format.

See [controlled cross-module evaluation](EVALUATION.md) and the offline `tools/validate_packet_trials.py` gate for reproducible, byte-matched assistant trials. No model responses are observed by AYA itself.

## Release gates

- Compile every applicable profile with a pinned source revision and independent inventory; inspect report and covered high-risk facts.
- Reconcile claim-level source truth with a released APK and independent reviewer, including any current upstream/provider policies.
- Hold out evaluation questions and target-agent outputs; verify real recipient ingestion and result correctness, not sharesheet appearance.
- Verify no private user content is embedded in the static packet; test app errors, invalid outputs, and explicit manual return.
- Mark untested integrations **unverified**. The fictional fixture is not proof of a working ParcelPad app.

The build-time compiler and JSON Schema are complementary. Neither can infer actual behavior merely from code shape, attest the completeness of a shallow independent inventory, or guarantee an LLM obeys its instructions.
