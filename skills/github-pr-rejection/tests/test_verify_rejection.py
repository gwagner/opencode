import importlib.util
import pathlib
import unittest


SCRIPT = pathlib.Path(__file__).parents[1] / "scripts" / "verify-rejection.py"
SPEC = importlib.util.spec_from_file_location("verify_rejection", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


class RejectionTests(unittest.TestCase):
    def test_exact_open_pr_matches(self):
        record = {"state": "OPEN", "headRefOid": "h", "headRefName": "feature/x", "baseRefName": "main"}
        self.assertTrue(MODULE.matches(record, "h", "main"))

    def test_changed_head_does_not_match(self):
        record = {"state": "OPEN", "headRefOid": "other", "headRefName": "feature/x", "baseRefName": "main"}
        self.assertFalse(MODULE.matches(record, "h", "main"))

    def test_closed_pr_does_not_match(self):
        record = {"state": "CLOSED", "headRefOid": "h", "headRefName": "feature/x", "baseRefName": "main"}
        self.assertFalse(MODULE.matches(record, "h", "main"))


if __name__ == "__main__":
    unittest.main()
