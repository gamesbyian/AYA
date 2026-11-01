---
schema_version: aya-structured-kit/v1
app_id: dev.example.chart
app_version: 1.0
schema_revision: chart-3
artifact_extension: .json
artifact_mime: application/json
source_revision: fictional-build-1
owner: fictional developer
---
## Artifact output contract
A **fictional** chart editor's importer accepts one JSON object. These statements illustrate the structure, but have not been verified against any real parser.
## Field semantics and bounds
A chart type has an enumerated layout; a series value has user-visible units and explicit numeric bounds in a real consuming host.
## Interactions and precedence
The host must document how chart type, axis mode and conditional series options interact. Do not invent interactions absent in the shipped host.
## State preservation and migration
The host must define stable identifiers and exact migration behavior. AYA performs no migration or preservation.
## Worked valid and invalid examples
A real host must independently test minimal, complex and invalid examples with its shipped importer. This fictional note is not that evidence.
## Agent clarification and safety
Clarify unclear axes, units, sources and destructive replacement choices. Do not request credentials or invent unsupported features.
## Host import and recovery
The user saves the file and explicitly opens host import preview, inspects differences and approves. AYA never imports generated files.
