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


SCRIPT = pathlib.Path(__file__).parents[1] / "scripts" / "close-issue.py"
SPEC = importlib.util.spec_from_file_location("close_issue", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def completed(argv, stdout="", returncode=0, stderr=""):
    return subprocess.CompletedProcess(argv, returncode, stdout, stderr)


class CloseIssueTests(LifecycleSnapshotTestCase):
    argv = [
        "close-issue.py", "--issue", "7", "--expected-pr", "https://github.com/o/r/pull/9",
        "--expected-head", "head", "--expected-branch", "feature/x", "--expected-merge-commit", "merge",
        "--authorize-closure",
    ]

    def recovery(self, disposition):
        return json.dumps({"version": 1, "status": "passed", "disposition": disposition,
                           "evidence": {"repository": {"nameWithOwner": "o/r"}}})

    def invoke(self, responses):
        output = io.StringIO()
        with mock.patch.object(MODULE, "run", side_effect=responses) as run, mock.patch.object(sys, "argv", self.with_policy(self.argv)), redirect_stdout(output):
            code = MODULE.main()
        return code, json.loads(output.getvalue()), run

    def test_rejects_missing_current_turn_authorization_before_recovery(self):
        output = io.StringIO()
        with mock.patch.object(MODULE, "run") as run, mock.patch.object(sys, "argv", self.with_policy(self.argv[:-1])), redirect_stdout(output):
            code = MODULE.main()
        self.assertEqual(code, 3)
        self.assertEqual(json.loads(output.getvalue())["disposition"], "waiting-user-authorization")
        run.assert_not_called()

    def test_authoritative_recovery_binds_repo_and_postverifies(self):
        code, result, run = self.invoke([
            completed([], self.recovery("merged-needs-close")),
            completed([], ""),
            completed([], self.recovery("closed")),
        ])
        self.assertEqual(code, 0)
        self.assertEqual(result["disposition"], "closed")
        self.assertEqual(run.call_args_list[1].args[0], ["gh", "issue", "close", "7", "--repo", "o/r"])

    def test_recovery_json_is_not_an_input_or_authority(self):
        code, result, run = self.invoke([completed([], self.recovery("closed"))])
        self.assertEqual(code, 0)
        self.assertEqual(result["disposition"], "already-closed")
        self.assertEqual(run.call_count, 1)

    def test_race_after_close_is_blocked(self):
        code, result, run = self.invoke([
            completed([], self.recovery("merged-needs-close")),
            completed([], ""),
            completed([], self.recovery("merged-needs-close")),
        ])
        self.assertEqual(code, 2)
        self.assertEqual(result["disposition"], "blocked-unsafe")
        self.assertEqual(run.call_count, 3)
