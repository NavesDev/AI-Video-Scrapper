import sys

# Adiciona diretório src principal aos caminhos do sistema para importações limpas
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from dotenv import load_dotenv

from core.cli import run_cli, show_playlist_extraction_progress, show_single_video_progress
from core.youtube_api import extract_playlist_id, fetch_playlist_videos, extract_video_id, fetch_playlist_title, fetch_video_metadata
from utils.validators import get_youtube_url_type, YouTubeLinkType
from rich.console import Console

console = Console()

def main():
    # Carrega variáveis de ambiente como do .env (necessário para YOUTUBE_API_KEY)
    load_dotenv()
    
    try:
        while True:
            # A CLI retorna as urls coletadas
            urls = run_cli()
            
            if urls:
                console.print("\n[dim]Analisando links e processando rotas...[/dim]")
                for url in urls:
                    url_type = get_youtube_url_type(url)
                    
                    if url_type == YouTubeLinkType.PLAYLIST:
                        playlist_id = extract_playlist_id(url)
                        # Descobre o nome real da playlist usando API
                        playlist_name = fetch_playlist_title(playlist_id)
                        
                        # Toda regra de interface de carregamento está isolada na CLI
                        videos = show_playlist_extraction_progress(playlist_id, playlist_name, fetch_playlist_videos)
                        
                    elif url_type == YouTubeLinkType.VIDEO:
                        video_id = extract_video_id(url)
                        if video_id:
                            video = show_single_video_progress(video_id, fetch_video_metadata)
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
