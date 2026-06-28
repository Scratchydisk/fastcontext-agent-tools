# Accuracy benchmark

Run: 2026-06-28
Iterations per query: 3

- label: `8gb-a2000-ollama-q6`
- endpoint: `http://127.0.0.1:11434/v1`
- model: `fc-q6-nothink:latest`
- FC_MAX_TOKENS: `4000`
- FC_TEMPERATURE: `0.2`
- FASTCONTEXT_REROOT_PATHS: `1`

**File-hit rate: 9/15** (1 attempt(s) timed out, counted as misses)

| # | hits | files cited (any iter) | avg tool calls |
|---|------|------------------------|----------------|
| 1 | 3/3 | runtime.py, server.py | 9.0 |
| 2 | 2/3 | server.py | 19.3 |
| 3 | 1/3 | runtime.py | 16.7 |
| 4 | 3/3 | runtime.py | 32.0 |
| 5 | 0/3 | (none) | 36.0 |

A *hit* means a returned citation pointed at an accepted ground-truth file for that query. A miss returned either no citation or one on a different file. Results vary run to run (sampling); re-run to confirm.
