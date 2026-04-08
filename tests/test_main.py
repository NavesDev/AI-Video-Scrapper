import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).parent.parent / "src"))

import main
from core.config import AppConfig
from utils.validators import YouTubeLinkType


def test_main_ingestion_route_keeps_flow_and_passes_config(mocker, tmp_path):
    session_dir = tmp_path / "session_1"
    session_dir.mkdir()
    config = AppConfig(gemini_model="gemini-3-pro", max_retries_429=9)

    mocker.patch("main.setup_environment")
    mocker.patch("main.load_dotenv")
    mocker.patch("main.init_session_dir", return_value=session_dir)
    mocker.patch("main.load_app_config", return_value=config)
    mocker.patch("main.get_youtube_url_type", side_effect=[YouTubeLinkType.PLAYLIST, YouTubeLinkType.VIDEO])
    mocker.patch("main.extract_playlist_id", return_value="pl123")
    mocker.patch("main.fetch_playlist_title", return_value="Playlist Name")
    mocker.patch("main.show_playlist_extraction_progress", return_value=[{"video_id": "A", "title": "A", "description": ""}])
    mocker.patch("main.extract_video_id", return_value="vid456")
    mocker.patch("main.show_single_video_progress", return_value={"video_id": "vid456", "title": "Single", "description": ""})
    append_extraction = mocker.patch("main.append_extraction")
    show_ai_generation_progress = mocker.patch("main.show_ai_generation_progress")
    run_cli = mocker.patch("main.run_cli", side_effect=[["playlist-url", "video-url"], KeyboardInterrupt()])
    mocker.patch("main.console.input", return_value="")
    mocker.patch("main.sys.exit", side_effect=SystemExit(0))

    with pytest.raises(SystemExit):
        main.main()

    assert append_extraction.call_count == 2
    run_cli.assert_called_with(app_config=config)
    assert show_ai_generation_progress.call_count == 2
    assert show_ai_generation_progress.call_args_list[0].kwargs["app_config"] == config
    assert show_ai_generation_progress.call_args_list[1].kwargs["app_config"] == config


def test_main_aggregate_current_run_generates_global_summary(mocker, tmp_path):
    session_dir = tmp_path / "session_2"
    session_dir.mkdir()
    config = AppConfig(max_retries_429=4)
    abstract_file = session_dir / "abstracts" / "a.md"
    abstract_file.parent.mkdir(parents=True)
    abstract_file.write_text("# A", encoding="utf-8")

    mocker.patch("main.setup_environment")
    mocker.patch("main.load_dotenv")
    mocker.patch("main.init_session_dir", return_value=session_dir)
    load_app_config = mocker.patch("main.load_app_config", return_value=config)
    mocker.patch("main.run_cli", side_effect=[{"action": "aggregate_current_run"}, KeyboardInterrupt()])
    collect_abstracts = mocker.patch("main.collect_abstracts_for_scope", return_value=[abstract_file])
    generate_global_summary = mocker.patch("main.generate_global_summary_from_abstracts", return_value="# Global")
    save_global_summary = mocker.patch("main.save_global_summary")
    mocker.patch("main.console.input", return_value="")
    mocker.patch("main.sys.exit", side_effect=SystemExit(0))

    with pytest.raises(SystemExit):
        main.main()

    base_dir = Path(main.__file__).resolve().parent.parent
    load_app_config.assert_called_once_with(base_dir / "config.json")
    collect_abstracts.assert_called_once_with(session_dir, scope="current_run")
    generate_global_summary.assert_called_once_with(["# A"], app_config=config)
    save_global_summary.assert_called_once_with(session_dir, "# Global")


def test_main_aggregate_selected_dir_uses_cli_directory_prompt(mocker, tmp_path):
    session_dir = tmp_path / "session_3"
    session_dir.mkdir()
    selected_dir = tmp_path / "selected"
    selected_dir.mkdir()
    abstract_file = selected_dir / "item.md"
    abstract_file.write_text("# Item", encoding="utf-8")
    config = AppConfig(retry_base_seconds=7)

    mocker.patch("main.setup_environment")
    mocker.patch("main.load_dotenv")
    mocker.patch("main.init_session_dir", return_value=session_dir)
    mocker.patch("main.load_app_config", return_value=config)
    mocker.patch("main.run_cli", side_effect=[{"action": "aggregate_selected_dir"}, KeyboardInterrupt()])
    get_summary_source_dir = mocker.patch("main.get_summary_source_dir", return_value=selected_dir)
    collect_abstracts = mocker.patch("main.collect_abstracts_for_scope", return_value=[abstract_file])
    generate_global_summary = mocker.patch("main.generate_global_summary_from_abstracts", return_value="# Selected")
    save_global_summary = mocker.patch("main.save_global_summary")
    mocker.patch("main.console.input", return_value="")
    mocker.patch("main.sys.exit", side_effect=SystemExit(0))

    with pytest.raises(SystemExit):
        main.main()

    get_summary_source_dir.assert_called_once()
    collect_abstracts.assert_called_once_with(
        current_session_dir=session_dir,
        scope="selected_dir",
        explicit_dir=selected_dir,
    )
    generate_global_summary.assert_called_once_with(["# Item"], app_config=config)
    save_global_summary.assert_called_once_with(selected_dir, "# Selected")


def test_generate_and_save_global_summary_skips_unreadable_non_utf8_file(mocker, tmp_path):
    config = AppConfig()
    readable = tmp_path / "ok.md"
    unreadable = tmp_path / "bad.md"
    readable.write_text("# Ok", encoding="utf-8")
    unreadable.write_bytes(b"\x80\x81")

    generate_global_summary = mocker.patch("main.generate_global_summary_from_abstracts", return_value="# Global")
    save_global_summary = mocker.patch("main.save_global_summary", return_value=tmp_path / "global-summary.md")
    console_print = mocker.patch("main.console.print")

    main._generate_and_save_global_summary(tmp_path, [readable, unreadable], config)

    generate_global_summary.assert_called_once_with(["# Ok"], app_config=config)
    save_global_summary.assert_called_once_with(tmp_path, "# Global")
    assert any(
        "Ignorando resumo não legível" in str(call.args[0]) and "bad.md" in str(call.args[0])
        for call in console_print.call_args_list
    )
