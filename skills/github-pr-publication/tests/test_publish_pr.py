import importlib.util
import io
import json
import pathlib
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from unittest import mock

TEST_SUPPORT = pathlib.Path(__file__).resolve().parents[2] / "tests"
sys.path.insert(0, str(TEST_SUPPORT))
from lifecycle_policy_test_support import LifecycleSnapshotTestCase


SCRIPT = pathlib.Path(__file__).parents[1] / "scripts" / "publish-pr.py"
SPEC = importlib.util.spec_from_file_location("publish_pr", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


class PublicationTests(LifecycleSnapshotTestCase):
    REPOSITORY = {"nameWithOwner": "o/r", "url": "https://github.com/o/r"}

    @staticmethod
    def completed(args, stdout="", stderr="", returncode=0):
        return subprocess.CompletedProcess(args, returncode, stdout, stderr)

    @classmethod
    def pull_request(cls, **changes):
        record = {
            "number": 1,
            "state": "OPEN",
            "url": "https://github.com/o/r/pull/1",
            "title": "x",
            "body": "OpenCode-Origin: cli\n",
            "baseRefName": "main",
            "headRefName": "feature/x",
            "headRefOid": "h",
            "isCrossRepository": False,
            "headRepository": {"nameWithOwner": "o/r"},
        }
        record.update(changes)
        return record

    def test_issue_body_has_reference(self):
        body = MODULE.canonical_body("github-issue", "Summary", "42")
        self.assertIn("OpenCode-Origin: github-issue", body)
        self.assertIn("Refs #42", body)

    def test_non_issue_body_has_no_reference(self):
        body = MODULE.canonical_body("cli", "Summary", None)
        self.assertNotIn("Refs #", body)

    def test_conflicting_reserved_markers_do_not_match(self):
        record = self.pull_request(body="OpenCode-Origin: cli\nOpenCode-Origin: github-issue\nRefs #7\n")
        self.assertFalse(MODULE.marker_matches(record, "cli", None))
        self.assertFalse(MODULE.marker_matches(record, "github-issue", "7"))
        self.assertTrue(MODULE.has_reserved_markers("summary\nRefs #7\n"))

    def test_no_match_creates(self):
        self.assertEqual(MODULE.select_pull_request([], self.REPOSITORY, "cli", None, "main", "feature/x"), ("create", None))

    def test_multiple_matches_block(self):
        action, record = MODULE.select_pull_request([{"state": "OPEN"}, {"state": "OPEN"}], self.REPOSITORY, "cli", None, "main", "feature/x")
        self.assertEqual(action, "blocked-unsafe")
        self.assertIsNone(record)

    def test_closed_match_blocks(self):
        action, _ = MODULE.select_pull_request([{"state": "CLOSED"}], self.REPOSITORY, "cli", None, "main", "feature/x")
        self.assertEqual(action, "blocked-unsafe")

    def test_reused_pr_requires_exact_provenance(self):
        record = self.pull_request()
        self.assertEqual(MODULE.select_pull_request([record], self.REPOSITORY, "cli", None, "main", "feature/x")[0], "reuse")
        self.assertEqual(MODULE.select_pull_request([record], self.REPOSITORY, "openchamber", None, "main", "feature/x")[0], "blocked-unsafe")

    def test_wrong_base_reuse_blocks(self):
        record = self.pull_request(baseRefName="release")
        self.assertEqual(MODULE.select_pull_request([record], self.REPOSITORY, "cli", None, "main", "feature/x")[0], "blocked-unsafe")

    def test_fork_reuse_blocks(self):
        record = self.pull_request(isCrossRepository=True, headRepository={"nameWithOwner": "fork/r"})
        self.assertEqual(MODULE.select_pull_request([record], self.REPOSITORY, "cli", None, "main", "feature/x")[0], "blocked-unsafe")

    def test_non_fast_forward_push_is_unsafe(self):
        self.assertEqual(MODULE.classify_push_failure("rejected (non-fast-forward)"), ("blocked", "blocked-unsafe"))

    def test_validated_head_mismatch_blocks_before_external_commands(self):
        argv = ["publish-pr.py", "--provenance", "cli", "--expected-head", "h", "--validated-head", "other", "--title", "x", "--body", "x"]
        output = io.StringIO()
        with mock.patch.object(MODULE, "run", side_effect=AssertionError("unexpected command")), mock.patch.object(sys, "argv", self.with_policy(argv)), redirect_stdout(output):
            return_code = MODULE.main()
        self.assertEqual(return_code, 2)
        self.assertEqual(json.loads(output.getvalue())["disposition"], "blocked-unsafe")

    def test_publication_without_authorization_is_denied_before_external_commands(self):
        argv = ["publish-pr.py", "--provenance", "cli", "--expected-head", "h", "--validated-head", "h", "--title", "x", "--body", "x"]
        output = io.StringIO()
        with mock.patch.object(MODULE, "run", side_effect=AssertionError("publication must remain local and committed")), mock.patch.object(sys, "argv", self.with_policy(argv)), redirect_stdout(output):
            return_code = MODULE.main()
        result = json.loads(output.getvalue())
        self.assertEqual(return_code, 2)
        self.assertEqual(result["disposition"], "blocked-unsafe")
        self.assertEqual(result["blocker"], "explicit publication authorization is required")

    def test_publication_pushes_only_validated_commit_refspec(self):
        calls = []
        list_results = iter([[], [self.pull_request()]])

        def fake_run(args, *, input_text=None):
            calls.append(args)
            if args[:3] == ["gh", "auth", "status"]:
                return self.completed(args)
            if args[:3] == ["gh", "repo", "view"]:
                return self.completed(args, json.dumps(self.REPOSITORY))
            if args == ["git", "remote", "get-url", "--all", "origin"] or args == ["git", "remote", "get-url", "--push", "--all", "origin"]:
                return self.completed(args, "git@github.com:o/r.git\n")
            if args == ["git", "branch", "--show-current"]:
                return self.completed(args, "feature/x\n")
            if args == ["git", "rev-parse", "HEAD"]:
                return self.completed(args, "h\n")
            if args == ["git", "status", "--porcelain=v1"]:
                return self.completed(args)
            if args[:3] == ["gh", "pr", "list"]:
                return self.completed(args, json.dumps(next(list_results)))
            if args[:2] == ["git", "push"]:
                return self.completed(args)
            if args[:4] == ["git", "ls-remote", "--heads", "origin"]:
                return self.completed(args, "h\trefs/heads/feature/x\n")
            if args[:3] == ["gh", "pr", "create"]:
                return self.completed(args, "https://github.com/o/r/pull/1\n")
            raise AssertionError(args)

        argv = ["publish-pr.py", "--provenance", "cli", "--expected-head", "h", "--validated-head", "h", "--title", "x", "--body", "x", "--authorize-publication"]
        output = io.StringIO()
        with mock.patch.object(MODULE, "run", side_effect=fake_run), mock.patch.object(sys, "argv", self.with_policy(argv)), redirect_stdout(output):
            return_code = MODULE.main()
        self.assertEqual(return_code, 0)
        self.assertIn(["git", "push", "--set-upstream", "origin", "h:refs/heads/feature/x"], calls)
        self.assertEqual(json.loads(output.getvalue())["disposition"], "created")

    def test_failed_create_recovers_exact_created_pr(self):
        calls = []
        list_results = iter([[], [self.pull_request()]])

        def fake_run(args, *, input_text=None):
            calls.append(args)
            if args[:3] == ["gh", "auth", "status"]:
                return self.completed(args)
            if args[:3] == ["gh", "repo", "view"]:
                return self.completed(args, json.dumps(self.REPOSITORY))
            if args[:3] == ["gh", "pr", "list"]:
                return self.completed(args, json.dumps(next(list_results)))
            if args[:3] == ["gh", "pr", "create"]:
                return self.completed(args, stderr="connection lost", returncode=1)
            if args == ["git", "branch", "--show-current"]:
                return self.completed(args, "feature/x\n")
            if args == ["git", "rev-parse", "HEAD"]:
                return self.completed(args, "h\n")
            if args == ["git", "status", "--porcelain=v1"] or args[:2] == ["git", "push"]:
                return self.completed(args)
            if args[:4] == ["git", "ls-remote", "--heads", "origin"]:
                return self.completed(args, "h\trefs/heads/feature/x\n")
            if args[:3] == ["git", "remote", "get-url"]:
                return self.completed(args, "git@github.com:o/r.git\n")
            raise AssertionError(args)

        argv = ["publish-pr.py", "--provenance", "cli", "--expected-head", "h", "--validated-head", "h", "--title", "x", "--body", "x", "--authorize-publication"]
        output = io.StringIO()
        with mock.patch.object(MODULE, "run", side_effect=fake_run), mock.patch.object(sys, "argv", self.with_policy(argv)), redirect_stdout(output):
            return_code = MODULE.main()
        result = json.loads(output.getvalue())
        self.assertEqual(return_code, 0)
        self.assertEqual(result["disposition"], "created")
        self.assertEqual(result["evidence"]["create_attribution"], "uncertain")

    def test_failed_push_recovers_exact_remote_and_pr(self):
        records = iter([[self.pull_request()], [self.pull_request()]])

        def fake_run(args, *, input_text=None):
            if args[:3] == ["gh", "auth", "status"]:
                return self.completed(args)
            if args[:3] == ["gh", "repo", "view"]:
                return self.completed(args, json.dumps(self.REPOSITORY))
            if args[:3] == ["gh", "pr", "list"]:
                return self.completed(args, json.dumps(next(records)))
            if args == ["git", "branch", "--show-current"]:
                return self.completed(args, "feature/x\n")
            if args == ["git", "rev-parse", "HEAD"]:
                return self.completed(args, "h\n")
            if args == ["git", "status", "--porcelain=v1"]:
                return self.completed(args)
            if args[:2] == ["git", "push"]:
                return self.completed(args, stderr="transport reset", returncode=1)
            if args[:4] == ["git", "ls-remote", "--heads", "origin"]:
                return self.completed(args, "h\trefs/heads/feature/x\n")
            if args[:3] == ["git", "remote", "get-url"]:
                return self.completed(args, "git@github.com:o/r.git\n")
            raise AssertionError(args)

        argv = ["publish-pr.py", "--provenance", "cli", "--expected-head", "h", "--validated-head", "h", "--title", "x", "--body", "x", "--authorize-publication"]
        output = io.StringIO()
        with mock.patch.object(MODULE, "run", side_effect=fake_run), mock.patch.object(sys, "argv", self.with_policy(argv)), redirect_stdout(output):
            return_code = MODULE.main()
        result = json.loads(output.getvalue())
        self.assertEqual(return_code, 0)
        self.assertEqual(result["disposition"], "reused")
        self.assertEqual(result["evidence"]["push_attribution"], "uncertain")


if __name__ == "__main__":
    unittest.main()
