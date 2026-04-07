import sys

# Adiciona diretório src principal aos caminhos do sistema para importações limpas
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from core.cli import run_cli
from rich.console import Console

console = Console()

def main():
    try:
        while True:
            # A CLI retorna as urls coletadas
            urls = run_cli()
            
            if urls:
                # TODO: Inicializar o pipeline do Scraper da pasta core aqui.
                pass
                
            console.input("\n[dim]Pressione ENTER para voltar ao menu principal...[/dim]")
            
    except KeyboardInterrupt:
        console.print("\n[dim]Aplicação encerrada pelo usuário.[/dim]")
        sys.exit(0)

if __name__ == "__main__":
    main()
