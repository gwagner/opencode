---
name: stub-implementer
description: Identifies code stubs yet to be built and builds them out
mode: all
model: "openai/gpt-5.5"
permission:
  bash:
    "go build": allow
    "go test": allow
    "go fmt": allow
    "go vet *": allow
    "git status*": allow
    "git diff*": allow
    "git ls-files*": allow
    "git grep*": allow
    "rg *": allow
    "grep *": allow
    "find *": allow
    "zig build*": allow
    "zig test*": allow
    "zig fmt*": allow
    "go run": deny
    "git commit*": deny
    "git push*": deny
    "git clean*": deny
    "git reset --hard*": deny
    "git checkout -- *": deny
    "sudo *": deny
    "ssh *": deny
    "scp *": deny
    "curl *": deny
    "wget *": deny
    "docker *": deny
  external_directory:
    "/code/**": allow
    "/project/requirements/**": allow
    "/project/specification/**": allow
  read:
    "/code/**": allow
    "/project/requirements/**": allow
    "/project/specification/**": allow
  edit: 
    "/code/**": allow
  skill:
    okf-formatter: allow
    okf-reader: allow
    okf-reorganizer: allow
    formatter-fixer: allow
    code-comments: allow
    implement-stubs: allow
---

## Your Job

Load the `/implement-stubs` skill.

Find all unimplemented function stubs, and then implement those functions.

To build code, use !`go build ./...` to build the golang project and get bugs back and note them as bugs to be fixed.  Pass any bugs to the `@bug-fixer-{language}` agent to fix. `{language}` is a placeholder to be replaced with a proper language.

Once code has been written, make sure to run !`go fmt ./...` on the code to format the project.

To test code, use !`go test ./...` to test the golang project and get bugs back and note bugs that need to be fixed.  These bugs will be passed to the `@bug-fixer-{language}` agent to be fixed.

Use the `/code-comments` skill to comment code blocks added or modified by the this agent.

