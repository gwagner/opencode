#!/bin/sh
set -eu

engine=${CONTAINER_ENGINE:-docker}
root=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)

"$engine" build -t opencode_golang "$root/containers/golang/"
"$engine" build -t openchamber "$root/containers/openchamber/"
"$engine" build -t obsidian "$root/containers/obsidian/"
