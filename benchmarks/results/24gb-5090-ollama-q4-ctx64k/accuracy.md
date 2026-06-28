# Accuracy benchmark

Run: 2026-06-28
Iterations per query: 3

- label: `24gb-5090-ollama-q4-ctx64k`
- endpoint: `http://127.0.0.1:30006/v1`
- model: `fc-q4-nothink-64k:latest`
- FC_MAX_TOKENS: `4000`
- FC_TEMPERATURE: `0.2`
- FASTCONTEXT_REROOT_PATHS: `1`

**File-hit rate: 12/15**

| # | hits | files cited (any iter) | avg tool calls |
|---|------|------------------------|----------------|
| 1 | 3/3 | fastcontext_cli.py, runtime.py, server.py | 12.3 |
| 2 | 2/3 | server.py | 39.3 |
| 3 | 1/3 | runtime.py, server.py | 77.7 |
| 4 | 3/3 | runtime.py | 102.3 |
| 5 | 3/3 | fastcontext_cli.py | 117.0 |

A *hit* means a returned citation pointed at an accepted ground-truth file for that query. A miss returned either no citation or one on a different file. Results vary run to run (sampling); re-run to confirm.
