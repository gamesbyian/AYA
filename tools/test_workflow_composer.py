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
    def test_order_independent(self):
        first=resolve(BASE, {'task':'restore','comparison':'yes','labels':'yes'})
        second=resolve(BASE, {'labels':'yes','comparison':'yes','task':'restore'})
        self.assertEqual(first,second)
if __name__=='__main__':unittest.main()
