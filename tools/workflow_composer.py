"""Portable deterministic AYA workflow reference composer (stdlib only).

Developer-side prototype; not a shipping SDK or recipient integration.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

class WorkflowError(ValueError):
    pass

def _ensure(condition: bool, message: str) -> None:
    if not condition:
        raise WorkflowError(message)

def _condition_matches(condition: dict[str, Any] | None, state: dict[str, Any]) -> bool:
    if condition is None:
        return True
    return all(state.get(key) == value for key, value in condition.items())

def validate(spec: dict[str, Any]) -> None:
    _ensure(spec.get('schema') == 'aya-workflow/v0', 'Unsupported workflow schema')
    _ensure(isinstance(spec.get('questions'), list) and bool(spec['questions']), 'Missing questions')
    _ensure(isinstance(spec.get('rules'), list), 'Missing rules')
    _ensure(isinstance(spec.get('title'), str) and bool(spec['title'].strip()), 'Missing title')
    questions: dict[str, dict[str, Any]] = {}
    for q in spec['questions']:
        _ensure(isinstance(q, dict) and isinstance(q.get('id'), str) and q['id'], 'Bad question ID')
        _ensure(q['id'] not in questions, f"Duplicate question {q['id']}")
        _ensure(isinstance(q.get('prompt'), str) and q['prompt'], f"Missing question prompt: {q['id']}")
        _ensure(isinstance(q.get('options'), list) and bool(q['options']), f"Missing options: {q['id']}")
        _ensure(all(isinstance(v, str) for v in q['options']), f"Non-string option: {q['id']}")
        _ensure(len(q['options']) == len(set(q['options'])), f"Duplicate option: {q['id']}")
        _ensure(isinstance(q.get('required', False), bool), f"Invalid required: {q['id']}")
        if 'default' in q:
            _ensure(q['default'] in q['options'], f"Invalid default: {q['id']}")
        questions[q['id']] = q
    for q in spec['questions']:
        cond = q.get('when', {})
        _ensure(isinstance(cond, dict), f"Invalid when: {q['id']}")
        for ref, value in cond.items():
            _ensure(ref in questions and ref != q['id'], f"Unknown or self-referencing condition: {q['id']}")
            _ensure(value in questions[ref]['options'], f"Invalid condition value: {q['id']}")
    visited: set[str] = set()
    visiting: set[str] = set()
    def visit(node: str) -> None:
        _ensure(node not in visiting, f'Conditional cycle at {node}')
        if node in visited:
            return
        visiting.add(node)
        for dep in questions[node].get('when', {}):
            visit(dep)
        visiting.remove(node)
        visited.add(node)
    for node in questions:
        visit(node)
    ids: set[str] = set()
    for rule in spec['rules']:
        _ensure(isinstance(rule, dict) and isinstance(rule.get('id'), str) and rule['id'], 'Bad rule ID')
        _ensure(rule['id'] not in ids, f"Duplicate rule {rule['id']}")
        ids.add(rule['id'])
        cond = rule.get('when', {})
        _ensure(isinstance(cond, dict), f"Invalid rule condition: {rule['id']}")
        for ref, value in cond.items():
            _ensure(ref in questions and value in questions[ref]['options'], f"Bad rule condition: {rule['id']}")
        _ensure(rule.get('section') in ('objective', 'operations', 'constraints', 'output'), f"Invalid section: {rule['id']}")
        _ensure(isinstance(rule.get('text'), str) and rule['text'].strip(), f"Empty text: {rule['id']}")
    for c in spec.get('conflicts', []):
        _ensure(isinstance(c, dict) and isinstance(c.get('when'), dict) and len(c['when']) > 0, 'Invalid conflict')
        _ensure(isinstance(c.get('message'), str) and c['message'], 'Invalid conflict message')
        for ref, value in c['when'].items():
            _ensure(ref in questions and value in questions[ref]['options'], f'Bad conflict condition: {ref}')

def resolve(spec: dict[str, Any], answers: dict[str, Any]) -> dict[str, Any]:
    validate(spec)
    _ensure(isinstance(answers, dict), 'Answers must be an object')
    questions = {q['id']: q for q in spec['questions']}
    _ensure(not (set(answers) - set(questions)), 'Unknown answer keys')
    for key, value in answers.items():
        _ensure(value in questions[key]['options'], f'Invalid answer: {key}')
    state: dict[str, Any] = {}
    ignored: list[str] = []
    remaining = dict(questions)
    while remaining:
        ready = [key for key, q in remaining.items() if set(q.get('when', {})).issubset(state.keys() | set(ignored))]
        _ensure(bool(ready), 'Unresolved conditional dependencies')
        for key in ready:
            q = remaining.pop(key)
            if not _condition_matches(q.get('when'), state):
                ignored.append(key)
                continue
            if key in answers:
                state[key] = answers[key]
            elif 'default' in q:
                state[key] = q['default']
            elif q.get('required', False):
                raise WorkflowError(f'Missing required answer: {key}')
    for conflict in spec.get('conflicts', []):
        if _condition_matches(conflict['when'], state):
            raise WorkflowError(conflict['message'])
    sections: dict[str, list[str]] = {s: [] for s in ('objective', 'operations', 'constraints', 'output')}
    trace: list[dict[str, Any]] = []
    for rule in spec['rules']:
        if _condition_matches(rule.get('when'), state):
            sections[rule['section']].append(rule['text'])
            trace.append({'rule_id': rule['id'], 'decisions': sorted(rule.get('when', {})), 'section': rule['section']})
    _ensure(bool(sections['objective']), 'No objective resolved')
    return {'schema': 'aya-task-intent/v0', 'title': spec['title'], 'answers': state,
            'ignored_answers': sorted(k for k in ignored if k in answers),
            'sections': sections, 'trace': trace}

def compose(intent: dict[str, Any]) -> str:
    labels = {'objective': 'Task', 'operations': 'Operations', 'constraints': 'Constraints', 'output': 'Requested output'}
    return '\n\n'.join(f"{labels[k]}:\n" + '\n'.join(f'- {line}' for line in intent['sections'][k])
                       for k in labels if intent['sections'].get(k))

def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description='Compile a host-authored workflow into handoff text')
    parser.add_argument('spec', type=Path)
    parser.add_argument('answers', type=Path)
    parser.add_argument('--trace', action='store_true')
    args = parser.parse_args()
    result = resolve(json.loads(args.spec.read_text(encoding='utf-8')), json.loads(args.answers.read_text(encoding='utf-8')))
    print(compose(result))
    if args.trace:
        print('\n--- LOCAL TRACE (not part of handoff) ---')
        print(json.dumps({'trace': result['trace'], 'ignored_answers': result['ignored_answers']}, indent=2))

if __name__ == '__main__':
    main()
