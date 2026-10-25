import importlib.util
import pathlib
import unittest


SCRIPT = pathlib.Path(__file__).parents[1] / "scripts" / "publish-pr.py"
SPEC = importlib.util.spec_from_file_location("publish_pr", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


class PublicationTests(unittest.TestCase):
    def test_issue_body_has_reference(self):
        body = MODULE.canonical_body("github-issue", "Summary", "42")
        self.assertIn("OpenCode-Origin: github-issue", body)
        self.assertIn("Refs #42", body)

    def test_non_issue_body_has_no_reference(self):
        body = MODULE.canonical_body("cli", "Summary", None)
        self.assertNotIn("Refs #", body)

    def test_no_match_creates(self):
        self.assertEqual(MODULE.select_pull_request([], "cli", None), ("create", None))

    def test_multiple_matches_block(self):
        action, record = MODULE.select_pull_request([{"state": "OPEN"}, {"state": "OPEN"}], "cli", None)
        self.assertEqual(action, "blocked-unsafe")
        self.assertIsNone(record)

    def test_closed_match_blocks(self):
        action, _ = MODULE.select_pull_request([{"state": "CLOSED"}], "cli", None)
        self.assertEqual(action, "blocked-unsafe")

    def test_reused_pr_requires_exact_provenance(self):
        record = {"state": "OPEN", "body": "OpenCode-Origin: cli\n"}
        self.assertEqual(MODULE.select_pull_request([record], "cli", None)[0], "reuse")
        self.assertEqual(MODULE.select_pull_request([record], "openchamber", None)[0], "blocked-unsafe")

    def test_non_fast_forward_push_is_unsafe(self):
        self.assertEqual(MODULE.classify_push_failure("rejected (non-fast-forward)"), ("blocked", "blocked-unsafe"))


if __name__ == "__main__":
    unittest.main()
