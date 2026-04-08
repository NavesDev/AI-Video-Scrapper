import sys
from pathlib import Path

# Garante que as importações achem o src corretamente nos testes
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

import pytest
import os
from unittest.mock import MagicMock
from core.youtube_api import extract_playlist_id, extract_video_id, fetch_playlist_videos, fetch_video_metadata

def test_extract_playlist_id():
    # Playlist URL Explicita
    assert extract_playlist_id("https://youtube.com/playlist?list=PL_foo") == "PL_foo"
    # Video integrado numa playlist
    assert extract_playlist_id("https://youtube.com/watch?v=123&list=PL_bar") == "PL_bar"
    # Falhas
    assert extract_playlist_id("https://youtube.com/watch?v=123") is None
    assert extract_playlist_id("invalid url") is None

def test_extract_video_id():
    assert extract_video_id("https://www.youtube.com/watch?v=XYZ123") == "XYZ123"
    assert extract_video_id("https://youtu.be/ABC987") == "ABC987"
    assert extract_video_id("https://www.youtube.com/shorts/SHORTS1") == "SHORTS1"
    # Sem ID
    assert extract_video_id("https://youtube.com/playlist?list=AAA") is None

def test_fetch_playlist_videos_exception_sem_apikey(mocker):
    # Força limpar environment para caso exista no host do runner
    mocker.patch.dict(os.environ, clear=True)
    
    with pytest.raises(ValueError, match="não foi encontrada nas variáveis de ambiente"):
        # Como é um gerador, para dar trigger de falha devemos inicializar a iteração
        generator = fetch_playlist_videos("any_playlist")
        next(generator)

def test_fetch_playlist_videos_paginado(mocker):
    # Mock das variáveis de ambiente garantindo que passe do step inicial
    mocker.patch.dict(os.environ, {"YOUTUBE_API_KEY": "fake_key"})
    
    mock_requests = mocker.patch("requests.get")
    
    # Criando respostas falsas de API
    response_page1 = MagicMock()
    response_page1.status_code = 200
    response_page1.json.return_value = {
        "nextPageToken": "TOKEN_SECRETO",
        "items": [
            {"snippet": {"title": "Titulo A", "description": "Desc A", "resourceId": {"videoId": "VID_A"}}}
        ]
    }
    
    response_page2 = MagicMock()
    response_page2.status_code = 200
    response_page2.json.return_value = {
        # Sem proxima pagina
        "items": [
            {"snippet": {"title": "Titulo B", "description": "Desc B", "resourceId": {"videoId": "VID_B"}}}
        ]
    }
    
    # Simula a iteração: a primeira request volta a pagina 1, a segunda volta a pagina 2
    mock_requests.side_effect = [response_page1, response_page2]
    
    generator = fetch_playlist_videos("FAKE_PLAYLIST")
    
    # Pagina 1
    lote1 = next(generator)
    assert len(lote1) == 1
    assert lote1[0]['video_id'] == "VID_A"
    
    # Pagina 2
    lote2 = next(generator)
    assert len(lote2) == 1
    assert lote2[0]['video_id'] == "VID_B"
    
    # Esgota lista
    with pytest.raises(StopIteration):
        next(generator)

def test_fetch_video_metadata(mocker):
    mocker.patch.dict(os.environ, {"YOUTUBE_API_KEY": "fake_key_video"})
    mock_requests = mocker.patch("requests.get")
    
    resposta_fake = MagicMock()
    resposta_fake.status_code = 200
    resposta_fake.json.return_value = {
        "items": [
            {"snippet": {"title": "Vid Titulo", "description": "Vid Desc"}}
        ]
    }
    mock_requests.return_value = resposta_fake
    
    resultado = fetch_video_metadata("FAKE_VID_123")
    
    assert resultado is not None
    assert resultado["video_id"] == "FAKE_VID_123"
    assert resultado["title"] == "Vid Titulo"
    assert resultado["description"] == "Vid Desc"
