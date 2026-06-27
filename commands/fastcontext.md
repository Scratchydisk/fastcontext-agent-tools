---
description: Locate code by delegating to the FastContext explorer (returns verified file:line citations)
argument-hint: <what to find, e.g. "where JWT auth middleware is applied">
---

Delegate a code-location search to FastContext, then verify the results.

1. If `$ARGUMENTS` is empty, ask what to locate and stop.
2. Call the `fastcontext_explore` MCP tool with:
   - `repo_path`: the absolute path of the current working directory (run `pwd` if unsure)
   - `query`: `$ARGUMENTS`
3. FastContext returns **candidate** file:line citations, not ground truth. Open
   each one and confirm it actually matches the query before reporting it.
4. Report the confirmed citations as `path:start-end` with a one-line note on
   what each contains. Drop any that don't match; if nothing matches, refine the
   query and search again (or say so).

Do not start editing or solving anything — this command only locates code.
