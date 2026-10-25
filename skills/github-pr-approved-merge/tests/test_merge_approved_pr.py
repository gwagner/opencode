import importlib.util
import io
import json
import pathlib
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from unittest import mock


SCRIPT = pathlib.Path(__file__).parents[1] / "scripts" / "merge-approved-pr.py"
SPEC = importlib.util.spec_from_file_location("merge_approved_pr", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


class MergeTests(unittest.TestCase):
    @staticmethod
    def completed(args, stdout="", stderr="", returncode=0):
        return subprocess.CompletedProcess(args, returncode, stdout, stderr)

    @staticmethod
    def record(state="OPEN", head="h", draft=False, mergeable="MERGEABLE"):
        return {
            "number": 1,
            "url": "u",
            "state": state,
            "isDraft": draft,
            "mergeable": mergeable,
            "baseRefName": "main",
            "headRefName": "feature/x",
            "headRefOid": head,
        }

    def test_exact_ready_pr_passes_merge_gate(self):
        self.assertTrue(MODULE.open_merge_gate(self.record(), "h", "main"))

    def test_draft_fails_merge_gate(self):
        self.assertFalse(MODULE.open_merge_gate(self.record(draft=True), "h", "main"))

    def test_changed_head_fails_merge_gate(self):
        self.assertFalse(MODULE.open_merge_gate(self.record(head="other"), "h", "main"))

    def test_unmergeable_fails_merge_gate(self):
        self.assertFalse(MODULE.open_merge_gate(self.record(mergeable="CONFLICTING"), "h", "main"))

    def test_repository_identity_requires_exact_pr_url(self):
        repository = {"nameWithOwner": "o/r", "url": "https://github.com/o/r"}
        local = {"number": 1, "url": "https://github.com/o/r/pull/1"}
        foreign = {"number": 1, "url": "https://github.com/other/r/pull/1"}
        self.assertTrue(MODULE.repository_matches(repository, local))
        self.assertFalse(MODULE.repository_matches(repository, foreign))

    def test_foreign_repository_blocks_before_merge(self):
        calls = []
        repository = {"nameWithOwner": "o/r", "url": "https://github.com/o/r"}
        pull_request = self.record()
        pull_request["url"] = "https://github.com/other/r/pull/1"

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
        argv = ["merge-approved-pr.py", "--pr", "https://github.com/other/r/pull/1", "--expected-head", "h"]
        with mock.patch.object(MODULE, "run", side_effect=fake_run), mock.patch.object(sys, "argv", argv), redirect_stdout(output):
            return_code = MODULE.main()
        self.assertEqual(return_code, 2)
        self.assertEqual(json.loads(output.getvalue())["disposition"], "blocked-unsafe")
        self.assertFalse(any(call[:3] == ["gh", "pr", "merge"] for call in calls))


if __name__ == "__main__":
    unittest.main()
