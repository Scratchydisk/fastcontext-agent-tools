"""Shared benchmark cases.

Ground truth is written against THIS repository's own source tree, so run the
benchmarks with the target repo pointing at a checkout of this repo (the
default). Override with FASTCONTEXT_BENCH_REPO to benchmark a different corpus
(you would then need to supply your own cases).

Each case is (query, acceptable_ground_truth_basenames, grep_terms). The grep
terms are what a competent agent might search for; they drive the independent
"grep + read" baseline in the token-usage benchmark.
"""
from __future__ import annotations

import os

TARGET_REPO = os.getenv(
    "FASTCONTEXT_BENCH_REPO",
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
)

CASES = [
    (
        "Where is the MCP JSON-RPC request routing and tool dispatch implemented?",
        {"server.py"},
        "handle_request|tools/call|dispatch",
    ),
    (
        "Where is the stdio message framing that reads and writes JSON-RPC messages?",
        {"server.py"},
        "read_message|write_message|stdin.buffer",
    ),
    (
        "Where are citations parsed out of the model's final_answer text?",
        {"runtime.py"},
        "parse_citations|final_answer",
    ),
    (
        "Where is the repo path validated against the allowed roots?",
        {"runtime.py"},
        "resolve_repo_path|allowed_roots|ALLOWED_ROOTS",
    ),
    (
        "Where are tool-call paths re-rooted under the workspace directory?",
        {"runtime.py", "fastcontext_cli.py"},
        "reroot_under|configure_path_tolerance",
    ),
]
