import json
import pathlib
import sys
import tempfile
import hashlib
import subprocess
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parents[1]))
import github_lifecycle_policy as policy


class LifecyclePolicyTests(unittest.TestCase):
    def write(self, value):
        handle = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        self.addCleanup(pathlib.Path(handle.name).unlink, missing_ok=True)
        json.dump(value, handle)
        handle.close()
        return handle.name

    def load(self, value):
        return policy.resolve_policy_source(json.dumps(value).encode())[0]

    def test_valid_repository_override_supports_approved_modes(self):
        loaded = self.load({
            "base_branch": "release",
            "feature_branch_prefix": "work/",
            "provenance": ["cli"],
            "remote": "upstream",
            "evidence": {
                "current_id": "delivery-current",
                "completion_id": "delivery-complete",
                "require_authenticated_actor": True,
            },
            "manual_merge": {"method": "rebase", "require_current_turn_attestation": True},
            "pull_request": {"ready_policy": "ask", "rejection_policy": "close-pr"},
            "validation": {
                "check_mode": "all",
                "check_names": ["test"],
                "max_rechecks": 2,
                "wait_seconds": 0,
                "max_corrections": 2,
                "visual_scenarios": ["settings"],
            },
            "remote_cleanup": "retain",
            "issue_completion": "comment-only",
            "blocked_issue_creation": True,
        })
        self.assertEqual(loaded["base_branch"], "release")
        self.assertEqual(loaded["manual_merge"]["method"], "rebase")

    def test_rejects_incompatible_completion(self):
        with self.assertRaisesRegex(ValueError, "requires remote_cleanup delete"):
            self.load({"remote_cleanup": "retain", "issue_completion": "close"})

    def test_external_actions_always_need_current_turn_authorization(self):
        loaded = self.load({})
        self.assertFalse(policy.authorized(loaded, "publication", False))
        self.assertTrue(policy.authorized(loaded, "publication", True))
        self.assertFalse(policy.authorized(loaded, "publication", False))
        with self.assertRaisesRegex(ValueError, "unsupported lifecycle policy key: authorization"):
            self.load({"authorization": {"publication": True}})

    def test_blocked_issue_creation_is_disabled_by_default_and_requires_boolean_policy(self):
        self.assertFalse(self.load({})["blocked_issue_creation"])
        self.assertTrue(self.load({"blocked_issue_creation": True})["blocked_issue_creation"])
        with self.assertRaisesRegex(ValueError, "invalid lifecycle policy type: blocked_issue_creation"):
            self.load({"blocked_issue_creation": "true"})

    def test_rejects_unknown_key(self):
        with self.assertRaisesRegex(ValueError, "unsupported"):
            self.load({"automatic_merge": True})

    def test_rejects_unsafe_or_ambiguous_policy_identities(self):
        for override in (
            {"base_branch": "../main"},
            {"feature_branch_prefix": "feature/../"},
            {"remote": "origin\nother"},
            {"evidence": {"current_id": "bad id"}},
            {"validation": {"check_names": ["check", "check"]}},
            {"validation": {"visual_scenarios": ["screen", "screen"]}},
            {"provenance": ["cli", "cli"]},
        ):
            with self.assertRaises(ValueError):
                self.load(override)

    def test_consumers_require_the_fixed_snapshot_and_its_digest(self):
        _, normalized, digest = policy.resolve_policy_source(b'{"base_branch":"release"}')
        snapshot = pathlib.Path(policy.SNAPSHOT_PATH)
        original = snapshot.read_bytes() if snapshot.exists() else None
        self.addCleanup(lambda: snapshot.write_bytes(original) if original is not None else snapshot.unlink(missing_ok=True))
        snapshot.write_bytes(normalized)
        self.assertEqual(policy.load_policy(policy.SNAPSHOT_PATH, digest)["base_branch"], "release")
        with self.assertRaisesRegex(ValueError, "fixed"):
            policy.load_policy("/tmp/other-policy.json", digest)
        with self.assertRaisesRegex(ValueError, "required"):
            policy.load_policy(policy.SNAPSHOT_PATH, None)
        with self.assertRaisesRegex(ValueError, "digest"):
            policy.load_policy(policy.SNAPSHOT_PATH, "0" * 64)
        snapshot.write_text('{"base_branch":"main"}')
        with self.assertRaisesRegex(ValueError, "digest"):
            policy.load_policy(policy.SNAPSHOT_PATH, digest)

    def test_all_lifecycle_consumers_use_the_shared_fail_closed_policy_loader(self):
        root = pathlib.Path(__file__).parents[1]
        consumers = [
            "feature-branch-setup/scripts/setup-feature-branch.py",
            "github-issue-close/scripts/close-issue.py",
            "github-issue-comment/scripts/post-comment.py",
            "github-pr-approved-merge/scripts/merge-approved-pr.py",
            "github-pr-check-validation/scripts/validate-checks.py",
            "github-pr-lifecycle-recovery/scripts/recover-pr.py",
            "github-pr-publication/scripts/publish-pr.py",
            "github-pr-ready/scripts/ready-pr.py",
            "github-pr-rejection/scripts/verify-rejection.py",
            "github-pr-remote-branch-cleanup/scripts/cleanup-remote-branch.py",
            "github-sdlc-lifecycle-recovery/scripts/recover-lifecycle.py",
            "openchamber-worktree-validation/scripts/validate-worktree.py",
        ]
        for relative in consumers:
            source = (root / relative).read_text()
            with self.subTest(consumer=relative):
                self.assertIn("add_policy_argument", source)
                self.assertIn("load_policy(", source)

    def test_all_lifecycle_consumers_reject_omitted_policy_or_digest_arguments(self):
        root = pathlib.Path(__file__).parents[1]
        consumers = [
            "feature-branch-setup/scripts/setup-feature-branch.py",
            "github-issue-close/scripts/close-issue.py",
            "github-issue-comment/scripts/post-comment.py",
            "github-pr-approved-merge/scripts/merge-approved-pr.py",
            "github-pr-check-validation/scripts/validate-checks.py",
            "github-pr-lifecycle-recovery/scripts/recover-pr.py",
            "github-pr-publication/scripts/publish-pr.py",
            "github-pr-ready/scripts/ready-pr.py",
            "github-pr-rejection/scripts/verify-rejection.py",
            "github-pr-remote-branch-cleanup/scripts/cleanup-remote-branch.py",
            "github-sdlc-lifecycle-recovery/scripts/recover-lifecycle.py",
            "openchamber-worktree-validation/scripts/validate-worktree.py",
        ]
        for relative in consumers:
            with self.subTest(consumer=relative):
                completed = subprocess.run(
                    [sys.executable, str(root / relative)],
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertNotEqual(completed.returncode, 0)
                self.assertIn("--policy", completed.stderr)
                self.assertIn("--expected-policy-digest", completed.stderr)

    def test_representative_consumer_rejects_missing_or_mismatched_policy_before_work(self):
        script = pathlib.Path(__file__).parents[1] / "feature-branch-setup/scripts/setup-feature-branch.py"
        missing = subprocess.run([sys.executable, str(script), "--outcome", "x"], text=True, capture_output=True, check=False)
        self.assertNotEqual(missing.returncode, 0)
        mismatch = subprocess.run([
            sys.executable, str(script), "--outcome", "x", "--policy", "/tmp/not-policy.json",
            "--expected-policy-digest", "0" * 64,
        ], text=True, capture_output=True, check=False)
        self.assertNotEqual(mismatch.returncode, 0)
        self.assertIn("fixed lifecycle policy snapshot", mismatch.stderr)
