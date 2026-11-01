using System;
using Aya.Handoff;
using Aya.Handoff.VisualScripting;
using Unity.VisualScripting;

internal static class VisualScriptingSmokeMain
{
    public static int Main()
    {
        var unit = new AyaOpenReviewedHelpUnit();
        unit.InitializeTestOnly();
        if (unit.enter == null || unit.returned == null || unit.card == null)
            throw new Exception("AYA graph action ports must be explicit");
        if (unit.enter.Key != "enter" || unit.returned.Key != "returned" ||
            unit.card.Key != "card")
            throw new Exception("AYA graph ports changed unexpectedly");

        // A missing host component is inert. Continuing synchronous graph
        // flow must never claim a review opened or a recipient received data.
        var next = unit.enter.Action(new Flow { Value = null });
        if (!Object.ReferenceEquals(next, unit.returned))
            throw new Exception("Expected exactly the local returned flow");

        // A host component with no description/disclosure/output-use copy
        // must refuse before any Android JNI operation.
        var host = new AyaUnityHelpButton();
        next = unit.enter.Action(new Flow { Value = host });
        if (!Object.ReferenceEquals(next, unit.returned))
            throw new Exception("Invalid host was not handled locally");

        // The real Unity package uses local-status events for asynchronous
        // results. The graph action has no callback into assistant replies.
        return 0;
    }
}
