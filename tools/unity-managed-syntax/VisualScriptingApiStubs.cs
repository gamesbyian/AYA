// Only compilation/flow smoke stand-ins; NEVER evidence of Unity Editor APIs.
using System;

namespace Unity.VisualScripting
{
    [AttributeUsage(AttributeTargets.Class)]
    public sealed class UnitCategoryAttribute : Attribute
    {
        public UnitCategoryAttribute(string category) { }
    }

    [AttributeUsage(AttributeTargets.Class)]
    public sealed class UnitTitleAttribute : Attribute
    {
        public UnitTitleAttribute(string title) { }
    }

    [AttributeUsage(AttributeTargets.Field | AttributeTargets.Property)]
    public sealed class DoNotSerializeAttribute : Attribute { }

    public sealed class ValueInput
    {
        public readonly string Key;
        public ValueInput(string key) { Key = key; }
    }

    public sealed class ControlOutput
    {
        public readonly string Key;
        public ControlOutput(string key) { Key = key; }
    }

    public sealed class Flow
    {
        public object Value;
        public T GetValue<T>(ValueInput input)
        {
            if (input == null || input.Key != "card")
                throw new InvalidOperationException("Unexpected graph port");
            return (T)Value;
        }
    }

    public sealed class ControlInput
    {
        public readonly string Key;
        public readonly Func<Flow, ControlOutput> Action;
        public ControlInput(string key, Func<Flow, ControlOutput> action)
        {
            Key = key;
            Action = action;
        }
    }

    public abstract class Unit
    {
        protected abstract void Definition();
        protected ControlInput ControlInput(string key, Func<Flow, ControlOutput> action)
            => new ControlInput(key, action);
        protected ControlOutput ControlOutput(string key) => new ControlOutput(key);
        protected ValueInput ValueInput<T>(string key) => new ValueInput(key);
        protected void Requirement(ValueInput source, ControlInput destination) { }
        protected void Succession(ControlInput source, ControlOutput destination) { }
        public void InitializeTestOnly() => Definition();
    }
}
