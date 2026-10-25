import importlib.util
import pathlib
import unittest


SCRIPT = pathlib.Path(__file__).parents[1] / "scripts" / "recover-lifecycle.py"
SPEC = importlib.util.spec_from_file_location("recover_lifecycle", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


class RecoveryTests(unittest.TestCase):
    def test_fresh_start(self):
        self.assertEqual(MODULE.classify("OPEN", [], False, [])[0], "fresh-start")

    def test_remote_branch_without_pr(self):
        self.assertEqual(MODULE.classify("OPEN", [], True, [])[0], "remote-branch-no-pr")

    def test_open_pr(self):
        pr = {"state": "OPEN", "url": "u", "headRefName": "feature/x", "headRefOid": "h"}
        self.assertEqual(MODULE.classify("OPEN", [pr], False, [])[0], "open-pull-request")

    def test_incomplete_pr_identity_blocks(self):
        pr = {"state": "OPEN", "url": "u", "headRefOid": "h"}
        self.assertEqual(MODULE.classify("OPEN", [pr], False, [])[0], "blocked-unsafe")

    def test_multiple_prs_block(self):
        pr = {"state": "OPEN"}
        self.assertEqual(MODULE.classify("OPEN", [pr, pr], False, [])[0], "blocked-unsafe")

    def test_closed_issue_is_terminal(self):
        self.assertEqual(MODULE.classify("CLOSED", [], False, [])[0], "closed")

    def test_merged_pr_requires_current_evidence(self):
        pr = {"state": "MERGED", "url": "u", "headRefName": "feature/x", "headRefOid": "h"}
        self.assertEqual(MODULE.classify("OPEN", [pr], False, [])[0], "blocked-unsafe")

    def test_duplicate_exact_current_evidence_is_recoverable(self):
        pr = {"state": "MERGED", "url": "u", "headRefName": "feature/x", "headRefOid": "h"}
        comment = {
            "body": "Lifecycle evidence: current\nu\nHead commit: h\nDelegate project-validation: passed\nRequired checks: passed"
        }
        self.assertEqual(MODULE.classify("OPEN", [pr], False, [comment, comment])[0], "merged-needs-completion")


if __name__ == "__main__":
    unittest.main()
