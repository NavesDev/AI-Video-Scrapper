import sys
from pathlib import Path

# Garante que as importações achem o src corretamente nos testes
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

import pytest
from core.cli import (
    get_single_link,
    get_multiple_links_manually,
    get_summary_source_dir,
    run_cli,
    show_header,
    show_playlist_extraction_progress,
    show_single_video_progress,
)
from unittest.mock import MagicMock

def test_get_single_link_valido(mocker):
    """Testa se, ao prover um link na CLI, ele é retornado corretamente numa lista."""
    # Mocka a corrente questionary.text("...").ask()
    mock_ask = mocker.patch('questionary.text')
    mock_ask.return_value.ask.return_value = "https://youtube.com/watch?v=123"
    
    links = get_single_link()
    assert links == ["https://youtube.com/watch?v=123"]

def test_get_single_link_vazio(mocker):
    """Se o usuário der ENTER numa entrava vazia para link único."""
    mock_ask = mocker.patch('questionary.text')
    mock_ask.return_value.ask.return_value = "   "
    
    links = get_single_link()
    assert links == []

def test_get_single_link_prompt_respects_bilingual_mode(mocker):
    mock_ask = mocker.patch("questionary.text")
    mock_ask.return_value.ask.return_value = ""

    get_single_link(True)
    get_single_link(False)

    assert mock_ask.call_args_list[0].args[0] == "Paste the YouTube link (Video or Playlist): / Cole o link do YouTube (Vídeo ou Playlist):"
    assert mock_ask.call_args_list[1].args[0] == "Cole o link do YouTube (Vídeo ou Playlist):"

def test_get_multiple_links_manually(mocker):
    """Testa o loop de obtenção manual, encerrando com string vazia."""
    # Lista de retornos sequenciais para mock_ask
    respostas = ["link1", "link2", ""]
    mock_ask = mocker.patch('questionary.text')
    mock_ask.return_value.ask.side_effect = respostas
    
    links = get_multiple_links_manually()
    assert links == ["link1", "link2"]

def test_get_links_from_file_prompt_respects_bilingual_mode(mocker):
    mock_path = mocker.patch("questionary.path")
    mock_path.return_value.ask.return_value = ""

    from core.cli import get_links_from_file
    get_links_from_file(True)
    get_links_from_file(False)

    assert mock_path.call_args_list[0].args[0] == "Enter the file path (.txt, .json, .csv): / Digite o caminho do arquivo (.txt, .json, .csv):"
    assert mock_path.call_args_list[1].args[0] == "Digite o caminho do arquivo (.txt, .json, .csv):"

def test_run_cli_passes_bilingual_mode_to_helpers(mocker):
    mock_select = mocker.patch("questionary.select")
    mock_select.return_value.ask.side_effect = [
        "1. Ingest links and generate summaries / Ingerir links e gerar resumos",
        "1. Insert a single link / Inserir um único link",
    ]
    helper = mocker.patch("core.cli.get_single_link", return_value=["https://www.youtube.com/watch?v=123"])

    run_cli(True)

    helper.assert_called_once_with(True)

def test_run_cli_rota_link_unico(mocker):
    """Testa se o fluxo de ingestão redireciona para link único e o retorna."""
    mock_select = mocker.patch('questionary.select')
    mock_select.return_value.ask.side_effect = [
        "1. Ingerir links e gerar resumos",
        "1. Inserir um único link"
    ]
    
    mock_get_single_link = mocker.patch('core.cli.get_single_link')
    valid_url = "https://www.youtube.com/watch?v=123"
    mock_get_single_link.return_value = [valid_url]
    
    urls = run_cli()
    assert urls == [valid_url]


def test_run_cli_uses_pt_br_prompts_when_bilingual_disabled(mocker):
    """Com bilingual_mode=False, os textos do menu devem ficar apenas em PT-BR."""
    mock_select = mocker.patch("questionary.select")
    mock_select.return_value.ask.side_effect = [
        "1. Ingerir links e gerar resumos",
        "4. Voltar",
    ]
    mocker.patch("core.cli.show_header")

    run_cli(False)

    first_prompt = mock_select.call_args_list[0].args[0]
    first_choices = mock_select.call_args_list[0].kwargs["choices"]
    second_prompt = mock_select.call_args_list[1].args[0]
    second_choices = mock_select.call_args_list[1].kwargs["choices"]

    assert first_prompt == "O que você deseja fazer?"
    assert first_choices[0] == "1. Ingerir links e gerar resumos"
    assert first_choices[3] == "4. Sair"
    assert second_prompt == "Como você deseja inserir os links?"
    assert second_choices[0] == "1. Inserir um único link"
    assert second_choices[3] == "4. Voltar"


def test_show_header_uses_pt_br_subtitle_when_bilingual_disabled(mocker):
    mock_console = mocker.patch("core.cli.console")

    show_header(False)

    panel_arg = mock_console.print.call_args_list[0].args[0]
    assert panel_arg.subtitle == "v0.1.0 • PT-BR"

def test_run_cli_rota_arquivo(mocker):
    """Testa se o fluxo de ingestão redireciona para input em arquivo e o retorna."""
    mock_select = mocker.patch('questionary.select')
    mock_select.return_value.ask.side_effect = [
        "1. Ingerir links e gerar resumos",
        "3. Importar a partir de um arquivo (.txt, .json, .csv)"
    ]
    
    mock_get_from_file = mocker.patch('core.cli.get_links_from_file')
    valid_url1 = "https://www.youtube.com/watch?v=111"
    valid_url2 = "https://www.youtube.com/watch?v=222"
    mock_get_from_file.return_value = [valid_url1, valid_url2]
    
    urls = run_cli()
    assert urls == [valid_url1, valid_url2]

def test_run_cli_aggregate_current_run(mocker):
    """Testa se a opção de resumo final da execução atual retorna payload de ação."""
    mock_select = mocker.patch('questionary.select')
    mock_select.return_value.ask.return_value = "2. Gerar resumo final da execução atual"

    payload = run_cli()
    assert payload == {"action": "aggregate_current_run"}

def test_run_cli_aggregate_selected_dir(mocker):
    """Testa se a opção de resumo final por pasta/sessão retorna payload de ação."""
    mock_select = mocker.patch('questionary.select')
    mock_select.return_value.ask.return_value = "3. Gerar resumo final de pasta/sessão selecionada"

    payload = run_cli()
    assert payload == {"action": "aggregate_selected_dir"}


def test_get_summary_source_dir_returns_path(mocker):
    mock_path = mocker.patch("questionary.path")
    mock_path.return_value.ask.return_value = "  /home/naves/mock-dir  "

    result = get_summary_source_dir()

    assert str(result) == "/home/naves/mock-dir"


def test_get_summary_source_dir_returns_none_for_empty_input(mocker):
    mock_path = mocker.patch("questionary.path")
    mock_path.return_value.ask.return_value = "   "

    result = get_summary_source_dir()

    assert result is None

def test_get_summary_source_dir_prompt_respects_bilingual_mode(mocker):
    mock_path = mocker.patch("questionary.path")
    mock_path.return_value.ask.return_value = ""

    get_summary_source_dir(True)
    get_summary_source_dir(False)

    assert mock_path.call_args_list[0].args[0] == "Enter the folder/session path containing Markdown summaries: / Digite o caminho da pasta/sessão contendo os resumos Markdown:"
    assert mock_path.call_args_list[1].args[0] == "Digite o caminho da pasta/sessão contendo os resumos Markdown:"

def test_show_playlist_extraction_progress(mocker):
    """Testa a extração interativa CLI simulando o console rich e o gerador de chunks em API."""
    mock_console = mocker.patch("core.cli.console")
    
    def gerador_test(pid):
        yield [
            {"title": "Video Longo Pra testar o corte de len maios que sessenta caracteres aqui", "video_id": "V1"}
        ]
        yield [
            {"title": "Video Curto", "video_id": "V2"}
        ]
        
    videos_coletados = show_playlist_extraction_progress("PL_dummy123", "Curso Legal", gerador_test)
    
    assert len(videos_coletados) == 2
    assert videos_coletados[0]["video_id"] == "V1"
    assert videos_coletados[1]["title"] == "Video Curto"
    
    assert mock_console.status.called
    assert mock_console.print.call_count > 0

def test_show_single_video_progress(mocker):
    """Testa a exibição visual de vídeo único importando Dicts estáticos."""
    mock_console = mocker.patch("core.cli.console")
    
    def fetch_mock(vid):
        if vid == "GOOD":
            return {"video_id": vid, "title": "Titulo de Video Simples Bem Grande Pra Testar o Layout Se Necessario", "description": "Desc"}
        return None
        
    resultado_bom = show_single_video_progress("GOOD", fetch_mock)
    assert resultado_bom is not None
    assert resultado_bom["video_id"] == "GOOD"
    assert mock_console.status.called
    assert mock_console.print.called
    
    # Falha
    resultado_ruim = show_single_video_progress("BAD", fetch_mock)
    assert resultado_ruim is None


def test_show_single_video_progress_runtime_texts_respect_bilingual_mode(mocker):
    mock_console = mocker.patch("core.cli.console")

    def fetch_mock(_):
        return None

    show_single_video_progress("BAD", fetch_mock, bilingual_mode=True)
    show_single_video_progress("BAD", fetch_mock, bilingual_mode=False)

    assert mock_console.status.call_args_list[0].args[0] == "[bold green]Connecting to YouTube and loading video... / Conectando com YouTube e buscando vídeo...[/bold green]"
    assert mock_console.status.call_args_list[1].args[0] == "[bold green]Conectando com YouTube e buscando vídeo...[/bold green]"
    assert mock_console.print.call_args_list[0].args[0] == "[red]⚠️ Could not load video metadata: BAD / Não foi possível carregar os metadados do vídeo: BAD[/red]"
    assert mock_console.print.call_args_list[1].args[0] == "[red]⚠️ Não foi possível carregar os metadados do vídeo: BAD[/red]"
