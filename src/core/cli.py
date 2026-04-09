import sys
from pathlib import Path
import questionary
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn

from utils.file_parser import parse_links_from_file
from utils.validators import is_valid_youtube_url

console = Console()

def _is_bilingual_enabled(app_config=None) -> bool:
    if isinstance(app_config, bool):
        return app_config
    if app_config is not None and hasattr(app_config, "bilingual_mode"):
        return bool(app_config.bilingual_mode)
    return True


def show_header(app_config=None):
    """Mostra um cabeçalho amigável para a experiência CLI."""
    bilingual_mode = _is_bilingual_enabled(app_config)
    console.clear()
    title = Text("🎥 VideoScrapper Copilot CLI", justify="center", style="bold cyan")
    if bilingual_mode:
        title.append("\nCollect links, summarize faster. / Colete links e resuma mais rápido.", style="dim white")
        title.append("\nChoose an action to continue. / Escolha uma ação para continuar.", style="white")
        subtitle = "v0.1.0 • PT-BR / EN"
    else:
        title.append("\nColete links e resuma mais rápido.", style="dim white")
        title.append("\nEscolha uma ação para continuar.", style="white")
        subtitle = "v0.1.0 • PT-BR"

    panel = Panel(title, border_style="cyan", subtitle=subtitle)
    console.print(panel)
    console.print()

def get_single_link(bilingual_mode: bool = True) -> list[str]:
    """Coleta um único link do usuário."""
    prompt = (
        "Paste the YouTube link (Video or Playlist): / Cole o link do YouTube (Vídeo ou Playlist):"
        if bilingual_mode else
        "Cole o link do YouTube (Vídeo ou Playlist):"
    )
    error_message = (
        "Please provide a valid YouTube URL. / Por favor, insira um link válido do YouTube."
        if bilingual_mode else
        "Por favor, insira um link válido do YouTube."
    )
    link = questionary.text(
        prompt,
        validate=lambda text: is_valid_youtube_url(text) or error_message
    ).ask()
    if link and link.strip():
        return [link.strip()]
    return []

def get_multiple_links_manually(bilingual_mode: bool = True) -> list[str]:
    """Coleta múltiplos links interativamente até o usuário enviar uma entrada vazia."""
    intro_message = (
        "[yellow]Paste one link at a time and press ENTER. Press ENTER on an empty input to finish. / "
        "Cole um link por vez e pressione ENTER. Pressione ENTER com o campo vazio para finalizar.[/yellow]"
        if bilingual_mode else
        "[yellow]Cole um link por vez e pressione ENTER. Pressione ENTER com o campo vazio para finalizar.[/yellow]"
    )
    prompt_template = (
        "Link {index} (empty to finish) / Link {index} (vazio para encerrar):"
        if bilingual_mode else
        "Link {index} (vazio para encerrar):"
    )
    invalid_message = (
        "Invalid link. Provide a valid YouTube URL. / Link inválido. Informe uma URL do YouTube."
        if bilingual_mode else
        "Link inválido. Informe uma URL do YouTube."
    )
    console.print(intro_message)
    links = []
    while True:
        link = questionary.text(
            prompt_template.format(index=len(links) + 1),
            validate=lambda text: True if not text.strip() else (is_valid_youtube_url(text) or invalid_message)
        ).ask()
        if not link or not link.strip():
            break
        links.append(link.strip())
    return links

def get_links_from_file(bilingual_mode: bool = True) -> list[str]:
    """Coleta links a partir de um arquivo local (.txt, .json, .csv) com tratamento de erros."""
    prompt = (
        "Enter the file path (.txt, .json, .csv): / Digite o caminho do arquivo (.txt, .json, .csv):"
        if bilingual_mode else
        "Digite o caminho do arquivo (.txt, .json, .csv):"
    )
    file_path = questionary.path(prompt).ask()
    if not file_path:
        return []
    
    try:
        links = parse_links_from_file(file_path)
        return links
    except FileNotFoundError as e:
        message = f"[red]Error / Erro:[/red] {e}" if bilingual_mode else f"[red]Erro:[/red] {e}"
        console.print(message)
    except Exception as e:
        message = (
            f"[red]An error occurred while reading the file / Ocorreu um erro ao ler o arquivo:[/red] {e}"
            if bilingual_mode else
            f"[red]Ocorreu um erro ao ler o arquivo:[/red] {e}"
        )
        console.print(message)

    return []


def get_summary_source_dir(bilingual_mode: bool = True) -> Path | None:
    """Solicita via CLI o diretório com resumos .md para agregação final."""
    prompt = (
        "Enter the folder/session path containing Markdown summaries: / Digite o caminho da pasta/sessão contendo os resumos Markdown:"
        if bilingual_mode else
        "Digite o caminho da pasta/sessão contendo os resumos Markdown:"
    )
    selected_path = questionary.path(
        prompt
    ).ask()
    if not selected_path or not selected_path.strip():
        return None
    return Path(selected_path.strip()).expanduser()


def run_cli(app_config=None):
    """Fluxo de execução central da interface via linha de comando."""
    bilingual_mode = _is_bilingual_enabled(app_config)
    show_header(app_config=app_config)

    action_prompt = (
        "What would you like to do? / O que você deseja fazer?"
        if bilingual_mode else
        "O que você deseja fazer?"
    )
    action_choices = (
        [
            "1. Ingest links and generate summaries / Ingerir links e gerar resumos",
            "2. Generate final summary for current run / Gerar resumo final da execução atual",
            "3. Generate final summary for selected folder/session / Gerar resumo final de pasta/sessão",
            "4. Exit / Sair"
        ]
        if bilingual_mode else
        [
            "1. Ingerir links e gerar resumos",
            "2. Gerar resumo final da execução atual",
            "3. Gerar resumo final de pasta/sessão",
            "4. Sair",
        ]
    )

    action_choice = questionary.select(
        action_prompt,
        choices=action_choices
    ).ask()

    if not action_choice or action_choice.startswith("4"):
        console.print("[dim]Saindo...[/dim]")
        sys.exit(0)

    if action_choice.startswith("2"):
        return {"action": "aggregate_current_run"}

    if action_choice.startswith("3"):
        return {"action": "aggregate_selected_dir"}

    ingest_prompt = (
        "How would you like to provide links? / Como você deseja inserir os links?"
        if bilingual_mode else
        "Como você deseja inserir os links?"
    )
    ingest_choices = (
        [
            "1. Insert a single link / Inserir um único link",
            "2. Insert multiple links manually / Inserir múltiplos links manualmente",
            "3. Import links from file (.txt, .json, .csv) / Importar links de arquivo (.txt, .json, .csv)",
            "4. Back / Voltar"
        ]
        if bilingual_mode else
        [
            "1. Inserir um único link",
            "2. Inserir múltiplos links manualmente",
            "3. Importar links de arquivo (.txt, .json, .csv)",
            "4. Voltar",
        ]
    )
    choice = questionary.select(ingest_prompt, choices=ingest_choices).ask()

    urls_to_process = []

    if not choice or choice.startswith("4"):
        cancel_message = (
            "[yellow]Operação cancelada. / Operation canceled.[/yellow]"
            if bilingual_mode else
            "[yellow]Operação cancelada.[/yellow]"
        )
        console.print(cancel_message)
        return []
    if choice.startswith("1"):
        urls_to_process = get_single_link(bilingual_mode)
    elif choice.startswith("2"):
        urls_to_process = get_multiple_links_manually(bilingual_mode)
    elif choice.startswith("3"):
        urls_to_process = get_links_from_file(bilingual_mode)

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

def show_ai_generation_progress(
    videos: list[dict],
    playlist_name: str | None,
    session_dir: Path,
    app_config=None,
):
    """
    Controla a exibição visual da IA. Se for 1 vídeo, mostra spinner simples. 
    Se for playlist, mostra barra de progresso numérica.
    """
    from core.gemini_api import generate_video_summary
    from core.storage import save_abstract
    
    if not videos:
        return
    
    # CASO 1: VÍDEO ÚNICO (Interface simplificada com Spinner)
    if len(videos) == 1:
        v = videos[0]
        title = v.get("title", "Desconhecido")
        vid_id = v.get("video_id", "")
        desc = v.get("description", "")
        
        if "Private video" in title or not vid_id:
            return
            
        url = f"https://www.youtube.com/watch?v={vid_id}"
        with console.status(f"[purple]Processando IA para vídeo único...[/purple] [cyan]{title[:40]}[/cyan]", spinner="aesthetic"):
            try:
                md_resp = generate_video_summary(url, title, desc, app_config=app_config)
                save_abstract(session_dir, md_resp, title, playlist_name)
                console.print(f"[bold green]✓ Resumo Gerado:[/bold green] {title}")
            except Exception as e:
                console.print(f"[red]Erro GenIA:[/red] {e}")
        return

    # CASO 2: PLAYLIST (Interface com Barra de Progresso e Porcentagem)
    label = f"[purple]Processando GenAI ({len(videos)} vídeos)...[/purple]"
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=40),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task(label, total=len(videos))
        
        for v in videos:
            title = v.get("title", "Desconhecido")
            vid_id = v.get("video_id", "")
            desc = v.get("description", "")
            
            if "Private video" in title or not vid_id:
                progress.advance(task)
                continue
            
            progress.update(task, description=f"[cyan]Resumindo:[/cyan] {title[:30]}...")
            url = f"https://www.youtube.com/watch?v={vid_id}"
            
            try:
                md_resp = generate_video_summary(url, title, desc, app_config=app_config)
                save_abstract(session_dir, md_resp, title, playlist_name)
                progress.console.print(f"  [dim]↳ Arquivo salvo com sucesso:[/dim] [green]{title[:40]}...[/green]")
            except Exception as e:
                progress.console.print(f"[red]Erro GenIA no vídeo '{title}':[/red] {e}")
                
            progress.advance(task)
            
    console.print(f"\n[bold green]✓ Todos os resumos Markdown gerados por IA e salvos na pasta 'abstracts'![/bold green]\n")
