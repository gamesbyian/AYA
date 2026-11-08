# Fictional image-task workflow: decision and composition fixture

**Illustrative only.** This is not a shipping AYA API or an external assistant acceptance test. The app and image-editing capabilities below are fictional.

## Decision inventory

| ID | Question | Answers | State semantics |
| --- | --- | --- | --- |
| TASK | What outcome do you want? | restore, reinterpret | required primary intent |
| FIDELITY | How closely should the original be preserved? | strict, flexible | applicable to both tasks; strict prohibits changes to original geometry |
| BACKGROUND | What should happen to the background? | preserve, replace | preserve forbids replacement; replace requires explicit user authorization |
| COMPARISON | Include a before/after comparison? | yes, no | presentational; does not authorize changes to the source |
| LABELS | Add explanatory labels? | yes, no | applicable only if COMPARISON=yes; when hidden, prior answer is ignored |

## Fictional input state

```json
{
  "TASK": "restore",
  "FIDELITY": "strict",
  "BACKGROUND": "preserve",
  "COMPARISON": "yes",
  "LABELS": "yes"
}
```

## Resolved intent (illustrative, not a normative schema)

```json
{
  "intent": "restore_image",
  "operations": ["repair_visible_damage", "prepare_before_after_comparison", "label_comparison"],
  "constraints": ["preserve_original_geometry", "preserve_original_background"],
  "output_contract": ["restored_image", "labelled_comparison"],
  "provenance": {
    "preserve_original_geometry": ["FIDELITY"],
    "preserve_original_background": ["BACKGROUND"],
    "label_comparison": ["COMPARISON", "LABELS"]
  }
}
```

## Composed handoff example

> Restore the supplied image by repairing visible damage. Preserve the original geometry and background. Prepare the restored image and a before/after comparison, labelling the comparison clearly. Do not invent previously invisible original detail; identify unrecoverable portions where necessary. The user will save the resulting files and import them through the host's own documented interface. The receiving assistant's actual capabilities and acceptance of the image are not guaranteed.

## Conflict example

A future mode may request replacing an object while a strict selection prohibits changing that same object. The resolver must report an incompatible combination and ask the user which goal to revise. It must not silently permit the replacement or ignore the requested modification.

## Tests for implementing hosts

1. With `COMPARISON=no`, changing `LABELS` from yes to no must not change the task specification or resulting prompt.
2. `FIDELITY=strict` must never produce language permitting changes to preserved geometry.
3. `BACKGROUND=preserve` must not produce instructions to remove or replace it.
4. Invalid `TASK`, missing required answer, or undocumented answer must fail validation.
5. Editing choices in different sequences must yield equivalent intents when final answers are identical.
6. Trace every material composed clause to user choices, host capabilities or the approved authoring contract.
7. Before Share/Copy, show the complete final text and disclose all attachments. Do not infer recipient ingestion from share completion.

The same machinery should also work for a substantially different fictional host, such as a data-report designer selecting comparison dimensions and output formats; application-specific terminology must remain outside the AYA core.
