import io
import pathlib
import subprocess
import sys
import unittest
from contextlib import redirect_stdout

sys.path.insert(0, str(pathlib.Path(__file__).parents[1]))
import github_pr_lifecycle_common as common


class LifecycleCommonTests(unittest.TestCase):
    repository = {"nameWithOwner": "owner/repository", "url": "https://github.com/owner/repository"}

    def test_exact_marker_identity_is_fail_closed(self):
        cases = (
            ({"body": "OpenCode-Origin: cli\n"}, "cli", None, True),
            ({"body": "OpenCode-Origin: cli\nRefs #7\n"}, "cli", None, False),
            ({"body": "OpenCode-Origin: github-issue\nRefs #7\n"}, "github-issue", "7", True),
            ({"body": "OpenCode-Origin: github-issue\nRefs #7\nRefs #8\n"}, "github-issue", "7", False),
            ({"body": "OpenCode-Origin: github-issue\nRefs #7\n"}, "github-issue", None, False),
        )
        for record, provenance, issue, expected in cases:
            with self.subTest(record=record, provenance=provenance, issue=issue):
                self.assertIs(common.marker_matches(record, provenance, issue), expected)

    def test_repository_and_remote_identity_are_fail_closed(self):
        pull_requests = (
            ({"number": 1, "url": "https://github.com/owner/repository/pull/1"}, True),
            ({"number": "1", "url": "https://github.com/owner/repository/pull/1"}, False),
            ({"number": 1, "url": "https://github.com/other/repository/pull/1"}, False),
        )
        for pull_request, expected in pull_requests:
            with self.subTest(pull_request=pull_request):
                self.assertIs(common.repository_matches(self.repository, pull_request), expected)
        remotes = (
            ("git@github.com:owner/repository.git", True),
            ("https://github.com/other/repository.git", False),
            ("not-a-remote", False),
        )
        for remote, expected in remotes:
            with self.subTest(remote=remote):
                self.assertIs(common.remote_repository_matches(self.repository, remote), expected)
        remote_sets = (
            ("git@github.com:owner/repository.git\nhttps://github.com/owner/repository.git\n", True),
            ("git@github.com:owner/repository.git\ngit@github.com:other/repository.git\n", False),
            ("", False),
        )
        for remotes, expected in remote_sets:
            with self.subTest(remotes=remotes):
                self.assertIs(common.remote_urls_match(self.repository, remotes), expected)
        heads = (
            ({"isCrossRepository": False, "headRepository": {"nameWithOwner": "owner/repository"}}, True),
            ({"isCrossRepository": True, "headRepository": {"nameWithOwner": "owner/repository"}}, False),
            ({"isCrossRepository": False, "headRepository": {"nameWithOwner": "fork/repository"}}, False),
        )
        for pull_request, expected in heads:
            with self.subTest(head=pull_request):
                self.assertIs(common.head_repository_matches(self.repository, pull_request), expected)

    def test_remote_ref_requires_one_expected_ref(self):
        cases = (
            ("", (None, True)),
            ("head\trefs/heads/feature/x\n", ("head", True)),
            ("head\trefs/heads/feature/other\n", (None, False)),
            ("head refs/heads/feature/x\nother refs/heads/feature/x\n", (None, False)),
        )
        for output, expected in cases:
            with self.subTest(output=output):
                self.assertEqual(common.parse_remote_head(output, "feature/x"), expected)

    def test_result_envelope_is_versioned_and_fail_closed(self):
        for status, expected_exit in (("passed", 0), ("waiting", 3), ("repair", 4), ("blocked", 2), ("unknown", 2)):
            with self.subTest(status=status):
                output = io.StringIO()
                with redirect_stdout(output):
                    self.assertEqual(common.emit(status, "disposition", {"key": "value"}), expected_exit)
                self.assertEqual(
                    output.getvalue(),
                    f'{{"blocker": null, "disposition": "disposition", "evidence": {{"key": "value"}}, "next_stage": null, "status": "{status}", "version": 1}}\n',
                )

    def test_json_parsers_reject_non_objects_and_failed_commands(self):
        self.assertIsNone(common.parse_object(subprocess.CompletedProcess(["test"], 1, "{}", "")))
        self.assertIsNone(common.parse_object(subprocess.CompletedProcess(["test"], 0, "[]", "")))
        self.assertIsNone(common.parse_list('{"not": "a list"}'))
        self.assertIsNone(common.parse_list('[{} , 1]'))


if __name__ == "__main__":
    unittest.main()
