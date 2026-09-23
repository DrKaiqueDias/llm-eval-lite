import json
import tempfile
import unittest
from pathlib import Path
from evaluate import evaluate_case, evaluate_file, main


class EvaluationTests(unittest.TestCase):
    def test_casefold_and_all_rules(self):
        result = evaluate_case({"id": "a", "response": "Straße",
                                "rules": {"contains": ["STRASSE"], "excludes": ["secret"], "max_chars": 6}})
        self.assertTrue(result["passed"])

    def test_failure_is_reported_per_rule(self):
        result = evaluate_case({"id": "a", "response": "secret",
                                "rules": {"excludes": ["SECRET"], "max_chars": 5}})
        self.assertEqual(result["checks"], {"excludes": False, "max_chars": False})

    def test_json_constants_rejected(self):
        for response in ("NaN", "Infinity", "{broken"):
            self.assertFalse(evaluate_case({"id": "a", "response": response,
                                           "rules": {"valid_json": True}})["passed"])

    def test_json_document(self):
        self.assertTrue(evaluate_case({"id": "a", "response": '{"ok": true}',
                                       "rules": {"valid_json": True}})["passed"])

    def test_invalid_rules(self):
        for rules in ({}, {"typo": 1}, {"contains": []}, {"max_chars": True},
                      {"excludes": [""]}, {"valid_json": False}):
            with self.assertRaises(ValueError):
                evaluate_case({"id": "a", "response": "", "rules": rules})

    def test_duplicate_ids_and_line_numbers(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "cases.jsonl"
            case = json.dumps({"id": "same", "response": "", "rules": {"max_chars": 0}})
            path.write_text(case + "\n" + case, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "line 2: duplicate"):
                evaluate_file(path)

    def test_empty_input(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "empty.jsonl"
            path.write_text("\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                evaluate_file(path)

    def test_cli_pass_and_fail(self):
        import contextlib
        import io
        with tempfile.TemporaryDirectory() as folder, contextlib.redirect_stdout(io.StringIO()):
            path = Path(folder) / "cases.jsonl"
            path.write_text('{"id":"a","response":"ok","rules":{"contains":["ok"]}}\n', encoding="utf-8")
            self.assertEqual(main([str(path)]), 0)
            path.write_text('{"id":"a","response":"no","rules":{"contains":["ok"]}}\n', encoding="utf-8")
            self.assertEqual(main([str(path)]), 1)


if __name__ == "__main__":
    unittest.main()
