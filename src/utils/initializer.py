import shutil
from pathlib import Path
import questionary
from rich.console import Console
from dotenv import get_key, set_key
from utils.validators import is_valid_gemini_api_key

console = Console()

def verify_api_keys(base_dir: Path):
    """Verifica e solicita as chaves de API caso faltem no .env."""
    env_file = base_dir / ".env"
    if not env_file.exists():
        env_file.touch()
        
    gemini_key = get_key(env_file, "GEMINI_API_KEY")
    gemini_key = gemini_key.strip() if gemini_key else ""
    gemini_key_is_valid = is_valid_gemini_api_key(gemini_key) if gemini_key else False
    gemini_key_needs_update = not gemini_key or not gemini_key_is_valid

    if gemini_key_needs_update:
        if gemini_key and not gemini_key_is_valid:
            console.print("\n[yellow]⚠️ GEMINI_API_KEY existente está em formato inválido![/yellow]")
        else:
            console.print("\n[yellow]⚠️ Chave da IA do Gemini (GEMINI_API_KEY) não encontrada![/yellow]")
        console.print("Obtenha sua chave gratuitamente em: [blue]https://aistudio.google.com/api-keys[/blue]")
        
        token = questionary.password("Coloque sua GEMINI_API_KEY aqui:").ask()
        token = token.strip() if token else ""
        if not token:
            raise ValueError(
                "GEMINI_API_KEY é obrigatória. "
                "Informe uma chave válida do Google AI Studio (ex.: começa com 'AIza')."
            )
        if not is_valid_gemini_api_key(token):
            raise ValueError(
                "Formato inválido para GEMINI_API_KEY. "
                "Use uma chave válida do Google AI Studio (ex.: começa com 'AIza')."
            )
        set_key(env_file, "GEMINI_API_KEY", token, quote_mode="always")
        console.print("[green]✓ Chave do Gemini salva no .env![/green]")
            
    youtube_key = get_key(env_file, "YOUTUBE_API_KEY")
    if not youtube_key or youtube_key.strip() == "":
        console.print("\n[yellow]⚠️ Chave do YouTube (YOUTUBE_API_KEY) não encontrada![/yellow]")
        console.print("Obtenha sua chave em: [blue]https://console.cloud.google.com/marketplace/product/google/youtube.googleapis.com[/blue]")
        
        token = questionary.password("Coloque sua YOUTUBE_API_KEY aqui:").ask()
        if token:
            set_key(env_file, "YOUTUBE_API_KEY", token.strip(), quote_mode="always")
            console.print("[green]✓ Chave do YouTube salva no .env![/green]\n")

def setup_environment(base_dir: Path = None, interactive: bool = True):
    """
    Roda na inicialização do script.
    Garanti a existência de arquivos críticos fazendo fallback pros templates `.example`.
    """
    if base_dir is None:
        base_dir = Path(__file__).parent.parent.parent
    
    # 1. Fallback do .env
    env_file = base_dir / ".env"
    env_example = base_dir / ".env.example"
    
    if not env_file.exists() and env_example.exists():
        shutil.copy(env_example, env_file)
    elif interactive and not env_file.exists():
        env_file.touch()
        
    # 2. Fallback do system_instruction.md
    sys_inst = base_dir / "system_instruction.md"
    sys_example = base_dir / "system_instruction.md.example"
    
    if not sys_inst.exists() and sys_example.exists():
        shutil.copy(sys_example, sys_inst)

    # 3. Fallback do config.json
    config_file = base_dir / "config.json"
    config_example = base_dir / "config.example.json"

    if not config_file.exists() and config_example.exists():
        shutil.copy(config_example, config_file)
        
    if interactive:
        verify_api_keys(base_dir)
