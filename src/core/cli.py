import sys
import questionary
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from utils.file_parser import parse_links_from_file

console = Console()

def show_header():
    """Mostra o cabeçalho estilizado da aplicação."""
    console.clear()
    title = Text("🎥 AI-Video-Scrapper", justify="center", style="bold cyan")
    title.append("\nBem-vindo à ferramenta de scraping de vídeos com IA!", style="dim white")
    panel = Panel(title, border_style="cyan", subtitle="v0.1.0")
    console.print(panel)
    console.print()

def get_single_link() -> list[str]:
    """Coleta um único link do usuário."""
    link = questionary.text("Cole o link do YouTube (Vídeo ou Playlist):").ask()
    if link and link.strip():
        return [link.strip()]
    return []

def get_multiple_links_manually() -> list[str]:
    """Coleta múltiplos links interativamente até o usuário enviar uma entrada vazia."""
    console.print("[yellow]Cole um link por vez e pressione ENTER. Pressione ENTER com o campo vazio para finalizar.[/yellow]")
    links = []
    while True:
        link = questionary.text(f"Link {len(links) + 1} (vazio para encerrar):").ask()
        if not link or not link.strip():
            break
        links.append(link.strip())
    return links

def get_links_from_file() -> list[str]:
    """Coleta links a partir de um arquivo local (.txt, .json, .csv) com tratamento de erros."""
    file_path = questionary.path("Digite o caminho do arquivo (.txt, .json, .csv):").ask()
    if not file_path:
        return []
    
    try:
        links = parse_links_from_file(file_path)
        return links
    except FileNotFoundError as e:
        console.print(f"[red]Erro:[/red] {e}")
    except Exception as e:
        console.print(f"[red]Ocorreu um erro ao ler o arquivo:[/red] {e}")

    return []

def run_cli():
    """Fluxo de execução central da interface via linha de comando."""
    show_header()

    choice = questionary.select(
        "Como você deseja inserir os links?",
        choices=[
            "1. Inserir um único link",
            "2. Inserir múltiplos links manualmente (colar um por um)",
            "3. Importar a partir de um arquivo (.txt ou .json)",
            "4. Sair"
        ]
    ).ask()

    urls_to_process = []

    if not choice or choice.startswith("4"):
        console.print("[dim]Saindo...[/dim]")
        sys.exit(0)

    elif choice.startswith("1"):
        urls_to_process = get_single_link()

    elif choice.startswith("2"):
        urls_to_process = get_multiple_links_manually()

    elif choice.startswith("3"):
        urls_to_process = get_links_from_file()

    # Feedback para o usuário sobre a coleta dos links
    if urls_to_process:
        console.print(f"\n[bold green]✅ Sucesso![/bold green] Foi coletado um total de [bold cyan]{len(urls_to_process)}[/bold cyan] link(s).")
        for idx, url in enumerate(urls_to_process, 1):
            console.print(f"  [dim]{idx}.[/dim] {url}")
        
        # O retorno dessa função poderia ser utilizado pelo core (scraper real) na main.py
        return urls_to_process
    else:
        console.print("\n[yellow]⚠️ Nenhum link foi inserido.[/yellow]")
        return []
