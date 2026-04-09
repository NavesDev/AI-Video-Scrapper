import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from core.config import load_app_config


def test_load_app_config_uses_values_from_file(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "gemini_model": "gemini-2.5-flash",
                "temperature": 0.7,
                "max_retries_429": 9,
                "retry_base_seconds": 5,
                "bilingual_mode": False,
            }
        ),
        encoding="utf-8",
    )

    config = load_app_config(config_path)

    assert config.gemini_model == "gemini-2.5-flash"
    assert config.temperature == 0.7
    assert config.max_retries_429 == 9
    assert config.retry_base_seconds == 5
    assert config.bilingual_mode is False


def test_load_app_config_returns_defaults_when_missing_file(tmp_path):
    config = load_app_config(tmp_path / "missing-config.json")

    assert config.gemini_model == "gemini-3-flash-preview"
    assert config.temperature == 0.3
    assert config.max_retries_429 == 6
    assert config.retry_base_seconds == 2
    assert config.bilingual_mode is True


def test_load_app_config_returns_defaults_when_path_is_directory(tmp_path):
    config = load_app_config(tmp_path)

    assert config.gemini_model == "gemini-3-flash-preview"
    assert config.temperature == 0.3
    assert config.max_retries_429 == 6
    assert config.retry_base_seconds == 2
    assert config.bilingual_mode is True


def test_load_app_config_converts_numeric_and_bool_values(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "temperature": "0.9",
                "max_retries_429": "7",
                "retry_base_seconds": "4",
                "bilingual_mode": "false",
            }
        ),
        encoding="utf-8",
    )

    config = load_app_config(config_path)

    assert config.temperature == 0.9
    assert config.max_retries_429 == 7
    assert config.retry_base_seconds == 4
    assert config.bilingual_mode is False


def test_load_app_config_returns_defaults_on_malformed_json(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text("{invalid json", encoding="utf-8")

    config = load_app_config(config_path)

    assert config.gemini_model == "gemini-3-flash-preview"
    assert config.temperature == 0.3
    assert config.max_retries_429 == 6
    assert config.retry_base_seconds == 2
    assert config.bilingual_mode is True


def test_load_app_config_uses_default_model_for_invalid_non_string_values(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps({"gemini_model": None}), encoding="utf-8")

    config = load_app_config(config_path)

    assert config.gemini_model == "gemini-3-flash-preview"


def test_load_app_config_returns_defaults_for_non_dict_json(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(["not", "a", "dict"]), encoding="utf-8")

    config = load_app_config(config_path)

    assert config.gemini_model == "gemini-3-flash-preview"
    assert config.temperature == 0.3
    assert config.max_retries_429 == 6
    assert config.retry_base_seconds == 2
    assert config.bilingual_mode is True


def test_load_app_config_uses_default_temperature_for_non_finite_values(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps({"temperature": "nan"}),
        encoding="utf-8",
    )

    config = load_app_config(config_path)

    assert config.temperature == 0.3


def test_load_app_config_uses_default_temperature_for_infinite_values(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps({"temperature": "inf"}),
        encoding="utf-8",
    )

    config = load_app_config(config_path)

    assert config.temperature == 0.3


def test_load_app_config_uses_default_temperature_for_out_of_range_values(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps({"temperature": 1.2}),
        encoding="utf-8",
    )

    config = load_app_config(config_path)

    assert config.temperature == 0.3


def test_load_app_config_uses_default_max_retries_for_negative_values(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps({"max_retries_429": -1}),
        encoding="utf-8",
    )

    config = load_app_config(config_path)

    assert config.max_retries_429 == 6


def test_load_app_config_uses_default_retry_base_seconds_for_non_positive_values(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps({"retry_base_seconds": 0}),
        encoding="utf-8",
    )

    config = load_app_config(config_path)

    assert config.retry_base_seconds == 2
