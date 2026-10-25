import importlib.util
import pathlib
import unittest


SCRIPT = pathlib.Path(__file__).parents[1] / "scripts" / "cleanup-remote-branch.py"
SPEC = importlib.util.spec_from_file_location("cleanup_remote_branch", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


class CleanupTests(unittest.TestCase):
    def test_absent_remote_is_valid(self):
        self.assertEqual(MODULE.parse_remote_head(""), (None, True))

    def test_one_remote_head_is_valid(self):
        self.assertEqual(MODULE.parse_remote_head("abc\trefs/heads/feature/x\n"), ("abc", True))

    def test_multiple_remote_heads_are_ambiguous(self):
        self.assertEqual(MODULE.parse_remote_head("a refs/heads/x\nb refs/heads/y\n"), (None, False))

    def test_exact_merged_identity_matches(self):
        record = {
            "number": 1,
            "url": "u",
            "state": "MERGED",
            "body": "OpenCode-Origin: cli\n",
            "baseRefName": "main",
            "headRefName": "feature/x",
            "headRefOid": "h",
        }
        self.assertTrue(MODULE.merged_identity_matches(record, "h", "main", "cli"))

    def test_provenance_mismatch_blocks_identity(self):
        record = {
            "number": 1,
            "url": "u",
            "state": "MERGED",
            "body": "OpenCode-Origin: openchamber\n",
            "baseRefName": "main",
            "headRefName": "feature/x",
            "headRefOid": "h",
        }
        self.assertFalse(MODULE.merged_identity_matches(record, "h", "main", "cli"))


if __name__ == "__main__":
    unittest.main()
