import sys
from pathlib import Path
import pytest

sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from utils.initializer import setup_environment

def test_setup_environment_creates_from_templates(tmp_path):
    """Copia corretamente ambos usando .example quando a raiz não os detém."""
    # Cria os exemplos simulados falsos
    env_ex = tmp_path / ".env.example"
    env_ex.write_text("API_KEY=123")
    
    sys_ex = tmp_path / "system_instruction.md.example"
    sys_ex.write_text("Hello Prompt")

    config_ex = tmp_path / "config.example.json"
    config_ex.write_text('{"gemini_model":"gemini-test"}')
    
    # Executa Bootloader silencioso para o ambiente
    setup_environment(base_dir=tmp_path, interactive=False)
    
    # Verifica se os recheios brotaram 
    env_oficial = tmp_path / ".env"
    assert env_oficial.exists()
    assert env_oficial.read_text() == "API_KEY=123"
    
    md_oficial = tmp_path / "system_instruction.md"
    assert md_oficial.exists()
    assert md_oficial.read_text() == "Hello Prompt"

    config_oficial = tmp_path / "config.json"
    assert config_oficial.exists()
    assert config_oficial.read_text() == '{"gemini_model":"gemini-test"}'

def test_setup_environment_skips_if_exist(tmp_path):
    """Testa se o Bootloader respeita arquivos consolidados prévidados, nunca dando Overwrite cego."""
    env_ex = tmp_path / ".env.example"
    env_ex.write_text("API_KEY=TEMPLATE")
    
    env_real = tmp_path / ".env"
    env_real.write_text("API_KEY=REAL")

    cfg_example = tmp_path / "config.example.json"
    cfg_example.write_text('{"gemini_model":"from-example"}')
    cfg_real = tmp_path / "config.json"
    cfg_real.write_text('{"gemini_model":"from-real"}')
    
    setup_environment(base_dir=tmp_path, interactive=False)
    
    # O output não pode ter sido modificado por template
    assert env_real.read_text() == "API_KEY=REAL"
    assert cfg_real.read_text() == '{"gemini_model":"from-real"}'
    
def test_setup_environment_skips_if_no_template(tmp_path):
    """Não deve quebrar nem tentar copiar se não existir fallback na sub-pasta .example."""
    env_real = tmp_path / ".env"
    
    setup_environment(base_dir=tmp_path, interactive=False)
    
    assert not env_real.exists()

def test_verify_api_keys_interactive(mocker, tmp_path):
    """Testa se a função aciona o Questionary solicitando as chaves e grava no arquivo cego."""
    env_real = tmp_path / ".env"
    env_real.touch()  # arquivo de properties vazio
    
    # Mocks do questionary simulando digitação
    mock_ask = mocker.patch("questionary.password")
    mock_ask.return_value.ask.side_effect = [
        "AIza12345678901234567890123456789012345",
        "xyz_youtube_999",
    ]
    
    # Executa com interactivo ativado explicitamente
    setup_environment(base_dir=tmp_path, interactive=True)
    
    # Lendo final para avaliar injeções do dotenv
    linhas = env_real.read_text()
    assert "AIza12345678901234567890123456789012345" in linhas
    assert "xyz_youtube_999" in linhas
    assert "GEMINI_API_KEY" in linhas
    assert "YOUTUBE_API_KEY" in linhas


def test_verify_api_keys_rejects_invalid_gemini_key(mocker, tmp_path):
    """Token Gemini inválido deve gerar erro explícito e não ser salvo."""
    env_real = tmp_path / ".env"
    env_real.touch()
    mock_ask = mocker.patch("questionary.password")
    mock_ask.return_value.ask.side_effect = ["short_token"]

    with pytest.raises(ValueError, match="GEMINI_API_KEY"):
        setup_environment(base_dir=tmp_path, interactive=True)


def test_verify_api_keys_rejects_existing_invalid_gemini_key(mocker, tmp_path):
    """Valor Gemini inválido já existente deve ser rejeitado e exigir correção."""
    env_real = tmp_path / ".env"
    env_real.write_text('GEMINI_API_KEY="placeholder"\nYOUTUBE_API_KEY="yt_key"\n')
    mock_ask = mocker.patch("questionary.password")
    mock_ask.return_value.ask.side_effect = ["placeholder"]

    with pytest.raises(ValueError, match="GEMINI_API_KEY"):
        setup_environment(base_dir=tmp_path, interactive=True)

    assert mock_ask.call_count == 1


def test_verify_api_keys_requires_gemini_key_when_missing(mocker, tmp_path):
    """Sem GEMINI_API_KEY, entrada vazia deve falhar com erro claro."""
    env_real = tmp_path / ".env"
    env_real.write_text('YOUTUBE_API_KEY="yt_key"\n')
    mock_ask = mocker.patch("questionary.password")
    mock_ask.return_value.ask.side_effect = [""]

    with pytest.raises(ValueError, match="GEMINI_API_KEY"):
        setup_environment(base_dir=tmp_path, interactive=True)


def test_verify_api_keys_requires_gemini_when_env_and_template_missing(mocker, tmp_path):
    """Sem .env e .env.example, setup interativo não pode pular validação da GEMINI_API_KEY."""
    mock_ask = mocker.patch("questionary.password")
    mock_ask.return_value.ask.side_effect = [""]

    with pytest.raises(ValueError, match="GEMINI_API_KEY"):
        setup_environment(base_dir=tmp_path, interactive=True)

    assert (tmp_path / ".env").exists()
    assert mock_ask.call_count == 1


def test_verify_api_keys_accepts_valid_process_env_gemini_key(mocker, tmp_path):
    """Com GEMINI_API_KEY válida no ambiente do processo, não deve pedir chave do Gemini."""
    env_real = tmp_path / ".env"
    env_real.write_text('GEMINI_API_KEY="placeholder"\nYOUTUBE_API_KEY="yt_key"\n')
    mocker.patch.dict(
        "os.environ",
        {"GEMINI_API_KEY": "AIza12345678901234567890123456789012345"},
        clear=True,
    )
    mock_ask = mocker.patch("questionary.password")
    mock_ask.return_value.ask.side_effect = ["AIza12345678901234567890123456789012345"]

    setup_environment(base_dir=tmp_path, interactive=True)

    assert mock_ask.call_count == 0
    linhas = env_real.read_text()
    assert "GEMINI_API_KEY" in linhas
    assert "AIza12345678901234567890123456789012345" in linhas
    assert 'GEMINI_API_KEY="placeholder"' not in linhas


def test_setup_environment_creates_env_and_saves_keys_without_templates(mocker, tmp_path):
    mock_ask = mocker.patch("questionary.password")
    mock_ask.return_value.ask.side_effect = [
        "AIza12345678901234567890123456789012345",
        "yt_key_123",
    ]

    setup_environment(base_dir=tmp_path, interactive=True)

    env_real = tmp_path / ".env"
    assert env_real.exists()
    linhas = env_real.read_text()
    assert "GEMINI_API_KEY" in linhas
    assert "AIza12345678901234567890123456789012345" in linhas
    assert "YOUTUBE_API_KEY" in linhas
    assert "yt_key_123" in linhas
