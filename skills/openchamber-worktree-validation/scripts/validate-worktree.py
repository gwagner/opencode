#!/usr/bin/env python3
"""Classify the current linked worktree without changing it."""
import argparse
import json
import subprocess


def run(*args):
    return subprocess.run(args, text=True, capture_output=True, check=False)


def result(status, disposition, evidence, blocker=None):
    print(json.dumps({"status": status, "disposition": disposition, "evidence": evidence, "blocker": blocker}, sort_keys=True))
    return 0 if status == "passed" else 3 if status == "waiting" else 2


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="main")
    args = parser.parse_args()
    root = run("git", "rev-parse", "--show-toplevel")
    branch = run("git", "branch", "--show-current")
    status = run("git", "status", "--porcelain=v1")
    conflicts = run("git", "diff", "--name-only", "--diff-filter=U")
    worktrees = run("git", "worktree", "list", "--porcelain")
    if any(command.returncode for command in (root, branch, status, conflicts, worktrees)):
        return result("blocked", "blocked-unsafe", {}, "current Git worktree cannot be inspected")
    evidence = {"root": root.stdout.strip(), "branch": branch.stdout.strip()}
    if not evidence["branch"] or evidence["branch"] == args.base:
        return result("blocked", "blocked-unsafe", evidence, "worktree must use an attached non-base branch")
    if f"worktree {evidence['root']}" not in worktrees.stdout:
        return result("blocked", "blocked-unsafe", evidence, "current worktree is not linked")
    if conflicts.stdout.strip():
        return result("blocked", "blocked-unsafe", evidence, "worktree contains merge conflicts")
    if status.stdout:
        return result("waiting", "waiting-user-cleanup", evidence, "worktree contains uncommitted changes")
    return result("passed", "passed", evidence)


if __name__ == "__main__":
    raise SystemExit(main())
