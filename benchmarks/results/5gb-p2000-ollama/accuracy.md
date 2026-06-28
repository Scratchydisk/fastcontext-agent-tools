# Accuracy benchmark

Run: 2026-06-28
Iterations per query: 2

- label: `5gb-p2000-ollama`
- endpoint: `http://127.0.0.1:30003/v1`
- model: `fastcontext-nothink:latest`
- FC_MAX_TOKENS: `4000`
- FC_TEMPERATURE: `0.2`
- FASTCONTEXT_REROOT_PATHS: `1`

**File-hit rate: 5/10**

| # | hits | files cited (any iter) | avg tool calls |
|---|------|------------------------|----------------|
| 1 | 1/2 | runtime.py, server.py | 3.0 |
| 2 | 0/2 | (none) | 3.0 |
| 3 | 2/2 | runtime.py, test_server.py | 15.5 |
| 4 | 2/2 | cases.py, runtime.py, test_server.py | 26.5 |
| 5 | 0/2 | (none) | 28.0 |

A *hit* means a returned citation pointed at an accepted ground-truth file for that query. A miss returned either no citation or one on a different file. Results vary run to run (sampling); re-run to confirm.
