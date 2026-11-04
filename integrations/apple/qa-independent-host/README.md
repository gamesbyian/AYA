# Second native iOS host for the root AYA Swift Package

**Status:** standalone fictional QA source fixture, not a production app, public App Store release, AI-recipient test or certified third-party adoption. An independent host implementation and installed-simulator test still require the exact-head [Apple CI run](../../../.github/workflows/apple-independent-host.yml).

This example deliberately exercises a *different kind of host* from the original Lantern layout sample: a simple, temporary reading-queue counter, a real AYAHelpCard, and **no import action**. It has a distinct iOS app ID `org.example.aya.readerqa`, version `0.1.0`, source-derived bundle guide and test target. The source owns the fictional UI, not any other project.

Crucially, `project.yml` uses **`packages: AYA: path: ../../..`**, pointing to the **repository root** Swift Package manifest added in #140. It integrates `AYAApple` by public product and module name, rather than reaching into its internal Swift source files or using the nested `integrations/apple/AYAApple` development manifest. This demonstrates the ordinary dependency boundary locally, but does not yet certify remote Git resolution on a macOS consumer.

CI must:
1. Validate the synthetic guide against the iOS AYA-RAS authoring profile.
2. Compile the independent app through XcodeGen using the root AYA SwiftPM product, with an authentic iOS SDK.
3. Inspect the built app for the exact source guide bytes, installed bundle ID and version.
4. Install and launch the **actual** app in an iPhone Simulator; tap its own Add sample title control, open AYA review, verify its **own** guide and Cancel without mutation.
5. Reject absence of native module linkage, missing guide, inherited Lantern content, a fake import button or nonexistent interactive consent screen.

No account, network permission, model/backend integration, receiver tracking, cross-sandbox import, or source hook into user projects is introduced. Actual independent *external adopter* and real AI provider acceptance remain distinct future gates. See [Apple distribution guide](../../../docs/apple/DISTRIBUTION.md).
