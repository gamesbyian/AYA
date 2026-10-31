using System;
using Aya.Handoff;

internal static class SmokeMain
{
    public static int Main()
    {
        // The host-neutral malformed-path guard must reject without JNI or
        // depending on a Unity Editor; this executes in both compile lanes.
        int called = 0;
        AyaAndroidHelp.OpenHelp(null, "../unsafe.md", "Test", result =>
        {
            called++;
            if (result.status != "rejected") throw new Exception("Unsafe path was not rejected.");
        });
        if (called != 1) throw new Exception("Expected exactly one local rejection.");
        // On editor or stubbed Android, there is no live Android Activity.
        called = 0;
        AyaAndroidHelp.OpenHelp(null, "aya-guide.md", "Test", result =>
        {
            called++;
            if (result.status != "rejected") throw new Exception("No native host should reject.");
        });
        if (called != 1) throw new Exception("Expected local unavailable-host rejection.");
        return 0;
    }
}
