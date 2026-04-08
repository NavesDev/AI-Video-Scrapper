import sys
from pathlib import Path

# Garante que as importações achem o src corretamente nos testes
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

import pytest
from core.cli import get_single_link, get_multiple_links_manually, run_cli, show_playlist_extraction_progress
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

def test_get_multiple_links_manually(mocker):
    """Testa o loop de obtenção manual, encerrando com string vazia."""
    # Lista de retornos sequenciais para mock_ask
    respostas = ["link1", "link2", ""]
    mock_ask = mocker.patch('questionary.text')
    mock_ask.return_value.ask.side_effect = respostas
    
    links = get_multiple_links_manually()
    assert links == ["link1", "link2"]

def test_run_cli_rota_link_unico(mocker):
    """Testa se a opção '1' redireciona para link único e o retorna."""
    mock_select = mocker.patch('questionary.select')
    mock_select.return_value.ask.return_value = "1. Inserir um único link"
    
    mock_get_single_link = mocker.patch('core.cli.get_single_link')
    valid_url = "https://www.youtube.com/watch?v=123"
    mock_get_single_link.return_value = [valid_url]
    
    urls = run_cli()
    assert urls == [valid_url]

def test_run_cli_rota_arquivo(mocker):
    """Testa se a opção '3' redireciona para input em arquivo e o retorna."""
    mock_select = mocker.patch('questionary.select')
    mock_select.return_value.ask.return_value = "3. Importar a partir de um arquivo"
    
    mock_get_from_file = mocker.patch('core.cli.get_links_from_file')
    valid_url1 = "https://www.youtube.com/watch?v=111"
    valid_url2 = "https://www.youtube.com/watch?v=222"
    mock_get_from_file.return_value = [valid_url1, valid_url2]
    
    urls = run_cli()
    assert urls == [valid_url1, valid_url2]

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
