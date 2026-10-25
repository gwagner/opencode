#!/usr/bin/env python3
"""Create exactly one policy-prefixed, unused local feature branch."""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from github_lifecycle_policy import add_policy_argument, load_policy, policy_evidence
from github_pr_lifecycle_common import run

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--outcome", required=True)
    add_policy_argument(p)
    a = p.parse_args()
    try: policy = load_policy(a.policy, a.expected_policy_digest, a.repository, a.lifecycle_run)
    except ValueError as e: print(e, file=sys.stderr); return 2
    slug = re.sub(r"[^a-z0-9]+", "-", a.outcome.lower()).strip("-")[:48]
    if not slug: print("outcome cannot produce a branch slug", file=sys.stderr); return 2
    branch = policy["feature_branch_prefix"] + slug
    if run(["git", "status", "--porcelain=v1"]).stdout or run(["git", "branch", "--show-current"]).stdout.strip() != policy["base_branch"]:
        print("worktree must be clean and attached to policy base", file=sys.stderr); return 2
    if run(["git", "branch", "--list", branch]).stdout.strip(): print(f"branch exists: {branch}", file=sys.stderr); return 2
    made = run(["git", "switch", "-c", branch, policy["base_branch"]])
    if made.returncode: print(made.stderr, file=sys.stderr); return 1
    print(json.dumps({"branch": branch, "evidence": policy_evidence(policy)}, sort_keys=True)); return 0
if __name__ == "__main__": raise SystemExit(main())
