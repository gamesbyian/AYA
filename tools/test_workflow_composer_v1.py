"""Portable v1 conformance corpus for future Kotlin/Swift/JS implementations."""
import copy
import json
from pathlib import Path
import unittest

from tools.workflow_composer_v1 import WorkflowV1Error, compose, resolve, validate

ROOT = Path(__file__).resolve().parent.parent / "docs" / "workflow"
SPEC = json.loads((ROOT / "examples" / "fictional-visual-v1.json").read_text(encoding="utf-8"))
CORPUS = json.loads((ROOT / "conformance" / "visual-v1-cases.json").read_text(encoding="utf-8"))


class TypedWorkflowTests(unittest.TestCase):
    def test_corpus(self):
        for name in ("visual", "report"):
            spec = json.loads((ROOT / "examples" / f"fictional-{name}-v1.json").read_text(encoding="utf-8"))
            corpus = json.loads((ROOT / "conformance" / f"{name}-v1-cases.json").read_text(encoding="utf-8"))
            self.assertEqual(corpus["schema"], "aya-workflow-cases/v1")
            for case in corpus["cases"]:
                with self.subTest(host=name, case=case["id"]):
                    if "error" in case:
                        with self.assertRaisesRegex(WorkflowV1Error, case["error"].replace(".", r"\.")):
                            resolve(spec, case["answers"])
                    else:
                        result = resolve(spec, case["answers"])
                        for field, expected in case["expected"].items():
                            self.assertEqual(result[field], expected)
                        self.assertTrue(compose(result).startswith("Task:\n"))

    def test_multi_answers_canonical(self):
        forward = resolve(SPEC, {"goal": "restore", "deliverables": ["image", "notes"]})
        reversed_ = resolve(SPEC, {"deliverables": ["notes", "image"], "goal": "restore"})
        self.assertEqual(forward, reversed_)

    def test_ordered_rule_dependencies(self):
        intent = resolve(SPEC, {"goal": "restore", "deliverables": ["notes"]})
        self.assertLess(intent["sections"]["operations"].index("Prepare supplemental materials."),
                        intent["sections"]["operations"].index("Add explanatory notes."))

    def test_inactive_required_predecessor_rejected(self):
        s = copy.deepcopy(SPEC)
        s["rules"].append({"id": "broken", "section": "operations", "text": "Broken",
                           "when": {"question": "goal", "equals": "restore"}, "after": ["annotate"]})
        with self.assertRaisesRegex(WorkflowV1Error, "required predecessor"):
            resolve(s, {"goal": "restore"})

    def test_not_does_not_match_absent_parent(self):
        s = copy.deepcopy(SPEC)
        s["questions"].append({"id": "optional", "kind": "choice", "prompt": "Optional",
                               "options": ["yes", "no"]})
        s["rules"].append({"id": "absent-negation", "section": "output", "text": "Wrong",
                           "when": {"not": {"question": "optional", "equals": "yes"}}})
        self.assertNotIn("Wrong", compose(resolve(s, {"goal": "restore"})))
        self.assertIn("Wrong", compose(resolve(s, {"goal": "restore", "optional": "no"})))

    def test_cycle_and_bad_references(self):
        s = copy.deepcopy(SPEC)
        s["questions"][0]["when"] = {"question": "detail", "equals": "high"}
        with self.assertRaisesRegex(WorkflowV1Error, "cycle"):
            validate(s)
        s = copy.deepcopy(SPEC)
        s["rules"][0]["when"] = {"question": "no-such-question", "equals": "x"}
        with self.assertRaisesRegex(WorkflowV1Error, "unknown predicate"):
            validate(s)

    def test_bad_answer_shapes(self):
        for bad in (1, "true", None):
            with self.subTest(bad=bad), self.assertRaises(WorkflowV1Error):
                resolve(SPEC, {"goal": "restore", "strict": bad})
        for bad in (["image", "image"], ["alien"], "image", [1], [True]):
            with self.subTest(bad=bad), self.assertRaises(WorkflowV1Error):
                resolve(SPEC, {"goal": "restore", "deliverables": bad})

    def test_bad_spec(self):
        for bad in (None, [], {}, "hi"):
            with self.subTest(bad=bad), self.assertRaises(WorkflowV1Error):
                validate(bad)
        for altered in ("bad-kind", "bad-dependency", "bad-multi-equals", "bad-predicate"):
            s = copy.deepcopy(SPEC)
            if altered == "bad-kind":
                s["questions"][0]["kind"] = "text"
            elif altered == "bad-dependency":
                s["rules"][0]["after"] = ["absent"]
            elif altered == "bad-multi-equals":
                s["rules"][0]["when"] = {"question": "deliverables", "equals": "notes"}
            else:
                s["rules"][0]["when"] = {"not": {"question": "missing", "equals": "yes"}}
            with self.subTest(altered=altered), self.assertRaises(WorkflowV1Error):
                validate(s)

    def test_equivalent_input_navigation_order(self):
        a = resolve(SPEC, {"goal": "design", "strict": False, "detail": "high"})
        b = resolve(SPEC, {"detail": "high", "strict": False, "goal": "design"})
        self.assertEqual(a, b)

    def test_both_schema_versions_independently_supported(self):
        from tools.workflow_composer import resolve as v0
        old = json.loads((ROOT / "examples" / "fictional-image-workflow.json").read_text())
        self.assertIn("Restore", v0(old, {"task": "restore"})["sections"]["objective"][0])
        with self.assertRaisesRegex(WorkflowV1Error, "unsupported workflow schema"):
            validate(old)


if __name__ == "__main__":
    unittest.main()
