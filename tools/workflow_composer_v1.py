"""Experimental AYA typed workflow v1 reference. No transport, UI, or agent API."""
from __future__ import annotations

from collections import defaultdict
from typing import Any

SECTIONS = ("objective", "operations", "constraints", "output")


class WorkflowV1Error(ValueError):
    """Malformed workflow, invalid answers, or unresolved task."""


def require(ok: bool, message: str) -> None:
    if not ok:
        raise WorkflowV1Error(message)


def keys(value: Any, allowed: set[str], label: str) -> None:
    require(isinstance(value, dict), f"{label} must be an object")
    require(not (set(value) - allowed), f"{label}: unknown fields {sorted(set(value) - allowed)}")


def refs(predicate: Any, questions: dict[str, dict[str, Any]]) -> set[str]:
    """Validate the deliberately small closed predicate language and return references."""
    keys(predicate, {"question", "equals", "contains", "all", "any", "not"}, "predicate")
    if "question" in predicate:
        require(set(predicate) in ({"question", "equals"}, {"question", "contains"}),
                "question predicate requires exactly equals or contains")
        qid = predicate["question"]
        require(isinstance(qid, str) and qid in questions, "unknown predicate question")
        q = questions[qid]
        if "contains" in predicate:
            require(q["kind"] == "multi" and type(predicate["contains"]) is str
                    and predicate["contains"] in q["options"], "invalid contains value")
        else:
            require(q["kind"] != "multi" and _valid_value(q, predicate["equals"]), "invalid equals value")
        return {qid}
    require(len(predicate) == 1, "predicate must specify exactly one operator")
    if "not" in predicate:
        return refs(predicate["not"], questions)
    op = "all" if "all" in predicate else "any" if "any" in predicate else ""
    require(bool(op) and isinstance(predicate[op], list) and bool(predicate[op]),
            "all/any needs a nonempty array")
    found: set[str] = set()
    for child in predicate[op]:
        found.update(refs(child, questions))
    return found


def _valid_value(q: dict[str, Any], value: Any, *, element: bool = False) -> bool:
    kind = q["kind"]
    if kind == "boolean":
        return type(value) is bool
    if kind == "choice":
        return type(value) is str and value in q["options"]
    if kind == "multi":
        if element:
            return type(value) is str and value in q["options"]
        return (isinstance(value, list) and len(value) == len(set(_hashable_strings(value)))
                and all(type(v) is str and v in q["options"] for v in value))
    return False


def _hashable_strings(values: list[Any]) -> list[str]:
    return [v if type(v) is str else repr(v) for v in values]


def _predicate_refs(predicate: dict[str, Any]) -> set[str]:
    if "question" in predicate:
        return {predicate["question"]}
    if "not" in predicate:
        return _predicate_refs(predicate["not"])
    children = predicate.get("all", predicate.get("any", []))
    return set().union(*(_predicate_refs(child) for child in children))


def _match(predicate: dict[str, Any] | None, state: dict[str, Any]) -> bool:
    if predicate is None:
        return True
    if "question" in predicate:
        qid = predicate["question"]
        if qid not in state:
            return False
        return (predicate["contains"] in state[qid] if "contains" in predicate
                else state[qid] == predicate["equals"])
    if "not" in predicate:
        return _predicate_refs(predicate["not"]).issubset(state) and not _match(predicate["not"], state)
    if "all" in predicate:
        return all(_match(p, state) for p in predicate["all"])
    return any(_match(p, state) for p in predicate["any"])


def _order(nodes: list[str], dependencies: dict[str, set[str]], label: str) -> list[str]:
    remaining = set(nodes)
    result: list[str] = []
    while remaining:
        ready = [id_ for id_ in nodes if id_ in remaining and not (dependencies[id_] & remaining)]
        require(bool(ready), f"{label}: dependency cycle")
        result.extend(ready)
        remaining.difference_update(ready)
    return result


def validate(spec: Any) -> None:
    keys(spec, {"schema", "title", "questions", "rules", "conflicts"}, "workflow")
    require(spec.get("schema") == "aya-workflow/v1", "unsupported workflow schema")
    require(isinstance(spec.get("title"), str) and bool(spec["title"].strip()), "missing title")
    require(isinstance(spec.get("questions"), list) and bool(spec["questions"]), "missing questions")
    require(isinstance(spec.get("rules"), list), "rules must be an array")
    require(isinstance(spec.get("conflicts", []), list), "conflicts must be an array")
    questions: dict[str, dict[str, Any]] = {}
    for q in spec["questions"]:
        keys(q, {"id", "prompt", "kind", "options", "required", "default", "when"}, "question")
        qid = q.get("id")
        require(isinstance(qid, str) and bool(qid) and qid not in questions, "invalid/duplicate question id")
        require(isinstance(q.get("prompt"), str) and bool(q["prompt"].strip()), f"{qid}: missing prompt")
        require(q.get("kind") in ("boolean", "choice", "multi"), f"{qid}: invalid kind")
        require(type(q.get("required", False)) is bool, f"{qid}: required must be boolean")
        if q["kind"] == "boolean":
            require("options" not in q, f"{qid}: boolean cannot have options")
        else:
            options = q.get("options")
            require(isinstance(options, list) and bool(options)
                    and all(type(v) is str and bool(v) for v in options)
                    and len(options) == len(set(options)), f"{qid}: invalid options")
        if "default" in q:
            require(_valid_value(q, q["default"]), f"{qid}: invalid default")
        questions[qid] = q
    qdeps = {}
    for qid, q in questions.items():
        qdeps[qid] = refs(q["when"], questions) if "when" in q else set()
        require(qid not in qdeps[qid], f"{qid}: self-dependent visibility")
    _order(list(questions), qdeps, "question visibility")
    rules: dict[str, dict[str, Any]] = {}
    rdeps = {}
    for r in spec["rules"]:
        keys(r, {"id", "section", "text", "when", "after"}, "rule")
        rid = r.get("id")
        require(isinstance(rid, str) and bool(rid) and rid not in rules, "invalid/duplicate rule id")
        require(r.get("section") in SECTIONS, f"{rid}: invalid section")
        require(isinstance(r.get("text"), str) and bool(r["text"].strip()), f"{rid}: invalid text")
        if "when" in r:
            refs(r["when"], questions)
        after = r.get("after", [])
        require(isinstance(after, list) and len(after) == len(set(_hashable_strings(after)))
                and all(type(a) is str for a in after), f"{rid}: invalid after")
        rules[rid] = r
        rdeps[rid] = set(after)
    for rid, r in rules.items():
        for parent in rdeps[rid]:
            require(parent in rules and parent != rid, f"{rid}: unknown/self dependency")
            require(rules[parent]["section"] == r["section"], f"{rid}: cross-section dependency")
    _order(list(rules), rdeps, "rule ordering")
    for c in spec.get("conflicts", []):
        keys(c, {"when", "message"}, "conflict")
        require("when" in c and "message" in c and isinstance(c["message"], str)
                and bool(c["message"].strip()), "invalid conflict")
        refs(c["when"], questions)


def resolve(spec: dict[str, Any], answers: dict[str, Any]) -> dict[str, Any]:
    validate(spec)
    require(isinstance(answers, dict), "answers must be an object")
    questions = {q["id"]: q for q in spec["questions"]}
    require(not (set(answers) - set(questions)), "unknown answer keys")
    for qid, value in answers.items():
        require(_valid_value(questions[qid], value), f"{qid}: invalid answer")
    qdeps = {qid: refs(q["when"], questions) if "when" in q else set()
             for qid, q in questions.items()}
    state: dict[str, Any] = {}
    ignored: list[str] = []
    for qid in _order(list(questions), qdeps, "question visibility"):
        q = questions[qid]
        if not _match(q.get("when"), state):
            if qid in answers:
                ignored.append(qid)
            continue
        if qid in answers:
            value = answers[qid]
        elif "default" in q:
            value = q["default"]
        elif q.get("required", False):
            raise WorkflowV1Error(f"{qid}: missing required answer")
        else:
            continue
        if q["kind"] == "multi":
            value = [option for option in q["options"] if option in value]
        state[qid] = value
    for c in spec.get("conflicts", []):
        if _match(c["when"], state):
            raise WorkflowV1Error(c["message"])
    rmap = {r["id"]: r for r in spec["rules"]}
    rdeps = {rid: set(r.get("after", [])) for rid, r in rmap.items()}
    ordered_rules = _order(list(rmap), rdeps, "rule ordering")
    sections: dict[str, list[str]] = {s: [] for s in SECTIONS}
    trace: list[dict[str, Any]] = []
    included: set[str] = set()
    for rid in ordered_rules:
        rule = rmap[rid]
        if not _match(rule.get("when"), state):
            continue
        require(rdeps[rid].issubset(included), f"{rid}: required predecessor not selected")
        included.add(rid)
        sections[rule["section"]].append(rule["text"])
        refs_used = sorted(refs(rule["when"], questions)) if "when" in rule else []
        trace.append({"rule_id": rid, "section": rule["section"], "decisions": refs_used})
    require(bool(sections["objective"]), "no objective resolved")
    return {"schema": "aya-task-intent/v1", "title": spec["title"], "answers": state,
            "ignored_answers": sorted(ignored), "sections": sections, "trace": trace}


def compose(intent: dict[str, Any]) -> str:
    labels = {"objective": "Task", "operations": "Operations",
              "constraints": "Constraints", "output": "Requested output"}
    return "\n\n".join(labels[s] + ":\n" + "\n".join("- " + line for line in intent["sections"][s])
                       for s in SECTIONS if intent["sections"].get(s))


def main() -> None:
    import argparse
    import json
    from pathlib import Path
    parser = argparse.ArgumentParser(description="Compile an experimental typed AYA workflow v1")
    parser.add_argument("spec", type=Path)
    parser.add_argument("answers", type=Path)
    parser.add_argument("--trace", action="store_true")
    args = parser.parse_args()
    intent = resolve(json.loads(args.spec.read_text(encoding="utf-8")),
                     json.loads(args.answers.read_text(encoding="utf-8")))
    print(compose(intent))
    if args.trace:
        print("\n--- LOCAL TRACE (not part of handoff) ---")
        print(json.dumps({"trace": intent["trace"], "ignored_answers": intent["ignored_answers"]}, indent=2))


if __name__ == "__main__":
    main()
