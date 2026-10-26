#!/bin/sh
set -eu
export PYTHONDONTWRITEBYTECODE=1
root=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)
python3 "$root/tests/validate-agent-skill-architecture.py" "$root"
printf '%s\n' 'agent-skill architecture validation passed'
