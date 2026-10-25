#!/usr/bin/env python3
"""Close one ordinary issue; lifecycle closure has a separate strict skill."""
from __future__ import annotations
import argparse
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from github_pr_lifecycle_common import emit, parse_object, run
def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument("--issue", required=True); parser.add_argument("--authorize-close", action="store_true"); args=parser.parse_args()
    if not args.authorize_close: return emit("waiting", "waiting-user-authorization", {}, "explicit generic closure authorization is required")
    repo=parse_object(run(["gh","repo","view","--json","nameWithOwner,url"]))
    if not repo: return emit("waiting","waiting-external",{},"repository unavailable")
    before=parse_object(run(["gh","issue","view",args.issue,"--repo",repo["nameWithOwner"],"--json","number,url,state"]))
    if not before: return emit("waiting","waiting-external",{"repository":repo},"issue unavailable")
    if before.get("state")=="CLOSED": return emit("passed","already-closed",{"repository":repo,"issue":before})
    changed=run(["gh","issue","close",args.issue,"--repo",repo["nameWithOwner"]])
    after=parse_object(run(["gh","issue","view",args.issue,"--repo",repo["nameWithOwner"],"--json","number,url,state"]))
    if not after or after.get("state")!="CLOSED": return emit("waiting","waiting-external",{"repository":repo},changed.stderr.strip() or "generic closure was not verified")
    return emit("passed","closed",{"repository":repo,"issue":after})
if __name__ == "__main__": raise SystemExit(main())
