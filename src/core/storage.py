import os
import json
from pathlib import Path

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
