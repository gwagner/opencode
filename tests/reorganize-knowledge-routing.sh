#!/bin/bash
set -euo pipefail

tmpdir=$(mktemp -d)
trap 'rm -rf "$tmpdir"' EXIT INT TERM

mkdir -p \
  "$tmpdir/docs/requirements/accounts" \
  "$tmpdir/docs/specification/api" \
  "$tmpdir/docs/specification/features" \
  "$tmpdir/docs/specification/schema" \
  "$tmpdir/docs/specification/architecture"

printf '%s\n' requirement > "$tmpdir/docs/requirements/accounts/login.md"
printf '%s\n' index > "$tmpdir/docs/requirements/index.md"
printf '%s\n' history > "$tmpdir/docs/specification/log.md"
printf '%s\n' api > "$tmpdir/docs/specification/api/login.md"
printf '%s\n' feature > "$tmpdir/docs/specification/features/login.md"
printf '%s\n' schema > "$tmpdir/docs/specification/schema/user.md"
printf '%s\n' architecture > "$tmpdir/docs/specification/architecture/system.md"

mkdir -p "$tmpdir/scripts"
cp /code/reorganize-knowledge "$tmpdir/reorganize-knowledge"
cp /code/scripts/markdown-segments.py "$tmpdir/scripts/markdown-segments.py"
cat > "$tmpdir/project-mounts.sh" <<'RESOLVER'
#!/bin/sh
resolve_project_mounts() {
  [ "${1:-}" = demo ] || return 1
  DOCS_MOUNT="${KNOWLEDGE_TEST_DOCS:?}/"
  CODE_MOUNT=/unused
  CONTAINER=unused
}
RESOLVER

cat > "$tmpdir/run" <<'RUNNER'
#!/bin/bash
set -eu
printf '%s\0' "$@" >> "${KNOWLEDGE_TEST_CALLS:?}"
prompt=$3
case "$prompt" in
  'Read-only reorganization assessment'*)
    if [ "${KNOWLEDGE_TEST_MODE:-keep}" = keep ]; then
      printf '%s\n' '<assessment>KEEP</assessment>'
    elif [ "${KNOWLEDGE_TEST_MODE:-keep}" = split-oversized ]; then
      case "$prompt" in
        *'Source profile: 11 lines across 4 semantic segments; preferred maximum 4 lines.'*'For an oversized source with multiple semantic segments, default to REPLACE when this segment can anchor a smaller coherent document'*)
          printf '%s\n' '<assessment>REPLACE</assessment>'
          ;;
        *) printf '%s\n' '<assessment>KEEP</assessment>' ;;
      esac
    elif [ "${KNOWLEDGE_TEST_MODE:-keep}" = split-large-feature ]; then
      case "$prompt" in
        *'Source profile: 17 lines across 5 semantic segments; preferred maximum 4 lines.'*'For an oversized source with multiple semantic segments, default to REPLACE when this segment can anchor a smaller coherent document'*)
          printf '%s\n' '<assessment>REPLACE</assessment>'
          ;;
        *) printf '%s\n' '<assessment>KEEP</assessment>' ;;
      esac
    else
      printf '%s\n' '<assessment>REPLACE</assessment>'
    fi
    ;;
  'Extract losslessly'*)
    staging=$(find "${KNOWLEDGE_TEST_DOCS:?}/requirements/.reorganization" -type d -name candidates | sort | tail -n 1)
    mkdir -p "$staging/accounts"
    if [ "${KNOWLEDGE_TEST_MODE:-keep}" = one-candidate ]; then
      printf '%s\n' '---' 'type: requirement' '---' '# Login policy' > "$staging/accounts/login-policy.md"
      printf '%s\n' '<extraction>DONE</extraction>'
    elif [ ! -f "$staging/accounts/login-policy.md" ]; then
      printf '%s\n' '---' 'type: requirement' '---' '# Login policy' > "$staging/accounts/login-policy.md"
      printf '%s\n' '<extraction>MORE</extraction>'
    elif [ ! -f "$staging/accounts/login-evidence.md" ]; then
      printf '%s\n' '---' 'type: requirement' '---' '# Login evidence' > "$staging/accounts/login-evidence.md"
      printf '%s\n' '<extraction>DONE</extraction>'
    else
      printf '%s\n' '<extraction>DONE</extraction>'
    fi
    ;;
  'Re-review compatibility'*) printf '%s\n' '<coverage>PASS</coverage>' ;;
  'Review exactly one staged candidate'*) printf '%s\n' '<candidate>PASS</candidate>' ;;
  'Prepare only the staged'*) printf '%s\n' '<navigation>DONE</navigation>' ;;
  'Perform a final READ-ONLY'*)
    if [ "${KNOWLEDGE_TEST_MODE:-keep}" = fail-final ]; then
      printf '%s\n' '<finalization>FAIL</finalization>'
    else
      printf '%s\n' '<finalization>PASS</finalization>'
    fi
    ;;
  *) printf '%s\n' 'unexpected prompt' >&2; exit 1 ;;
esac
RUNNER
chmod +x "$tmpdir/reorganize-knowledge" "$tmpdir/run"

export KNOWLEDGE_TEST_DOCS="$tmpdir/docs"
export KNOWLEDGE_TEST_CALLS="$tmpdir/calls"

"$tmpdir/reorganize-knowledge" --test demo > "$tmpdir/dry-run.out"
grep -q '/project/requirements/accounts/login.md' "$tmpdir/dry-run.out"
grep -q '/project/specification/api/login.md' "$tmpdir/dry-run.out"
grep -q '/project/specification/features/login.md' "$tmpdir/dry-run.out"
grep -q '/project/specification/schema/user.md' "$tmpdir/dry-run.out"
grep -q '/project/specification/architecture/system.md' "$tmpdir/dry-run.out"
grep -q 'Agent:   prd-strategist' "$tmpdir/dry-run.out"
grep -q 'Agent:   code-spec-engineer' "$tmpdir/dry-run.out"
grep -q 'Agent:   app-spec-architect' "$tmpdir/dry-run.out"
if grep -q '/project/requirements/index.md ->' "$tmpdir/dry-run.out"; then
  printf '%s\n' 'requirements index was incorrectly processed' >&2
  exit 1
fi
if grep -q '/project/specification/log.md ->' "$tmpdir/dry-run.out"; then
  printf '%s\n' 'specification log was incorrectly processed' >&2
  exit 1
fi
grep -q 'No agents will run and no files will change' "$tmpdir/dry-run.out"
grep -q 'Dry run sampled 5 semantic unit(s) from 5 source file(s)' "$tmpdir/dry-run.out"
grep -q 'All discovered semantic units fit within the sample limit' "$tmpdir/dry-run.out"
if grep -q 'Return exactly one token' "$tmpdir/dry-run.out"; then
  printf '%s\n' 'dry run leaked verbose agent prompts' >&2
  exit 1
fi

"$tmpdir/reorganize-knowledge" --test=2 demo > "$tmpdir/limited-dry-run.out"
[ "$(grep -c '^\[[0-9][0-9]*\] /project/' "$tmpdir/limited-dry-run.out")" -eq 2 ]
grep -q 'Dry run sampled 2 semantic unit(s)' "$tmpdir/limited-dry-run.out"
grep -q 'Sample limit reached; remaining sources were not scanned' "$tmpdir/limited-dry-run.out"
if grep -q '/project/specification/architecture/system.md' "$tmpdir/limited-dry-run.out"; then
  printf '%s\n' 'limited dry run printed beyond its sample' >&2
  exit 1
fi

export KNOWLEDGE_TEST_MODE=keep
"$tmpdir/reorganize-knowledge" demo > "$tmpdir/run.out"
grep -q '5 kept unchanged, 0 finalized' "$tmpdir/run.out"

python3 - "$KNOWLEDGE_TEST_CALLS" <<'PY'
import sys

args = open(sys.argv[1], "rb").read().split(b"\0")
if args[-1] == b"":
    args.pop()

assert len(args) == 25, args
calls = [args[index:index + 5] for index in range(0, len(args), 5)]
expected = [
    (b"/project/requirements/accounts/login.md", b"prd-strategist"),
    (b"/project/specification/api/login.md", b"code-spec-engineer"),
    (b"/project/specification/architecture/system.md", b"app-spec-architect"),
    (b"/project/specification/features/login.md", b"code-spec-engineer"),
    (b"/project/specification/schema/user.md", b"code-spec-engineer"),
]

for call, (path, agent) in zip(calls, expected):
    assert call[0:2] == [b"demo", b"run"], call
    assert path in call[2], call
    assert call[3:5] == [b"--agent", agent], call
PY

replacement_docs="$tmpdir/replacement-docs"
mkdir -p "$replacement_docs/requirements/accounts"
printf '%s\n' '# Login and unrelated combined policy' > "$replacement_docs/requirements/accounts/login.md"
export KNOWLEDGE_TEST_DOCS="$replacement_docs"
export KNOWLEDGE_TEST_CALLS="$tmpdir/replacement-calls"
export KNOWLEDGE_TEST_MODE=replace
"$tmpdir/reorganize-knowledge" demo > "$tmpdir/replacement.out"
[ ! -f "$replacement_docs/requirements/accounts/login.md" ]
[ -f "$replacement_docs/requirements/accounts/login-policy.md" ]
find "$replacement_docs/requirements/.reorganization" -name original.md -type f | grep -q .
grep -q '0 kept unchanged, 1 finalized' "$tmpdir/replacement.out"

oversized_docs="$tmpdir/oversized-docs"
mkdir -p "$oversized_docs/requirements/incidents"
cat > "$oversized_docs/requirements/incidents/detail.md" <<'MARKDOWN'
# Scope
Incident detail only.

# Requirements
- Preserve delivery ordering.
- Preserve pagination.

# Decisions
- Use hybrid refresh.

# Evidence
MARKDOWN
export KNOWLEDGE_TEST_DOCS="$oversized_docs"
export KNOWLEDGE_TEST_CALLS="$tmpdir/oversized-calls"
export KNOWLEDGE_TEST_MODE=split-oversized
REORGANIZE_PREFERRED_SEGMENT_LINES=4 "$tmpdir/reorganize-knowledge" demo > "$tmpdir/oversized.out"
grep -q '0 kept unchanged, 1 finalized' "$tmpdir/oversized.out"
[ ! -f "$oversized_docs/requirements/incidents/detail.md" ]
[ -f "$oversized_docs/requirements/accounts/login-policy.md" ]

large_feature_docs="$tmpdir/large-feature-docs"
mkdir -p "$large_feature_docs/requirements/incidents"
cat > "$large_feature_docs/requirements/incidents/detail.md" <<'MARKDOWN'
# Scope
Incident detail only.

# Actor and outcome
Customers inspect incident state and delivery outcomes.

# Requirements
- Preserve workflow actions.
- Refresh incident state.
- Reconcile delivery structure.

# Acceptance criteria
- State becomes current without reload.
- Delivery pages remain stable.

# Decisions
- Use bounded hybrid refresh.
MARKDOWN
export KNOWLEDGE_TEST_DOCS="$large_feature_docs"
export KNOWLEDGE_TEST_CALLS="$tmpdir/large-feature-calls"
export KNOWLEDGE_TEST_MODE=split-large-feature
REORGANIZE_PREFERRED_SEGMENT_LINES=4 "$tmpdir/reorganize-knowledge" demo > "$tmpdir/large-feature.out"
tr '\0' '\n' < "$tmpdir/large-feature-calls" |
  grep -Fq 'For an oversized source with multiple semantic segments, default to REPLACE when this segment can anchor a smaller coherent document'
grep -q '0 kept unchanged, 1 finalized' "$tmpdir/large-feature.out"
[ ! -f "$large_feature_docs/requirements/incidents/detail.md" ]
[ -f "$large_feature_docs/requirements/accounts/login-policy.md" ]

one_candidate_docs="$tmpdir/one-candidate-docs"
mkdir -p "$one_candidate_docs/requirements/accounts"
printf '%s\n' '# Combined policy' > "$one_candidate_docs/requirements/accounts/login.md"
export KNOWLEDGE_TEST_DOCS="$one_candidate_docs"
export KNOWLEDGE_TEST_CALLS="$tmpdir/one-candidate-calls"
export KNOWLEDGE_TEST_MODE=one-candidate
status=0
"$tmpdir/reorganize-knowledge" demo > "$tmpdir/one-candidate.out" 2>&1 || status=$?
[ "$status" -eq 1 ]
[ -f "$one_candidate_docs/requirements/accounts/login.md" ]
grep -q 'at least two are required. Original retained.' "$tmpdir/one-candidate.out"

rollback_docs="$tmpdir/rollback-docs"
mkdir -p "$rollback_docs/requirements/accounts"
printf '%s\n' '# Preserve me' > "$rollback_docs/requirements/accounts/login.md"
export KNOWLEDGE_TEST_DOCS="$rollback_docs"
export KNOWLEDGE_TEST_CALLS="$tmpdir/rollback-calls"
export KNOWLEDGE_TEST_MODE=fail-final
status=0
"$tmpdir/reorganize-knowledge" demo > "$tmpdir/rollback.out" 2>&1 || status=$?
[ "$status" -eq 1 ]
[ -f "$rollback_docs/requirements/accounts/login.md" ]
[ ! -f "$rollback_docs/requirements/accounts/login-policy.md" ]
grep -q 'promoted files rolled back and original retained' "$tmpdir/rollback.out"

cat > "$tmpdir/structured.md" <<'MARKDOWN'
# Product
Overview.

## First workflow
Intro.

```md
## This is code, not structure

example
```

Second paragraph.

Compatibility
-------------
| State | Result |
| --- | --- |
| on | works |
MARKDOWN
python3 /code/scripts/markdown-segments.py "$tmpdir/structured.md" 4 > "$tmpdir/segments"
python3 - "$tmpdir/segments" <<'PY'
import sys

values = open(sys.argv[1], "rb").read().split(b"\0")
if values[-1] == b"":
    values.pop()
segments = [tuple(item.decode() for item in values[index:index + 4]) for index in range(0, len(values), 4)]
contexts = [item[2] for item in segments]
assert contexts[0] == "Product", segments
assert "Product > First workflow [block group 2/3]" in contexts, segments
assert not any("This is code" in context for context in contexts), segments
assert contexts[-1] == "Product > Compatibility", segments
assert segments[-1][0] == "15" and segments[-1][1] == "19", segments
PY

cat > "$tmpdir/loose-list.md" <<'MARKDOWN'
# Steps
- First item

- Second item
MARKDOWN
python3 /code/scripts/markdown-segments.py "$tmpdir/loose-list.md" 2 > "$tmpdir/list-segments"
python3 - "$tmpdir/list-segments" <<'PY'
import sys

values = open(sys.argv[1], "rb").read().split(b"\0")
assert values == [b"1", b"4", b"Steps", b"none", b""], values
PY

cat > "$tmpdir/frontmatter.md" <<'MARKDOWN'
---
type: requirement
tags: [authentication]
---
# Login
Users can sign in.
MARKDOWN
python3 /code/scripts/markdown-segments.py "$tmpdir/frontmatter.md" 80 > "$tmpdir/frontmatter-segments"
python3 - "$tmpdir/frontmatter-segments" <<'PY'
import sys

values = open(sys.argv[1], "rb").read().split(b"\0")
assert values == [b"5", b"6", b"Login", b"1-4", b""], values
PY

cat > "$tmpdir/whitespace-preambles.md" <<'MARKDOWN'
---
type: requirement
---
   
	
# Login
Users can sign in.
MARKDOWN
python3 /code/scripts/markdown-segments.py "$tmpdir/whitespace-preambles.md" 80 > "$tmpdir/whitespace-preamble-segments"
python3 - "$tmpdir/whitespace-preamble-segments" <<'PY'
import sys

values = open(sys.argv[1], "rb").read().split(b"\0")
assert values == [b"6", b"7", b"Login", b"1-3", b""], values
PY

cat > "$tmpdir/document-start-preamble.md" <<'MARKDOWN'

  
# Product
Overview.
MARKDOWN
python3 /code/scripts/markdown-segments.py "$tmpdir/document-start-preamble.md" 80 > "$tmpdir/document-start-preamble-segments"
python3 - "$tmpdir/document-start-preamble-segments" <<'PY'
import sys

values = open(sys.argv[1], "rb").read().split(b"\0")
assert values == [b"3", b"4", b"Product", b"none", b""], values
PY

cat > "$tmpdir/nonempty-preamble.md" <<'MARKDOWN'
Introduction.

# Product
Overview.
MARKDOWN
python3 /code/scripts/markdown-segments.py "$tmpdir/nonempty-preamble.md" 80 > "$tmpdir/nonempty-preamble-segments"
python3 - "$tmpdir/nonempty-preamble-segments" <<'PY'
import sys

values = open(sys.argv[1], "rb").read().split(b"\0")
assert values == [
    b"1", b"2", b"Document preamble", b"none",
    b"3", b"4", b"Product", b"none", b"",
], values
PY

cat > "$tmpdir/metadata-only.md" <<'MARKDOWN'
---
type: requirement
---
MARKDOWN
python3 /code/scripts/markdown-segments.py "$tmpdir/metadata-only.md" 80 > "$tmpdir/metadata-only-segments"
[ ! -s "$tmpdir/metadata-only-segments" ]

status=0
"$tmpdir/reorganize-knowledge" missing > "$tmpdir/missing.out" 2>&1 || status=$?
[ "$status" -eq 1 ]
