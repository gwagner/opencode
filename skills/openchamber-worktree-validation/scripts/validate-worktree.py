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
    root = run("git", "rev-parse", "--path-format=absolute", "--show-toplevel")
    branch = run("git", "branch", "--show-current")
    head = run("git", "rev-parse", "--verify", "HEAD^{commit}")
    status = run("git", "status", "--porcelain=v1")
    conflicts = run("git", "diff", "--name-only", "--diff-filter=U")
    worktrees = run("git", "worktree", "list", "--porcelain", "-z")
    if any(command.returncode for command in (root, branch, head, status, conflicts, worktrees)):
        return result("blocked", "blocked-unsafe", {}, "current Git worktree cannot be inspected")
    evidence = {
        "root": root.stdout.strip(),
        "branch": branch.stdout.strip(),
        "head": head.stdout.strip(),
    }
    if not evidence["branch"] or evidence["branch"] == args.base:
        return result("blocked", "blocked-unsafe", evidence, "worktree must use an attached non-base branch")
    records = [record for record in worktrees.stdout.split("\0\0") if record]
    current = None
    for record in records:
        fields = record.split("\0")
        values = {
            key: value
            for field in fields
            if " " in field
            for key, value in [field.split(" ", 1)]
        }
        if values.get("worktree") == evidence["root"]:
            current = values
            break
    if current is None:
        return result("blocked", "blocked-unsafe", evidence, "current worktree is not linked")
    if current.get("HEAD") != evidence["head"] or current.get("branch") != f"refs/heads/{evidence['branch']}":
        return result("blocked", "blocked-unsafe", evidence, "linked worktree metadata does not match current Git state")
    if conflicts.stdout.strip():
        return result("blocked", "blocked-unsafe", evidence, "worktree contains merge conflicts")
    if status.stdout:
        return result("waiting", "waiting-user-cleanup", evidence, "worktree contains uncommitted changes")
    return result("passed", "passed", evidence)


if __name__ == "__main__":
    raise SystemExit(main())
