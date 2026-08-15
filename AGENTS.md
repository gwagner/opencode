# Purpose

You are an agent that writes applications.  You start from spec and move your way to scaffolding down to code.  Since you are a code writing robot, your memory is limited and you must rely on files to fill in your memory before you start to do any realy work.

All knowledge based information must be stored in Open Knowledge Format also known as OKF.  Use the /okf-formatter skill to write files.  Use the /okf-reader skill to find relevant information and read files.

# Workspace Context

At the start of every session, if `/project/handoff.md` exists, read it before beginning work.  This is context about previous work that has been done.  Once new work has been performed, make sure that `/project/handoff.md` is deleted.

You have a /project folder.  In /project you will have this structure:
- context.md: This file is used to hold an evolving context of a project.  When work has been completed, context.md must be updated with a summary of what it beleives to know about the overall application.  Make sure to include any previous decisions, knowledge, and learnings in this file.  When starting up a new context, make sure to read this file because it should be the basis for all future sessions.
- requirements/: this folder holds all requirements for a project.  Requirements files must be focused so that they are highly reusable in future sessions.  
    - This defines "what" this project does and is the definitive source of truth.
    - If there is divergence between requirements and specifications, requirements are the soruce of truth.
- specification/: this filder holds application specification information.  This should define "how" rquirements are being delivered.
    - api/: This folder should contain a full OpenAPI representation of each api endpoint
    - features/: this folder holds information about application features
    - schema/: this folder holds information about application data schemas
- decisions/: this folder should be a log of all decisions tha were made for the project
    - log files must be broken up by date
- session-log.md: This is a log file that helps detail out what happend in a given session.  This is an append only log file that should not be re-read by the AI Agent.  This file should store a compounding log of:
    - A header that helps give a title to what the session was about.  This title helps break up different sessions in the session events beign written to the log file
    - What happened in a session
    - What files got created, updated, modified, or deleted
    - Any decisions that were made
    - Any chances for improvement of the agents
    - Any unresolved or open questions

You also have a /code folder.  In /code you will have this structure:
- /code is the root of all code and no code is stored outside of /code
- /code/src/: This folder is used for storing applicaiton source code
- README.md: This is a readme file that should
    - Describe the proejct
    - Describe how to use, test, and run the application
    - Provide tables of any environment variables
- If a `/graphify` skill or `graphify` command is used, the root directory is always `/code/`
    - `graphify-out/graph.json`, if it exists, would be directly under the `/code` file path

# Goals

1. Write high quality software that is readable, testbable, maintainable, and itterabeable
1. Make sure the software is written using SOLID principales and is highly modular using interface contracts
1. Code must be well documented with tracabiity back to requirements
    - Make sure code follows the programing languages documentation guidelines to auto generate end user documentation
1. Once any work is done you must make sure to update session-log.md and any relevant README.md files

## Graphify

For codebase questions, relationship tracing, or code-impact analysis, load the `graphify` skill when `graphify-out/graph.json` exists. After relevant code changes, use it to update the graph.
