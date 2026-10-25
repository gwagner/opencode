"""Shared fixed-snapshot setup for lifecycle script tests."""
from __future__ import annotations

import pathlib
import sys
import unittest


SKILLS_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILLS_ROOT))

from github_lifecycle_policy import SNAPSHOT_PATH, resolve_policy_source


class LifecycleSnapshotTestCase(unittest.TestCase):
    """Give each script invocation the production fixed path and exact digest."""

    def setUp(self):
        super().setUp()
        self.snapshot = pathlib.Path(SNAPSHOT_PATH)
        self.snapshot.parent.mkdir(parents=True, exist_ok=True)
        self._saved_snapshot = (
            (self.snapshot.read_bytes(), self.snapshot.stat().st_mode)
            if self.snapshot.exists()
            else None
        )
        _, normalized, self.policy_digest = resolve_policy_source(b"{}")
        self.snapshot.write_bytes(normalized)

    def tearDown(self):
        if self._saved_snapshot is None:
            self.snapshot.unlink(missing_ok=True)
        else:
            contents, mode = self._saved_snapshot
            self.snapshot.write_bytes(contents)
            self.snapshot.chmod(mode)
        super().tearDown()

    def with_policy(self, argv: list[str]) -> list[str]:
        return [
            *argv,
            "--policy",
            str(self.snapshot),
            "--expected-policy-digest",
            self.policy_digest,
        ]
