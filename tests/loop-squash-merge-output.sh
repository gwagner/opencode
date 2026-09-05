#!/bin/sh
set -eu
. /code/tests/loop-test-lib.sh

tmpdir=$(mktemp -d)
trap 'rm -rf "$tmpdir"' EXIT INT TERM

install_loop_fixture "$tmpdir"
cat > "$tmpdir/run" <<'EOF'
#!/bin/sh
printf '%s\n' '<task>DONE</task>'
EOF
chmod +x "$tmpdir/loop" "$tmpdir/run"

repo="$tmpdir/repo"
mkdir "$repo"
cat > "$repo/.gitignore" <<'EOF'
todo.md
blocked-todos.md
EOF
printf '%s\n' 'base' > "$repo/base.txt"
git init -q -b main "$repo"
git -C "$repo" config user.name 'Loop Test'
git -C "$repo" config user.email 'loop-test@example.invalid'
git -C "$repo" add .gitignore base.txt
git -C "$repo" commit -q -m 'Initialize repository'

git -C "$repo" switch -q -c test/merge-output
printf '%s\n' 'task work' > "$repo/task.txt"
git -C "$repo" add task.txt
git -C "$repo" commit -q -m 'Implement task part one'
printf '%s\n' 'second task change' > "$repo/second-task.txt"
git -C "$repo" add second-task.txt
git -C "$repo" commit -q -m 'Implement task part two'
task_tip=$(git -C "$repo" rev-parse HEAD)
git -C "$repo" switch -q main
printf '%s\n' 'new main work' > "$repo/main.txt"
git -C "$repo" add main.txt
git -C "$repo" commit -q -m 'Advance main'
main_before=$(git -C "$repo" rev-parse HEAD)

cat > "$repo/todo.md" <<'EOF'
- [ ] merge completed task branch
  - Branch: test/merge-output
EOF

real_git=$(command -v git)
mkdir "$tmpdir/bin"
cat > "$tmpdir/bin/git" <<EOF
#!/bin/sh
case " \$* " in
  *' commit --no-gpg-sign --allow-empty -m Complete todo: preserve commit failure '*)
    printf '%s\n' 'fatal: simulated squash commit failure' >&2
    exit 43
    ;;
  *' merge --squash '*)
    printf '%s\n' 'Useful merge detail' >&2
    case " \$* " in
      *' test/merge-failure '*)
        printf '%s\n' 'fatal: simulated merge failure' >&2
        exit 42
        ;;
    esac
    ;;
esac
exec "$real_git" "\$@"
EOF
chmod +x "$tmpdir/bin/git"

output="$tmpdir/output.txt"
use_loop_repo "$repo"
PATH="$tmpdir/bin:$PATH" "$tmpdir/loop" demo-project worker > "$output" 2>&1

grep -q 'Useful merge detail' "$output"
grep -q 'task completed' "$output"
grep -q 'All todo tasks processed.' "$output"
test "$(git -C "$repo" branch --show-current)" = main
test "$(git -C "$repo" rev-list --count "$main_before"..main)" -eq 1
if git -C "$repo" merge-base --is-ancestor "$task_tip" main; then
  printf '%s\n' 'Squashed task tip unexpectedly became main ancestry.' >&2
  exit 1
fi
if git -C "$repo" show-ref --verify --quiet refs/heads/test/merge-output; then
  printf '%s\n' 'Completed task branch was not deleted.' >&2
  exit 1
fi
test "$(cat "$repo/task.txt")" = 'task work'
test "$(cat "$repo/second-task.txt")" = 'second task change'

failure_repo="$tmpdir/failure-repo"
mkdir "$failure_repo"
cat > "$failure_repo/todo.md" <<'EOF'
- [ ] preserve merge failure
  - Branch: test/merge-failure
EOF
init_loop_repo "$failure_repo"
git -C "$failure_repo" switch -q -c test/merge-failure
printf '%s\n' 'failing task work' > "$failure_repo/task.txt"
git -C "$failure_repo" add task.txt
git -C "$failure_repo" commit -q -m 'Implement failing task'
git -C "$failure_repo" switch -q main
failure_main=$(git -C "$failure_repo" rev-parse HEAD)

failure_output="$tmpdir/failure-output.txt"
use_loop_repo "$failure_repo"
failure_status=0
PATH="$tmpdir/bin:$PATH" "$tmpdir/loop" demo-project worker > "$failure_output" 2>&1 || failure_status=$?
test "$failure_status" -eq 42
grep -q 'fatal: simulated merge failure' "$failure_output"
grep -q 'Useful merge detail' "$failure_output"
test "$(git -C "$failure_repo" branch --show-current)" = main
test "$(git -C "$failure_repo" rev-parse HEAD)" = "$failure_main"
git -C "$failure_repo" show-ref --verify --quiet refs/heads/test/merge-failure

commit_failure_repo="$tmpdir/commit-failure-repo"
mkdir "$commit_failure_repo"
cat > "$commit_failure_repo/todo.md" <<'EOF'
- [ ] preserve commit failure
  - Branch: test/commit-failure
EOF
init_loop_repo "$commit_failure_repo"
git -C "$commit_failure_repo" switch -q -c test/commit-failure
printf '%s\n' 'staged safely after failure' > "$commit_failure_repo/task.txt"
git -C "$commit_failure_repo" add task.txt
git -C "$commit_failure_repo" commit -q -m 'Implement commit-failure task'
git -C "$commit_failure_repo" switch -q main
commit_failure_main=$(git -C "$commit_failure_repo" rev-parse HEAD)

commit_failure_output="$tmpdir/commit-failure-output.txt"
use_loop_repo "$commit_failure_repo"
commit_failure_status=0
PATH="$tmpdir/bin:$PATH" "$tmpdir/loop" demo-project worker > "$commit_failure_output" 2>&1 || commit_failure_status=$?
test "$commit_failure_status" -eq 43
grep -q 'fatal: simulated squash commit failure' "$commit_failure_output"
grep -q 'preserving the task branch and staged merge result' "$commit_failure_output"
test "$(git -C "$commit_failure_repo" branch --show-current)" = main
test "$(git -C "$commit_failure_repo" rev-parse HEAD)" = "$commit_failure_main"
git -C "$commit_failure_repo" show-ref --verify --quiet refs/heads/test/commit-failure
git -C "$commit_failure_repo" diff --cached --quiet -- task.txt && exit 1
