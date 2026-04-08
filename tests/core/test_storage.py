import sys
import json
from pathlib import Path
import pytest

sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from core.storage import init_session_dir, append_extraction

def test_init_session_dir(mocker, tmp_path):
    """Testa se a inicialização gera subpastas incrementais na pasta correta sem reciclar."""
    mocker.patch("core.storage.DATA_DIR", tmp_path)
    
    # Primeiro boot
    session1 = init_session_dir()
    assert session1.name == "session_1"
    
    # Próximo boot gera sempre sessão nova
    session2 = init_session_dir()
    assert session2.name == "session_2"

def test_append_extraction_single_video(tmp_path):
    """Verifica se o empacotamento Video isolado faz merge com os meta-dados raiz."""
    
    # Passamos um diretório alvo
    mock_payload = {"video_id": "A1B2", "title": "VidName", "description": "Desc"}
    append_extraction(tmp_path, name="Vídeo Legal", extract_type="VIDEO", payload=mock_payload)
    
    json_path = tmp_path / "video-metadatas.json"
    assert json_path.exists()
    
    with open(json_path, "r", encoding="utf-8") as f:
        dados = json.load(f)
        
    assert len(dados) == 1
    assert "name" not in dados[0]  # O root não deve possuir key unificada mais num single video
    assert dados[0]["type"] == "VIDEO"
    assert dados[0]["video_id"] == "A1B2" 
    assert dados[0]["title"] == "VidName" # Embuído nele próprio
    assert dados[0]["description"] == "Desc"

def test_append_extraction_playlist_multiarquivos(tmp_path):
    """
    Testa se uma playlist guarda os links submersos array 'videos'.
    Além disso, testa se salva múltiplos arquivos video-metadatas-N.json consecutivamente.
    """
    mock_payload = [{"video_id": "PL1"}]
    
    # Primeira inserção
    append_extraction(tmp_path, name="Curso 1", extract_type="PLAYLIST", payload=mock_payload)
    json_primeiro = tmp_path / "video-metadatas.json"
    assert json_primeiro.exists()
    
    # Segunda inserção
    append_extraction(tmp_path, name="Curso 2", extract_type="PLAYLIST", payload=mock_payload)
    json_segundo = tmp_path / "video-metadatas-2.json"
    assert json_segundo.exists()
    
    # Terceira
    append_extraction(tmp_path, name="Curso 3", extract_type="PLAYLIST", payload=mock_payload)
    json_terceiro = tmp_path / "video-metadatas-3.json"
    assert json_terceiro.exists()
    
    with open(json_terceiro, "r", encoding="utf-8") as f:
        dados = json.load(f)
        
    assert len(dados) == 1
    assert dados[0]["name"] == "Curso 3"
    assert dados[0]["videos"][0]["video_id"] == "PL1"
