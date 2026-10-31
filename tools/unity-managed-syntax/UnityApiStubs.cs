// Tiny *testing-only* signatures. They do not establish real Unity API compatibility.
using System;

namespace UnityEngine
{
    [AttributeUsage(AttributeTargets.Field)]
    public sealed class SerializeField : Attribute { }
    [AttributeUsage(AttributeTargets.Field)]
    public sealed class TextAreaAttribute : Attribute
    {
        public TextAreaAttribute(int min, int max) { }
    }
    [AttributeUsage(AttributeTargets.Field)]
    public sealed class TooltipAttribute : Attribute
    {
        public TooltipAttribute(string message) { }
    }
    public class MonoBehaviour { }
    public static class JsonUtility
    {
        public static T FromJson<T>(string value) { return default(T); }
    }
    public delegate void AndroidJavaRunnable();
    public class AndroidJavaObject : IDisposable
    {
        public void Dispose() { }
        public void Call(string name, params object[] args) { }
        public T Call<T>(string name, params object[] args) { return default(T); }
        public T GetStatic<T>(string name) { return default(T); }
    }
    public sealed class AndroidJavaClass : AndroidJavaObject
    {
        public AndroidJavaClass(string name) { }
        public T CallStatic<T>(string name, params object[] args) { return default(T); }
    }
}
namespace UnityEngine.Events
{
    public class UnityEvent<TFirst, TSecond>
    {
        public void Invoke(TFirst first, TSecond second) { }
    }
}
namespace UnityEditor
{
    [AttributeUsage(AttributeTargets.Class)]
    public sealed class CustomEditor : Attribute
    {
        public CustomEditor(Type targetType) { }
    }
    public class Editor
    {
        public virtual void OnInspectorGUI() { }
        protected void DrawDefaultInspector() { }
    }
    public enum MessageType { Info, Warning }
    public enum BuildTarget { Android, StandaloneWindows64 }
    public static class EditorUserBuildSettings
    {
        public static BuildTarget activeBuildTarget;
    }
    public static class EditorGUILayout
    {
        public static void HelpBox(string text, MessageType type) { }
    }
}
