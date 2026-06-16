from __future__ import annotations

import shlex
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from evaluation.official_benchmark_probes import probe_env, truncate


HARNESS_TIMEOUT_SECONDS: Final = 180


@dataclass(frozen=True, slots=True)
class HarnessProbe:
    name: str
    command: str
    cwd: str | None
    returncode: int | None
    duration_seconds: float
    dry_run_instances: int
    stdout_excerpt: str
    stderr_excerpt: str


def collect_official_harness_probes(
    upstream_root: Path | None,
    *,
    timeout_seconds: int = HARNESS_TIMEOUT_SECONDS,
) -> list[HarnessProbe]:
    if upstream_root is None:
        return []
    return [run_mini_swe_agent_zero_instance_probe(upstream_root, timeout_seconds)]


def run_mini_swe_agent_zero_instance_probe(upstream_root: Path, timeout_seconds: int) -> HarnessProbe:
    with tempfile.TemporaryDirectory(prefix="fastcontext-official-dryrun-") as tmp:
        tmp_root = Path(tmp)
        output = tmp_root / "preds.json"
        logs = tmp_root / "logs"
        _ = logs.mkdir(parents=True, exist_ok=True)
        command = [
            "uv",
            "run",
            "--group",
            "benchmark",
            "python",
            "benchmark/evaluation/bench_mini_swe_agent.py",
            "--bench",
            "swebench-multilingual",
            "--agent-config",
            "prompts/gpt-multi-fc.yaml",
            "--config",
            "benchmark/evaluation/configs/example.env",
            "--output",
            str(output),
            "--logs-dir",
            str(logs),
            "--workers",
            "1",
            "--run-head",
            "0",
        ]
        return run_harness_probe(
            name="mini_swe_agent_zero_instance",
            command=command,
            cwd=upstream_root,
            timeout_seconds=timeout_seconds,
        )


def run_harness_probe(
    *,
    name: str,
    command: list[str],
    cwd: Path,
    timeout_seconds: int,
) -> HarnessProbe:
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
        return make_failed_harness_probe(name, command, cwd, duration, str(exc))
    except subprocess.TimeoutExpired as exc:
        duration = time.monotonic() - started
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        return HarnessProbe(
            name=name,
            command=shlex.join(command),
            cwd=str(cwd.resolve()),
            returncode=None,
            duration_seconds=round(duration, 3),
            dry_run_instances=0,
            stdout_excerpt=truncate(stdout),
            stderr_excerpt=truncate(stderr or f"timed out after {timeout_seconds}s"),
        )

    duration = time.monotonic() - started
    return HarnessProbe(
        name=name,
        command=shlex.join(command),
        cwd=str(cwd.resolve()),
        returncode=completed.returncode,
        duration_seconds=round(duration, 3),
        dry_run_instances=0,
        stdout_excerpt=truncate(completed.stdout),
        stderr_excerpt=truncate(completed.stderr),
    )


def make_failed_harness_probe(
    name: str,
    command: list[str],
    cwd: Path,
    duration_seconds: float,
    stderr: str,
) -> HarnessProbe:
    return HarnessProbe(
        name=name,
        command=shlex.join(command),
        cwd=str(cwd.resolve()),
        returncode=None,
        duration_seconds=round(duration_seconds, 3),
        dry_run_instances=0,
        stdout_excerpt="",
        stderr_excerpt=truncate(stderr),
    )


def harness_probes_passed(harness_probes: list[HarnessProbe]) -> bool:
    return all(probe.returncode == 0 for probe in harness_probes)
