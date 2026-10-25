import importlib.util
import io
import json
import pathlib
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from unittest import mock


SCRIPT = pathlib.Path(__file__).parents[1] / "scripts" / "cleanup-remote-branch.py"
SPEC = importlib.util.spec_from_file_location("cleanup_remote_branch", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


class CleanupTests(unittest.TestCase):
    @staticmethod
    def completed(args, stdout="", stderr="", returncode=0):
        return subprocess.CompletedProcess(args, returncode, stdout, stderr)

    def test_absent_remote_is_valid(self):
        self.assertEqual(MODULE.parse_remote_head(""), (None, True))

    def test_one_remote_head_is_valid(self):
        self.assertEqual(MODULE.parse_remote_head("abc\trefs/heads/feature/x\n"), ("abc", True))

    def test_multiple_remote_heads_are_ambiguous(self):
        self.assertEqual(MODULE.parse_remote_head("a refs/heads/x\nb refs/heads/y\n"), (None, False))

    def test_wrong_remote_ref_is_ambiguous(self):
        self.assertEqual(MODULE.parse_remote_head("abc refs/heads/other\n", "feature/x"), (None, False))

    def test_exact_merged_identity_matches(self):
        record = {
            "number": 1,
            "url": "u",
            "state": "MERGED",
            "body": "OpenCode-Origin: cli\n",
            "baseRefName": "main",
            "headRefName": "feature/x",
            "headRefOid": "h",
        }
        self.assertTrue(MODULE.merged_identity_matches(record, "h", "main", "cli"))

    def test_provenance_mismatch_blocks_identity(self):
        record = {
            "number": 1,
            "url": "u",
            "state": "MERGED",
            "body": "OpenCode-Origin: openchamber\n",
            "baseRefName": "main",
            "headRefName": "feature/x",
            "headRefOid": "h",
        }
        self.assertFalse(MODULE.merged_identity_matches(record, "h", "main", "cli"))

    def test_repository_identity_requires_exact_pr_url(self):
        repository = {"nameWithOwner": "o/r", "url": "https://github.com/o/r"}
        local = {"number": 1, "url": "https://github.com/o/r/pull/1"}
        foreign = {"number": 1, "url": "https://github.com/other/r/pull/1"}
        self.assertTrue(MODULE.repository_matches(repository, local))
        self.assertFalse(MODULE.repository_matches(repository, foreign))

    def test_foreign_repository_blocks_before_branch_deletion(self):
        calls = []
        repository = {"nameWithOwner": "o/r", "url": "https://github.com/o/r"}
        pull_request = {
            "number": 1,
            "url": "https://github.com/other/r/pull/1",
            "state": "MERGED",
            "body": "OpenCode-Origin: cli\n",
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
        argv = [
            "cleanup-remote-branch.py",
            "--pr",
            "https://github.com/other/r/pull/1",
            "--expected-head",
            "h",
            "--provenance",
            "cli",
        ]
        with mock.patch.object(MODULE, "run", side_effect=fake_run), mock.patch.object(sys, "argv", argv), redirect_stdout(output):
            return_code = MODULE.main()
        self.assertEqual(return_code, 2)
        self.assertEqual(json.loads(output.getvalue())["disposition"], "blocked-unsafe")
        self.assertFalse(any(call[:2] == ["git", "push"] for call in calls))

    def test_deletion_uses_exact_expected_head_lease(self):
        calls = []
        repository = {"nameWithOwner": "o/r", "url": "https://github.com/o/r"}
        pull_request = {
            "number": 1,
            "url": "https://github.com/o/r/pull/1",
            "state": "MERGED",
            "body": "OpenCode-Origin: cli\n",
            "baseRefName": "main",
            "headRefName": "feature/x",
            "headRefOid": "h",
        }
        remote_reads = iter(["h\trefs/heads/feature/x\n", ""])

        def fake_run(args):
            calls.append(args)
            if args[:3] == ["gh", "auth", "status"]:
                return self.completed(args)
            if args[:3] == ["gh", "repo", "view"]:
                return self.completed(args, json.dumps(repository))
            if args[:3] == ["gh", "pr", "view"]:
                return self.completed(args, json.dumps(pull_request))
            if args[:4] == ["git", "ls-remote", "--heads", "origin"]:
                return self.completed(args, next(remote_reads))
            if args[:2] == ["git", "push"]:
                return self.completed(args)
            raise AssertionError(args)

        output = io.StringIO()
        argv = ["cleanup-remote-branch.py", "--pr", "1", "--expected-head", "h", "--provenance", "cli"]
        with mock.patch.object(MODULE, "run", side_effect=fake_run), mock.patch.object(sys, "argv", argv), redirect_stdout(output):
            return_code = MODULE.main()
        self.assertEqual(return_code, 0)
        self.assertEqual(json.loads(output.getvalue())["disposition"], "deleted")
        self.assertIn(
            ["git", "push", "--force-with-lease=refs/heads/feature/x:h", "--delete", "origin", "feature/x"],
            calls,
        )


if __name__ == "__main__":
    unittest.main()
