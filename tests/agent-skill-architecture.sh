#!/bin/sh
set -eu
export PYTHONDONTWRITEBYTECODE=1

script_dir=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
root=$(CDPATH='' cd -- "$script_dir/.." && pwd)

root_agents="$root/AGENTS.md"
grep -Fq 'dynamically resolve `/code` by running `git rev-parse --show-toplevel`' "$root_agents"
grep -Fq 'returned Git root of the current linked worktree is the code root' "$root_agents"
grep -Fq 'Resolve `/project` from the `references.docs.path` value in `/code/.opencode/opencode.json`.' "$root_agents"

for file in "$root"/agents/*.md; do
  expected=$(basename "$file" .md)
  grep -q "^name: $expected$" "$file"
  grep -Eq '^classification: (technical|non-technical)$' "$file"
done

for file in "$root"/skills/*/SKILL.md; do
  expected=$(basename "$(dirname "$file")")
  grep -q "^name: $expected$" "$file"
  grep -Eq '^classification: (technical|non-technical)$' "$file"
  grep -q '^opencode_permission:$' "$file"
  grep -q '^inputs:$' "$file"
  grep -q '^## Inputs$' "$file"
done

test -f "$root/agents/sdlc-orchestrator.md"
test ! -e "$root/agents/github-sdlc.md"
test ! -e "$root/agents/merge-evidence-resolver.md"
test ! -e "$root/skills/git-main-sync/SKILL.md"
test ! -e "$root/skills/evidence-based-merge-resolution/SKILL.md"
test ! -e "$root/skills/git-agent-skill-change-publication/SKILL.md"

orchestrator="$root/agents/sdlc-orchestrator.md"
for identity in feature-branch-setup openchamber-worktree-validation \
  github-sdlc-lifecycle-recovery github-pr-lifecycle-recovery issue-worktree-validation git-change-baseline \
  git-delegated-change-commit github-pr-publication github-pr-check-validation \
  github-pr-ready github-pr-user-decision github-issue-comment github-issue-close; do
  grep -q "^    $identity: allow$" "$orchestrator"
  grep -q "skill: $identity" "$orchestrator"
done
for identity in github-pr-approved-merge github-pr-rejection; do
  grep -q "^    $identity: allow$" "$orchestrator"
  grep -q "skill: $identity" "$root/skills/github-pr-user-decision/SKILL.md"
done
grep -q '^    grillme: allow$' "$root/skills/github-pr-user-decision/SKILL.md"
grep -Fq 'never infer approval or rejection' "$root/skills/github-pr-user-decision/SKILL.md"

for entrypoint in cli openchamber github-issue; do
  grep -q "$entrypoint" "$orchestrator"
done
grep -Fq 'rejected-open-pr' "$orchestrator"
grep -Fq 'waiting-external' "$orchestrator"
grep -Fq 'Repeat a repair only after a material change' "$orchestrator"

issue_manager="$root/agents/github-issue-manager.md"
issue_contract="$root/skills/github-work-issue-contract/SKILL.md"
issue_capture="$root/skills/github-issue-capture/SKILL.md"
grep -q '^    sdlc-orchestrator: allow$' "$issue_manager"
grep -q '^    agent: sdlc-orchestrator$' "$issue_manager"
grep -Fq 'execution_route: sdlc-orchestrator' "$issue_contract"
grep -Fq 'execution_route: sdlc-orchestrator' "$issue_capture"

for specialist in api-integration-tester bug-fixer code-implementor frontend-reference-builder spec-gap-detector; do
  grep -q '^mode: subagent$' "$root/agents/$specialist.md"
done
grep -Fq 'When directly invoked, audit and propose only' "$root/agents/agent-builder.md"

for script in \
  "$root/skills/openchamber-worktree-validation/scripts/validate-worktree.py" \
  "$root/skills/github-pr-publication/scripts/publish-pr.py" \
  "$root/skills/github-pr-check-validation/scripts/validate-checks.py" \
  "$root/skills/github-sdlc-lifecycle-recovery/scripts/recover-lifecycle.py" \
  "$root/skills/github-pr-lifecycle-recovery/scripts/recover-pr.py" \
  "$root/skills/github-pr-rejection/scripts/verify-rejection.py"; do
  test -f "$script"
  python3 - "$script" <<'PY'
from pathlib import Path
import sys
compile(Path(sys.argv[1]).read_text(), sys.argv[1], "exec")
PY
done

python3 -m unittest discover -s "$root/skills/openchamber-worktree-validation/tests" -p 'test_*.py'
python3 -m unittest discover -s "$root/skills/github-pr-publication/tests" -p 'test_*.py'
python3 -m unittest discover -s "$root/skills/github-pr-check-validation/tests" -p 'test_*.py'
python3 -m unittest discover -s "$root/skills/github-sdlc-lifecycle-recovery/tests" -p 'test_*.py'
python3 -m unittest discover -s "$root/skills/github-pr-lifecycle-recovery/tests" -p 'test_*.py'
python3 -m unittest discover -s "$root/skills/github-pr-rejection/tests" -p 'test_*.py'

python3 - "$root" <<'PY'
from pathlib import Path
import re
import sys

root = Path(sys.argv[1])
files = list((root / "agents").glob("*.md")) + list((root / "skills").glob("*/SKILL.md"))
broken = []
flow = []
for path in files:
    text = path.read_text()
    lines = text.splitlines()
    in_frontmatter = False
    in_yaml = False
    delimiters = 0
    for number, line in enumerate(lines, 1):
        if line == "---" and delimiters < 2:
            delimiters += 1
            in_frontmatter = delimiters == 1
            continue
        if line == "```yaml":
            in_yaml = True
            continue
        if line == "```" and in_yaml:
            in_yaml = False
            continue
        if (in_frontmatter or in_yaml) and re.search(r":\s*\[[^\]]+\]|:\s*\{[^}]+\}", line):
            flow.append(f"{path.relative_to(root)}:{number}")
    for match in re.finditer(r"\[[^\]]*\]\(([^)]+\.md)(?:#[^)]+)?\)", text):
        target = match.group(1)
        if target.startswith(("/", "http://", "https://")):
            continue
        if not (path.parent / target).resolve().exists():
            broken.append(f"{path.relative_to(root)} -> {target}")
if flow:
    raise SystemExit("flow-style YAML: " + ", ".join(flow))
if broken:
    raise SystemExit("broken Markdown links: " + ", ".join(broken))
PY

if grep -R -qE 'agent: github-sdlc|execution_route: github-sdlc|`github-sdlc`' "$root/agents" "$root/skills"; then
  printf '%s\n' 'obsolete github-sdlc routing remains' >&2
  exit 1
fi

printf '%s\n' 'agent-skill architecture validation passed'
