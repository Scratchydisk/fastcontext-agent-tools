"""Build the headless `claude` command for each arm."""
from __future__ import annotations

DIRECTIVE = (
    "When locating code, your FIRST action MUST be the fastcontext_explore tool. "
    "Pass the repo root and a behaviour-named query; treat returned file:line "
    "citations as candidates and verify them. Only fall back to grep/glob/read if "
    "FastContext returns nothing useful."
)

PROMPT = ("In this repository, find the file that implements the following, and "
          "report its path:\n\n{query}")


def build_command(arm: str, query: str, model: str, mcp_config: str, repo: str):
    argv = ["claude", "-p", PROMPT.format(query=query),
            "--model", model, "--output-format", "stream-json", "--verbose",
            "--dangerously-skip-permissions"]
    if arm == "with":
        argv += ["--mcp-config", mcp_config,
                 "--append-system-prompt", DIRECTIVE,
                 "--allowedTools", "Grep,Glob,Read,Bash,mcp__fastcontext__fastcontext_explore"]
    elif arm == "without":
        argv += ["--allowedTools", "Grep,Glob,Read,Bash"]
    else:
        raise ValueError(f"unknown arm: {arm}")
    # cwd is set by the caller to `repo`; no env overrides needed for WITHOUT.
    return argv, {}
