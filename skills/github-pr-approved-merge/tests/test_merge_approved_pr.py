import importlib.util
import pathlib
import unittest


SCRIPT = pathlib.Path(__file__).parents[1] / "scripts" / "merge-approved-pr.py"
SPEC = importlib.util.spec_from_file_location("merge_approved_pr", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


class MergeTests(unittest.TestCase):
    @staticmethod
    def record(state="OPEN", head="h", draft=False, mergeable="MERGEABLE"):
        return {
            "number": 1,
            "url": "u",
            "state": state,
            "isDraft": draft,
            "mergeable": mergeable,
            "baseRefName": "main",
            "headRefName": "feature/x",
            "headRefOid": head,
        }

    def test_exact_ready_pr_passes_merge_gate(self):
        self.assertTrue(MODULE.open_merge_gate(self.record(), "h", "main"))

    def test_draft_fails_merge_gate(self):
        self.assertFalse(MODULE.open_merge_gate(self.record(draft=True), "h", "main"))

    def test_changed_head_fails_merge_gate(self):
        self.assertFalse(MODULE.open_merge_gate(self.record(head="other"), "h", "main"))

    def test_unmergeable_fails_merge_gate(self):
        self.assertFalse(MODULE.open_merge_gate(self.record(mergeable="CONFLICTING"), "h", "main"))


if __name__ == "__main__":
    unittest.main()
