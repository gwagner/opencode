#!/usr/bin/env python3
"""Close one issue only with explicit closure authorization and verified recovery evidence."""
import argparse
import subprocess
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from github_lifecycle_policy import add_authorization_argument, add_policy_argument, authorized, load_policy

def main():
    p=argparse.ArgumentParser(); p.add_argument("--issue", required=True); p.add_argument("--recovery-json", required=True)
    add_policy_argument(p); add_authorization_argument(p, "closure"); a=p.parse_args()
    try: policy=load_policy(a.policy)
    except ValueError as e: print(e, file=sys.stderr); return 2
    if policy["issue_completion"] != "close": print("issue completion policy does not permit closure", file=sys.stderr); return 2
    if not authorized(policy, "closure", a.authorize_closure): print("explicit closure authorization is required", file=sys.stderr); return 2
    if '"disposition": "merged-needs-close"' not in Path(a.recovery_json).read_text(): print("recovery evidence does not permit closure", file=sys.stderr); return 2
    return subprocess.run(["gh", "issue", "close", a.issue]).returncode
if __name__ == "__main__": raise SystemExit(main())
