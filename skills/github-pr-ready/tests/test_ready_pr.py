import importlib.util
import pathlib
import unittest


SCRIPT = pathlib.Path(__file__).parents[1] / "scripts" / "ready-pr.py"
SPEC = importlib.util.spec_from_file_location("ready_pr", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


class ReadyTests(unittest.TestCase):
    def test_exact_open_identity_matches(self):
        record = {
            "number": 1,
            "url": "u",
            "state": "OPEN",
            "isDraft": True,
            "baseRefName": "main",
            "headRefName": "feature/x",
            "headRefOid": "h",
        }
        self.assertTrue(MODULE.identity_matches(record, "h", "main"))

    def test_changed_head_does_not_match(self):
        record = {
            "number": 1,
            "url": "u",
            "state": "OPEN",
            "baseRefName": "main",
            "headRefName": "feature/x",
            "headRefOid": "other",
        }
        self.assertFalse(MODULE.identity_matches(record, "h", "main"))

    def test_closed_pr_does_not_match(self):
        record = {
            "number": 1,
            "url": "u",
            "state": "CLOSED",
            "baseRefName": "main",
            "headRefName": "feature/x",
            "headRefOid": "h",
        }
        self.assertFalse(MODULE.identity_matches(record, "h", "main"))

    def test_missing_draft_state_does_not_match(self):
        record = {
            "number": 1,
            "url": "u",
            "state": "OPEN",
            "baseRefName": "main",
            "headRefName": "feature/x",
            "headRefOid": "h",
        }
        self.assertFalse(MODULE.identity_matches(record, "h", "main"))


if __name__ == "__main__":
    unittest.main()
