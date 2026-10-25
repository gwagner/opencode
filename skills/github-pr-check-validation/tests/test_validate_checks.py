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

    def test_transient_command_failure_waits(self):
        self.assertEqual(MODULE.classify(1, "", "HTTP 502 from GitHub")[0], "waiting-external")

    def test_malformed_success_blocks(self):
        self.assertEqual(MODULE.classify(0, "not-json", "")[0], "blocked-unsafe")

    def test_empty_is_only_candidate(self):
        self.assertEqual(MODULE.classify(0, "[]", "")[0], "zero-candidate")

    def test_repository_identity_requires_exact_pr_url(self):
        repository = {"nameWithOwner": "o/r", "url": "https://github.com/o/r"}
        local = {"number": 1, "url": "https://github.com/o/r/pull/1"}
        foreign = {"number": 1, "url": "https://github.com/other/r/pull/1"}
        self.assertTrue(MODULE.repository_matches(repository, local))
        self.assertFalse(MODULE.repository_matches(repository, foreign))

    def test_origin_and_head_repository_require_checkout_repository(self):
        repository = {"nameWithOwner": "o/r", "url": "https://github.com/o/r"}
        self.assertTrue(MODULE.remote_urls_match(repository, "git@github.com:o/r.git\nhttps://github.com/o/r.git\n"))
        self.assertFalse(MODULE.remote_urls_match(repository, "git@github.com:o/r.git\ngit@github.com:other/r.git\n"))
        local = {"isCrossRepository": False, "headRepository": {"nameWithOwner": "o/r"}}
        fork = {"isCrossRepository": True, "headRepository": {"nameWithOwner": "fork/r"}}
        self.assertTrue(MODULE.head_repository_matches(repository, local))
        self.assertFalse(MODULE.head_repository_matches(repository, fork))


if __name__ == "__main__":
    unittest.main()
