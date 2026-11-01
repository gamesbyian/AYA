using Unity.VisualScripting;

namespace Aya.Handoff.VisualScripting
{
    /// <summary>
    /// Optional AYA action node. "Returned" means the host action method
    /// returned synchronously; it NEVER means that a model received a prompt
    /// or that the local Android review opened.
    ///
    /// The referenced host component enforces visible description, attachment
    /// disclosure and answer-use instructions, and delegates exclusively to
    /// the installed-version-guarded Android AYA bridge.
    /// </summary>
    [UnitCategory("AYA/Help")]
    [UnitTitle("Request Reviewed Help")]
    public sealed class AyaOpenReviewedHelpUnit : Unit
    {
        [DoNotSerialize] public ControlInput enter;
        [DoNotSerialize] public ControlOutput returned;
        [DoNotSerialize] public ValueInput card;

        protected override void Definition()
        {
            returned = ControlOutput("returned");
            card = ValueInput<AyaUnityHelpButton>("card");
            enter = ControlInput("enter", flow =>
            {
                AyaUnityHelpButton host = flow.GetValue<AyaUnityHelpButton>(card);
                if (host != null)
                    host.OpenHelp();
                // No success output: host.onLocalStatus reports only local
                // question/review opening or rejection asynchronously.
                return returned;
            });
            Requirement(card, enter);
            Succession(enter, returned);
        }
    }
}
