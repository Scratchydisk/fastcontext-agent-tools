from __future__ import annotations

import json
import shlex
import subprocess
import time
from dataclasses import dataclass
from typing import Final, cast

from evaluation.endpoint_readiness import JsonValue
from evaluation.official_benchmark_datasets import DatasetProbe
from evaluation.official_benchmark_probes import truncate


IMAGE_TIMEOUT_SECONDS: Final = 60


@dataclass(frozen=True, slots=True)
class ImageManifestProbe:
    name: str
    instance_id: str | None
    image: str | None
    command: str | None
    returncode: int | None
    duration_seconds: float
    media_type: str | None
    manifest_found: bool
    stdout_excerpt: str
    stderr_excerpt: str


def collect_official_image_probes(
    dataset_probes: list[DatasetProbe],
    *,
    timeout_seconds: int = IMAGE_TIMEOUT_SECONDS,
) -> list[ImageManifestProbe]:
    return [
        run_image_manifest_probe(probe.name, probe.first_instance_id, timeout_seconds)
        for probe in dataset_probes
    ]


def run_image_manifest_probe(
    name: str,
    instance_id: str | None,
    timeout_seconds: int,
) -> ImageManifestProbe:
    if instance_id is None:
        return ImageManifestProbe(
            name=name,
            instance_id=None,
            image=None,
            command=None,
            returncode=None,
            duration_seconds=0.0,
            media_type=None,
            manifest_found=False,
            stdout_excerpt="",
            stderr_excerpt="dataset probe did not return an instance_id",
        )
    image = derive_swebench_image_name(instance_id)
    command = ["docker", "manifest", "inspect", image]
    started = time.monotonic()
    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
    except FileNotFoundError as exc:
        duration = time.monotonic() - started
        return make_failed_image_probe(name, instance_id, image, command, duration, str(exc))
    except subprocess.TimeoutExpired as exc:
        duration = time.monotonic() - started
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        return ImageManifestProbe(
            name=name,
            instance_id=instance_id,
            image=image,
            command=shlex.join(command),
            returncode=None,
            duration_seconds=round(duration, 3),
            media_type=None,
            manifest_found=False,
            stdout_excerpt=truncate(stdout),
            stderr_excerpt=truncate(stderr or f"timed out after {timeout_seconds}s"),
        )

    duration = time.monotonic() - started
    media_type = parse_manifest_media_type(completed.stdout)
    return ImageManifestProbe(
        name=name,
        instance_id=instance_id,
        image=image,
        command=shlex.join(command),
        returncode=completed.returncode,
        duration_seconds=round(duration, 3),
        media_type=media_type,
        manifest_found=completed.returncode == 0 and media_type is not None,
        stdout_excerpt=truncate(completed.stdout),
        stderr_excerpt=truncate(completed.stderr),
    )


def make_failed_image_probe(
    name: str,
    instance_id: str,
    image: str,
    command: list[str],
    duration_seconds: float,
    stderr: str,
) -> ImageManifestProbe:
    return ImageManifestProbe(
        name=name,
        instance_id=instance_id,
        image=image,
        command=shlex.join(command),
        returncode=None,
        duration_seconds=round(duration_seconds, 3),
        media_type=None,
        manifest_found=False,
        stdout_excerpt="",
        stderr_excerpt=truncate(stderr),
    )


def derive_swebench_image_name(instance_id: str) -> str:
    image_name = instance_id.replace("__", "_1776_")
    return f"docker.io/swebench/sweb.eval.x86_64.{image_name}:latest".lower()


def parse_manifest_media_type(stdout: str) -> str | None:
    try:
        raw = cast(JsonValue, json.loads(stdout))
    except json.JSONDecodeError:
        return None
    if not isinstance(raw, dict):
        return None
    media_type = raw.get("mediaType")
    return media_type if isinstance(media_type, str) else None


def image_probes_passed(image_probes: list[ImageManifestProbe]) -> bool:
    return all(probe.manifest_found for probe in image_probes)
