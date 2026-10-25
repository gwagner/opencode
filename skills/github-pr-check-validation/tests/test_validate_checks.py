import importlib.util
import json
import pathlib
import unittest


SCRIPT = pathlib.Path(__file__).parents[1] / "scripts" / "validate-checks.py"
SPEC = importlib.util.spec_from_file_location("validate_checks", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


class ClassificationTests(unittest.TestCase):
    def test_pass(self):
        records = [{"name": "test", "bucket": "pass", "state": "SUCCESS"}]
        self.assertEqual(MODULE.classify(0, json.dumps(records), "")[0], "passed")

    def test_pending(self):
        records = [{"name": "test", "bucket": "pending", "state": "IN_PROGRESS"}]
        self.assertEqual(MODULE.classify(8, json.dumps(records), "")[0], "pending")

    def test_failure_needs_repair(self):
        records = [{"name": "test", "bucket": "fail", "state": "FAILURE"}]
        self.assertEqual(MODULE.classify(1, json.dumps(records), "")[0], "repair-needed")

    def test_unknown_pair_blocks(self):
        records = [{"name": "test", "bucket": "pass", "state": "PENDING"}]
        self.assertEqual(MODULE.classify(0, json.dumps(records), "")[0], "blocked-unsafe")

    def test_empty_is_only_candidate(self):
        self.assertEqual(MODULE.classify(0, "[]", "")[0], "zero-candidate")


if __name__ == "__main__":
    unittest.main()
