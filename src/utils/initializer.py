import shutil
from pathlib import Path
import questionary
from rich.console import Console
from dotenv import get_key, set_key

console = Console()

def verify_api_keys(base_dir: Path):
    """Verifica e solicita as chaves de API caso faltem no .env."""
    env_file = base_dir / ".env"
    if not env_file.exists():
        return
        
    gemini_key = get_key(env_file, "GEMINI_API_KEY")
    if not gemini_key or gemini_key.strip() == "":
        console.print("\n[yellow]⚠️ Chave da IA do Gemini (GEMINI_API_KEY) não encontrada![/yellow]")
        console.print("Obtenha sua chave gratuitamente em: [blue]https://aistudio.google.com/api-keys[/blue]")
        
        token = questionary.password("Coloque sua GEMINI_API_KEY aqui:").ask()
        if token:
            set_key(env_file, "GEMINI_API_KEY", token.strip(), quote_mode="always")
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
        
    # 2. Fallback do system_instruction.md
    sys_inst = base_dir / "system_instruction.md"
    sys_example = base_dir / "system_instruction.md.example"
    
    if not sys_inst.exists() and sys_example.exists():
        shutil.copy(sys_example, sys_inst)
        
    if interactive:
        verify_api_keys(base_dir)
