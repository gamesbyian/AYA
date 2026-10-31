using System;
using System.Threading;
using UnityEngine;

namespace Aya.Handoff
{
    [Serializable]
    public sealed class AyaLocalResult
    {
        public string status;
        public string reason;
    }

    /// <summary>
    /// Android-only, one-way AYA help action for host Buttons and visual graphs.
    /// A callback reports local review/question UI opening or rejection only.
    /// There is NEVER a callback for assistant receipt, replies or imported output.
    /// </summary>
    public static class AyaAndroidHelp
    {
        private const string NativeBridge = "dev.aya.unity.AyaUnityBridge";

        private static AyaLocalResult Rejected(string message)
        {
            return new AyaLocalResult { status = "rejected", reason = message };
        }

        public static void OpenHelp(
            string question,
            string guideAsset,
            string screenName,
            Action<AyaLocalResult> onLocalResult,
            bool? askQuestion = null)
        {
            if (string.IsNullOrEmpty(guideAsset) ||
                !System.Text.RegularExpressions.Regex.IsMatch(
                    guideAsset, @"^[A-Za-z0-9_-]+(?:/[A-Za-z0-9_-]+)*\.md$"))
            {
                onLocalResult?.Invoke(Rejected("Provide a safe, bundled AYA guide path."));
                return;
            }
            bool showComposer = askQuestion ?? (question == null);
#if UNITY_ANDROID && !UNITY_EDITOR
            // Capture Unity's synchronization context before crossing to
            // Android's UI thread; callbacks must return to Unity's main thread.
            var unityContext = SynchronizationContext.Current;
            if (unityContext == null)
            {
                onLocalResult?.Invoke(Rejected("Call AYA from the Unity main thread."));
                return;
            }

            AndroidJavaObject activity = null;
            try
            {
                using (var player = new AndroidJavaClass("com.unity3d.player.UnityPlayer"))
                {
                    activity = player.GetStatic<AndroidJavaObject>("currentActivity");
                }
                if (activity == null)
                {
                    onLocalResult?.Invoke(Rejected("An active Android Activity is required."));
                    return;
                }
                var retainedActivity = activity;
                activity.Call("runOnUiThread", new AndroidJavaRunnable(() =>
                {
                    AyaLocalResult result;
                    try
                    {
                        using (var bridge = new AndroidJavaClass(NativeBridge))
                        {
                            string raw = bridge.CallStatic<string>(
                                "openHelp",
                                retainedActivity,
                                guideAsset,
                                screenName,
                                question ?? "",
                                showComposer);
                            result = ParseLocalResult(raw);
                        }
                    }
                    catch (Exception)
                    {
                        result = Rejected("AYA native review could not open.");
                    }
                    finally
                    {
                        retainedActivity.Dispose();
                    }

                    try
                    {
                        unityContext.Post(_ => onLocalResult?.Invoke(result), null);
                    }
                    catch (Exception)
                    {
                        // Unity is shutting down; do not invent a result or
                        // retry any user-facing action on another thread.
                    }
                }));
                activity = null; // Runnable owns this Java reference now.
            }
            catch (Exception)
            {
                activity?.Dispose();
                onLocalResult?.Invoke(Rejected("AYA Android bridge is unavailable."));
            }
#else
            onLocalResult?.Invoke(Rejected(
                "AYA Android help is unavailable in the Unity Editor and non-Android builds."));
#endif
        }

        private static AyaLocalResult ParseLocalResult(string json)
        {
            if (string.IsNullOrEmpty(json))
                return Rejected("Empty AYA native status.");
            try
            {
                var value = JsonUtility.FromJson<AyaLocalResult>(json);
                if (value == null)
                    return Rejected("Malformed AYA native status.");
                if (value.status == "review_opened" || value.status == "question_opened")
                    return new AyaLocalResult { status = value.status };
                if (value.status == "rejected")
                    return Rejected(string.IsNullOrEmpty(value.reason)
                        ? "AYA native request was rejected."
                        : value.reason);
                return Rejected("Unknown local AYA status.");
            }
            catch (Exception)
            {
                return Rejected("Invalid AYA native status.");
            }
        }
    }
}
