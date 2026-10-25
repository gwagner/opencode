import importlib.util
import io
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest import mock


SCRIPT = pathlib.Path(__file__).parents[1] / "scripts" / "post-comment.py"
SPEC = importlib.util.spec_from_file_location("post_comment", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


class PostCommentTests(unittest.TestCase):
    ACTOR = "lifecycle-user"
    BODY = "Update complete\nOpenCode-Comment-ID: update-7\n"

    @staticmethod
    def completed(args, stdout="", stderr="", returncode=0):
        return subprocess.CompletedProcess(args, returncode, stdout, stderr)

    def comment(self, identifier="c1", body=None):
        return {
            "id": identifier,
            "url": f"https://github.com/o/r/issues/7#issuecomment-{identifier}",
            "author": {"login": self.ACTOR},
            "body": self.BODY if body is None else body,
        }

    def issue(self, comments):
        return {"number": 7, "title": "x", "state": "OPEN", "url": "https://github.com/o/r/issues/7", "comments": comments}

    def run_main(self, snapshots, *, post_returncode=0, body=None, argv=None):
        calls = []
        snapshots = iter(snapshots)

        def fake_run(args):
            calls.append(args)
            if args == ["gh", "auth", "status"]:
                return self.completed(args)
            if args == ["gh", "repo", "view", "--json", "nameWithOwner,url"]:
                return self.completed(args, json.dumps({"nameWithOwner": "o/r", "url": "https://github.com/o/r"}))
            if args == ["gh", "api", "--hostname", "github.com", "user", "--jq", ".login"]:
                return self.completed(args, self.ACTOR + "\n")
            if args[:3] == ["gh", "issue", "view"]:
                return self.completed(args, json.dumps(next(snapshots)))
            if args[:3] == ["gh", "issue", "comment"]:
                return self.completed(args, stderr="transport ended", returncode=post_returncode)
            raise AssertionError(args)

        with tempfile.TemporaryDirectory(dir="/tmp/opencode") as directory:
            body_file = pathlib.Path(directory) / "comment.md"
            body_file.write_text(self.BODY if body is None else body)
            output = io.StringIO()
            arguments = argv or ["post-comment.py", "--issue", "7", "--identity", "update-7", "--authorize-comment"]
            with (
                mock.patch.object(MODULE, "BODY_FILE", body_file),
                mock.patch.object(MODULE, "run", side_effect=fake_run),
                mock.patch.object(sys, "argv", arguments),
                redirect_stdout(output),
            ):
                return_code = MODULE.main()
            self.assertFalse(body_file.exists())
        return return_code, json.loads(output.getvalue()), calls

    def test_reuses_one_exact_actor_owned_comment_without_mutation(self):
        return_code, result, calls = self.run_main([self.issue([self.comment()])])
        self.assertEqual(return_code, 0)
        self.assertEqual(result["disposition"], "reused")
        self.assertFalse(any(call[:3] == ["gh", "issue", "comment"] for call in calls))

    def test_failed_post_is_success_when_reread_proves_one_exact_new_comment(self):
        return_code, result, _ = self.run_main(
            [self.issue([]), self.issue([self.comment()])],
            post_returncode=1,
        )
        self.assertEqual(return_code, 0)
        self.assertEqual(result["disposition"], "posted")
        self.assertEqual(result["evidence"]["mutation_attribution"], "uncertain")

    def test_conflicting_stable_identity_blocks_before_mutation(self):
        conflicting = self.comment(body="Different\nOpenCode-Comment-ID: update-7\n")
        return_code, result, calls = self.run_main([self.issue([conflicting])])
        self.assertEqual(return_code, 2)
        self.assertEqual(result["disposition"], "blocked-unsafe")
        self.assertFalse(any(call[:3] == ["gh", "issue", "comment"] for call in calls))

    def test_other_actor_cannot_satisfy_or_reuse_identity(self):
        foreign = self.comment()
        foreign["author"] = {"login": "other-user"}
        return_code, result, calls = self.run_main([self.issue([foreign])])
        self.assertEqual(return_code, 2)
        self.assertEqual(result["disposition"], "blocked-unsafe")
        self.assertFalse(any(call[:3] == ["gh", "issue", "comment"] for call in calls))

    def test_missing_embedded_generic_identity_blocks_before_github_access(self):
        return_code, result, calls = self.run_main([], body="Update complete\n")
        self.assertEqual(return_code, 2)
        self.assertEqual(result["disposition"], "blocked-unsafe")
        self.assertEqual(calls, [])

    def test_lifecycle_completion_preflight_rejects_missing_cleanup(self):
        body = "\n".join([
            "Lifecycle completion: merged-pr",
            "Pull request: https://github.com/o/r/pull/3",
            "Head commit: abc",
            "Merge result: merged",
            "Delegate project-validation: passed",
            "Required checks: passed",
        ])
        argv = [
            "post-comment.py", "--issue", "7", "--identity", "completion:https://github.com/o/r/pull/3:abc",
            "--kind", "completion", "--pr", "https://github.com/o/r/pull/3", "--head", "abc",
            "--authorize-comment",
        ]
        return_code, result, calls = self.run_main([], body=body, argv=argv)
        self.assertEqual(return_code, 2)
        self.assertEqual(result["disposition"], "blocked-unsafe")
        self.assertEqual(calls, [])

    def test_generic_attachment_body_requires_same_alt_and_uploaded_github_url(self):
        attachment = "/tmp/opencode/evidence.mp4#Demo video"
        expected = "[Demo video](/tmp/opencode/evidence.mp4)\nOpenCode-Comment-ID: update-7\n"
        actual = "[Demo video](https://github.com/user-attachments/assets/demo)\nOpenCode-Comment-ID: update-7\n"
        self.assertTrue(MODULE.local_attachment_body_matches(expected, [attachment]))
        self.assertTrue(MODULE.attached_body_matches(expected, actual, [attachment]))
        self.assertFalse(MODULE.attached_body_matches(expected, actual.replace("github.com", "example.com"), [attachment]))


if __name__ == "__main__":
    unittest.main()
