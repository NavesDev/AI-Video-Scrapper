import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class AppConfig:
    gemini_model: str = "gemini-3-flash-preview"
    temperature: float = 0.3
    max_retries_429: int = 6
    retry_base_seconds: int = 2
    bilingual_mode: bool = True


def _to_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _to_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _to_bool(value: Any, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "1", "yes", "on"}:
            return True
        if lowered in {"false", "0", "no", "off"}:
            return False
    if isinstance(value, (int, float)):
        return bool(value)
    return default


def _to_string(value: Any, default: str) -> str:
    if isinstance(value, str):
        stripped_value = value.strip()
        if stripped_value:
            return stripped_value
    return default


def load_app_config(config_path: Path) -> AppConfig:
    defaults = AppConfig()
    if not config_path.exists():
        return defaults

    try:
        with config_path.open("r", encoding="utf-8") as config_file:
            data = json.load(config_file)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return defaults

    if not isinstance(data, dict):
        return defaults

    return AppConfig(
        gemini_model=_to_string(data.get("gemini_model"), defaults.gemini_model),
        temperature=_to_float(data.get("temperature"), defaults.temperature),
        max_retries_429=_to_int(data.get("max_retries_429"), defaults.max_retries_429),
        retry_base_seconds=_to_int(data.get("retry_base_seconds"), defaults.retry_base_seconds),
        bilingual_mode=_to_bool(data.get("bilingual_mode"), defaults.bilingual_mode),
    )
