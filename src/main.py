import sys

# Adiciona diretório src principal aos caminhos do sistema para importações limpas
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from dotenv import load_dotenv

from core.abstracts import collect_abstracts_for_scope
from core.cli import (
    get_summary_source_dir,
    run_cli,
    show_playlist_extraction_progress,
    show_single_video_progress,
    show_ai_generation_progress,
)
from core.config import AppConfig, load_app_config
from core.gemini_api import generate_global_summary_from_abstracts
from core.youtube_api import extract_playlist_id, fetch_playlist_videos, extract_video_id, fetch_playlist_title, fetch_video_metadata
from core.storage import append_extraction, init_session_dir, save_global_summary
from utils.validators import get_youtube_url_type, YouTubeLinkType
from utils.initializer import setup_environment
from rich.console import Console

console = Console()


def _generate_and_save_global_summary(target_dir: Path, abstract_files: list[Path], app_config: AppConfig):
    if not abstract_files:
        console.print("\n[yellow]⚠️ Nenhum resumo Markdown encontrado para agregação.[/yellow]")
        return

    abstract_markdowns: list[str] = []
    for abstract_file in abstract_files:
        try:
            abstract_markdowns.append(abstract_file.read_text(encoding="utf-8"))
        except OSError as error:
            console.print(f"[red]❌ Falha ao ler resumo '{abstract_file}':[/red] {error}")

    if not abstract_markdowns:
        console.print("\n[yellow]⚠️ Nenhum resumo pôde ser lido para gerar o consolidado.[/yellow]")
        return

    try:
        consolidated = generate_global_summary_from_abstracts(abstract_markdowns, app_config=app_config)
        output_path = save_global_summary(target_dir, consolidated)
        console.print(f"[bold green]✓ Resumo global salvo em:[/bold green] {output_path}")
    except (ValueError, RuntimeError, OSError) as error:
        console.print(f"[red]❌ Falha ao gerar/salvar resumo global:[/red] {error}")


def main():
    # Prepara arquivos esqueleto automaticamente pro usuário se ele não preencheu/criou
    setup_environment()
    
    # Carrega variáveis de ambiente como do .env (necessário para YOUTUBE_API_KEY)
    load_dotenv()
    base_dir = Path(__file__).resolve().parent.parent
    app_config = load_app_config(base_dir / "config.json")
    try:
        # Inicializa o diretório /data/session_N desta sessão
        session_dir = init_session_dir()
        console.print(f"[dim]📁 Repositório da sessão salvo em: {session_dir.relative_to(session_dir.parent.parent)}[/dim]\n")
        
        while True:
            cli_payload = run_cli()

            if isinstance(cli_payload, dict):
                action = cli_payload.get("action")
                if action == "aggregate_current_run":
                    abstract_files = collect_abstracts_for_scope(session_dir, scope="current_run")
                    _generate_and_save_global_summary(session_dir, abstract_files, app_config)
                elif action == "aggregate_selected_dir":
                    selected_dir = get_summary_source_dir()
                    if selected_dir is None:
                        console.print("\n[yellow]⚠️ Nenhum diretório informado para agregação.[/yellow]")
                    else:
                        abstract_files = collect_abstracts_for_scope(
                            current_session_dir=session_dir,
                            scope="selected_dir",
                            explicit_dir=selected_dir,
                        )
                        _generate_and_save_global_summary(selected_dir, abstract_files, app_config)
                else:
                    console.print(f"\n[yellow]⚠️ Ação não reconhecida:[/yellow] {action}")
            elif cli_payload:
                console.print("\n[dim]Analisando links e processando rotas...[/dim]")
                for url in cli_payload:
                    url_type = get_youtube_url_type(url)
                    
                    if url_type == YouTubeLinkType.PLAYLIST:
                        playlist_id = extract_playlist_id(url)
                        # Descobre o nome real da playlist usando API
                        playlist_name = fetch_playlist_title(playlist_id)
                        
                        # Toda regra de interface de carregamento está isolada na CLI
                        videos = show_playlist_extraction_progress(playlist_id, playlist_name, fetch_playlist_videos)
                        if videos:
                            # Registra o Node Playlist -> Enum name = "PLAYLIST"
                            append_extraction(session_dir, name=playlist_name, extract_type=url_type.name, payload=videos)
                            console.print(f"[dim]💾 Dados anexados em 'video-metadatas.json'.[/dim]")
                            
                            # Etapa 2: Repassa pra cadeia multimodal sumariar localmente:
                            show_ai_generation_progress(videos, playlist_name, session_dir, app_config=app_config)
                        
                    elif url_type == YouTubeLinkType.VIDEO:
                        video_id = extract_video_id(url)
                        if video_id:
                            video = show_single_video_progress(video_id, fetch_video_metadata)
                            if video:
                                # Registra o Node Video Único -> Enum name = "VIDEO"
                                append_extraction(session_dir, name=video["title"], extract_type=url_type.name, payload=video)
                                console.print(f"[dim]💾 Dados anexados em 'video-metadatas.json'.[/dim]")
                                
                                # Etapa 2: Repassa pra cadeia multimodal 
                                show_ai_generation_progress([video], None, session_dir, app_config=app_config)
                        else:
                            console.print(f"\n[red]❌ Erro ao extrair ID do vídeo na URL:[/red] {url}")
                        
                    else:
                        console.print(f"\n[red]❌ URL não processável nativamente:[/red] {url}")
                
            console.input("\n[dim]Pressione ENTER para voltar ao menu principal...[/dim]")
            
    except KeyboardInterrupt:
        console.print("\n[dim]Aplicação encerrada pelo usuário.[/dim]")
        sys.exit(0)

if __name__ == "__main__":
    main()
