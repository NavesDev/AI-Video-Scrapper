import sys
from pathlib import Path

# Garante que as importações achem o src corretamente nos testes
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

import json
import pytest
from utils.file_parser import parse_links_from_file

def test_parse_links_from_txt(tmp_path):
    """Testa se o parser lê corretamente linhas de um arquivo de texto (.txt)."""
    # Cria arquivo temporário TXT
    teste_txt = tmp_path / "links.txt"
    teste_txt.write_text("https://youtube.com/video1\nhttps://youtube.com/video2\n", encoding="utf-8")
    
    links = parse_links_from_file(str(teste_txt))
    assert links == ["https://youtube.com/video1", "https://youtube.com/video2"]

def test_parse_links_from_csv(tmp_path):
    """Testa se o parser lê corretamente linhas de um arquivo .csv simples."""
    teste_csv = tmp_path / "links.csv"
    teste_csv.write_text("https://youtube.com/video1,algum,dado\nhttps://youtube.com/video2,outro,dado\n", encoding="utf-8")
    
    links = parse_links_from_file(str(teste_csv))
    assert links == ["https://youtube.com/video1", "https://youtube.com/video2"]

def test_parse_links_from_json(tmp_path):
    """Testa se o parser lê lista de strings de um arquivo .json adequadamente."""
    teste_json = tmp_path / "links.json"
    dados = ["https://youtube.com/1", "https://youtube.com/2"]
    teste_json.write_text(json.dumps(dados), encoding="utf-8")
    
    links = parse_links_from_file(str(teste_json))
    assert links == dados

def test_parse_links_from_json_invalid_format(tmp_path):
    """Garante que um ValueError é levantado se o json não for uma array."""
    teste_json = tmp_path / "links_erro.json"
    dados = {"url": "https://youtube.com/1"}  # Dicionário ao invés de lista
    teste_json.write_text(json.dumps(dados), encoding="utf-8")
    
    with pytest.raises(ValueError, match="O arquivo JSON deve conter uma lista de strings"):
        parse_links_from_file(str(teste_json))

def test_parse_links_from_unreachable_file():
    """Garante que FileNotFoundError é levantado se arquivo não existe."""
    with pytest.raises(FileNotFoundError):
        parse_links_from_file("caminho_inexistente_bizarro.txt")
