import importlib.util
import io
import json
import pathlib
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from unittest import mock


SCRIPT = pathlib.Path(__file__).parents[1] / "scripts" / "recover-lifecycle.py"
SPEC = importlib.util.spec_from_file_location("recover_lifecycle", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


class RecoveryTests(unittest.TestCase):
    def test_fresh_start(self):
        self.assertEqual(MODULE.classify("OPEN", [], "not-applicable", [])[0], "fresh-start")

    def test_remote_branch_without_pr(self):
        self.assertEqual(MODULE.classify("OPEN", [], "present-exact", [])[0], "remote-branch-no-pr")

    def test_open_pr(self):
        pr = {"state": "OPEN", "url": "u", "headRefName": "feature/x", "headRefOid": "h"}
        self.assertEqual(MODULE.classify("OPEN", [pr], "present-exact", [])[0], "open-pull-request")

    def test_open_pr_without_remote_branch_blocks(self):
        pr = {"state": "OPEN", "url": "u", "headRefName": "feature/x", "headRefOid": "h"}
        self.assertEqual(MODULE.classify("OPEN", [pr], "already-absent", [])[0], "blocked-unsafe")

    def test_incomplete_pr_identity_blocks(self):
        pr = {"state": "OPEN", "url": "u", "headRefOid": "h"}
        self.assertEqual(MODULE.classify("OPEN", [pr], "not-applicable", [])[0], "blocked-unsafe")

    def test_multiple_prs_block(self):
        pr = {"state": "OPEN"}
        self.assertEqual(MODULE.classify("OPEN", [pr, pr], "not-applicable", [])[0], "blocked-unsafe")

    def test_closed_issue_is_terminal(self):
        self.assertEqual(MODULE.classify("CLOSED", [], "not-applicable", [])[0], "closed")

    def test_merged_pr_requires_current_evidence(self):
        pr = {"state": "MERGED", "url": "u", "headRefName": "feature/x", "headRefOid": "h"}
        self.assertEqual(MODULE.classify("OPEN", [pr], "already-absent", [])[0], "blocked-unsafe")

    def test_merged_pr_with_remote_branch_resumes_cleanup(self):
        pr = {"state": "MERGED", "url": "u", "headRefName": "feature/x", "headRefOid": "h"}
        result = MODULE.classify("OPEN", [pr], "present-exact", [])
        self.assertEqual(result[:2], ("merged-needs-cleanup", "remote-branch-cleanup"))

    def test_duplicate_exact_current_evidence_is_recoverable(self):
        pr = {"state": "MERGED", "url": "u", "headRefName": "feature/x", "headRefOid": "h"}
        comment = {
            "body": "Lifecycle evidence: current\nu\nHead commit: h\nDelegate project-validation: passed\nRequired checks: passed"
        }
        self.assertEqual(MODULE.classify("OPEN", [pr], "already-absent", [comment, comment])[0], "merged-needs-completion")

    def test_exact_completion_evidence_resumes_close(self):
        pr = {"state": "MERGED", "url": "u", "headRefName": "feature/x", "headRefOid": "h"}
        current = {
            "body": "Lifecycle evidence: current\nu\nHead commit: h\nDelegate project-validation: passed\nRequired checks: passed"
        }
        comment = {
            "body": "\n".join([
                "Lifecycle completion: merged-pr",
                "Pull request: u",
                "Head commit: h",
                "Merge result: merged",
                "Delegate project-validation: passed",
                "Required checks: passed",
                "Remote cleanup: already-absent",
            ])
        }
        self.assertEqual(MODULE.classify("OPEN", [pr], "already-absent", [current, comment])[0], "merged-needs-close")

    def test_partial_completion_evidence_does_not_resume_close(self):
        pr = {"state": "MERGED", "url": "u", "headRefName": "feature/x", "headRefOid": "h"}
        current = {
            "body": "Lifecycle evidence: current\nu\nHead commit: h\nDelegate project-validation: passed\nRequired checks: passed"
        }
        partial = {"body": "Lifecycle completion: merged-pr\nPull request: u\nHead commit: h"}
        self.assertEqual(MODULE.classify("OPEN", [pr], "already-absent", [current, partial])[0], "merged-needs-completion")

    @staticmethod
    def completed(args, stdout="", stderr="", returncode=0):
        return subprocess.CompletedProcess(args, returncode, stdout, stderr)

    def run_main(self, supplied_branch=None, remote_stdout=""):
        pr = {
            "number": 33,
            "state": "MERGED",
            "url": "https://github.com/o/r/pull/33",
            "title": "x",
            "body": "Refs #7\nOpenCode-Origin: github-issue\n",
            "baseRefName": "main",
            "headRefName": "feature/real",
            "headRefOid": "abc",
            "mergedAt": "now",
        }
        current = {
            "body": "Lifecycle evidence: current\nhttps://github.com/o/r/pull/33\nHead commit: abc\nDelegate project-validation: passed\nRequired checks: passed"
        }
        issue = {"number": 7, "title": "x", "state": "OPEN", "url": "https://github.com/o/r/issues/7", "comments": [current]}
        calls = []

        def fake_run(args):
            calls.append(args)
            if args[:3] == ["gh", "auth", "status"]:
                return self.completed(args)
            if args[:3] == ["gh", "repo", "view"]:
                return self.completed(args, json.dumps({"nameWithOwner": "o/r", "url": "https://github.com/o/r"}))
            if args[:3] == ["gh", "issue", "view"]:
                return self.completed(args, json.dumps(issue))
            if args[:3] == ["gh", "pr", "list"]:
                return self.completed(args, json.dumps([pr]))
            if args[:4] == ["git", "ls-remote", "--heads", "origin"]:
                return self.completed(args, remote_stdout)
            if args == ["git", "rev-parse", "HEAD"]:
                return self.completed(args, "abc\n")
            raise AssertionError(args)

        argv = ["recover-lifecycle.py", "--issue", "7"]
        if supplied_branch:
            argv.extend(["--branch", supplied_branch])
        output = io.StringIO()
        with mock.patch.object(MODULE, "run", side_effect=fake_run), mock.patch.object(sys, "argv", argv), redirect_stdout(output):
            return_code = MODULE.main()
        return return_code, json.loads(output.getvalue()), calls

    def test_merged_pr_derives_present_canonical_branch_without_argument(self):
        return_code, result, calls = self.run_main(remote_stdout="abc\trefs/heads/feature/real\n")
        self.assertEqual(return_code, 0)
        self.assertEqual(result["disposition"], "merged-needs-cleanup")
        self.assertIn(["git", "ls-remote", "--heads", "origin", "feature/real"], calls)

    def test_conflicting_supplied_branch_blocks_before_remote_lookup(self):
        return_code, result, calls = self.run_main(supplied_branch="feature/wrong")
        self.assertEqual(return_code, 2)
        self.assertEqual(result["disposition"], "blocked-unsafe")
        self.assertFalse(any(call[:2] == ["git", "ls-remote"] for call in calls))

    def test_absent_canonical_branch_carries_cleanup_evidence(self):
        return_code, result, _ = self.run_main(remote_stdout="")
        self.assertEqual(return_code, 0)
        self.assertEqual(result["disposition"], "merged-needs-completion")
        self.assertEqual(result["evidence"]["cleanup_disposition"], "already-absent")


if __name__ == "__main__":
    unittest.main()
