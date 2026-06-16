from __future__ import annotations

from pathlib import Path

from evaluation.official_benchmark_datasets import DatasetProbe, dataset_probes_passed
from evaluation.official_benchmark_env import EnvConfigCheck
from evaluation.official_benchmark_harness import HarnessProbe, harness_probes_passed
from evaluation.official_benchmark_images import ImageManifestProbe, image_probes_passed
from evaluation.official_benchmark_probes import CommandProbe, probes_passed
from evaluation.official_benchmark_tools import ToolAvailability


def collect_blockers(
    *,
    upstream_root: Path | None,
    missing_files: list[str],
    tools: ToolAvailability,
    env_config: EnvConfigCheck,
    serving_ready: bool,
    command_probes: list[CommandProbe],
    dataset_probes: list[DatasetProbe],
    image_probes: list[ImageManifestProbe],
    harness_probes: list[HarnessProbe],
) -> list[str]:
    blockers: list[str] = []
    if upstream_root is None:
        blockers.append("official FastContext upstream checkout was not provided")
    elif missing_files:
        blockers.append("official upstream checkout is missing required benchmark files or built wheel")
    if not tools.uv:
        blockers.append("uv is not available on PATH")
    if not tools.docker:
        blockers.append("Docker is not available on PATH")
    elif not tools.docker_daemon:
        blockers.append("Docker daemon is not reachable")
    if env_config.config_path is None:
        blockers.append("official benchmark .env config was not provided")
    if env_config.missing_keys:
        blockers.append("official benchmark .env is missing required FastContext/main model keys")
    if env_config.placeholder_keys:
        blockers.append("official benchmark .env still contains placeholder credential values")
    if not env_config.has_main_credential:
        blockers.append("official benchmark .env has no usable main-agent credential")
    if not serving_ready:
        blockers.append("official serving preflight is not ready")
    if command_probes and not probes_passed(command_probes):
        blockers.append("official benchmark CLI smoke probes failed")
    if dataset_probes and not dataset_probes_passed(dataset_probes):
        blockers.append("official benchmark dataset probes failed")
    if image_probes and not image_probes_passed(image_probes):
        blockers.append("official benchmark Docker image manifest probes failed")
    if harness_probes and not harness_probes_passed(harness_probes):
        blockers.append("official benchmark zero-instance harness probes failed")
    return blockers


def collect_warnings(
    upstream_root: Path | None,
    command_probes: list[CommandProbe],
    dataset_probes: list[DatasetProbe],
    image_probes: list[ImageManifestProbe],
    harness_probes: list[HarnessProbe],
) -> list[str]:
    if upstream_root is None:
        return ["Run against a clone of https://github.com/microsoft/fastcontext after uv build."]
    warnings: list[str] = []
    if not command_probes:
        warnings.append("Official benchmark CLI smoke probes were not run.")
    if not dataset_probes:
        warnings.append("Official benchmark dataset probes were not run.")
    if not image_probes:
        warnings.append("Official benchmark Docker image manifest probes were not run.")
    if not harness_probes:
        warnings.append("Official benchmark zero-instance harness probes were not run.")
    return warnings
