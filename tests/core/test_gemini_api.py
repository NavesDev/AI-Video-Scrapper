import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from core.config import AppConfig
from core.gemini_api import generate_video_summary


def test_generate_video_summary_retries_on_rate_limit_and_succeeds(mocker):
    mocker.patch.dict("os.environ", {"GEMINI_API_KEY": "AIza_fake"})
    mocker.patch("core.gemini_api._load_system_instruction", return_value="instr")
    mocker.patch("core.gemini_api.genai.configure")
    mock_sleep = mocker.patch("core.gemini_api.time.sleep")

    model = mocker.MagicMock()
    model.generate_content.side_effect = [
        Exception("429 RESOURCE_EXHAUSTED"),
        SimpleNamespace(text="summary-ok"),
    ]
    mocker.patch("core.gemini_api.genai.GenerativeModel", return_value=model)

    config = AppConfig(max_retries_429=3, retry_base_seconds=2)
    summary = generate_video_summary("https://youtube.com/watch?v=123", "video", "desc", app_config=config)

    assert summary == "summary-ok"
    assert model.generate_content.call_count == 2
    mock_sleep.assert_called_once_with(2)


def test_generate_video_summary_raises_runtime_error_for_non_retryable_failure(mocker):
    mocker.patch.dict("os.environ", {"GEMINI_API_KEY": "AIza_fake"})
    mocker.patch("core.gemini_api._load_system_instruction", return_value="instr")
    mocker.patch("core.gemini_api.genai.configure")
    mock_sleep = mocker.patch("core.gemini_api.time.sleep")

    model = mocker.MagicMock()
    model.generate_content.side_effect = Exception("500 INTERNAL")
    mocker.patch("core.gemini_api.genai.GenerativeModel", return_value=model)

    with pytest.raises(RuntimeError, match="Falha ao gerar resumo com Gemini"):
        generate_video_summary("https://youtube.com/watch?v=123", "video", "desc")

    assert model.generate_content.call_count == 1
    mock_sleep.assert_not_called()


def test_generate_video_summary_raises_after_exhausting_rate_limit_retries(mocker):
    mocker.patch.dict("os.environ", {"GEMINI_API_KEY": "AIza_fake"})
    mocker.patch("core.gemini_api._load_system_instruction", return_value="instr")
    mocker.patch("core.gemini_api.genai.configure")
    mock_sleep = mocker.patch("core.gemini_api.time.sleep")

    model = mocker.MagicMock()
    model.generate_content.side_effect = [
        Exception("429 RESOURCE_EXHAUSTED"),
        Exception("RESOURCE_EXHAUSTED"),
        Exception("too many requests"),
        Exception("429 RESOURCE_EXHAUSTED"),
    ]
    mocker.patch("core.gemini_api.genai.GenerativeModel", return_value=model)

    config = AppConfig(max_retries_429=3, retry_base_seconds=1.5)
    with pytest.raises(RuntimeError, match="após 3 retries por limite de taxa"):
        generate_video_summary("https://youtube.com/watch?v=123", "video", "desc", app_config=config)

    assert model.generate_content.call_count == 4
    assert mock_sleep.call_args_list == [
        mocker.call(1.5),
        mocker.call(3.0),
        mocker.call(6.0),
    ]
