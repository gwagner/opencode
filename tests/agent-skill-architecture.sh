#!/bin/sh
set -eu
export PYTHONDONTWRITEBYTECODE=1
root=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)
python3 "$root/tests/validate-agent-skill-architecture.py" "$root"
python3 -m unittest discover -s "$root/tests" -p 'test_*.py'
printf '%s\n' 'agent-skill architecture and behavioral validation passed'
