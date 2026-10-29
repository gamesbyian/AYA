# AppFunctions and ACTION_PROCESS_TEXT: separate exploration decision

**Research snapshot:** 2026-10-29. The core AYA SDK remains **one-way handoff only**, with no agent calls into the host and no result callbacks.

## AppFunctions

[Android Jetpack AppFunctions 1.0.0-beta01](https://developer.android.com/jetpack/androidx/releases/appfunctions) was released October 21, 2026. Google describes discovering and invoking typed app operations from authorized AI agents. That is a meaningful adjacent opportunity, but it reverses the normal AYA direction: the assistant **acts on the host**. Merely exposing `getSelectedMedia` or `openArtworkPicker` can disclose private data or perform consequential operations. AppFunctions is not needed for any existing AYA workflow.

**Decision:** document an optional, separately versioned adapter for future consideration; do **not** add the AppFunctions dependency, permission declarations, manifest services, or executable functions to AYA core yet. Implementation gate requires at least one eligible assistant on a real Android target, documented access and authorization controls, data/scope consent, comprehensive policy for read-only versus mutation actions, API stability review, and independent test coverage. No assumption that beta release means universally callable assistant functions.

Potential eventual opt-in names: `readPublicArtworkRequirements()` and `openArtworkEditor()`. These are examples, not implemented functions or promised APIs. Ensure the host developer chooses every exposed operation; do not derive executable operations automatically from AYA-RAS documentation.

## ACTION_PROCESS_TEXT

Android [ACTION_PROCESS_TEXT](https://developer.android.com/reference/android/content/Intent#ACTION_PROCESS_TEXT) processes selected text, including a possible replacement result. It is designed for text-selection targets and processing actions, not universally for launching an external AI conversation with a large guide. Inbound processing in AYA would make AYA a selectable text tool; it would still need a host identity/reference and an explicit user review. Outbound targeting requires an actually declared receiver; it cannot be assumed from a generic AI app.

**Decision:** keep this as optional research, with manual receiver contract tests before implementing. No text-replacement callback or replacement-of-selected-text behaviour will be inserted into AYA's existing help/creative share path.

## Local inference providers

An AI app using an on-device model is simply another eligible share target **if** it implements a compatible Android receiver. AYA will not download or host models, connect to unauthorized localhost APIs or require cloud credentials. Standard Sharesheet and Copy fallback already serve the provider-neutral goal.

## Evidence requirement

Keep declared Android affordances, documented provider capabilities, and manually reproduced real-app ingestion separate, as recorded in [capability evidence model](RECIPIENT_CAPABILITIES.md). No AYA backend, monitoring service, or runtime agent-output instrumentation.
