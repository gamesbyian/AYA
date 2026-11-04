#!/usr/bin/env bash
# Exact-source test-only emulator script. Run independent instrumented packages
# in separate transactions: a foreign-share Activity can retain focus while
# Espresso starts sample host tests. Never relax test assertions or silently
# mask a failing application.
set -euo pipefail

show_evidence() {
  echo "::group::Bounded external-receiver emulator evidence"
  adb logcat -d -v brief -s AYA_URI_QA:I ActivityTaskManager:W AndroidRuntime:E '*:S' | tail -n 160 || true
  echo "::endgroup::"
}
trap 'show_evidence' ERR

gradle :qa-external-receiver:installDebug --no-daemon --stacktrace
echo "::group::AYA library and real cross-UID URI grant tests"
gradle :aya:connectedDebugAndroidTest --no-daemon --stacktrace
echo "::endgroup::"

# Terminate the independently installed synthetic recipient explicitly.
# Reset focus to Launcher before a completely new host test process starts.
# No app data or content URIs are deleted, and the sample suite must still
# independently pass all its exact UI and lifecycle assertions.
adb shell am force-stop dev.aya.qa.receiver
adb shell input keyevent KEYCODE_HOME
adb shell input keyevent KEYCODE_BACK || true
sleep 2
echo "::group::Sample host reviewed handoff UI tests"
gradle :sample:connectedDebugAndroidTest --no-daemon --stacktrace
echo "::endgroup::"
echo "Android library, separate UID, and sample instrumentation passed."
