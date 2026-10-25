import json
import pathlib
import sys
import tempfile
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

    def test_valid_repository_override_supports_approved_modes(self):
        loaded = policy.load_policy(self.write({
            "base_branch": "release",
            "feature_branch_prefix": "work/",
            "provenance": ["cli"],
            "remote": "upstream",
            "evidence": {
                "current_id": "delivery-current",
                "completion_id": "delivery-complete",
                "require_authenticated_actor": True,
            },
            "authorization": {
                "publication": True,
                "cleanup": True,
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
            "delegates": {"hints": ["small-batches"], "commit_strategy": "single-task", "message_scope": "single-task"},
            "remote_cleanup": "retain",
            "issue_completion": "comment-only",
            "blocked_issue_creation": True,
        }))
        self.assertEqual(loaded["base_branch"], "release")
        self.assertEqual(loaded["manual_merge"]["method"], "rebase")
        self.assertTrue(loaded["authorization"]["publication"])

    def test_rejects_incompatible_completion(self):
        with self.assertRaisesRegex(ValueError, "requires remote_cleanup delete"):
            policy.load_policy(self.write({"remote_cleanup": "retain", "issue_completion": "close"}))

    def test_default_external_actions_need_authorization(self):
        loaded = policy.load_policy(None)
        self.assertFalse(policy.authorized(loaded, "publication", False))
        self.assertTrue(policy.authorized(loaded, "publication", True))

    def test_blocked_issue_creation_is_disabled_by_default_and_requires_boolean_policy(self):
        self.assertFalse(policy.load_policy(None)["blocked_issue_creation"])
        self.assertTrue(policy.load_policy(self.write({"blocked_issue_creation": True}))["blocked_issue_creation"])
        with self.assertRaisesRegex(ValueError, "invalid lifecycle policy type: blocked_issue_creation"):
            policy.load_policy(self.write({"blocked_issue_creation": "true"}))

    def test_rejects_unknown_key(self):
        with self.assertRaisesRegex(ValueError, "unsupported"):
            policy.load_policy(self.write({"automatic_merge": True}))
