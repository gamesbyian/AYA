using Aya.Handoff;
using UnityEditor;
using UnityEngine;

namespace Aya.Handoff.Editor
{
    [CustomEditor(typeof(AyaUnityHelpButton))]
    public sealed class AyaUnityHelpButtonEditor : UnityEditor.Editor
    {
        public override void OnInspectorGUI()
        {
            EditorGUILayout.HelpBox(
                "AYA works only in compiled Android builds with the exact-version " +
                "host guide and staged native AARs. This component is an action: " +
                "your UI must visibly display the description, offered attachment " +
                "and instructions for using the assistant's answer. It never " +
                "monitors replies or imports generated files.",
                MessageType.Info);
            DrawDefaultInspector();
            if (EditorUserBuildSettings.activeBuildTarget != BuildTarget.Android)
            {
                EditorGUILayout.HelpBox(
                    "The Unity Editor and non-Android players reject AYA help locally.",
                    MessageType.Warning);
            }
        }
    }
}
