import sys
import questionary
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from utils.file_parser import parse_links_from_file
from utils.validators import is_valid_youtube_url

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
    link = questionary.text(
        "Cole o link do YouTube (Vídeo ou Playlist):",
        validate=lambda text: is_valid_youtube_url(text) or "Por favor, insira um link válido do YouTube."
    ).ask()
    if link and link.strip():
        return [link.strip()]
    return []

def get_multiple_links_manually() -> list[str]:
    """Coleta múltiplos links interativamente até o usuário enviar uma entrada vazia."""
    console.print("[yellow]Cole um link por vez e pressione ENTER. Pressione ENTER com o campo vazio para finalizar.[/yellow]")
    links = []
    while True:
        link = questionary.text(
            f"Link {len(links) + 1} (vazio para encerrar):",
            validate=lambda text: True if not text.strip() else (is_valid_youtube_url(text) or "Link inválido. Informe uma URL do YouTube.")
        ).ask()
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

    # Validação rigorosa dos links coletados (especialmente para arquivos)
    valid_urls = [u for u in urls_to_process if is_valid_youtube_url(u)]
    invalid_count = len(urls_to_process) - len(valid_urls)
    
    if invalid_count > 0:
        console.print(f"\n[yellow]⚠️ Foram filtrados e ignorados {invalid_count} link(s) inválido(s).[/yellow]")

    # Feedback para o usuário sobre a coleta dos links
    if valid_urls:
        console.print(f"\n[bold green]✅ Sucesso![/bold green] Foi coletado um total de [bold cyan]{len(valid_urls)}[/bold cyan] link(s) válido(s).")
        for idx, url in enumerate(valid_urls, 1):
            console.print(f"  [dim]{idx}.[/dim] {url}")
        
        # O retorno dessa função poderia ser utilizado pelo core (scraper real) na main.py
        return valid_urls
    else:
        console.print("\n[yellow]⚠️ Nenhum link válido foi inserido.[/yellow]")
        return []

def show_playlist_extraction_progress(playlist_id: str, playlist_name: str, fetch_generator) -> list[dict]:
    """Exibe o status visual da extração de uma playlist na CLI."""
    console.print(f"\n[cyan]🗂️ Playlist:[/cyan] [bold]{playlist_name}[/bold] [dim]({playlist_id})[/dim]")
    videos = []
    try:
        # Usa um 'status' loader do rich enquanto puxa dados em cascata
        with console.status("[bold green]Conectando com o YouTube...[/bold green]", spinner="dots") as status:
            for video_batch in fetch_generator(playlist_id):
                for v in video_batch:
                    videos.append(v)
                    # Diminui p/ max 60 chars para não estourar o layout
                    short_title = v['title'][:60] + "..." if len(v['title']) > 60 else v['title']
                    console.print(f"  [dim]📥 Extraído:[/dim] {short_title}")
                    status.update(f"[bold green]Puxando mais vídeos... ({len(videos)} processados)[/bold green]")
        
        console.print(f"\n[bold green]✓ Sucesso! Total de {len(videos)} vídeos capturados de forma estruturada![/bold green]")
        return videos
    except Exception as e:
        console.print(f"[red]Erro ao extrair metadados da playlist: {e}[/red]")
        return []

def show_single_video_progress(video_id: str, fetch_func) -> dict | None:
    """Exibe no painel o carregamento visual e resultado da busca de um único vídeo."""
    try:
        with console.status(f"[bold green]Conectando com YouTube e buscando vídeo...[/bold green]", spinner="dots"):
            video_data = fetch_func(video_id)
            
        if video_data:
            short_title = video_data['title'][:60] + "..." if len(video_data['title']) > 60 else video_data['title']
            console.print(f"\n[cyan]🎬 Vídeo Detectado:[/cyan] [bold]{short_title}[/bold] [dim]({video_id})[/dim]")
            return video_data
        else:
            console.print(f"[red]⚠️ Não foi possível carregar os metadados do vídeo: {video_id}[/red]")
            return None
    except Exception as e:
        console.print(f"[red]Erro ao consultar API do YouTube: {e}[/red]")
        return None
