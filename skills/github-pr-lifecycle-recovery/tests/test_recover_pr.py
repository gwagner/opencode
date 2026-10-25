import importlib.util
import io
import json
import pathlib
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from unittest import mock


SCRIPT = pathlib.Path(__file__).parents[1] / "scripts" / "recover-pr.py"
SPEC = importlib.util.spec_from_file_location("recover_pr", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


class RecoveryTests(unittest.TestCase):
    @staticmethod
    def completed(args, stdout="", stderr="", returncode=0):
        return subprocess.CompletedProcess(args, returncode, stdout, stderr)

    @staticmethod
    def pr(state="OPEN", head="h", provenance="openchamber"):
        return {
            "state": state,
            "url": "u",
            "headRefName": "feature/x",
            "headRefOid": head,
            "baseRefName": "main",
            "body": f"OpenCode-Origin: {provenance}\n",
        }

    def test_fresh_local(self):
        self.assertEqual(MODULE.classify([], None, "h", "h", "openchamber")[0], "fresh-local")

    def test_fresh_cli_continues_to_baseline(self):
        self.assertEqual(MODULE.classify([], None, "h", "h", "cli")[1], "ownership-baseline")

    def test_unpublished_local_commits_block(self):
        self.assertEqual(MODULE.classify([], None, "local", "base", "cli")[0], "blocked-unsafe")

    def test_expected_clean_local_commit_resumes_publication(self):
        result = MODULE.classify([], None, "local", "base", "cli", "main", True, "local")
        self.assertEqual(result[:2], ("local-commit-no-remote", "pr-publication"))

    def test_expected_dirty_local_commit_waits(self):
        result = MODULE.classify([], None, "local", "base", "cli", "main", False, "local")
        self.assertEqual(result[0], "waiting-user-cleanup")

    def test_remote_without_pr(self):
        self.assertEqual(MODULE.classify([], "h", "h", "base", "openchamber", "main", True, "h")[:2], ("remote-branch-no-pr", "worktree-validation"))

    def test_openchamber_local_commit_resumes_worktree_validation(self):
        result = MODULE.classify([], None, "local", "base", "openchamber", "main", True, "local")
        self.assertEqual(result[:2], ("local-commit-no-remote", "worktree-validation"))

    def test_remote_without_pr_requires_validated_head(self):
        self.assertEqual(MODULE.classify([], "h", "h", "base", "openchamber")[0], "blocked-unsafe")

    def test_different_remote_without_pr_blocks(self):
        self.assertEqual(MODULE.classify([], "other", "h", "base", "openchamber")[0], "blocked-unsafe")

    def test_open_pr(self):
        self.assertEqual(MODULE.classify([self.pr()], "h", "h", "base", "openchamber")[:2], ("open-pull-request", "worktree-validation"))

    def test_cli_open_pr(self):
        self.assertEqual(MODULE.classify([self.pr(provenance="cli")], "h", "h", "base", "cli")[:2], ("open-pull-request", "ownership-baseline"))

    def test_dirty_open_pr_waits(self):
        result = MODULE.classify([self.pr(provenance="cli")], "h", "h", "base", "cli", "main", False)
        self.assertEqual(result[0], "waiting-user-cleanup")

    def test_dirty_closed_pr_still_blocks_unsafe_state(self):
        result = MODULE.classify([self.pr(state="CLOSED", provenance="cli")], "h", "h", "base", "cli", "main", False)
        self.assertEqual(result[0], "blocked-unsafe")

    def test_changed_head_blocks(self):
        self.assertEqual(MODULE.classify([self.pr(head="other")], "other", "h", "base", "openchamber")[0], "blocked-unsafe")

    def test_wrong_provenance_blocks(self):
        pr = self.pr()
        pr["body"] = "OpenCode-Origin: cli\n"
        self.assertEqual(MODULE.classify([pr], "h", "h", "base", "openchamber")[0], "blocked-unsafe")

    def test_recovered_merged_pr_blocks_without_owned_merge_evidence(self):
        self.assertEqual(MODULE.classify([self.pr(state="MERGED")], None, "h", "base", "openchamber")[0], "blocked-unsafe")

    def test_recovered_merged_pr_with_remote_branch_still_blocks(self):
        result = MODULE.classify([self.pr(state="MERGED")], "h", "h", "base", "openchamber")
        self.assertEqual(result[0], "blocked-unsafe")

    def test_conflicting_provenance_or_issue_marker_blocks(self):
        conflicting = self.pr(provenance="cli")
        conflicting["body"] += "OpenCode-Origin: openchamber\n"
        self.assertEqual(MODULE.classify([conflicting], "h", "h", "base", "cli")[0], "blocked-unsafe")
        issue_marked = self.pr(provenance="cli")
        issue_marked["body"] += "Refs #7\n"
        self.assertEqual(MODULE.classify([issue_marked], "h", "h", "base", "cli")[0], "blocked-unsafe")

    def test_non_main_base_blocks(self):
        self.assertEqual(MODULE.classify([], None, "h", "base", "cli", "release")[0], "blocked-unsafe")

    def test_remote_head_requires_one_exact_ref(self):
        self.assertEqual(MODULE.parse_remote_head("", "feature/x"), (None, True))
        self.assertEqual(MODULE.parse_remote_head("h\trefs/heads/feature/x\n", "feature/x"), ("h", True))
        self.assertEqual(MODULE.parse_remote_head("h refs/heads/feature/x\nother refs/heads/feature/x\n", "feature/x"), (None, False))
        self.assertEqual(MODULE.parse_remote_head("h refs/heads/feature/other\n", "feature/x"), (None, False))

    def test_fork_pull_request_blocks_before_remote_branch_lookup(self):
        calls = []
        repository = {"nameWithOwner": "o/r", "url": "https://github.com/o/r"}
        pull_request = {
            "number": 1,
            "state": "OPEN",
            "url": "https://github.com/o/r/pull/1",
            "title": "x",
            "body": "OpenCode-Origin: openchamber\n",
            "baseRefName": "main",
            "headRefName": "feature/x",
            "headRefOid": "h",
            "mergedAt": None,
            "mergeCommit": None,
            "isCrossRepository": True,
            "headRepository": {"nameWithOwner": "fork/r"},
        }

        def fake_run(args):
            calls.append(args)
            if args == ["git", "branch", "--show-current"]:
                return self.completed(args, "feature/x\n")
            if args == ["git", "rev-parse", "HEAD"]:
                return self.completed(args, "h\n")
            if args == ["git", "rev-parse", "main"]:
                return self.completed(args, "base\n")
            if args == ["git", "status", "--porcelain=v1"]:
                return self.completed(args)
            if args[:3] == ["gh", "auth", "status"]:
                return self.completed(args)
            if args[:3] == ["gh", "repo", "view"]:
                return self.completed(args, json.dumps(repository))
            if args == ["git", "remote", "get-url", "--all", "origin"]:
                return self.completed(args, "git@github.com:o/r.git\n")
            if args == ["git", "remote", "get-url", "--push", "--all", "origin"]:
                return self.completed(args, "git@github.com:o/r.git\n")
            if args[:3] == ["gh", "pr", "list"]:
                return self.completed(args, json.dumps([pull_request]))
            raise AssertionError(args)

        output = io.StringIO()
        argv = ["recover-pr.py", "--provenance", "openchamber"]
        with mock.patch.object(MODULE, "run", side_effect=fake_run), mock.patch.object(sys, "argv", argv), redirect_stdout(output):
            return_code = MODULE.main()
        self.assertEqual(return_code, 2)
        self.assertEqual(json.loads(output.getvalue())["disposition"], "blocked-unsafe")
        self.assertFalse(any(call[:2] == ["git", "ls-remote"] for call in calls))


if __name__ == "__main__":
    unittest.main()
