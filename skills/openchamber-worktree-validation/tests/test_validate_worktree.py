import importlib.util
import pathlib
import sys
import unittest


SCRIPT = pathlib.Path(__file__).parents[1] / "scripts" / "validate-worktree.py"
SPEC = importlib.util.spec_from_file_location("validate_worktree", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class ClassifyTests(unittest.TestCase):
    def test_fresh_clean_passes(self):
        self.assertEqual(MODULE.classify("fresh", True, "a", "a", None), ("passed", None))

    def test_fresh_unknown_commits_block(self):
        disposition, blocker = MODULE.classify("fresh", True, "a", "b", None)
        self.assertEqual(disposition, "blocked-unsafe")
        self.assertTrue(blocker)

    def test_resume_ahead_recovers_publication(self):
        self.assertEqual(MODULE.classify("resume-publication", True, "a", "b", "a"), ("resume-publication", None))

    def test_recovered_pull_request_resumes_baseline(self):
        self.assertEqual(MODULE.classify("resume-pull-request", True, "a", "b", "a"), ("resume-pull-request", None))

    def test_dirty_waits_without_destroying_work(self):
        disposition, blocker = MODULE.classify("fresh", False, "a", "a", None)
        self.assertEqual(disposition, "waiting-user-cleanup")
        self.assertTrue(blocker)

    def test_unexpected_resume_head_blocks(self):
        disposition, blocker = MODULE.classify("resume-publication", True, "a", "b", "c")
        self.assertEqual(disposition, "blocked-unsafe")
        self.assertTrue(blocker)

    def test_resume_requires_expected_head(self):
        disposition, blocker = MODULE.classify("resume-pull-request", True, "a", "b", None)
        self.assertEqual(disposition, "blocked-unsafe")
        self.assertTrue(blocker)

    def test_only_current_worktree_block_is_selected(self):
        listing = "worktree /code/current\nHEAD a\nbranch refs/heads/feature\n\nworktree /code/other\nHEAD b\nlocked reason"
        self.assertEqual(
            MODULE.current_worktree_blocks(listing, "/code/current"),
            [["worktree /code/current", "HEAD a", "branch refs/heads/feature"]],
        )


if __name__ == "__main__":
    unittest.main()
