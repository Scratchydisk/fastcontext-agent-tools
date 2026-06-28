# Accuracy benchmark

Run: 2026-06-28
Iterations per query: 3

- label: `12gb-3060-ollama-q4`
- endpoint: `http://127.0.0.1:30004/v1`
- model: `fc-q4-nothink-16k:latest`
- FC_MAX_TOKENS: `4000`
- FC_TEMPERATURE: `0.2`
- FASTCONTEXT_REROOT_PATHS: `1`

**File-hit rate: 15/15**

| # | hits | files cited (any iter) | avg tool calls |
|---|------|------------------------|----------------|
| 1 | 3/3 | runtime.py, server.py | 9.7 |
| 2 | 3/3 | server.py | 23.3 |
| 3 | 3/3 | runtime.py, server.py | 34.0 |
| 4 | 3/3 | runtime.py | 43.3 |
| 5 | 3/3 | fastcontext_cli.py, runtime.py | 53.0 |

A *hit* means a returned citation pointed at an accepted ground-truth file for that query. A miss returned either no citation or one on a different file. Results vary run to run (sampling); re-run to confirm.
