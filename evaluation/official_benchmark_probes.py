from __future__ import annotations

import os
import shlex
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Final


COMMAND_TIMEOUT_SECONDS: Final = 90
MAX_EXCERPT_CHARS: Final = 1200


@dataclass(frozen=True, slots=True)
class CommandProbe:
    name: str
    command: str
    cwd: str | None
    returncode: int | None
    duration_seconds: float
    stdout_excerpt: str
    stderr_excerpt: str


def collect_official_command_probes(
    upstream_root: Path | None,
    *,
    timeout_seconds: int = COMMAND_TIMEOUT_SECONDS,
) -> list[CommandProbe]:
    if upstream_root is None:
        return []

    commands = [
        (
            "mini_swe_agent_help",
            [
                "uv",
                "run",
                "--group",
                "benchmark",
                "python",
                "benchmark/evaluation/bench_mini_swe_agent.py",
                "--help",
            ],
        ),
        (
            "swebench_fastcontext_help",
            [
                "uv",
                "run",
                "--group",
                "benchmark",
                "python",
                "benchmark/swebench/bench_fastcontext.py",
                "--help",
            ],
        ),
        (
            "run_score_import",
            [
                "uv",
                "run",
                "--group",
                "benchmark",
                "python",
                "-c",
                "import sys; sys.path.insert(0, 'benchmark/evaluation'); import run_score; print('run_score import ok')",
            ],
        ),
    ]
    return [run_command_probe(name, command, upstream_root, timeout_seconds) for name, command in commands]


def run_command_probe(
    name: str,
    command: list[str],
    cwd: Path,
    timeout_seconds: int,
) -> CommandProbe:
    started = time.monotonic()
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            env=probe_env(),
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
    except FileNotFoundError as exc:
        duration = time.monotonic() - started
        return CommandProbe(
            name=name,
            command=shlex.join(command),
            cwd=str(cwd.resolve()),
            returncode=None,
            duration_seconds=round(duration, 3),
            stdout_excerpt="",
            stderr_excerpt=truncate(str(exc)),
        )
    except subprocess.TimeoutExpired as exc:
        duration = time.monotonic() - started
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        return CommandProbe(
            name=name,
            command=shlex.join(command),
            cwd=str(cwd.resolve()),
            returncode=None,
            duration_seconds=round(duration, 3),
            stdout_excerpt=truncate(stdout),
            stderr_excerpt=truncate(stderr or f"timed out after {timeout_seconds}s"),
        )

    duration = time.monotonic() - started
    return CommandProbe(
        name=name,
        command=shlex.join(command),
        cwd=str(cwd.resolve()),
        returncode=completed.returncode,
        duration_seconds=round(duration, 3),
        stdout_excerpt=truncate(completed.stdout),
        stderr_excerpt=truncate(completed.stderr),
    )


def probes_passed(command_probes: list[CommandProbe]) -> bool:
    return all(probe.returncode == 0 for probe in command_probes)


def probe_env() -> dict[str, str]:
    env = os.environ.copy()
    _ = env.pop("VIRTUAL_ENV", None)
    return env


def truncate(value: str) -> str:
    clean = value.strip()
    if len(clean) <= MAX_EXCERPT_CHARS:
        return clean
    return clean[: MAX_EXCERPT_CHARS - 3].rstrip() + "..."
