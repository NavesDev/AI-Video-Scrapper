import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from utils.formatters import normalize_name

def test_normalize_name_corte_comprimento():
    # Deve cortar seco após bater 20 caracteres sem deixar hifens flutuando
    assert normalize_name("Playlist Gigante Maravilhosa Da NASA") == "playlist-gigante-mar"

def test_normalize_name_acentuacoes():
    # Acentos como á, é, ão devem decair pra ASCII 
    assert normalize_name("Ninguém Sabe O Que É") == "ninguem-sabe-o-que-e"

def test_normalize_name_pontuacoes_desiguais():
    # Símbolos que o terminal recusa pra nome de arquivo não devem passar
    assert normalize_name("Crashando: * / ! @ $ com traço") == "crashando-com-traco"

def test_normalize_name_borda_lixo():
    assert normalize_name("   -  Espaços - No Final   -") == "espacos-no-final"

def test_normalize_name_vazio():
    assert normalize_name(None) == "gerado-sem-nome"
    assert normalize_name("!!!***!!!") == "gerado-sem-nome"
