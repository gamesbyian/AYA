# Independent-app iOS JSON return acceptance

**Candidate implementation:** [PR #162](https://github.com/gamesbyian/AYA/pull/162). This checks a *real* Apple system-mediated document handoff from one installed app to another, separate from the broken multi-document SwiftUI Files-picker gate in [PR #147](https://github.com/gamesbyian/AYA/pull/147). This is an executable test plan, not a declaration of success.

## What is being proved

1. Install the independent QA source `org.example.aya.shareqa` **and** the unrelated fictional Lantern host `org.example.ayalantern` on the same simulator/device.
2. Launch QA, tap **Prepare seven Files test documents** and verify its exact preparation acknowledgement. The QA app alone writes the synthetic files into its own Documents.
3. Under the QA source's **Synthetic document to send** selector choose `aya-layout-valid.json`, then tap **Share selected JSON with another app**. Apple's actual activity UI must appear with an appropriate **AYA Lantern** destination target; a synthetic direct call into Lantern is prohibited.
4. Select Lantern from the system UI, require the **receiving app** to show its own review with **Apply to demo**. The host stays one column/warm until the person cancels or applies. Cancel preserves state; select again through QA's actual system sharing UI and Apply changes the state to three columns/cool.
5. Repeat the system handoff after selecting `aya-layout-invalid.json`. Require a visible `Cannot use this file` host rejection, no Apply, unchanged layout. No automatic mutation even though the source asked another app to open JSON.

The QA source uses an iOS 16+ native `ShareLink(item:)` with a real file URL inside its own Documents. An earlier custom JSON `FileRepresentation` was also tested, but its native Share Sheet did not expose Lantern in the same runtime, while URL-sharing did. Apple documents that offered services depend on `Transferable` representations, so this choice remains evidence-driven rather than a universal rule. The incoming host must independently prove the transferred **file bytes**, not accept a link or displayed filename as successful delivery. The receiving app can be targeted only through Apple's UI and document registration. All byte snapshots, type/limit checks, review and Apply remain controlled by the receiving app. The AYA module never searches another app's sandbox or monitors user files.

## CI and human verification

The bounded [Apple genuine cross-app Open In handoff workflow](https://github.com/gamesbyian/AYA/actions/workflows/apple-open-in-independent-app.yml) generates and builds both Xcode projects on macOS, verifies Lantern's built `CFBundleDocumentTypes` advertises `public.json` and `LSSupportsOpeningDocumentsInPlace`, then installs Lantern before native QA-host UI tests on an iPhone simulator. Two independently expressed tests require the *actual* target selection and observable receiver behavior.

The system chooser is sometimes unstable. Distinguish failures precisely: missing target (Launch Services discovery), target selected but receiving app never launched (OS dispatch), app launched without preview (URL/permission/snapshot), and preview present but invalid content accepted (host validation). Preserve the real XCTest exit code, screenshots, and SHA-tagged diagnostics. **Do not** bypass a missing target by calling `.onOpenURL` directly or passing a test-owned `AYAImportFile`.

For signed-device acceptance, use a real iPhone/iPad and signing, keep the two app IDs independent, repeat both tests by tapping the system interface yourself, record exact iOS/build/host SHAs and provider. Include large-text and VoiceOver checks separately. A passing simulator shows an installed OS-to-OS handoff in that runtime; it does not establish physical-device compatibility or compatibility with ChatGPT, Claude, Gemini, Grok or another AI app.

**Gate separation:** a passing native ShareLink/Open In journey cannot replace the separate `.fileImporter` seven-file acceptance in #147; that failure remains documented in [the upstream reproduction](FILES_PROVIDER_UPSTREAM_REPORT.md). This test also cannot qualify in-flight provider cancellation or signed release packaging.
