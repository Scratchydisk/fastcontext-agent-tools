from __future__ import annotations

import os
import runpy


def configure_path_tolerance() -> None:
    # Small / heavily-quantised models often mangle the workspace path in tool
    # arguments -- e.g. truncating "/mnt/a/b/repo" to "/repo" -- so every Read,
    # Grep, and Glob is rejected as "outside the working directory" and the
    # agent never reads anything. When FASTCONTEXT_REROOT_PATHS is enabled,
    # re-root such paths under the real working directory before the tool runs.
    # Off by default: full-precision models on larger GPUs follow the path
    # instructions correctly and should keep the strict upstream behaviour.
    #
    # The re-rooted path still passes through each tool's own containment check
    # (read/grep/glob all enforce is_relative_to(cwd) upstream), so this only
    # corrects the path; it never widens access.
    from fastcontext_mcp.runtime import reroot_under, truthy

    if not truthy(os.getenv("FASTCONTEXT_REROOT_PATHS")):
        return
    try:
        import json as _json
        from pathlib import Path as _Path

        from fastcontext.agent.tool.glob import GlobTool
        from fastcontext.agent.tool.grep import GrepTool
        from fastcontext.agent.tool.read import ReadTool
    except ModuleNotFoundError:
        return

    for cls, keys in ((ReadTool, ("path",)), (GrepTool, ("path",)), (GlobTool, ("directory",))):
        original_call = cls.call

        async def patched_call(self, parameters, *args, _orig=original_call, _keys=keys, **kwargs):
            cwd = kwargs.get("cwd")
            if cwd and isinstance(parameters, str):
                try:
                    data = _json.loads(parameters or "{}")
                except _json.JSONDecodeError:
                    data = None
                if isinstance(data, dict):
                    changed = False
                    for key in _keys:
                        if isinstance(data.get(key), str):
                            fixed = reroot_under(data[key], _Path(cwd))
                            if fixed != data[key]:
                                data[key] = fixed
                                changed = True
                    if changed:
                        parameters = _json.dumps(data)
            return await _orig(self, parameters, *args, **kwargs)

        cls.call = patched_call


def main() -> None:
    configure_path_tolerance()
    runpy.run_module("fastcontext.cli", run_name="__main__")


if __name__ == "__main__":
    main()
