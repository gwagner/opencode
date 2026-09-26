#!/bin/sh
# shellcheck disable=SC2016 # The fixture line must retain its literal variable.
set -eu

script_dir=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
root=$(CDPATH='' cd -- "$script_dir/.." && pwd)
audit="$root/scripts/audit-asset-references.py"

python3 "$audit" --root "$root"

fixture=$(mktemp -d "${TMPDIR:-/tmp}/asset-reference-audit.XXXXXX")
trap 'rm -rf "$fixture"' EXIT HUP INT TERM
mkdir -p "$fixture/scripts" "$fixture/tests"
cp -R "$root/agents" "$root/skills" "$fixture/"
cp "$root/README.md" "$fixture/README.md"
cp "$root/tests/agent-skill-architecture.sh" "$fixture/tests/"

expect_failure() {
  expected=$1
  if python3 "$audit" --root "$fixture" >"$fixture/stdout" 2>"$fixture/stderr"; then
    printf '%s\n' "audit unexpectedly accepted $expected" >&2
    exit 1
  fi
  grep -q "$expected" "$fixture/stderr"
}

cp "$fixture/README.md" "$fixture/README.clean"
sed '/| Agent | Purpose |/a | missing-agent | Fixture. |' "$fixture/README.clean" >"$fixture/README.md"
expect_failure "README.md:[0-9][0-9]*: dangling agent reference 'missing-agent'"

sed '/| Skill | Purpose |/a | missing-skill | Fixture. |' "$fixture/README.clean" >"$fixture/README.md"
expect_failure "README.md:[0-9][0-9]*: dangling skill reference 'missing-skill'"

cp "$fixture/README.clean" "$fixture/README.md"
printf '%s\n' 'test -f "$root/missing-asset.md"' >>"$fixture/tests/agent-skill-architecture.sh"
expect_failure "tests/agent-skill-architecture.sh:[0-9][0-9]*: dangling checked /code asset reference '/code/missing-asset.md'"
