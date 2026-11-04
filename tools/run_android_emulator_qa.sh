#!/usr/bin/env bash
# Exact-source test-only emulator script. The runner invokes this as one
# command so conditionals remain intact and native failures are never masked.
set -euo pipefail
gradle :qa-external-receiver:installDebug --no-daemon --stacktrace

if gradle :aya:connectedDebugAndroidTest :sample:connectedDebugAndroidTest --no-daemon --stacktrace; then
  echo "Android instrumentation finished successfully."
else
  echo "::group::Bounded external-receiver emulator evidence"
  # Synthetic CI emulator only. Filter to QA metadata and Android activity
  # errors, never dump the referenced text, entire logcat or user content.
  adb logcat -d -v brief -s AYA_URI_QA:I ActivityTaskManager:W AndroidRuntime:E '*:S' | tail -n 160 || true
  echo "::endgroup::"
  exit 1
fi
