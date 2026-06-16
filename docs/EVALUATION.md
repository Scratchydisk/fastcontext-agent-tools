# Evaluation

This project currently has two evidence layers:

1. Local integration QA for this MCP server and Codex skill package.
2. Model-quality evidence from the upstream Microsoft FastContext project.

![Evaluation summary](assets/evaluation-summary.svg)

The summary image is intentionally split by data source and evidence type:

- Official Microsoft FastContext benchmark data.
- Local wrapper QA checks from this repository.
- One local MICE check-in before/after token smoke test.

## Local Integration QA

The repeatable local check is:

```bash
python -m evaluation.run_wrapper_eval
```

Last checked result committed in `evaluation/wrapper-eval.json`:

| Check | Result | Evidence |
| --- | --- | --- |
| Unit tests | PASS | Runs 13 tests covering parser, runtime, server, and wrapper behavior |
| MCP initialize | PASS | Starts the stdio server and completes JSON-RPC `initialize` |
| MCP tool discovery | PASS | Verifies `tools/list` exposes `fastcontext_health`, `fastcontext_explore`, and `fastcontext_explore_with_trace` |
| Health uses bundled CLI | PASS | Verifies `fastcontext_health` reports `fastcontext_mcp.fastcontext_cli` as the command module |
| Citation parsing | PASS | Runs `fastcontext_explore` through a fake FastContext CLI and parses two file-line citations |
| Trace output | PASS | Runs `fastcontext_explore_with_trace` and verifies the trajectory file is written inside the repo |
| Path allowlist guard | PASS | Calls a repo outside `FASTCONTEXT_ALLOWED_ROOTS` and verifies it is rejected |

Scope:

- MCP protocol basics: `initialize`, `tools/list`, and `tools/call`.
- Tool contract: `fastcontext_health`, `fastcontext_explore`, and `fastcontext_explore_with_trace`.
- Citation parsing from a FastContext-style `<final_answer>` block.
- Read-safety guard through `FASTCONTEXT_ALLOWED_ROOTS`.
- Trace file creation when `trajectory_path` is supplied.

Limitation:

- This wrapper evaluation uses a fake `fastcontext.cli` package so it can run without a GPU or model endpoint.
- It proves the integration wrapper, not FastContext model quality or before/after task impact.

## Local Before/After Token Smoke Test

One local before/after token smoke test is committed in
`evaluation/mice-checkin-before-after.json`.

Question:

> Locate the central check-in verification endpoint that writes Log records,
> marks tickets as used, updates subTickets, and may enqueue Printer jobs.

Project under test:

```text
/Users/jakevinlo/project/NodeProject/mice-gcloud-version
```

Ground truth:

- `app/routers/logs.js`
- `POST /log/add`
- Relevant lines include `192`, `233`, `275`, `304`, and `340`.

Token measurement uses `tiktoken` `cl100k_base` as a consistent local estimator
for main-agent context. It does not include FastContext's internal endpoint
tokens.

| Condition | Main-agent context tokens | Correctly found ground truth? | Notes |
| --- | ---: | --- | --- |
| Direct exploration | 6,979 | Yes | Search task symbols, then read `app/routers/logs.js:192-360` |
| FastContext raw output | 85 | No | Returned short citations, but missed `app/routers/logs.js` |
| FastContext cited-file verification | 1,251 | No | Read the files FastContext cited; still missed the endpoint |
| FastContext plus fallback | 8,230 | Yes | Had to fall back to direct exploration; +17.9% tokens versus direct |

For this local task, FastContext did not produce a token win when correctness is
required. The raw response was short, but the missed citation forced fallback.

A broader local benchmark should compare the same coding tasks under two
conditions:

- Direct exploration: the main agent reads and searches the repository itself.
- FastContext-delegated exploration: the main agent asks FastContext for
  candidate file-line citations, then solves from that focused evidence.

Both conditions need the same main agent, same endpoint configuration, same task
set, and measured outcomes such as task success, main-agent tokens, wall time,
and cited-file precision.

## Upstream Model Evidence

The model-quality claims should be attributed to Microsoft FastContext:

- Project: <https://github.com/microsoft/fastcontext>
- Model card: <https://huggingface.co/microsoft/FastContext-1.0-4B-SFT>
- Paper: <https://arxiv.org/abs/2606.14066>

Microsoft reports that FastContext is a lightweight repository-exploration subagent using read-only `READ`, `GLOB`, and `GREP` tools, returning compact file-line citations. Their reported Mini-SWE-Agent integration results include up to 5.5 score improvement and up to 60.3% main-agent token reduction across SWE-bench Multilingual, SWE-bench Pro, and SWE-QA.

This repository does not re-run those benchmarks. Reproducing them requires the upstream benchmark harness, task datasets, and configured main-agent and FastContext model endpoints.
