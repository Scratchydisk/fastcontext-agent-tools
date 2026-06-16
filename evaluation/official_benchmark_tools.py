from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ToolAvailability:
    uv: bool
    docker: bool
    docker_daemon: bool


def collect_tools() -> ToolAvailability:
    has_docker = shutil.which("docker") is not None
    return ToolAvailability(
        uv=shutil.which("uv") is not None,
        docker=has_docker,
        docker_daemon=has_docker and docker_daemon_available(),
    )


def docker_daemon_available() -> bool:
    try:
        completed = subprocess.run(
            ["docker", "info"],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=15,
        )
    except subprocess.TimeoutExpired:
        return False
    return completed.returncode == 0
