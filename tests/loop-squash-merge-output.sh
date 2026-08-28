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

git -C "$repo" switch -q -c test/squash-output
printf '%s\n' 'task work' > "$repo/task.txt"
git -C "$repo" add task.txt
git -C "$repo" commit -q -m 'Implement task'
git -C "$repo" switch -q main
printf '%s\n' 'new main work' > "$repo/main.txt"
git -C "$repo" add main.txt
git -C "$repo" commit -q -m 'Advance main'

cat > "$repo/todo.md" <<'EOF'
- [ ] hide raw squash merge message
  - Branch: test/squash-output
EOF

real_git=$(command -v git)
mkdir "$tmpdir/bin"
cat > "$tmpdir/bin/git" <<EOF
#!/bin/sh
case " \$* " in
  *' merge --squash '*)
    printf '%s\n' 'Useful merge detail' >&2
    case " \$* " in
      *' test/merge-failure '*)
        printf '%s\n' 'fatal: simulated merge failure' >&2
        exit 42
        ;;
    esac
    printf '%s\n' 'Automatic merge went well; stopped before committing as requested' >&2
    ;;
esac
exec "$real_git" "\$@"
EOF
chmod +x "$tmpdir/bin/git"

output="$tmpdir/output.txt"
use_loop_repo "$repo"
PATH="$tmpdir/bin:$PATH" "$tmpdir/loop" demo-project worker > "$output" 2>&1

if grep -q 'Automatic merge went well; stopped before committing as requested' "$output"; then
  printf '%s\n' 'Raw Git squash-merge message was not suppressed.' >&2
  exit 1
fi
grep -q 'Useful merge detail' "$output"
grep -q 'task completed' "$output"
grep -q 'All todo tasks processed.' "$output"
test "$(git -C "$repo" branch --show-current)" = main
test ! -e "$repo/.git/refs/heads/test/squash-output"
test -f "$repo/task.txt"

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

failure_output="$tmpdir/failure-output.txt"
use_loop_repo "$failure_repo"
failure_status=0
PATH="$tmpdir/bin:$PATH" "$tmpdir/loop" demo-project worker > "$failure_output" 2>&1 || failure_status=$?
test "$failure_status" -eq 42
grep -q 'fatal: simulated merge failure' "$failure_output"
grep -q 'Useful merge detail' "$failure_output"
