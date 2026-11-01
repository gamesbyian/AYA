# App Inventor v206 bundles an older AndroidX annotation artifact.
# Newer annotations used only for compilation may not be available there.
-dontwarn androidx.annotation.**

# Provider and share receiver are Android-manifest entry points. AAR/Rush
# manifest integration must retain them as well as the host's public blocks.
-keep class dev.aya.android.AyaFileProvider { *; }
-keep class dev.aya.android.AyaShareSelectionReceiver { *; }
