# AYA native API compatibility and guide-variant policy

**Status: source-preview policy, not a stable public SDK release.** The
current default Maven coordinate is `dev.aya:aya-android:0.1.0-SNAPSHOT`;
`aya-compose` and the framework adapters are optional. CI can stage a
non-SNAPSHOT versioned preview for manual testing. There is no Maven Central
or npm release, no guarantee of future binary compatibility for snapshots,
and no automatic update service.

## Entry points and compatibility responsibilities

| API surface | Intended role | Compatibility policy |
|---|---|---|
| `Aya.ask(activity, AyaRequest)` | Developer-supplied in-memory guide followed by local question editing | **Legacy/manual**. Retained for source consumers, but cannot prove the request corresponds to the installed APK. No automatic version guard. Not recommended for new integrations. |
| `Aya.launch(activity, AyaRequest)` | Developer-supplied in-memory request, local editable review | **Legacy/manual**. Retained for source consumers; subject to host-owned guide accuracy. Does not check the installed version. |
| `Aya.launchBundled(activity, guideAsset, screenName, question, askQuestion)` | Preferred help and reference handoff | Runtime reads the supplied APK asset and rejects mismatched app ID, version, missing reference or malformed structure **before** opening local UI. |
| `Aya.launchCreativeBundled`, `Aya.launchTranslationBundled`, `Aya.launchFilesystemBundled` | Optional capability-specific handoffs | Preserve the same exact-version reference guard plus each module's independent task/kit requirements. Host-generated outputs remain untrusted. |
| `AyaComponentAction.Help` and related typed actions | Compose, Views, Flutter, Expo, Godot and Unity integration bridge | Must delegate to the guarded bundled APIs. No direct Sharesheet, backend, provider-specific shortcuts or assistant reply tracking. |
| `AyaBundledLaunchResult` | Local caller status | `QuestionOpened`, `PreviewOpened`, `Rejected` are **local UI states**, never evidence of recipient ingestion, AI response or completed import. |

Manual `Aya.ask` and `Aya.launch` are **not presently annotated
`@Deprecated`**. This policy is advisory, not a surprise compile warning
or runtime failure for existing adopters. Do not remove or silently redirect
them in a preview patch. A future breaking-release proposal must document
migration steps, publish actual artifact evidence, define an explicit
compatibility window, and test downstream source/binary consumers before
introducing deprecation warnings or removals. No removal date is promised.

**Versioning:** while the SDK is unpublished, `-SNAPSHOT` is mutable
development evidence and `-preview.N` is an immutable *intended* trial
coordinate only when its generated AAR/POM, checksums and consuming host
tests have actually been recorded. A stable `1.0.0` should require an
explicit release decision, signed provenance, documented dependencies and
dated device accessibility/receiver observations. Avoid claiming binary
compatibility between different versions merely because Kotlin sources
compile. Publish core and optional adapters as a reviewed compatibility
set and keep all core coordinates exactly aligned.

## Exact-version, variant and locale selection

AYA-RAS v1 identifies `app_id`, `app_version_min`,
`app_version_max`, `platform`, `locale`, `source_revision` and
other provenance. The **runtime** currently enforces app ID, Android
platform, nonblank provenance, 12 sections and an exact match of both
version bounds to the installed `versionName`. It **does not** assert that
`locale` equals the Android device locale, detect the host's feature flags,
check a document hash against source, or choose the correct asset
automatically. A valid but semantically incorrect same-package/version
guide can still be harmful. Independent build-time source audits and host
acceptance remain mandatory.

A developer may pass a different **bundled** `guideAsset` to
`Aya.launchBundled`. This is host-owned selection, not a global AYA
language resolver. Safe release procedure:

1. Source-inventory each APK product flavor/variant and locale separately.
   Use a distinct, safe asset path for each installed release-specific guide
   (for example `aya-guide-en.md` and `aya-guide-fr.md`), or package only
   the single applicable guide in each variant. Asset names are examples,
   never a required folder structure.
2. Generate and audit each guide from *that variant's* actual UI,
   capabilities, locale and exact installed `versionName`. Its metadata
   must match the real APK ID/version; a fallback guide for another variant
   must not be substituted just to satisfy the guard.
3. The **host** resolves the currently active language/variant through its
   normal settings and passes the corresponding asset explicitly. If the
   required guide is absent, stale, untranslated or not verified, reject the
   handoff and show a useful local explanation. Never silently pick a
   mismatched-language guide or infer truth from its file name.
4. For translation/filesystem modules, select independently source-audited
   kits matching the same host identity/version and target capabilities.
   A locale-specific help guide cannot establish that an output-import
   schema or task executor exists.
5. Inspect the final APK bytes, installed package/version, merged manifest
   and source traceability for **every supported shipped variant**.
   Test failures, stale assets, wrong-locale selection and Copy fallback
   on real Android as separate acceptance gates.

If supporting a variant matrix would require runtime validation of
`locale`, feature identifiers or source revisions, propose an AYA-RAS
v2 schema/verification API as a separately versioned change with migration
tests. Do not smuggle it into v1 or claim it already exists.

## Release and evidence obligations

For a preview: deterministic AAR/POM build, pinned dependency coordinates,
source-derived install guide, independent consumer APK with exact reference,
manifest/DEX inspection, checksum inventory and a record of known
unverified behaviors. For general availability: external host onboarding,
Android version and accessibility matrix, verified Copy/Share, dated
recipient-specific attachment ingestion, defined upstream dependency
maintenance policy and explicit signing/provenance decisions. No host's
successful build, choice of assistant, or visible Sharesheet proves
assistant reception.

See [Versioned Maven previews](components/DISTRIBUTION.md),
[Module Portability](MODULE_PORTABILITY.md) and
[Native integration](INTEGRATION.md).
