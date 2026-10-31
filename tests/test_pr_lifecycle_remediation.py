"""Behavioral regressions for PR #33's permission and publication remediation."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


validator = load_module("architecture_validator", ROOT / "tests/validate-agent-skill-architecture.py")
publisher = load_module(
    "pr_publisher", ROOT / "skills/github-pr-publication/scripts/publish-pr.py"
)
branch_setup = load_module(
    "feature_branch_setup", ROOT / "skills/feature-branch-setup/scripts/setup-feature-branch.py"
)


class OrderedPermissionRegressionTest(unittest.TestCase):
    def test_last_matching_rule_wins_for_allow_ask_and_deny(self) -> None:
        rules = {
            "bash": {
                "*": "allow",
                "git *": "ask",
                "git push *": "deny",
            }
        }
        self.assertEqual(validator.permission_effect(rules, "bash", "git status --short"), "ask")
        self.assertEqual(validator.permission_effect(rules, "bash", "git push origin main"), "deny")
        self.assertEqual(validator.permission_effect(rules, "bash", "python -V"), "allow")

    def test_runtime_wildcards_treat_brackets_as_literals(self) -> None:
        self.assertTrue(validator.matches("read file[1]", "read file[1]"))
        self.assertFalse(validator.matches("read file[1]", "read file1"))

    def test_skill_contract_rejects_a_later_deny(self) -> None:
        caller = {
            "bash": {
                "*": "allow",
                "git commit --only *": "deny",
            }
        }
        contract = {
            "bash": {
                "git commit --only *": "ask",
            }
        }
        self.assertFalse(validator.covers(caller, contract))

    def test_architecture_rejects_a_non_runtime_agent_mode(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "agents").mkdir()
            (root / "skills").mkdir()
            (root / "agents" / "invalid.md").write_text(
                "---\n"
                "name: invalid\n"
                "description: Invalid mode fixture.\n"
                "classification: technical\n"
                "mode: specialist\n"
                "permission: deny\n"
                "---\n"
            )
            with patch("sys.argv", ["validate-agent-skill-architecture.py", directory]):
                with self.assertRaisesRegex(AssertionError, "mode must be all, primary, or subagent"):
                    validator.main()


class PartialPublicationRegressionTest(unittest.TestCase):
    def test_reports_pushed_branch_when_pr_creation_fails(self) -> None:
        with tempfile.NamedTemporaryFile() as body:
            responses = iter(
                [
                    publisher.subprocess.CompletedProcess([], 0, "feature/example\n", ""),
                    publisher.subprocess.CompletedProcess([], 0, "", ""),
                    publisher.subprocess.CompletedProcess([], 0, "abc123\n", ""),
                    publisher.subprocess.CompletedProcess([], 0, "base123\n", ""),
                    publisher.subprocess.CompletedProcess([], 0, "https://github.test/acme/example.git\n", ""),
                    publisher.subprocess.CompletedProcess([], 0, "", ""),
                    publisher.subprocess.CompletedProcess([], 0, '{"nameWithOwner":"acme/example","url":"https://github.test/acme/example"}', ""),
                    publisher.subprocess.CompletedProcess([], 0, "[]", ""),
                    publisher.subprocess.CompletedProcess([], 0, "", ""),
                    publisher.subprocess.CompletedProcess([], 1, "", "gh create failed"),
                ]
            )
            commands = []
            output = io.StringIO()
            standard_output = io.StringIO()
            def run(*args):
                commands.append(args)
                return next(responses)

            with patch.object(publisher, "run", side_effect=run):
                with patch("sys.argv", ["publish-pr.py", "--title", "Title", "--body-file", body.name]):
                    with contextlib.redirect_stderr(output), contextlib.redirect_stdout(standard_output):
                        self.assertEqual(publisher.main(), 1)
        self.assertIn("publication status: branch-pushed; pull-request-not-created", output.getvalue())
        self.assertIn("do not retry automatically", output.getvalue())
        evidence = json.loads(standard_output.getvalue())
        self.assertEqual(evidence["status"], "partial")
        self.assertEqual(evidence["head"], "abc123")
        self.assertEqual(evidence["branch"], "feature/example")
        self.assertIn(("gh", "pr", "list", "--repo", "acme/example", "--head", "feature/example", "--state", "all", "--json", "number,url,state,headRefOid"), commands)
        self.assertIn("--repo", commands[-1])
        self.assertIn("acme/example", commands[-1])

    def test_blocks_when_origin_and_github_repository_differ(self) -> None:
        with tempfile.NamedTemporaryFile() as body:
            responses = iter(
                [
                    publisher.subprocess.CompletedProcess([], 0, "feature/example\n", ""),
                    publisher.subprocess.CompletedProcess([], 0, "", ""),
                    publisher.subprocess.CompletedProcess([], 0, "abc123\n", ""),
                    publisher.subprocess.CompletedProcess([], 0, "base123\n", ""),
                    publisher.subprocess.CompletedProcess([], 0, "git@github.test:acme/example.git\n", ""),
                    publisher.subprocess.CompletedProcess([], 0, "", ""),
                    publisher.subprocess.CompletedProcess([], 0, '{"nameWithOwner":"other/example","url":"https://github.test/other/example"}', ""),
                ]
            )
            with patch.object(publisher, "run", side_effect=lambda *args: next(responses)):
                with patch("sys.argv", ["publish-pr.py", "--title", "Title", "--body-file", body.name]):
                    with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
                        self.assertEqual(publisher.main(), 2)

    def test_blocks_malformed_existing_pull_request_evidence_before_push(self) -> None:
        with tempfile.NamedTemporaryFile() as body:
            responses = iter(
                [
                    publisher.subprocess.CompletedProcess([], 0, "feature/example\n", ""),
                    publisher.subprocess.CompletedProcess([], 0, "", ""),
                    publisher.subprocess.CompletedProcess([], 0, "abc123\n", ""),
                    publisher.subprocess.CompletedProcess([], 0, "base123\n", ""),
                    publisher.subprocess.CompletedProcess([], 0, "https://github.test/acme/example.git\n", ""),
                    publisher.subprocess.CompletedProcess([], 0, "", ""),
                    publisher.subprocess.CompletedProcess([], 0, '{"nameWithOwner":"acme/example","url":"https://github.test/acme/example"}', ""),
                    publisher.subprocess.CompletedProcess([], 0, "{}", ""),
                ]
            )
            commands = []

            def run(*args):
                commands.append(args)
                return next(responses)

            with patch.object(publisher, "run", side_effect=run):
                with patch("sys.argv", ["publish-pr.py", "--title", "Title", "--body-file", body.name]):
                    with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
                        self.assertEqual(publisher.main(), 2)
        self.assertFalse(any(command[:2] == ("git", "push") for command in commands))


class FeatureBranchSetupRegressionTest(unittest.TestCase):
    def test_switches_at_the_reported_immutable_base_revision(self) -> None:
        responses = iter(
            [
                branch_setup.subprocess.CompletedProcess([], 0, "", ""),
                branch_setup.subprocess.CompletedProcess([], 0, "main\n", ""),
                branch_setup.subprocess.CompletedProcess([], 0, "base123\n", ""),
                branch_setup.subprocess.CompletedProcess([], 0, "", ""),
                branch_setup.subprocess.CompletedProcess([], 0, "", ""),
            ]
        )
        commands = []

        def run(*args):
            commands.append(args)
            return next(responses)

        output = io.StringIO()
        with patch.object(branch_setup, "run", side_effect=run):
            with patch("sys.argv", ["setup-feature-branch.py", "--outcome", "Example"]):
                with contextlib.redirect_stdout(output):
                    self.assertEqual(branch_setup.main(), 0)
        self.assertEqual(commands[-1], ("git", "switch", "-c", "feature/example", "base123"))
        self.assertEqual(json.loads(output.getvalue())["base_revision"], "base123")


if __name__ == "__main__":
    unittest.main()
