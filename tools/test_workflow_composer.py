import copy
import unittest
from tools.workflow_composer import WorkflowError, resolve, compose, validate

BASE = {
  'schema': 'aya-workflow/v0', 'title': 'Fictional visual editor',
  'questions': [
    {'id': 'task', 'prompt': 'Task?', 'options': ['restore', 'reinterpret'], 'required': True},
    {'id': 'fidelity', 'prompt': 'Fidelity?', 'options': ['strict', 'flexible'], 'default': 'strict'},
    {'id': 'comparison', 'prompt': 'Comparison?', 'options': ['yes', 'no'], 'default': 'no'},
    {'id': 'labels', 'prompt': 'Labels?', 'options': ['yes', 'no'], 'when': {'comparison': 'yes'}, 'default': 'no'}
  ],
  'rules': [
    {'id': 'r1', 'when': {'task': 'restore'}, 'section': 'objective', 'text': 'Restore image'},
    {'id': 'r2', 'when': {'task': 'reinterpret'}, 'section': 'objective', 'text': 'Reinterpret image'},
    {'id': 'r3', 'when': {'fidelity': 'strict'}, 'section': 'constraints', 'text': 'Preserve geometry'},
    {'id': 'r4', 'when': {'comparison': 'yes'}, 'section': 'output', 'text': 'Include comparison'},
    {'id': 'r5', 'when': {'labels': 'yes'}, 'section': 'output', 'text': 'Label comparison'}
  ],
  'conflicts': [{'when': {'task': 'reinterpret', 'fidelity': 'strict'}, 'message': 'Choose flexible fidelity for reinterpretation'}]
}
class TestWorkflow(unittest.TestCase):
    def test_valid(self):
        validate(BASE)
    def test_baseline(self):
        a = resolve(BASE, {'task':'restore'})
        self.assertIn('Restore image', compose(a))
        self.assertEqual(a['answers']['fidelity'], 'strict')
    def test_hidden_stale_answer_ignored(self):
        a=resolve(BASE, {'task':'restore', 'comparison':'no', 'labels':'yes'})
        self.assertEqual(a['ignored_answers'], ['labels'])
        self.assertNotIn('Label comparison', compose(a))
    def test_visible_answer(self):
        a=resolve(BASE, {'task':'restore', 'comparison':'yes','labels':'yes'})
        self.assertIn('Label comparison', compose(a))
    def test_conflict(self):
        with self.assertRaisesRegex(WorkflowError, 'flexible'):
            resolve(BASE, {'task':'reinterpret'})
    def test_missing_required(self):
        with self.assertRaisesRegex(WorkflowError, 'Missing required'):
            resolve(BASE,{})
    def test_invalid_answer(self):
        with self.assertRaises(WorkflowError): resolve(BASE,{'task':'delete'})
    def test_unknown(self):
        with self.assertRaises(WorkflowError): resolve(BASE,{'task':'restore','extra':'x'})
    def test_cycles(self):
        s=copy.deepcopy(BASE)
        s['questions'][2]['when']={'labels':'yes'}
        with self.assertRaisesRegex(WorkflowError, 'cycle'):
            validate(s)
    def test_trace(self):
        a=resolve(BASE, {'task':'restore'})
        self.assertEqual([x['rule_id'] for x in a['trace']],['r1','r3'])
    def test_second_host_fixture(self):
        import json
        from pathlib import Path
        root = Path(__file__).resolve().parent.parent
        directory = root / 'docs' / 'workflow' / 'examples'
        spec = json.loads((directory / 'fictional-report-workflow.json').read_text(encoding='utf-8'))
        answers = json.loads((directory / 'fictional-report-answers.json').read_text(encoding='utf-8'))
        result = resolve(spec, answers)
        text = compose(result)
        self.assertIn('Compare the supplied dataset groups', text)
        self.assertIn('Identify meaningful between-group differences', text)
        self.assertIn('Cite supplied source material', text)
        self.assertNotIn('Summarize the supplied dataset', text)
        stale = resolve(spec, {'goal': 'summary', 'differences': 'yes'})
        self.assertEqual(stale['ignored_answers'], ['differences'])
        self.assertNotIn('between-group differences', compose(stale))
    def test_optional_absent_dependency_does_not_deadlock(self):
        s = copy.deepcopy(BASE)
        s['questions'].append({'id': 'notes', 'prompt': 'Optional?', 'options': ['yes', 'no']})
        s['questions'].append({'id': 'detail', 'prompt': 'Dependent?', 'options': ['long', 'short'], 'when': {'notes': 'yes'}})
        s['rules'].append({'id': 'r6', 'when': {'detail': 'long'}, 'section': 'operations', 'text': 'Long detail'})
        result = resolve(s, {'task': 'restore'})
        self.assertNotIn('notes', result['answers'])
        self.assertNotIn('detail', result['answers'])
        self.assertNotIn('Long detail', compose(result))
    def test_malformed_spec_rejected_as_workflow_error(self):
        for bad in [None, [], 'text', 9]:
            with self.subTest(spec=bad), self.assertRaises(WorkflowError):
                validate(bad)
        for invalid in [None, {}, 'bad']:
            s = copy.deepcopy(BASE)
            s['conflicts'] = invalid
            with self.subTest(conflicts=invalid), self.assertRaises(WorkflowError):
                validate(s)
    def test_empty_option_rejected(self):
        s = copy.deepcopy(BASE)
        s['questions'][0]['options'].append('')
        with self.assertRaises(WorkflowError):
            validate(s)
    def test_hidden_required_question_does_not_block(self):
        s = copy.deepcopy(BASE)
        s['questions'][3]['required'] = True
        del s['questions'][3]['default']
        self.assertEqual(resolve(s, {'task': 'restore'})['ignored_answers'], [])
        with self.assertRaisesRegex(WorkflowError, 'Missing required answer: labels'):
            resolve(s, {'task': 'restore', 'comparison': 'yes'})
    def test_unknown_schema_fields_rejected(self):
        for location in ('workflow', 'question', 'rule', 'conflict'):
            s = copy.deepcopy(BASE)
            if location == 'workflow':
                s['accidental'] = True
            elif location == 'question':
                s['questions'][0]['accidental'] = True
            elif location == 'rule':
                s['rules'][0]['accidental'] = True
            else:
                s['conflicts'][0]['accidental'] = True
            with self.subTest(location=location), self.assertRaisesRegex(WorkflowError, 'Unknown'):
                validate(s)
    def test_schema_and_examples_are_json(self):
        import json
        from pathlib import Path
        root = Path(__file__).resolve().parent.parent / 'docs' / 'workflow'
        schema = json.loads((root / 'schema' / 'aya-workflow-v0.schema.json').read_text(encoding='utf-8'))
        self.assertEqual(schema['properties']['schema']['const'], 'aya-workflow/v0')
        for fixture in ('fictional-image-workflow.json', 'fictional-report-workflow.json'):
            with self.subTest(fixture=fixture):
                validate(json.loads((root / 'examples' / fixture).read_text(encoding='utf-8')))
    def test_exhaustive_fictional_small_workflows(self):
        import itertools
        import json
        from pathlib import Path
        root = Path(__file__).resolve().parent.parent / 'docs' / 'workflow' / 'examples'
        for filename in ('fictional-image-workflow.json', 'fictional-report-workflow.json'):
            spec = json.loads((root / filename).read_text(encoding='utf-8'))
            ids = [q['id'] for q in spec['questions']]
            options = [q['options'] for q in spec['questions']]
            checked = 0
            for values in itertools.product(*options):
                answers = dict(zip(ids, values))
                try:
                    intent = resolve(spec, answers)
                except WorkflowError as exc:
                    # The only declared conflict in these fixtures is image reinterpret + strict.
                    self.assertEqual(filename, 'fictional-image-workflow.json')
                    self.assertEqual(answers['task'], 'reinterpret')
                    self.assertEqual(answers['fidelity'], 'strict')
                    continue
                checked += 1
                text = compose(intent)
                self.assertTrue(text.startswith('Task:'))
                if filename.startswith('fictional-image'):
                    if answers['fidelity'] == 'strict':
                        self.assertIn('Preserve original geometry', text)
                    if answers['comparison'] == 'no':
                        self.assertNotIn('Label the before/after comparison', text)
                        self.assertEqual('labels' in intent['ignored_answers'], True)
                else:
                    if answers['goal'] == 'summary':
                        self.assertNotIn('between-group differences', text)
                        self.assertIn('differences', intent['ignored_answers'])
                    if answers['citations'] == 'no':
                        self.assertNotIn('Cite supplied source', text)
            self.assertGreater(checked, 0)
    def test_order_independent(self):
        first=resolve(BASE, {'task':'restore','comparison':'yes','labels':'yes'})
        second=resolve(BASE, {'labels':'yes','comparison':'yes','task':'restore'})
        self.assertEqual(first,second)
if __name__=='__main__':unittest.main()
