# MIT App Inventor and Kodular: Android-only AYA block prototype

**Status:** source prototype, with a proposed real `.aix` compiler gate. App Inventor/Kodular-consuming APKs, exact raw app assets, receiving assistants and editor/companion behaviour are **not yet verified**. It is an optional implementation of the AYA handoff convention and is not required to use the idea.

## The technical opportunity

[MIT App Inventor](https://appinventor.mit.edu/) extensions are non-visible blocks that can be attached to a host-created layout. The [Rush 2.1.2 extension builder](https://github.com/shreyashsaitwal/rush-cli/tree/v2.1.2) supports Maven/local Android AARs, binary resources and merged Android manifests when building an extension against App Inventor v206. This is a substantial change from older extension toolchains that could not reliably package native Android AARs. See the [official Rush dependency](https://github.com/shreyashsaitwal/rush-cli/blob/v2.1.2/docs/dependencies.md), [manifest](https://github.com/shreyashsaitwal/rush-cli/blob/v2.1.2/docs/manifest.md) and [writing extension](https://github.com/shreyashsaitwal/rush-cli/blob/v2.1.2/docs/writing-extensions.md) documentation.

The AYA prototype uses only canonical `AyaComponentAction.Help`, a Java `@Extension` class and three public App Inventor block surfaces:

- `HostIdentity()` returns this **installed app's actual package@version**, which the developer can use for an exact AYA-RAS guide.
- `OpenHelp(guideAsset, screenName, question)` verifies a safe relative Markdown asset path, invokes the canonical guarded Android AYA review and delegates **all** actual identity/guide validation to the AYA SDK. A blank question is a valid host-supplied input, so no duplicate composer is required.
- `LocalStatus(status, reason)` fires **only** for local `review_opened`, `question_opened` or `rejected`. It cannot report that the receiving AI read the document, generated an answer or saved a file.

See the [actual Rush project](../../integrations/app-inventor/aya-rush/README.md) for source and detailed host integration instructions.

## Verified shape of the actual Rush 2 AIX archive

A real [Rush 2.1.2 CI artifact](https://github.com/gamesbyian/AYA/actions/runs/41267356990) established that the generated `.aix` uses `dev.aya.appinventor/components.json`, `files/component_build_infos.json`, an outer `classes.jar` containing `classes.dex`, and a separately **relocated private native AYA AAR**. The resulting AAR contains canonical AYA's guarded help dispatcher, the scoped `AyaFileProvider`, share chooser receiver and `res/xml/` cache-path declaration under Rush's namespaced class/resource names. The extension's build-info manifest fragments register the provider and receiver for a future consuming package without requesting unrelated Android permissions.

The offline `tools/verify_appinventor_aix.py` therefore inspects **that actual binary shape after every Rush compilation**, rather than trusting source imports or the mere existence of a ZIP. It follows Android DEX `class_defs` for the public App Inventor component, verifies the three local-only block surfaces, the relocated AAR's compiled class entries and manifest, the matching provider/receiver build-info declarations, the scoped cache-path XML, and absence of added permissions. Synthetic positive and destructive negative-control fixtures run before the heavy build. This is still **S1 native archive packaging evidence**: only a genuine App Inventor-built host APK can prove whether App Inventor merges and loads those entries at runtime.

## Honest limits before distributing any AIX

1. The compiled AYA core AAR is staged from the same source checkout; it is not publicly distributed as a stable Maven dependency. Only a fresh, reproducible AIX build artifact from CI can qualify as a source preview.
2. Rush 2 reports that App Inventor v206 always provides an older AndroidX Core version. The AYA adapter cannot override that bundled version, so any AAR resolution/merge success must be followed by actual native runtime testing. The prototype does **not** require Jetpack Compose.
3. Rush 2 can private-repackage Kotlin/Android classes, resources and library manifests. The final **App Inventor-generated APK** must still be checked independently for AYA's scoped `AyaFileProvider` authority, chooser receiver, resource XML, installed package identity, exact guide asset bytes and defined DEX classes. No manifest override to hide conflicts is acceptable.
4. Extensions based on AARs are unsupported by the **live MIT AI Companion**, according to the Rush 2 documentation. Test a fully built Android app instead.
5. The consuming app **owns its real UI**. App Inventor extensions do not create drag-and-drop visible designer widgets. The host should display the standard AYA disclosure, optional question field, result-use instructions and accessible Ask button through its normal Arrangement/Labels/TextBox/Button blocks, and connect the button's Click block to `OpenHelp`.
6. Asset/media paths and the generated Android package name vary by adopting project. The developer must produce and bundle the host-specific guide for the **final installed version**, then verify that `Activity.assets.open()` can read it. No version wildcards, another project's packet or asset-path guesswork.
7. A success in Rush compiling a real `.aix` establishes only source packaging (S1). An App Inventor/Kodular-built actual APK (S2/S2+) and independent adopter, Android device, TalkBack/large fonts, manual user review/Copy/Share and recipient ingestion (S3-S5) remain independent.

**Next acceptance:** import the produced AIX into an actual MIT App Inventor v206 project, compile an APK against its own genuine AYA-RAS guide, inspect compiled provider/Dex/guide and test the reviewed local help handoff and safe Copy fallback. Repeat in Kodular separately; compatibility is not inherited from App Inventor.
