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
    ACTOR = "lifecycle-user"

    def test_fresh_start(self):
        self.assertEqual(MODULE.classify("OPEN", [], "not-applicable", [], self.ACTOR)[0], "fresh-start")

    def test_remote_branch_without_pr(self):
        self.assertEqual(MODULE.classify("OPEN", [], "present-exact", [], self.ACTOR)[0], "remote-branch-no-pr")

    def test_open_pr(self):
        pr = {"state": "OPEN", "url": "u", "headRefName": "feature/x", "headRefOid": "h"}
        self.assertEqual(MODULE.classify("OPEN", [pr], "present-exact", [], self.ACTOR)[:2], ("open-pull-request", "worktree-validation"))

    def test_open_pr_without_remote_branch_blocks(self):
        pr = {"state": "OPEN", "url": "u", "headRefName": "feature/x", "headRefOid": "h"}
        self.assertEqual(MODULE.classify("OPEN", [pr], "already-absent", [], self.ACTOR)[0], "blocked-unsafe")

    def test_incomplete_pr_identity_blocks(self):
        pr = {"state": "OPEN", "url": "u", "headRefOid": "h"}
        self.assertEqual(MODULE.classify("OPEN", [pr], "not-applicable", [], self.ACTOR)[0], "blocked-unsafe")

    def test_multiple_prs_block(self):
        pr = {"state": "OPEN"}
        self.assertEqual(MODULE.classify("OPEN", [pr, pr], "not-applicable", [], self.ACTOR)[0], "blocked-unsafe")

    def test_closed_issue_without_merged_pr_blocks(self):
        self.assertEqual(MODULE.classify("CLOSED", [], "not-applicable", [], self.ACTOR)[0], "blocked-unsafe")

    def test_merged_pr_requires_current_evidence(self):
        pr = {"state": "MERGED", "url": "u", "headRefName": "feature/x", "headRefOid": "h", "mergeCommit": {"oid": "m"}}
        self.assertEqual(MODULE.classify("OPEN", [pr], "already-absent", [], self.ACTOR)[0], "blocked-unsafe")

    def test_merged_pr_with_remote_branch_resumes_cleanup(self):
        pr = {"state": "MERGED", "url": "u", "headRefName": "feature/x", "headRefOid": "h", "mergeCommit": {"oid": "m"}}
        result = MODULE.classify("OPEN", [pr], "present-exact", [], self.ACTOR)
        self.assertEqual(result[:2], ("merged-needs-cleanup", "remote-branch-cleanup"))

    def test_duplicate_exact_current_evidence_is_recoverable(self):
        pr = {"state": "MERGED", "url": "u", "headRefName": "feature/x", "headRefOid": "h", "mergeCommit": {"oid": "m"}}
        comment = {
            "author": {"login": self.ACTOR},
            "body": "Lifecycle evidence: current\nDelivered outcome: fixed\nPull request: u\nHead commit: h\nDelegate project-validation: passed\nRequired checks: passed",
        }
        self.assertEqual(MODULE.classify("OPEN", [pr], "already-absent", [comment, comment], self.ACTOR)[0], "merged-needs-completion")

    def test_conflicting_current_evidence_blocks(self):
        pr = {"state": "MERGED", "url": "u", "headRefName": "feature/x", "headRefOid": "h", "mergeCommit": {"oid": "m"}}
        first = {
            "author": {"login": self.ACTOR},
            "body": "Lifecycle evidence: current\nDelivered outcome: first\nPull request: u\nHead commit: h\nDelegate project-validation: passed\nRequired checks: passed",
        }
        second = dict(first, body=first["body"].replace("Delivered outcome: first", "Delivered outcome: second"))
        self.assertEqual(MODULE.classify("OPEN", [pr], "already-absent", [first, second], self.ACTOR)[0], "blocked-unsafe")

    def test_exact_completion_evidence_resumes_close(self):
        pr = {"state": "MERGED", "url": "u", "headRefName": "feature/x", "headRefOid": "h", "mergeCommit": {"oid": "m"}}
        current = {
            "author": {"login": self.ACTOR},
            "body": "Lifecycle evidence: current\nDelivered outcome: fixed\nPull request: u\nHead commit: h\nDelegate project-validation: passed\nRequired checks: passed",
        }
        comment = {
            "author": {"login": self.ACTOR},
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
        self.assertEqual(MODULE.classify("OPEN", [pr], "already-absent", [current, comment], self.ACTOR)[0], "merged-needs-close")

    def test_duplicate_exact_completion_evidence_is_recoverable(self):
        pr = {"state": "MERGED", "url": "u", "headRefName": "feature/x", "headRefOid": "h", "mergeCommit": {"oid": "m"}}
        current = {
            "author": {"login": self.ACTOR},
            "body": "Lifecycle evidence: current\nDelivered outcome: fixed\nPull request: u\nHead commit: h\nDelegate project-validation: passed\nRequired checks: passed",
        }
        completion = {
            "author": {"login": self.ACTOR},
            "body": "Lifecycle completion: merged-pr\nPull request: u\nHead commit: h\nMerge result: merged\nDelegate project-validation: passed\nRequired checks: passed\nRemote cleanup: deleted",
        }
        self.assertEqual(MODULE.classify("OPEN", [pr], "already-absent", [current, completion, completion], self.ACTOR)[0], "merged-needs-close")

    def test_conflicting_completion_evidence_blocks(self):
        pr = {"state": "MERGED", "url": "u", "headRefName": "feature/x", "headRefOid": "h", "mergeCommit": {"oid": "m"}}
        current = {
            "author": {"login": self.ACTOR},
            "body": "Lifecycle evidence: current\nDelivered outcome: fixed\nPull request: u\nHead commit: h\nDelegate project-validation: passed\nRequired checks: passed",
        }
        first = {
            "author": {"login": self.ACTOR},
            "body": "Lifecycle completion: merged-pr\nPull request: u\nHead commit: h\nMerge result: merged\nDelegate project-validation: passed\nRequired checks: passed\nRemote cleanup: deleted",
        }
        second = dict(first, body=first["body"].replace("Remote cleanup: deleted", "Remote cleanup: already-absent"))
        self.assertEqual(MODULE.classify("OPEN", [pr], "already-absent", [current, first, second], self.ACTOR)[0], "blocked-unsafe")

    def test_closed_issue_is_terminal_only_with_complete_evidence(self):
        pr = {"state": "MERGED", "url": "u", "headRefName": "feature/x", "headRefOid": "h", "mergeCommit": {"oid": "m"}}
        current = {
            "author": {"login": self.ACTOR},
            "body": "Lifecycle evidence: current\nDelivered outcome: fixed\nPull request: u\nHead commit: h\nDelegate project-validation: passed\nRequired checks: passed",
        }
        completion = {
            "author": {"login": self.ACTOR},
            "body": "\n".join([
                "Lifecycle completion: merged-pr",
                "Pull request: u",
                "Head commit: h",
                "Merge result: merged",
                "Delegate project-validation: passed",
                "Required checks: passed",
                "Remote cleanup: deleted",
            ])
        }
        self.assertEqual(MODULE.classify("CLOSED", [pr], "already-absent", [current, completion], self.ACTOR)[0], "closed")

    def test_partial_completion_evidence_does_not_resume_close(self):
        pr = {"state": "MERGED", "url": "u", "headRefName": "feature/x", "headRefOid": "h", "mergeCommit": {"oid": "m"}}
        current = {
            "author": {"login": self.ACTOR},
            "body": "Lifecycle evidence: current\nDelivered outcome: fixed\nPull request: u\nHead commit: h\nDelegate project-validation: passed\nRequired checks: passed",
        }
        partial = {"author": {"login": self.ACTOR}, "body": "Lifecycle completion: merged-pr\nPull request: u\nHead commit: h"}
        self.assertEqual(MODULE.classify("OPEN", [pr], "already-absent", [current, partial], self.ACTOR)[0], "merged-needs-completion")

    def test_foreign_comment_author_does_not_supply_current_evidence(self):
        pr = {"state": "MERGED", "url": "u", "headRefName": "feature/x", "headRefOid": "h", "mergeCommit": {"oid": "m"}}
        comment = {
            "author": {"login": "other"},
            "body": "Lifecycle evidence: current\nDelivered outcome: fixed\nPull request: u\nHead commit: h\nDelegate project-validation: passed\nRequired checks: passed",
        }
        self.assertEqual(MODULE.classify("OPEN", [pr], "already-absent", [comment], self.ACTOR)[0], "blocked-unsafe")

    def test_merged_pr_requires_merge_commit_evidence(self):
        pr = {"state": "MERGED", "url": "u", "headRefName": "feature/x", "headRefOid": "h"}
        self.assertEqual(MODULE.classify("OPEN", [pr], "already-absent", [], self.ACTOR)[0], "blocked-unsafe")

    def test_origin_and_pull_request_repositories_require_checkout_repository(self):
        repository = {"nameWithOwner": "o/r", "url": "https://github.com/o/r"}
        self.assertTrue(MODULE.remote_urls_match(repository, "git@github.com:o/r.git\nhttps://github.com/o/r.git\n"))
        self.assertFalse(MODULE.remote_urls_match(repository, "git@github.com:o/r.git\ngit@github.com:other/r.git\n"))
        pull_request = {
            "number": 1,
            "url": "https://github.com/o/r/pull/1",
            "isCrossRepository": False,
            "headRepository": {"nameWithOwner": "o/r"},
        }
        self.assertTrue(MODULE.pull_request_repositories_match(repository, pull_request))
        pull_request["isCrossRepository"] = True
        pull_request["headRepository"] = {"nameWithOwner": "fork/r"}
        self.assertFalse(MODULE.pull_request_repositories_match(repository, pull_request))

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
            "mergeCommit": {"oid": "merge"},
            "isCrossRepository": False,
            "headRepository": {"nameWithOwner": "o/r"},
        }
        current = {
            "author": {"login": self.ACTOR},
            "body": "Lifecycle evidence: current\nDelivered outcome: fixed\nPull request: https://github.com/o/r/pull/33\nHead commit: abc\nDelegate project-validation: passed\nRequired checks: passed",
        }
        issue = {"number": 7, "title": "x", "state": "OPEN", "url": "https://github.com/o/r/issues/7", "comments": [current]}
        calls = []

        def fake_run(args):
            calls.append(args)
            if args[:3] == ["gh", "auth", "status"]:
                return self.completed(args)
            if args[:3] == ["gh", "repo", "view"]:
                return self.completed(args, json.dumps({"nameWithOwner": "o/r", "url": "https://github.com/o/r"}))
            if args == ["git", "remote", "get-url", "--all", "origin"]:
                return self.completed(args, "git@github.com:o/r.git\n")
            if args == ["git", "remote", "get-url", "--push", "--all", "origin"]:
                return self.completed(args, "git@github.com:o/r.git\n")
            if args == ["gh", "api", "--hostname", "github.com", "user", "--jq", ".login"]:
                return self.completed(args, self.ACTOR + "\n")
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

    def test_foreign_issue_blocks_before_pull_request_search(self):
        calls = []
        issue = {
            "number": 7,
            "title": "foreign",
            "state": "OPEN",
            "url": "https://github.com/other/r/issues/7",
            "comments": [],
        }

        def fake_run(args):
            calls.append(args)
            if args[:3] == ["gh", "auth", "status"]:
                return self.completed(args)
            if args[:3] == ["gh", "repo", "view"]:
                return self.completed(args, json.dumps({"nameWithOwner": "o/r", "url": "https://github.com/o/r"}))
            if args == ["git", "remote", "get-url", "--all", "origin"]:
                return self.completed(args, "git@github.com:o/r.git\n")
            if args == ["git", "remote", "get-url", "--push", "--all", "origin"]:
                return self.completed(args, "git@github.com:o/r.git\n")
            if args == ["gh", "api", "--hostname", "github.com", "user", "--jq", ".login"]:
                return self.completed(args, self.ACTOR + "\n")
            if args[:3] == ["gh", "issue", "view"]:
                return self.completed(args, json.dumps(issue))
            raise AssertionError(args)

        output = io.StringIO()
        argv = ["recover-lifecycle.py", "--issue", "https://github.com/other/r/issues/7"]
        with mock.patch.object(MODULE, "run", side_effect=fake_run), mock.patch.object(sys, "argv", argv), redirect_stdout(output):
            return_code = MODULE.main()
        self.assertEqual(return_code, 2)
        self.assertEqual(json.loads(output.getvalue())["disposition"], "blocked-unsafe")
        self.assertFalse(any(call[:3] == ["gh", "pr", "list"] for call in calls))

    def test_remote_branch_without_pr_requires_current_branch(self):
        issue = {"number": 7, "title": "x", "state": "OPEN", "url": "https://github.com/o/r/issues/7", "comments": []}

        def fake_run(args):
            if args[:3] == ["gh", "auth", "status"]:
                return self.completed(args)
            if args[:3] == ["gh", "repo", "view"]:
                return self.completed(args, json.dumps({"nameWithOwner": "o/r", "url": "https://github.com/o/r"}))
            if args == ["git", "remote", "get-url", "--all", "origin"]:
                return self.completed(args, "git@github.com:o/r.git\n")
            if args == ["git", "remote", "get-url", "--push", "--all", "origin"]:
                return self.completed(args, "git@github.com:o/r.git\n")
            if args == ["gh", "api", "--hostname", "github.com", "user", "--jq", ".login"]:
                return self.completed(args, self.ACTOR + "\n")
            if args[:3] == ["gh", "issue", "view"]:
                return self.completed(args, json.dumps(issue))
            if args[:3] == ["gh", "pr", "list"]:
                return self.completed(args, "[]")
            if args[:4] == ["git", "ls-remote", "--heads", "origin"]:
                return self.completed(args, "abc\trefs/heads/feature/real\n")
            if args == ["git", "rev-parse", "HEAD"]:
                return self.completed(args, "abc\n")
            if args == ["git", "branch", "--show-current"]:
                return self.completed(args, "feature/other\n")
            raise AssertionError(args)

        output = io.StringIO()
        argv = ["recover-lifecycle.py", "--issue", "7", "--branch", "feature/real"]
        with mock.patch.object(MODULE, "run", side_effect=fake_run), mock.patch.object(sys, "argv", argv), redirect_stdout(output):
            return_code = MODULE.main()
        self.assertEqual(return_code, 2)
        self.assertEqual(json.loads(output.getvalue())["disposition"], "blocked-unsafe")


if __name__ == "__main__":
    unittest.main()
