import importlib.util
import pathlib
import unittest


SCRIPT = pathlib.Path(__file__).parents[1] / "scripts" / "recover-pr.py"
SPEC = importlib.util.spec_from_file_location("recover_pr", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


class RecoveryTests(unittest.TestCase):
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

    def test_remote_without_pr(self):
        self.assertEqual(MODULE.classify([], "h", "h", "base", "openchamber")[0], "remote-branch-no-pr")

    def test_different_remote_without_pr_blocks(self):
        self.assertEqual(MODULE.classify([], "other", "h", "base", "openchamber")[0], "blocked-unsafe")

    def test_open_pr(self):
        self.assertEqual(MODULE.classify([self.pr()], "h", "h", "base", "openchamber")[0], "open-pull-request")

    def test_cli_open_pr(self):
        self.assertEqual(MODULE.classify([self.pr(provenance="cli")], "h", "h", "base", "cli")[0], "open-pull-request")

    def test_changed_head_blocks(self):
        self.assertEqual(MODULE.classify([self.pr(head="other")], "other", "h", "base", "openchamber")[0], "blocked-unsafe")

    def test_wrong_provenance_blocks(self):
        pr = self.pr()
        pr["body"] = "OpenCode-Origin: cli\n"
        self.assertEqual(MODULE.classify([pr], "h", "h", "base", "openchamber")[0], "blocked-unsafe")

    def test_merged_without_remote_branch_is_terminal(self):
        self.assertEqual(MODULE.classify([self.pr(state="MERGED")], None, "h", "base", "openchamber")[0], "merged")

    def test_merged_with_remote_branch_reports_cleanup_pending(self):
        self.assertEqual(MODULE.classify([self.pr(state="MERGED")], "h", "h", "base", "openchamber")[0], "merged-cleanup-pending")


if __name__ == "__main__":
    unittest.main()
