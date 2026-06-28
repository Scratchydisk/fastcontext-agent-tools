"""Shared setup for the benchmark scripts.

Sets sensible endpoint defaults (without overriding anything already exported),
exposes the FastContext runtime, and provides small helpers. Point at your own
endpoint by exporting BASE_URL / MODEL / API_KEY before running.
"""
from __future__ import annotations

import os

# Endpoint + behaviour defaults. setdefault means your environment wins.
os.environ.setdefault("BASE_URL", "http://127.0.0.1:30000/v1")
os.environ.setdefault("MODEL", "microsoft/FastContext-1.0-4B-RL")
os.environ.setdefault("API_KEY", "")
os.environ.setdefault("FASTCONTEXT_ALLOWED_ROOTS", "/")
os.environ.setdefault("FC_MAX_TOKENS", "4000")
os.environ.setdefault("FC_TEMPERATURE", "0.2")
os.environ.setdefault("FASTCONTEXT_REROOT_PATHS", "1")

from fastcontext_mcp.runtime import run_fastcontext  # noqa: E402


def explore(repo: str, query: str, max_turns: int = 10, timeout: int | None = None) -> dict:
    if timeout is None:
        timeout = int(os.getenv("BENCH_TIMEOUT", "220"))
    return run_fastcontext(
        {
            "repo_path": repo,
            "query": query,
            "max_turns": max_turns,
            "citation": True,
            "timeout_seconds": timeout,
        }
    )


def config_lines() -> list[str]:
    return [
        f"- label: `{os.getenv('BENCH_LABEL') or '(none)'}`",
        f"- endpoint: `{os.environ['BASE_URL']}`",
        f"- model: `{os.environ['MODEL']}`",
        f"- FC_MAX_TOKENS: `{os.environ['FC_MAX_TOKENS']}`",
        f"- FC_TEMPERATURE: `{os.environ['FC_TEMPERATURE']}`",
        f"- FASTCONTEXT_REROOT_PATHS: `{os.environ['FASTCONTEXT_REROOT_PATHS']}`",
    ]
