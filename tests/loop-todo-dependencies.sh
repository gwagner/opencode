#!/bin/sh
set -eu
. /code/tests/loop-test-lib.sh

tmpdir=$(mktemp -d)
cleanup() {
  rm -rf "$tmpdir"
}
trap cleanup EXIT INT TERM

install_loop_fixture "$tmpdir"
cat > "$tmpdir/run" <<'EOF'
#!/bin/sh
count=$(cat "$RUN_COUNT" 2>/dev/null || printf 0)
count=$((count + 1))
printf '%s' "$count" > "$RUN_COUNT"
printf '%s\n' "$3" >> "$PROMPTS"
printf '%s\n' '<task>DONE</task>'
EOF
chmod +x "$tmpdir/loop" "$tmpdir/run"

repo="$tmpdir/repo"
mkdir "$repo"
cat > "$repo/todo.md" <<'EOF'
- [ ] dependent task
  - Branch: test/dependent
  - Depends on: test/prerequisite
- [ ] prerequisite task
  - Branch: test/prerequisite
EOF
init_loop_repo "$repo"

RUN_COUNT="$tmpdir/run.count"
PROMPTS="$tmpdir/prompts"
export RUN_COUNT PROMPTS
use_loop_repo "$repo"
output="$tmpdir/output"
MAX_LOOPS=2 "$tmpdir/loop" demo-agent worker >"$output" 2>&1

[ "$(cat "$RUN_COUNT")" -eq 2 ]
grep -q 'WARNING: skipping todo line 1 because its dependencies are incomplete: test/prerequisite' "$output"
grep -q '^\- \[x\] dependent task$' "$repo/todo.md"
grep -q '^\- \[x\] prerequisite task$' "$repo/todo.md"
prerequisite_line=$(grep -n -- '- \[ \] prerequisite task' "$PROMPTS" | cut -d: -f1)
dependent_line=$(grep -n -- '- \[ \] dependent task' "$PROMPTS" | cut -d: -f1)
[ "$prerequisite_line" -lt "$dependent_line" ]
