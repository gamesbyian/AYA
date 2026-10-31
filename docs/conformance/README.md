# SDK-independent AYA interaction trace checks

AYA is an optional interaction **convention**. A developer can implement it
without adopting any AYA library. The offline checker in
`tools/validate_handoff_trace.py` helps review one narrow safety property:
whether a supplied **local lifecycle-event trace** follows AYA's
reference-validation, editable-review and deliberate Copy/Share ordering.

This is an instrumentable, synthetic/developer-supplied **structural test**,
not a certification of an app, guide accuracy, accessibility or assistant
attachment ingestion. Traces can be inaccurate or fabricated; independently
repeat the test with real device instrumentation before making compatibility
claims. Opening Android's chooser proves nothing about what a model received.

## Use without AYA dependencies

Record events in your own Android app or test harness, omitting all user
questions, reference bodies, file paths, recipients, URI, timestamps and
identifying data. The trace contains only app ID, version, a safe source
revision identifier and event **names**.

Use the completely fictional example as a guide to shape, not evidence of an
existing application's behavior:

```sh
python3 tools/validate_handoff_trace.py docs/conformance/examples/lantern-trace.json
python3 -m unittest discover -s tools -p 'test_validate_handoff_trace.py'
```

Every trace file must include six cases, each once:

| Scenario | Required local observations |
| --- | --- |
| `review_share` | Reference validated, editable review opened/approved, explicit Share requested, Android chooser opened |
| `review_copy` | Reference validated, review approved, explicit Copy requested and completed |
| `cancel` | Review opened, cancelled, **no** sharing/copying |
| `version_mismatch` | Stale/incorrect installed guide rejected, **no** review/dispatch |
| `no_receiver` | User-approved share attempt unavailable, explicit Copy fallback |
| `no_activity` | Detached/absent Android Activity rejected locally, without any sharing |

The optional `question_opened` and `review_edited` events represent local
steps only. The checker rejects unknown event names, duplicate terminal
events, dispatch before review approval, chooser before request, editing
after approval, contradictory negative cases, and unexpected payload keys.
It accepts neither recipient replies nor imported outputs as handoff events.

The test intentionally cannot infer which app consumed a payload, detect
hidden telemetry or automatic response monitoring from the trace, or inspect
the installed APK for correct AYA-RAS guide bytes. Those requirements belong
to the independent device and packaging evidence gates.

Use [release evidence levels](../components/RELEASE-EVIDENCE.md) to describe
results accurately. This validator proves only consistency of the **provided
metadata**; real compatibility requires an independently reviewed
implementation and observation of its actual behavior.
