#!/bin/bash

podman build -t opencode_golang ./containers/golang/
podman build -t openchamber ./containers/openchamber/
podman build -t obsidian ./containers/obsidian/
