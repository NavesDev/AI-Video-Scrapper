import os
import json
from pathlib import Path
from utils.formatters import normalize_name

DATA_DIR = Path(__file__).parent.parent.parent / "data"

def init_session_dir() -> Path:
    """Cria e retorna um diretório `data/session_N` novo para a sessão atual."""
    DATA_DIR.mkdir(exist_ok=True, parents=True)
    
    existing_sessions = []
    for item in DATA_DIR.iterdir():
        if item.is_dir() and item.name.startswith("session_"):
            try:
                num = int(item.name.replace("session_", ""))
                existing_sessions.append(num)
            except ValueError:
                pass
                
    next_num = max(existing_sessions) + 1 if existing_sessions else 1
    
    session_dir = DATA_DIR / f"session_{next_num}"
    session_dir.mkdir(exist_ok=True)
    return session_dir

def append_extraction(session_dir: Path, name: str, extract_type: str, payload):
    """
    Empacota a extração no formato estrutural superior de sessão e gera arquivos json incrementais:
    video-metadatas.json, video-metadatas-2.json...
    Formato: {"name": "Nome", "type": "VIDEO|PLAYLIST", ...dados}
    """
    if not payload:
        return
        
    i = 1
    file_path = session_dir / "video-metadatas.json"
    while file_path.exists():
        i += 1
        file_path = session_dir / f"video-metadatas-{i}.json"
                
    # Modelagem do Node
    node = {
        "type": extract_type
    }
    
    if extract_type == "PLAYLIST":
        node["name"] = name
        node["videos"] = payload
    elif extract_type == "VIDEO":
        # Se for video isolado, funde as chaves nativas (video_id, description, title) na raiz
        if isinstance(payload, dict):
            node.update(payload)
            
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump([node], f, indent=4, ensure_ascii=False)

def save_abstract(session_dir: Path, markdown_content: str, title: str, playlist_name: str | None = None):
    """Grava o resumo Markdown gerado pela IA seguindo os limites estruturais de 20 caracteres nos subfolders."""
    abstracts_dir = session_dir / "abstracts"
    
    # Roteamento se for Playlilst (Subpasta extra isolada)
    if playlist_name:
        playlist_norm = normalize_name(playlist_name)
        abstracts_dir = abstracts_dir / playlist_norm
        
    abstracts_dir.mkdir(parents=True, exist_ok=True)
    
    title_base = normalize_name(title)
    file_path = abstracts_dir / f"{title_base}.md"
    
    # Lógica de incremento para evitar colisão em títulos com mesmos 20 caracteres iniciais
    counter = 2
    while file_path.exists():
        file_path = abstracts_dir / f"{title_base}-{counter}.md"
        counter += 1
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)
