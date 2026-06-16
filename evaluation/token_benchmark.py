from __future__ import annotations

import argparse
import importlib
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol, runtime_checkable


ROOT = Path(__file__).resolve().parents[1]
FASTCONTEXT_COMMAND = [sys.executable, "-m", "fastcontext_mcp.fastcontext_cli"]


@runtime_checkable
class TokenEncoding(Protocol):
    def encode(self, text: str) -> list[int]: ...


@runtime_checkable
class TokenModule(Protocol):
    def get_encoding(self, name: str) -> TokenEncoding: ...


def token_count(text: str) -> int:
    try:
        tiktoken_module = importlib.import_module("tiktoken")
    except ImportError as exc:
        raise SystemExit("Install tiktoken to run token benchmarks: python -m pip install tiktoken") from exc
    if not isinstance(tiktoken_module, TokenModule):
        raise SystemExit("Installed tiktoken module does not expose get_encoding().")
    return len(tiktoken_module.get_encoding("cl100k_base").encode(text))


def run_command(command: list[str], cwd: Path, env: dict[str, str] | None = None, timeout: int = 240) -> dict[str, Any]:
    started = time.perf_counter()
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "command": command,
            "returncode": 124,
            "stdout": timeout_text(exc.stdout),
            "stderr": timeout_text(exc.stderr) + f"\nTimed out after {timeout} seconds.",
            "seconds": round(time.perf_counter() - started, 3),
        }
    return {
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "seconds": round(time.perf_counter() - started, 3),
    }


def timeout_text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def command_text(results: list[dict[str, Any]]) -> str:
    return "\n".join(str(result["stdout"]) + str(result["stderr"]) for result in results)


def parse_citations(output: str, repo: Path) -> list[dict[str, Any]]:
    citations = []
    pattern = r"(?P<path>(?:/Users/[^:\n]+?|/[A-Za-z0-9_.-]+/[^:\n]+?|[A-Za-z0-9_.-]+/[^:\n]+?)):(?P<start>\d+)(?:-(?P<end>\d+))?"
    for match in re.finditer(pattern, output):
        raw = match.group("path").strip()
        rel = normalize_path(raw, repo)
        start = int(match.group("start"))
        end = int(match.group("end") or str(start + 80))
        citations.append(
            {
                "raw": raw,
                "rel": str(rel) if rel else None,
                "start": start,
                "end": end,
            }
        )
    return citations


def normalize_path(raw: str, repo: Path) -> Path | None:
    if raw.startswith("/Users/"):
        path = Path(raw)
        return path.relative_to(repo) if str(path).startswith(str(repo)) else None
    if raw.startswith(f"/{repo.name}/"):
        return Path(raw.removeprefix(f"/{repo.name}/"))
    candidate = Path(raw)
    return candidate if (repo / candidate).exists() or not raw.startswith("/") else None


def read_citations(citations: list[dict[str, Any]], repo: Path) -> tuple[str, list[dict[str, Any]], list[dict[str, Any]]]:
    parts = []
    existing = []
    missing = []
    ranges_by_file: dict[str, list[tuple[int, int]]] = {}
    for citation in citations:
        rel = citation["rel"]
        if rel and (repo / rel).exists():
            start = max(1, int(citation["start"]) - 20)
            end = min(int(citation["end"]) + 20, int(citation["start"]) + 220)
            ranges_by_file.setdefault(rel, []).append((start, end))
            existing.append({**citation, "read_start": start, "read_end": end})
        else:
            missing.append(citation)
    for rel, ranges in ranges_by_file.items():
        for start, end in merge_ranges(ranges):
            output = run_command(["sed", "-n", f"{start},{end}p", rel], repo)
            parts.append(f"--- {rel}:{start}-{end} ---\n{output['stdout']}{output['stderr']}")
    return "\n".join(parts), existing, missing


def merge_ranges(ranges: list[tuple[int, int]]) -> list[tuple[int, int]]:
    merged: list[tuple[int, int]] = []
    for start, end in sorted(ranges):
        if not merged or start > merged[-1][1] + 1:
            merged.append((start, end))
            continue
        merged[-1] = (merged[-1][0], max(merged[-1][1], end))
    return merged


def benchmark_task(task: dict[str, Any]) -> dict[str, Any]:
    repo = Path(task["repo_path"]).resolve()
    direct_results = [run_command(command, repo) for command in task["direct_commands"]]
    direct_text = command_text(direct_results)
    fastcontext = run_fastcontext(task, repo)
    fastcontext_text = str(fastcontext["stdout"]) + str(fastcontext["stderr"])
    verify_text, existing, missing = read_citations(parse_citations(str(fastcontext["stdout"]), repo), repo)
    hits = {path: path in fastcontext_text or path in verify_text for path in task["ground_truth_files"]}
    all_hit = all(hits.values())
    corrected_text = fastcontext_text + "\n" + verify_text + ("" if all_hit else "\n" + direct_text)
    direct_tokens = token_count(direct_text)
    corrected_tokens = token_count(corrected_text)
    return {
        "id": task["id"],
        "project_under_test": str(repo),
        "question": task["question"],
        "tokenizer": "tiktoken cl100k_base",
        "ground_truth_files": task["ground_truth_files"],
        "direct_before": {
            "main_agent_context_tokens": direct_tokens,
            "wall_seconds": round(sum(float(result["seconds"]) for result in direct_results), 3),
            "found_ground_truth": all(path in direct_text for path in task["ground_truth_files"]),
        },
        "fastcontext_after_raw": {
            "main_agent_context_tokens": token_count(fastcontext_text),
            "wall_seconds": fastcontext["seconds"],
            "returncode": fastcontext["returncode"],
            "found_all_ground_truth_files": all_hit,
            "ground_truth_hits": hits,
            "returned_existing_citations": existing,
            "returned_missing_citations": missing,
            "stdout": fastcontext["stdout"],
        },
        "fastcontext_after_verified": {
            "main_agent_context_tokens": corrected_tokens,
            "fastcontext_output_tokens": token_count(fastcontext_text),
            "returned_file_read_tokens": token_count(verify_text),
            "fallback_direct_tokens": 0 if all_hit else direct_tokens,
            "delta_vs_direct_tokens": corrected_tokens - direct_tokens,
            "delta_vs_direct_percent": round((corrected_tokens - direct_tokens) * 100 / direct_tokens, 1),
        },
    }


def run_fastcontext(task: dict[str, Any], repo: Path) -> dict[str, Any]:
    env = os.environ.copy()
    env.setdefault("API_KEY", task.get("api_key", "ollama"))
    env.setdefault("BASE_URL", task["base_url"])
    env.setdefault("MODEL", task["model"])
    return run_command(
        [
            *FASTCONTEXT_COMMAND,
            "--query",
            task["question"],
            "--max-turns",
            str(task.get("max_turns", 6)),
            "--citation",
        ],
        repo,
        env=env,
        timeout=int(task.get("timeout_seconds", 240)),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("task_file", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    task_data = json.loads(args.task_file.read_text(encoding="utf-8"))
    tasks = task_data["tasks"] if isinstance(task_data, dict) and "tasks" in task_data else [task_data]
    results = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "results": [benchmark_task(task) for task in tasks],
    }
    text = json.dumps(results, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
