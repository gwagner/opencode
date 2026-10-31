"""Behavioral regressions for PR #33's permission and publication remediation."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import shutil
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
baseline_capture = load_module(
    "git_change_baseline",
    ROOT / "skills/git-change-baseline/scripts/capture-baseline.py",
)
worktree_validator = load_module(
    "openchamber_worktree_validator",
    ROOT / "skills/openchamber-worktree-validation/scripts/validate-worktree.py",
)
deployment_validator = load_module(
    "deployment_validator", ROOT / "scripts/validate-deployment.py"
)


def workflow_invocations(agent_path: Path):
    _data, text = validator.frontmatter(agent_path)
    workflows, findings = validator.yaml_workflows(agent_path, text)
    assert not findings
    return validator.workflow_invocations(workflows[0]["workflow"])


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

    def test_runtime_trailing_space_wildcard_accepts_bare_command(self) -> None:
        self.assertTrue(validator.matches("git status *", "git status"))
        self.assertTrue(validator.matches("git status *", "git status --short"))

    def test_runtime_wildcards_normalize_slashes_and_question_matches_one(self) -> None:
        self.assertTrue(validator.matches("src/*.py", r"src\module.py"))
        self.assertTrue(validator.matches("file?.txt", "file1.txt"))
        self.assertFalse(validator.matches("file?.txt", "file10.txt"))

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

    def test_ask_command_with_absolute_path_requires_external_directory_access(self) -> None:
        permission = {
            "bash": {"python3 /code/tool.py *": "ask"},
            "external_directory": {},
        }
        self.assertEqual(validator.fixed_absolute_bash_paths(permission), ["/code/tool.py"])
        self.assertFalse(validator.external_path_is_covered(permission, "/code/tool.py"))


class SdlcArchitectureScenarioTest(unittest.TestCase):
    def test_openchamber_precedes_explicit_cli_fallback(self) -> None:
        text = (ROOT / "agents/sdlc-orchestrator.md").read_text()
        self.assertIn("OpenChamber is the authoritative entry point", text)
        self.assertIn("directly launch the same workflow from the CLI only as an explicit fallback", text)
        self.assertLess(text.index("OpenChamber is the authoritative"), text.index("CLI only as an explicit fallback"))

    def test_branch_commit_and_publication_are_not_default_stages(self) -> None:
        orchestrator = workflow_invocations(ROOT / "agents/sdlc-orchestrator.md")
        conditions = {(kind, target): condition.lower() for kind, target, condition in orchestrator}
        self.assertIn("explicit", conditions[("skill", "feature-branch-setup")])
        self.assertIn("authoriz", conditions[("skill", "git-delegated-change-commit")])
        self.assertNotIn(("skill", "github-pr-publication"), conditions)
        self.assertNotIn(("skill", "github-sdlc-lifecycle-recovery"), conditions)

        publisher = workflow_invocations(ROOT / "agents/github-pr-publisher.md")
        self.assertEqual(publisher[0][1], "github-pr-publication")
        self.assertIn("explicit", publisher[0][2].lower())

    def test_attached_issue_is_a_primary_agent_handoff_not_delegation(self) -> None:
        data, text = validator.frontmatter(ROOT / "agents/github-issue-manager.md")
        self.assertNotEqual(
            validator.permission_effect(data.get("permission", {}), "task", "sdlc-orchestrator"),
            "allow",
        )
        self.assertIn("select `sdlc-orchestrator` from OpenChamber", text)
        self.assertNotIn(("agent", "sdlc-orchestrator"), [(kind, target) for kind, target, _ in workflow_invocations(ROOT / "agents/github-issue-manager.md")])

    def test_standard_evidence_schema_is_complete(self) -> None:
        text = (ROOT / "skills/execution-evidence-reporting/SKILL.md").read_text()
        required = (
            "outcome",
            "owned changed paths",
            "project-validation state",
            "exact project-validation commands and material results",
            "decisions",
            "assumptions",
            "unresolved questions",
            "blockers",
            "baseline",
        )
        for field in required:
            self.assertIn(field, text)

    def test_validator_rejects_primary_agent_delegation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(ROOT / "agents", root / "agents")
            shutil.copytree(ROOT / "skills", root / "skills")
            path = root / "agents/github-issue-manager.md"
            path.write_text(path.read_text().replace("  question: allow\n", "  question: allow\n  task:\n    sdlc-orchestrator: allow\n", 1))
            with patch("sys.argv", ["validate-agent-skill-architecture.py", directory]):
                with self.assertRaisesRegex(AssertionError, "primary agent sdlc-orchestrator must not be task-delegable"):
                    validator.main()

    def test_validator_rejects_unstructured_branch_preparation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(ROOT / "agents", root / "agents")
            shutil.copytree(ROOT / "skills", root / "skills")
            path = root / "agents/sdlc-orchestrator.md"
            path.write_text(path.read_text().replace(
                'when: "Before the first task-owned edit only in a legacy CLI request that explicitly asks to prepare a fresh local feature branch."',
                'when: "Before the first task-owned edit."',
            ))
            with patch("sys.argv", ["validate-agent-skill-architecture.py", directory]):
                with self.assertRaisesRegex(AssertionError, "feature-branch-setup requires an explicit requester condition"):
                    validator.main()

    def test_validator_rejects_missing_standard_evidence_edge(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(ROOT / "agents", root / "agents")
            shutil.copytree(ROOT / "skills", root / "skills")
            path = root / "agents/code-implementor.md"
            path.write_text(path.read_text().replace(
                '  - id: "execution-evidence"\n    when: "After project validation."\n    skill: "execution-evidence-reporting"\n',
                "",
            ))
            with patch("sys.argv", ["validate-agent-skill-architecture.py", directory]):
                with self.assertRaisesRegex(AssertionError, "project-validation requires execution-evidence-reporting"):
                    validator.main()


class DeploymentContractTest(unittest.TestCase):
    def test_checked_in_deployment_contract(self) -> None:
        with patch("sys.argv", ["validate-deployment.py", str(ROOT)]):
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(deployment_validator.main(), 0)


class PartialPublicationRegressionTest(unittest.TestCase):
    def test_reports_pushed_branch_when_pr_creation_fails(self) -> None:
        with tempfile.NamedTemporaryFile() as body:
            responses = iter(
                [
                    publisher.subprocess.CompletedProcess([], 0, "feature/example\n", ""),
                    publisher.subprocess.CompletedProcess([], 0, "", ""),
                    publisher.subprocess.CompletedProcess([], 0, "abc123\n", ""),
                    publisher.subprocess.CompletedProcess([], 0, "base123\n", ""),
                    publisher.subprocess.CompletedProcess([], 0, "1\n", ""),
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
        self.assertIn(("git", "remote", "get-url", "--push", "--all", "origin"), commands)
        self.assertIn(
            ("git", "push", "--no-tags", "--no-follow-tags", "origin", "HEAD:refs/heads/feature/example"),
            commands,
        )
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
                    publisher.subprocess.CompletedProcess([], 0, "1\n", ""),
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
                    publisher.subprocess.CompletedProcess([], 0, "1\n", ""),
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

    def test_blocks_branch_without_a_commit_ahead_of_base_before_remote_checks(self) -> None:
        with tempfile.NamedTemporaryFile() as body:
            responses = iter(
                [
                    publisher.subprocess.CompletedProcess([], 0, "feature/example\n", ""),
                    publisher.subprocess.CompletedProcess([], 0, "", ""),
                    publisher.subprocess.CompletedProcess([], 0, "base123\n", ""),
                    publisher.subprocess.CompletedProcess([], 0, "base123\n", ""),
                    publisher.subprocess.CompletedProcess([], 0, "0\n", ""),
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
        self.assertFalse(any(command[0] == "gh" for command in commands))

    def test_blocks_multiple_push_urls_before_any_push(self) -> None:
        with tempfile.NamedTemporaryFile() as body:
            responses = iter(
                [
                    publisher.subprocess.CompletedProcess([], 0, "feature/example\n", ""),
                    publisher.subprocess.CompletedProcess([], 0, "", ""),
                    publisher.subprocess.CompletedProcess([], 0, "abc123\n", ""),
                    publisher.subprocess.CompletedProcess([], 0, "base123\n", ""),
                    publisher.subprocess.CompletedProcess([], 0, "1\n", ""),
                    publisher.subprocess.CompletedProcess([], 0, "git@github.test:acme/example.git\nhttps://github.test/acme/example.git\n", ""),
                    publisher.subprocess.CompletedProcess([], 0, "", ""),
                    publisher.subprocess.CompletedProcess([], 0, '{"nameWithOwner":"acme/example","url":"https://github.test/acme/example"}', ""),
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
        self.assertFalse(any(command[0] == "gh" for command in commands))


class FeatureBranchSetupRegressionTest(unittest.TestCase):
    def test_switches_at_the_reported_immutable_base_revision(self) -> None:
        responses = iter(
            [
                branch_setup.subprocess.CompletedProcess([], 0, "main\n", ""),
                branch_setup.subprocess.CompletedProcess([], 0, "", ""),
                branch_setup.subprocess.CompletedProcess([], 0, "main\n", ""),
                branch_setup.subprocess.CompletedProcess([], 0, "base123\n", ""),
                branch_setup.subprocess.CompletedProcess([], 1, "", ""),
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
        self.assertEqual(commands[0], ("git", "check-ref-format", "--branch", "main"))
        self.assertEqual(commands[3], ("git", "rev-parse", "--verify", "refs/heads/main^{commit}"))
        self.assertEqual(json.loads(output.getvalue())["base_revision"], "base123")

    def test_does_not_switch_when_local_branches_cannot_be_inspected(self) -> None:
        responses = iter(
            [
                branch_setup.subprocess.CompletedProcess([], 0, "main\n", ""),
                branch_setup.subprocess.CompletedProcess([], 0, "", ""),
                branch_setup.subprocess.CompletedProcess([], 0, "main\n", ""),
                branch_setup.subprocess.CompletedProcess([], 0, "base123\n", ""),
                branch_setup.subprocess.CompletedProcess([], 2, "", "inspection failed"),
            ]
        )
        commands = []

        def run(*args):
            commands.append(args)
            return next(responses)

        with patch.object(branch_setup, "run", side_effect=run):
            with patch("sys.argv", ["setup-feature-branch.py", "--outcome", "Example"]):
                with contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(branch_setup.main(), 2)
        self.assertFalse(any(command[:2] == ("git", "switch") for command in commands))

    def test_rejects_invalid_base_before_inspecting_or_switching(self) -> None:
        commands = []

        def run(*args):
            commands.append(args)
            return branch_setup.subprocess.CompletedProcess([], 1, "", "invalid ref")

        with patch.object(branch_setup, "run", side_effect=run):
            with patch("sys.argv", ["setup-feature-branch.py", "--outcome", "Example", "--base", "../main"]):
                with contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(branch_setup.main(), 2)
        self.assertEqual(commands, [("git", "check-ref-format", "--branch", "../main")])


class GitChangeBaselineTest(unittest.TestCase):
    def test_records_unstaged_and_untracked_changes_with_an_empty_index(self) -> None:
        responses = iter(
            [
                baseline_capture.subprocess.CompletedProcess([], 0, "feature/example\n", ""),
                baseline_capture.subprocess.CompletedProcess([], 0, "abc123\n", ""),
                baseline_capture.subprocess.CompletedProcess([], 0, "", ""),
                baseline_capture.subprocess.CompletedProcess([], 0, " M README.md\0?? notes.txt\0", ""),
            ]
        )
        output = io.StringIO()
        with patch.object(baseline_capture, "run", side_effect=lambda *args: next(responses)):
            with contextlib.redirect_stdout(output):
                self.assertEqual(baseline_capture.main(), 0)
        evidence = json.loads(output.getvalue())
        self.assertEqual(evidence["baseline_commit"], "abc123")
        self.assertEqual(
            evidence["preexisting_changes"],
            [
                {"path": "README.md", "status": " M"},
                {"path": "notes.txt", "status": "??"},
            ],
        )

    def test_blocks_a_nonempty_index(self) -> None:
        responses = iter(
            [
                baseline_capture.subprocess.CompletedProcess([], 0, "feature/example\n", ""),
                baseline_capture.subprocess.CompletedProcess([], 0, "abc123\n", ""),
                baseline_capture.subprocess.CompletedProcess([], 1, "", ""),
                baseline_capture.subprocess.CompletedProcess([], 0, "M  staged.txt\0", ""),
            ]
        )
        output = io.StringIO()
        with patch.object(baseline_capture, "run", side_effect=lambda *args: next(responses)):
            with contextlib.redirect_stdout(output):
                self.assertEqual(baseline_capture.main(), 2)
        self.assertEqual(json.loads(output.getvalue())["blocker"], "baseline requires an empty index")


class OpenChamberWorktreeValidationTest(unittest.TestCase):
    def test_accepts_exact_linked_worktree_without_mutating_git(self) -> None:
        responses = iter(
            [
                worktree_validator.subprocess.CompletedProcess([], 0, "/worktrees/example\n", ""),
                worktree_validator.subprocess.CompletedProcess([], 0, "feature/example\n", ""),
                worktree_validator.subprocess.CompletedProcess([], 0, "abc123\n", ""),
                worktree_validator.subprocess.CompletedProcess([], 0, "", ""),
                worktree_validator.subprocess.CompletedProcess([], 0, "", ""),
                worktree_validator.subprocess.CompletedProcess([], 0, "worktree /worktrees/example\0HEAD abc123\0branch refs/heads/feature/example\0\0", ""),
            ]
        )
        commands = []

        def run(*args):
            commands.append(args)
            return next(responses)

        output = io.StringIO()
        with patch.object(worktree_validator, "run", side_effect=run):
            with patch("sys.argv", ["validate-worktree.py"]):
                with contextlib.redirect_stdout(output):
                    self.assertEqual(worktree_validator.main(), 0)
        self.assertEqual(json.loads(output.getvalue())["status"], "passed")
        self.assertTrue(all(command[0] == "git" for command in commands))
        self.assertFalse(any(command[1] in {"fetch", "merge", "switch", "clean", "reset"} for command in commands))

    def test_rejects_a_path_that_only_prefix_matches_a_linked_worktree(self) -> None:
        responses = iter(
            [
                worktree_validator.subprocess.CompletedProcess([], 0, "/worktrees/example\n", ""),
                worktree_validator.subprocess.CompletedProcess([], 0, "feature/example\n", ""),
                worktree_validator.subprocess.CompletedProcess([], 0, "abc123\n", ""),
                worktree_validator.subprocess.CompletedProcess([], 0, "", ""),
                worktree_validator.subprocess.CompletedProcess([], 0, "", ""),
                worktree_validator.subprocess.CompletedProcess([], 0, "worktree /worktrees/example-extra\0HEAD abc123\0branch refs/heads/feature/example\0\0", ""),
            ]
        )
        output = io.StringIO()
        with patch.object(worktree_validator, "run", side_effect=lambda *args: next(responses)):
            with patch("sys.argv", ["validate-worktree.py"]):
                with contextlib.redirect_stdout(output):
                    self.assertEqual(worktree_validator.main(), 2)
        self.assertEqual(json.loads(output.getvalue())["disposition"], "blocked-unsafe")

    def test_rejects_mismatched_linked_worktree_metadata(self) -> None:
        responses = iter(
            [
                worktree_validator.subprocess.CompletedProcess([], 0, "/worktrees/example\n", ""),
                worktree_validator.subprocess.CompletedProcess([], 0, "feature/example\n", ""),
                worktree_validator.subprocess.CompletedProcess([], 0, "abc123\n", ""),
                worktree_validator.subprocess.CompletedProcess([], 0, "", ""),
                worktree_validator.subprocess.CompletedProcess([], 0, "", ""),
                worktree_validator.subprocess.CompletedProcess([], 0, "worktree /worktrees/example\0HEAD other\0branch refs/heads/feature/example\0\0", ""),
            ]
        )
        output = io.StringIO()
        with patch.object(worktree_validator, "run", side_effect=lambda *args: next(responses)):
            with patch("sys.argv", ["validate-worktree.py"]):
                with contextlib.redirect_stdout(output):
                    self.assertEqual(worktree_validator.main(), 2)
        self.assertIn("metadata does not match", json.loads(output.getvalue())["blocker"])


if __name__ == "__main__":
    unittest.main()
