# Adaptive Director Question Bank

**Use selectively.** These questions are templates for investigating actual unresolved product decisions, not a mandatory survey or permission to repeatedly question the director. Always frame the chosen question using repo evidence, current interpretation and the material consequence of different answers.

## Product purpose

- What recurring user difficulty should this app eliminate particularly well?
- What would a successful experience look like to someone who never reads its documentation?
- What principle would you preserve even if implementation changes radically?
- Which functions are intentionally outside scope?

## Audience and user expectations

- Who should feel comfortable without expert knowledge, and what should experts still be able to control?
- Where do users arrive with assumptions learned from competing apps?
- Which user mistake is especially understandable or costly?
- Which accessibility or offline conditions should shape the ordinary workflow?

## Agency and automation

- When the user ignores an optional setting, what sensible default outcome should occur?
- Which routine actions should the app perform autonomously, and which need explicit consent?
- Which expert controls should remain discoverable even if automatic defaults handle most cases?
- Where should the system explain a decision rather than require the user to make it?

## Priorities and tensions

- When reliability competes with speed, what is the intended default trade-off?
- Should a risk of irreversible loss override an otherwise smooth workflow, and where?
- When simplicity competes with flexibility, how should the UI expose complexity?
- Is a current compromise an intended principle or a temporary implementation limitation?

## Ontology and terminology

- Which objects or states sound similar but must never be conflated?
- Does a technical term reflect the user's actual task or only the code's internals?
- Which distinctions must an assistant preserve in help, translation and generated artifacts?
- Which terms can be simplified, and what would that simplification lose?

## Failures and consequences

- Which consequences require explicit confirmation or a reversible preview?
- What should happen when an operation's outcome cannot be independently confirmed?
- Where should recovery be automatic, and where could retries duplicate harm?
- What information should an assistant refuse to assume from a status indicator?

## Tone and explanations

- How much detail should be presented by default, and how can users request deeper technical context?
- Should unfamiliar terms be explained in place, through optional disclosure, or only in help?
- Where is playful language desirable, and where would it undermine precision?
- How should the app communicate uncertainty without sounding broken or evasive?

## Future and unresolved decisions

- Which advertised goals are firm intentions rather than implemented functionality?
- Which existing behaviors are known temporary compromises?
- Where can the developer agent exercise its own judgment, and where should it consult?
- Should this ambiguity remain explicitly open until user research or tests settle it?

## Better than a generic questionnaire

Weak: "How should advanced settings work?"

Evidence-driven: "The settings panel currently exposes manual controls for X, Y and Z, while the product guidance prefers low-friction defaults. Should those controls remain available but optional, with automatic defaults, or is explicit configuration an intended part of this workflow? This affects onboarding and AYA's explanation of normal operation."

Allow: **confirm / correct / conditional / delegate / defer / freeform**. Do not pressure the director to answer an issue they would reasonably prefer to leave unresolved.
