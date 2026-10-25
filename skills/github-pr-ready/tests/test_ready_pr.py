import importlib.util
import io
import json
import pathlib
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from unittest import mock


SCRIPT = pathlib.Path(__file__).parents[1] / "scripts" / "ready-pr.py"
SPEC = importlib.util.spec_from_file_location("ready_pr", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


class ReadyTests(unittest.TestCase):
    @staticmethod
    def completed(args, stdout="", stderr="", returncode=0):
        return subprocess.CompletedProcess(args, returncode, stdout, stderr)

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

    def test_repository_identity_requires_exact_pr_url(self):
        repository = {"nameWithOwner": "o/r", "url": "https://github.com/o/r"}
        local = {"number": 1, "url": "https://github.com/o/r/pull/1"}
        foreign = {"number": 1, "url": "https://github.com/other/r/pull/1"}
        self.assertTrue(MODULE.repository_matches(repository, local))
        self.assertFalse(MODULE.repository_matches(repository, foreign))

    def test_foreign_repository_blocks_before_ready_mutation(self):
        calls = []
        repository = {"nameWithOwner": "o/r", "url": "https://github.com/o/r"}
        pull_request = {
            "number": 1,
            "url": "https://github.com/other/r/pull/1",
            "state": "OPEN",
            "isDraft": True,
            "baseRefName": "main",
            "headRefName": "feature/x",
            "headRefOid": "h",
        }

        def fake_run(args):
            calls.append(args)
            if args[:3] == ["gh", "auth", "status"]:
                return self.completed(args)
            if args[:3] == ["gh", "repo", "view"]:
                return self.completed(args, json.dumps(repository))
            if args[:3] == ["gh", "pr", "view"]:
                return self.completed(args, json.dumps(pull_request))
            raise AssertionError(args)

        output = io.StringIO()
        argv = ["ready-pr.py", "--pr", "https://github.com/other/r/pull/1", "--expected-head", "h"]
        with mock.patch.object(MODULE, "run", side_effect=fake_run), mock.patch.object(sys, "argv", argv), redirect_stdout(output):
            return_code = MODULE.main()
        self.assertEqual(return_code, 2)
        self.assertEqual(json.loads(output.getvalue())["disposition"], "blocked-unsafe")
        self.assertFalse(any(call[:3] == ["gh", "pr", "ready"] for call in calls))

    def test_changed_pre_mutation_head_blocks_ready(self):
        calls = []
        repository = {"nameWithOwner": "o/r", "url": "https://github.com/o/r"}
        before = {
            "number": 1,
            "url": "https://github.com/o/r/pull/1",
            "state": "OPEN",
            "isDraft": True,
            "baseRefName": "main",
            "headRefName": "feature/x",
            "headRefOid": "h",
        }
        changed = dict(before, headRefOid="other")
        views = iter([before, changed])

        def fake_run(args):
            calls.append(args)
            if args[:3] == ["gh", "auth", "status"]:
                return self.completed(args)
            if args[:3] == ["gh", "repo", "view"]:
                return self.completed(args, json.dumps(repository))
            if args[:3] == ["gh", "pr", "view"]:
                return self.completed(args, json.dumps(next(views)))
            raise AssertionError(args)

        output = io.StringIO()
        argv = ["ready-pr.py", "--pr", "1", "--expected-head", "h"]
        with mock.patch.object(MODULE, "run", side_effect=fake_run), mock.patch.object(sys, "argv", argv), redirect_stdout(output):
            return_code = MODULE.main()
        self.assertEqual(return_code, 2)
        self.assertEqual(json.loads(output.getvalue())["disposition"], "blocked-unsafe")
        self.assertFalse(any(call[:3] == ["gh", "pr", "ready"] for call in calls))


if __name__ == "__main__":
    unittest.main()
