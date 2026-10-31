using System;
using UnityEngine;
using UnityEngine.Events;

namespace Aya.Handoff
{
    [Serializable]
    public sealed class AyaLocalStatusEvent : UnityEvent<string, string> { }

    /// <summary>
    /// Attach this component to a GameObject and assign OpenHelp to a UI Button.
    /// The host must display description, disclosure and output-use copy itself.
    /// </summary>
    public sealed class AyaUnityHelpButton : MonoBehaviour
    {
        [SerializeField] private string guideAsset = "aya-guide.md";
        [SerializeField] private string screenName = "";
        [TextArea(2, 5)] [SerializeField] private string description = "";
        [TextArea(2, 5)] [SerializeField] private string attachmentDisclosure = "";
        [TextArea(2, 5)] [SerializeField] private string outputInstructions = "";

        [Tooltip("Enable only if your host displays a question input linked to SetQuestionText.")]
        [SerializeField] private bool hostHasQuestionField = false;

        [NonSerialized] private string questionText = "";
        [NonSerialized] private bool pending;
        public AyaLocalStatusEvent onLocalStatus = new AyaLocalStatusEvent();

        public void SetQuestionText(string text)
        {
            questionText = text ?? "";
        }

        public void OpenHelp()
        {
            if (pending) return;
            if (string.IsNullOrWhiteSpace(description) ||
                string.IsNullOrWhiteSpace(attachmentDisclosure) ||
                string.IsNullOrWhiteSpace(outputInstructions))
            {
                onLocalStatus?.Invoke("rejected",
                    "Provide visible host-specific description, attachment and answer-use instructions.");
                return;
            }
            pending = true;
            AyaAndroidHelp.OpenHelp(
                hostHasQuestionField ? questionText : null,
                guideAsset,
                screenName,
                result =>
                {
                    pending = false;
                    if (this == null) return;
                    onLocalStatus?.Invoke(result.status, result.reason ?? "");
                });
        }
    }
}
