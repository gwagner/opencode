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


class MergeVerificationTests(unittest.TestCase):
    REPOSITORY = {"nameWithOwner": "o/r", "url": "https://github.com/o/r"}

    @staticmethod
    def completed(args, stdout="", stderr="", returncode=0):
        return subprocess.CompletedProcess(args, returncode, stdout, stderr)

    @staticmethod
    def record(state="MERGED", head="h", base="main", branch="feature/x", draft=False, mergeable="MERGEABLE"):
        return {
            "number": 1,
            "url": "https://github.com/o/r/pull/1",
            "state": state,
            "isDraft": draft,
            "mergeable": mergeable,
            "baseRefName": base,
            "headRefName": branch,
            "headRefOid": head,
            "mergedAt": "now" if state == "MERGED" else None,
            "mergeCommit": {"oid": "m"} if state == "MERGED" else None,
            "isCrossRepository": False,
            "headRepository": {"nameWithOwner": "o/r"},
        }

    def run_main(self, pull_request):
        calls = []

        def fake_run(args):
            calls.append(args)
            if args[:3] == ["gh", "auth", "status"]:
                return self.completed(args)
            if args[:3] == ["gh", "repo", "view"]:
                return self.completed(args, json.dumps(self.REPOSITORY))
            if args == ["git", "remote", "get-url", "--all", "origin"] or args == ["git", "remote", "get-url", "--push", "--all", "origin"]:
                return self.completed(args, "git@github.com:o/r.git\n")
            if args[:3] == ["gh", "pr", "view"]:
                return self.completed(args, json.dumps(pull_request))
            raise AssertionError(args)

        output = io.StringIO()
        argv = ["merge-approved-pr.py", "--pr", "1", "--expected-head", "h", "--expected-branch", "feature/x"]
        with mock.patch.object(MODULE, "run", side_effect=fake_run), mock.patch.object(sys, "argv", argv), redirect_stdout(output):
            return_code = MODULE.main()
        return return_code, json.loads(output.getvalue()), calls

    def test_exact_manual_merge_is_verified_without_merge_command(self):
        return_code, result, calls = self.run_main(self.record())
        self.assertEqual(return_code, 0)
        self.assertEqual(result["disposition"], "user-merged")
        self.assertFalse(any(call[:3] == ["gh", "pr", "merge"] for call in calls))

    def test_unchanged_open_pr_waits_for_user_merge(self):
        return_code, result, calls = self.run_main(self.record(state="OPEN"))
        self.assertEqual(return_code, 3)
        self.assertEqual(result["disposition"], "waiting-user-merge")
        self.assertFalse(any(call[:3] == ["gh", "pr", "merge"] for call in calls))

    def test_changed_head_blocks(self):
        return_code, result, _ = self.run_main(self.record(head="other"))
        self.assertEqual(return_code, 2)
        self.assertEqual(result["disposition"], "blocked-unsafe")

    def test_changed_branch_blocks(self):
        return_code, result, _ = self.run_main(self.record(branch="feature/other"))
        self.assertEqual(return_code, 2)
        self.assertEqual(result["disposition"], "blocked-unsafe")

    def test_changed_base_blocks_without_agent_mutation(self):
        return_code, result, calls = self.run_main(self.record(base="release"))
        self.assertEqual(return_code, 2)
        self.assertEqual(result["disposition"], "blocked-unsafe")
        self.assertFalse(any(call[:3] == ["gh", "pr", "merge"] for call in calls))

    def test_incomplete_merge_evidence_blocks(self):
        record = self.record()
        record["mergeCommit"] = None
        return_code, result, _ = self.run_main(record)
        self.assertEqual(return_code, 2)
        self.assertEqual(result["disposition"], "blocked-unsafe")

    def test_foreign_repository_blocks(self):
        record = self.record()
        record["url"] = "https://github.com/other/r/pull/1"
        return_code, result, calls = self.run_main(record)
        self.assertEqual(return_code, 2)
        self.assertEqual(result["disposition"], "blocked-unsafe")
        self.assertFalse(any(call[:3] == ["gh", "pr", "merge"] for call in calls))


if __name__ == "__main__":
    unittest.main()
