"""Shared fixed-snapshot setup for lifecycle script tests."""
from __future__ import annotations

import pathlib
import sys
import unittest


SKILLS_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILLS_ROOT))

from github_lifecycle_policy import resolve_policy_source, snapshot_path


class LifecycleSnapshotTestCase(unittest.TestCase):
    """Give each script invocation a repository/run-bound exact digest."""

    def setUp(self):
        super().setUp()
        self.repository = "o/r"
        self.lifecycle_run = f"test-{self.__class__.__name__.lower()}"
        self.snapshot = pathlib.Path(snapshot_path(self.repository, self.lifecycle_run))
        self.snapshot.parent.mkdir(parents=True, exist_ok=True)
        self._saved_snapshot = (
            (self.snapshot.read_bytes(), self.snapshot.stat().st_mode)
            if self.snapshot.exists()
            else None
        )
        if self.snapshot.exists():
            self.snapshot.chmod(0o600)
        _, normalized, self.policy_digest = resolve_policy_source(b"{}", self.repository, self.lifecycle_run)
        self.snapshot.write_bytes(normalized)

    def tearDown(self):
        if self._saved_snapshot is None:
            if self.snapshot.exists():
                self.snapshot.chmod(0o600)
            self.snapshot.unlink(missing_ok=True)
        else:
            contents, mode = self._saved_snapshot
            self.snapshot.chmod(0o600)
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
            "--repository",
            self.repository,
            "--lifecycle-run",
            self.lifecycle_run,
        ]
