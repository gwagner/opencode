import hashlib
import json
import os
import pathlib
import subprocess
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[3]
SOURCE = pathlib.Path("/tmp/opencode/lifecycle-policy.json")
REPOSITORY = "test-owner/test-repository"
RUN = "resolver-test-run"
SNAPSHOT = pathlib.Path("/tmp/opencode/lifecycle-policy." + hashlib.sha256(REPOSITORY.encode()).hexdigest()[:16] + "." + RUN + ".snapshot.json")
TERMINAL = pathlib.Path(f"/tmp/opencode/lifecycle-terminal.{RUN}.json")
SCRIPT = ROOT / "skills/github-policy-resolution/scripts/resolve-policy.py"


class ResolveLifecyclePolicyTests(unittest.TestCase):
    def setUp(self):
        self.saved = {
            path: (path.read_bytes(), path.stat().st_mode & 0o777) if path.exists() else None
            for path in (SOURCE, SNAPSHOT, TERMINAL)
        }
        for path in (SOURCE, SNAPSHOT, TERMINAL):
            path.unlink(missing_ok=True)

    def tearDown(self):
        for path in (SOURCE, SNAPSHOT, TERMINAL):
            path.unlink(missing_ok=True)
            saved = self.saved[path]
            if saved is not None:
                contents, mode = saved
                path.write_bytes(contents)
                os.chmod(path, mode)

    def resolve(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), "--repository", REPOSITORY, "--lifecycle-run", RUN, *args], text=True, capture_output=True, check=False)

    def result(self, completed):
        self.assertEqual(completed.returncode, 0, completed.stderr)
        return json.loads(completed.stdout)

    def test_creates_normalized_snapshot_from_source(self):
        SOURCE.write_text('{ "base_branch": "release" }')
        result = self.result(self.resolve())
        self.assertEqual(result["snapshot"], str(SNAPSHOT))
        self.assertEqual(result["digest"], hashlib.sha256(SNAPSHOT.read_bytes()).hexdigest())
        self.assertEqual(json.loads(SNAPSHOT.read_text())["base_branch"], "release")

    def test_creates_default_when_source_is_absent(self):
        result = self.result(self.resolve())
        self.assertEqual(json.loads(SNAPSHOT.read_text())["base_branch"], "main")
        self.assertEqual(result["digest"], hashlib.sha256(SNAPSHOT.read_bytes()).hexdigest())

    def test_rejects_malformed_source_without_snapshot(self):
        SOURCE.write_text("not json")
        completed = self.resolve()
        self.assertNotEqual(completed.returncode, 0)
        self.assertFalse(SNAPSHOT.exists())

    def test_rejects_stale_non_normalized_snapshot(self):
        SNAPSHOT.write_text("{}\n")
        digest = hashlib.sha256(SNAPSHOT.read_bytes()).hexdigest()
        completed = self.resolve("--expected-policy-digest", digest)
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("bindings are required", completed.stderr)

    def test_resumes_only_with_exact_snapshot_digest_and_ignores_source_mutation(self):
        SOURCE.write_text('{"base_branch":"release"}')
        first = self.result(self.resolve())
        SOURCE.write_text('{"base_branch":"main"}')
        resumed = self.result(self.resolve("--expected-policy-digest", first["digest"]))
        self.assertEqual(resumed["digest"], first["digest"])
        self.assertEqual(json.loads(SNAPSHOT.read_text())["base_branch"], "release")
        self.assertNotEqual(self.resolve("--expected-policy-digest", "0" * 64).returncode, 0)

    def test_cleanup_requires_verified_digest_and_exact_terminal_disposition(self):
        digest = self.result(self.resolve())["digest"]
        self.assertNotEqual(self.resolve("--cleanup", "--expected-policy-digest", digest).returncode, 0)
        terminal = {"version": 1, "status": "passed", "disposition": "closed", "next_stage": None, "blocker": None, "evidence": {"policy_digest": digest, "policy_binding": {"repository": REPOSITORY, "lifecycle_run": RUN}, "pull_request": {"url": "https://github.com/test-owner/test-repository/pull/1", "headRefName": "feature/test", "headRefOid": "a", "baseRefName": "main"}}}
        TERMINAL.write_text(json.dumps(terminal, sort_keys=True))
        terminal_digest = hashlib.sha256(TERMINAL.read_bytes()).hexdigest()
        self.result(self.resolve("--cleanup", "--terminal-disposition", "closed", "--terminal-evidence", str(TERMINAL), "--terminal-evidence-digest", terminal_digest, "--expected-policy-digest", digest))
        self.assertFalse(SNAPSHOT.exists())

    def test_cleanup_rejects_premature_or_cross_run_envelope(self):
        digest = self.result(self.resolve())["digest"]
        TERMINAL.write_text(json.dumps({"version": 1, "status": "passed", "disposition": "closed", "next_stage": None, "blocker": None, "evidence": {"policy_digest": digest, "policy_binding": {"repository": REPOSITORY, "lifecycle_run": "another-run"}, "pull_request": {"url": "x", "headRefName": "feature/x", "headRefOid": "x", "baseRefName": "main"}}}))
        result = self.resolve("--cleanup", "--terminal-disposition", "closed", "--terminal-evidence", str(TERMINAL), "--terminal-evidence-digest", hashlib.sha256(TERMINAL.read_bytes()).hexdigest(), "--expected-policy-digest", digest)
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(SNAPSHOT.exists())
