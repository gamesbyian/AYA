# Final APK verification for multiple Android FileProviders

**Purpose:** prevent apparently successful integration builds from replacing an adopter's FileProvider, widening AYA's shared file paths or confusing two providers' authorities. An Android library's manifest is merged into the host application, and that merger keys providers by their class name, so generic `androidx.core.content.FileProvider` declarations in multiple libraries can collide even when they use different authorities.

AYA declares its own concrete `dev.aya.android.AyaFileProvider` subclass with `${applicationId}.aya.files`, `exported=false`, temporary URI grants and `@xml/aya_file_paths`. Other engines and host apps may declare their *own* providers and separate authorities.

## Exact binary inspection

Run `tools/verify_android_manifest_providers.py` on the **final built APK**, after compiling both host and library with their actual Android manifest merge:

```sh
python3 tools/verify_android_manifest_providers.py \
  --apk path/to/app-debug.apk --aapt /path/to/android-sdk/build-tools/35.0.0/aapt \
  --provider dev.aya.android.AyaFileProvider=dev.example.host.aya.files \
  --provider androidx.core.content.FileProvider=dev.example.host.fileprovider
```

The host provider class above is an example only; the real host can use any independently named provider subclass. Use the *actual* installed app ID and actual declared authorities, never a guessed `applicationId`. The verifier reads Android SDK `aapt dump xmltree` output, pairs **each direct application's `<provider>`** with its own class, authority, explicit non-export flag, URI-grant flag and child `FILE_PROVIDER_PATHS` resource, and rejects duplicate classes/authorities, missing providers, accidental exposure, missing paths and cross-element decoys.

This is a packaging check only. The validator verifies that **a** scoped XML resource is referenced under the right provider; a separate source audit and device test must establish that the resource's path list is correctly restricted to the intended AYA cache directory. It cannot prove that the recipient can read the URI, that an Android Activity starts, or that ChatGPT, Claude, Gemini or another assistant ingests the file.

On Android, separately test `ContentResolver.openInputStream()`, non-exported provider identity, URI grant lifetimes, denied out-of-scope files, and concurrent host/AYA shares. Never silence manifest conflicts by adding `tools:replace="android:authorities"` or `tools:replace="android:resource"`, because that would erase one component's settings rather than allow both to coexist.

Offline negative fixtures are covered by `python3 -m unittest discover -s tools -p 'test_verify_android_manifest_providers.py'`. Native APK and on-device evidence remain independent.
