# Versioned native AYA Maven previews

**Status:** an explicit, manual **unpublished preview workflow**, not a public release or a new hosted AYA service. AYA still has no backend, model, API key, response tracking or licence requirement.

AYA's native AARs form a single compatibility set: `dev.aya:aya-android` and optional `dev.aya:aya-compose`. The source checkout defaults to `0.1.0-SNAPSHOT`. Set `-Paya.version=<semver>` on both the build and the consumer to construct a consistent, independently named staged Maven repository. The module's generated POM must declare Compose's dependency on the same `aya-android` version.

## Build a non-production preview

From a checkout:

```sh
gradle :aya:testDebugUnitTest :aya:assembleRelease :aya-compose:assembleRelease \
  :aya:publishReleasePublicationToStagingRepository \
  :aya-compose:publishReleasePublicationToStagingRepository \
  -Paya.version=0.1.0-preview.1 --no-daemon

python3 tools/validate_staged_maven.py \
  --root aya/build/staging-maven --version 0.1.0-preview.1 \
  --checksum-output aya-staging-sha256.txt

gradle :sample:assembleDebug -Paya.consumePublished=true \
  -Paya.version=0.1.0-preview.1 --no-daemon
```

Alternatively, use GitHub Actions **Versioned AYA Maven preview (manual, unpublished)** with an explicit version input. It stages, validates and uploads the Maven directory plus SHA-256 checksums as a GitHub Actions artifact. This workflow has **read-only contents permissions and never publishes a GitHub release, changes the default branch, pushes a Maven registry or enables GitHub Pages**. Its output is temporary build evidence, not a stable public dependency source. Compare checksums independently and pin versions.

## Public API compatibility and locale/variant policy

Read the [native API compatibility policy](../API_COMPATIBILITY.md) before adopting a staged preview. It distinguishes the legacy/manual `Aya.ask` and `Aya.launch` entry points from guarded `Aya.launchBundled` and typed component actions; source availability or a staged Maven coordinate does not imply binary stability. For multiple locales, flavors or feature variants, hosts must source-audit and explicitly select their own exact-installed-version APK guides. AYA-RAS v1 does **not** choose the device locale or establish variant truth automatically.

## Why distribution is still blocked

Do not advertise the Flutter source plugin or FlutterFlow templates as one-click installable: they require the native `aya-android` coordinate to resolve from a suitable repository. The manual preview is only a preparation step. A public Maven-compatible repository, versioned tags, supply-chain provenance, and a real host build with an APK-level matching AYA-RAS guide must be reviewed before a release. Physical-device, 200% font/TalkBack and recipient-specific testing are separate gates.

The sample app only proves that the staged AAR/POM pair is consumer-compatible in a controlled Gradle environment. It does not certify any external AI app's handling of the approved document or any host's generated-file importer.
