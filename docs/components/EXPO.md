# AYA Expo Android guide prebuild helper (source preview)

**Status:** a small, optional Expo CNG guide-asset plugin with offline Node safety tests. This is NOT a released React Native native module, an Expo Go integration, a published npm package, or verified native APK export. It solves one prerequisite for a future Expo module: packaging a host-authored, exact-version AYA-RAS reference in native Android APK assets.

## Why this exists

The canonical AYA Android SDK reads `Activity.assets.open("aya-guide.md")`. Merely adding the guide to Expo's JavaScript assets will **not** guarantee it appears as a native Android asset. The host app also must identify itself by the actual installed Android package name and versionName. A missing/stale guide must cause the native AYA review to refuse rather than share misleading instructions.

The [Expo config-plugin documentation](https://docs.expo.dev/modules/config-plugin-and-native-module-tutorial/) confirms that Android prebuild plugins can prepare native project resources. This source preview uses an Android-only `withDangerousMod` copy because it writes a native asset file. [Expo warns](https://docs.expo.dev/config-plugins/dangerous-mods/) that dangerous mods require special idempotency and update testing; the helper explicitly records a plugin-owned SHA-256 provenance marker and refuses unrelated file overwrites.

## Usage in a source checkout

Copy `integrations/expo/guide-plugin/` into a trusted folder inside your Expo project, e.g. `plugins/aya-guide/`. Complete an independent host app model, strict AYA-RAS reference, source inventory and held-out questions. Store the **host's own** guide at `support/aya-guide.md`, inside the Expo project. Never copy the sample's guide, and do not expose app credentials.

For an app with Expo config:

```json
{
  "expo": {
    "name": "Your App",
    "slug": "your-app",
    "version": "1.0.0",
    "android": { "package": "com.example.yourapp" },
    "plugins": [
      ["./plugins/aya-guide/app.plugin.js", { "guidePath": "support/aya-guide.md" }]
    ]
  }
}
```

Make `app_id` equal to `android.package` and both `app_version_min` and `app_version_max` equal to the exact Android **versionName** that will be built. The prebuild hook rejects mismatch and unresolved reference placeholders.

Run `npx expo prebuild --platform android` only after the package's real Android SDK dependency and chosen Expo module integration are set up. The helper writes `android/app/src/main/assets/aya-guide.md` and a plugin-owned provenance record at `android/app/.aya-guide-prebuild.json`. It never edits an existing application manifest, installs SDK dependencies, creates a model, or sends messages.

Repeated identical prebuilds are idempotent. Changing the source guide is allowed if the previously installed native file still matches the plugin's recorded hash. A foreign/tampered destination or provenance file causes a visible failure, requiring deliberate reconciliation; never silently overwrite a user's unrelated assets. Symlink escapes, path traversal, missing/mismatched guides and invalid UTF-8 fail closed.

## What still must be proven

- A complete Expo development-build/prebuild Android project, with native AYA module and staged/published AAR, must compile.
- A built APK's package ID/version, guide bytes and FileProvider declaration must be independently inspected, as for the Flutter host contract.
- Real-device Activity lifecycle, rotation, keyboard, TalkBack, 200% fonts, recipient behavior and Copy/Share flow remain separately unverified.
- Expo Go cannot load arbitrary custom native code; use a compiled native development build or exported APK. iOS and web exports have no AYA Android handoff.

Tests: `node --test integrations/expo/guide-plugin/test/*.test.cjs`. These are structural, filesystem and identity negative controls, not an Expo editor acceptance certificate.
