import json
from pathlib import Path

def parse_links_from_file(file_path: str) -> list[str]:
    """Lê um arquivo local (.txt, .csv, .json) e retorna uma lista de links."""
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Arquivo '{file_path}' não encontrado.")

    links = []
    
    if path.suffix == '.json':
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                links = [item.strip() for item in data if isinstance(item, str) and item.strip()]
            else:
                raise ValueError("O arquivo JSON deve conter uma lista de strings (links).")
    else:
        # Padrão .txt ou .csv simples, um em cada linha ou separado por vírgula no ínicio
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                clean_line = line.strip()
                if clean_line:
                    # Se for CSV simples, pegará a primeira coluna
                    links.append(clean_line.split(',')[0].strip())
                    
    return links
