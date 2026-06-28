# Accuracy benchmark

Run: 2026-06-28
Iterations per query: 3

- label: `24gb-5090-ollama-q4`
- endpoint: `http://127.0.0.1:30006/v1`
- model: `fc-q4-nothink-16k:latest`
- FC_MAX_TOKENS: `4000`
- FC_TEMPERATURE: `0.2`
- FASTCONTEXT_REROOT_PATHS: `1`

**File-hit rate: 14/15**

| # | hits | files cited (any iter) | avg tool calls |
|---|------|------------------------|----------------|
| 1 | 3/3 | fastcontext_cli.py, runtime.py, server.py | 7.7 |
| 2 | 3/3 | runtime.py, server.py | 46.7 |
| 3 | 2/3 | runtime.py, server.py | 79.7 |
| 4 | 3/3 | cases.py, runtime.py, test_server.py | 91.7 |
| 5 | 3/3 | env.local.sh.example, fastcontext_cli.py, runtime.py, serve-model.sh | 105.0 |

A *hit* means a returned citation pointed at an accepted ground-truth file for that query. A miss returned either no citation or one on a different file. Results vary run to run (sampling); re-run to confirm.
