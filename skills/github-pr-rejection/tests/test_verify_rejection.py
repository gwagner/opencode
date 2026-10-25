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
        self.assertTrue(MODULE.matches(record, "h", "main", "feature/x"))

    def test_changed_head_does_not_match(self):
        record = {"state": "OPEN", "headRefOid": "other", "headRefName": "feature/x", "baseRefName": "main"}
        self.assertFalse(MODULE.matches(record, "h", "main", "feature/x"))

    def test_closed_pr_does_not_match(self):
        record = {"state": "CLOSED", "headRefOid": "h", "headRefName": "feature/x", "baseRefName": "main"}
        self.assertFalse(MODULE.matches(record, "h", "main", "feature/x"))

    def test_changed_branch_does_not_match(self):
        record = {"state": "OPEN", "headRefOid": "h", "headRefName": "feature/other", "baseRefName": "main"}
        self.assertFalse(MODULE.matches(record, "h", "main", "feature/x"))

    def test_repository_identity_requires_exact_pr_url(self):
        repository = {"nameWithOwner": "o/r", "url": "https://github.com/o/r"}
        local = {"number": 1, "url": "https://github.com/o/r/pull/1"}
        foreign = {"number": 1, "url": "https://github.com/other/r/pull/1"}
        self.assertTrue(MODULE.repository_matches(repository, local))
        self.assertFalse(MODULE.repository_matches(repository, foreign))

    def test_origin_and_head_repository_require_checkout_repository(self):
        repository = {"nameWithOwner": "o/r", "url": "https://github.com/o/r"}
        self.assertTrue(MODULE.remote_urls_match(repository, "git@github.com:o/r.git\n"))
        self.assertFalse(MODULE.remote_urls_match(repository, "git@github.com:other/r.git\n"))
        local = {"isCrossRepository": False, "headRepository": {"nameWithOwner": "o/r"}}
        fork = {"isCrossRepository": True, "headRepository": {"nameWithOwner": "fork/r"}}
        self.assertTrue(MODULE.head_repository_matches(repository, local))
        self.assertFalse(MODULE.head_repository_matches(repository, fork))


if __name__ == "__main__":
    unittest.main()
