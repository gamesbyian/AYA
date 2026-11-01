package dev.aya.android

import androidx.core.content.FileProvider

/**
 * AYA-owned provider identity for reviewed one-file Android Sharesheet handoffs.
 *
 * Each library must declare its own concrete provider class: Android manifest
 * merging matches provider nodes by android:name. Declaring FileProvider
 * directly would merge AYA's authorities/path metadata with unrelated host
 * FileProviders (including Godot's), breaking both instead of safely sharing.
 *
 * FileProvider's existing canonical-path and temporary URI-grant checks remain
 * in force. Do not override getUriForFile, openFile, query or attachInfo here.
 */
class AyaFileProvider : FileProvider()
