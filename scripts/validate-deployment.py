#!/usr/bin/env python3
"""Validate the checked-in OpenCode/OpenChamber deployment contract."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml


OPENCODE_VERSION = "2.1.2"
OPENCHAMBER_VERSION = "2.5.3"


def require(condition: bool, message: str, findings: list[str]) -> None:
    if not condition:
        findings.append(message)


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).parents[1]).resolve()
    findings: list[str] = []

    config = json.loads((root / "opencode.jsonc").read_text())
    require("plugin" not in config and "plugins" not in config, "config references a plugin not shipped by the bundle", findings)
    require("tools" not in config, "config fabricates a tool availability override", findings)
    for skill_path in config.get("skills", []):
        require(skill_path == "/opt/plugins/", f"unsupported external skill path: {skill_path}", findings)

    for link in (root / ".opencode").iterdir():
        if link.is_symlink():
            require(link.exists(), f"broken configuration symlink: {link.relative_to(root)}", findings)

    golang = (root / "containers/golang/Dockerfile").read_text()
    chamber = (root / "containers/openchamber/Dockerfile").read_text()
    require(f"ghcr.io/anomalyco/opencode:{OPENCODE_VERSION}" in golang, "OpenCode image is not pinned to the approved version", findings)
    require("USER ${USERNAME}" in golang and "WORKDIR /home/${USERNAME}" in golang, "OpenCode image does not start from the mounted global-config home", findings)
    require("/opt/plugins/opencode-skill-ascii-art-diagrams/" in golang, "configured external skill directory is not populated by the image", findings)
    require(f"ARG OPENCODE_VERSION={OPENCODE_VERSION}" in chamber, "OpenChamber CLI OpenCode version is not pinned", findings)
    require(f"ARG OPENCHAMBER_VERSION={OPENCHAMBER_VERSION}" in chamber, "OpenChamber version is not pinned", findings)
    require("@opencode/cli@${OPENCODE_VERSION}" in chamber, "OpenChamber image does not use its OpenCode version pin", findings)
    require("@openchamber/web@${OPENCHAMBER_VERSION}" in chamber, "OpenChamber image does not use its version pin", findings)

    compose = yaml.safe_load((root / "openchamber.yaml").read_text())
    services = compose.get("services", {})
    require(set(services) == {"obsidian", "opencode", "openchamber"}, "unexpected deployment service set", findings)
    opencode_volumes = services.get("opencode", {}).get("volumes", [])
    chamber_volumes = services.get("openchamber", {}).get("volumes", [])
    require("./:/home/opencode/.config/opencode" in opencode_volumes, "bundle is not mounted as the OpenCode config source", findings)
    require(services.get("opencode", {}).get("command", [])[:1] == ["serve"], "OpenCode service is not the explicit server process", findings)
    for mount in ("/opt/opencode/workspace:/workspace", "/opt/opencode/worktrees:/worktrees", "/opt/opencode/tmp:/tmp/opencode"):
        require(mount in opencode_volumes and mount in chamber_volumes, f"OpenCode/OpenChamber do not share {mount.split(':', 1)[0]}", findings)
    chamber_environment = services.get("openchamber", {}).get("environment", {})
    require(chamber_environment.get("OPENCODE_HOST") == "http://opencode:4096", "OpenChamber is not pointed at the deployed OpenCode service", findings)
    require(chamber_environment.get("OPENCODE_SKIP_START") == "true", "OpenChamber may start an unapproved embedded OpenCode", findings)

    require((root / "agents/sdlc-orchestrator.md").is_file(), "primary SDLC agent is missing", findings)
    require((root / "skills/execution-evidence-reporting/SKILL.md").is_file(), "standard evidence skill is missing", findings)
    require(not re.search(r"npm install -g .*@(latest|next)(?:\s|$)", chamber), "deployment uses a floating npm version", findings)

    if findings:
        print("deployment validation failed:", file=sys.stderr)
        for finding in findings:
            print(f"- {finding}", file=sys.stderr)
        return 1
    print(
        "static deployment validation passed: "
        f"external OpenCode {OPENCODE_VERSION}, OpenChamber {OPENCHAMBER_VERSION}; "
        "runtime capability smoke verification remains required"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
