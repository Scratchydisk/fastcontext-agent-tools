from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Final


REQUIRED_ENV_KEYS: Final = [
    "MAIN_MODEL",
    "FASTCONTEXT_MODEL",
    "FASTCONTEXT_API_KEY",
    "FASTCONTEXT_BASE_URL",
]
MAIN_CREDENTIAL_KEYS: Final = ["AZURE_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY"]


@dataclass(frozen=True, slots=True)
class EnvConfigCheck:
    config_path: str | None
    required_keys: list[str]
    main_credential_options: list[str]
    missing_keys: list[str]
    placeholder_keys: list[str]
    has_main_credential: bool


def check_env_config(config_path: Path | None) -> EnvConfigCheck:
    values = read_env_file(config_path)
    missing = [key for key in REQUIRED_ENV_KEYS if not values.get(key)]
    placeholder = [
        key
        for key, value in values.items()
        if is_placeholder(value) and key in [*REQUIRED_ENV_KEYS, *MAIN_CREDENTIAL_KEYS]
    ]
    has_main_credential = any(values.get(key) and not is_placeholder(values[key]) for key in MAIN_CREDENTIAL_KEYS)
    return EnvConfigCheck(
        config_path=str(config_path.resolve()) if config_path else None,
        required_keys=list(REQUIRED_ENV_KEYS),
        main_credential_options=list(MAIN_CREDENTIAL_KEYS),
        missing_keys=missing,
        placeholder_keys=sorted(placeholder),
        has_main_credential=has_main_credential,
    )


def read_env_file(config_path: Path | None) -> dict[str, str]:
    if config_path is None or not config_path.exists():
        return {}
    values: dict[str, str] = {}
    for raw_line in config_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        values[key.strip()] = value.strip().strip("\"'")
    return values


def is_placeholder(value: str) -> bool:
    normalized = value.strip().lower()
    return not normalized or normalized.startswith("your-") or "your-" in normalized
