import os
import requests
from urllib.parse import urlparse, parse_qs

def extract_playlist_id(url: str) -> str | None:
    """Extrai o ID da playlist a partir de uma URL válida do YouTube."""
    try:
        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        if 'list' in query:
            return query['list'][0]
    except Exception:
        pass
    return None

def extract_video_id(url: str) -> str | None:
    """Extrai o ID do vídeo a partir de uma URL."""
    try:
        parsed = urlparse(url)
        path_lower = parsed.path.lower()
        query = parse_qs(parsed.query)
        if 'youtu.be' in parsed.netloc.lower():
            return parsed.path[1:]
        elif path_lower.startswith('/shorts/'):
            return parsed.path[8:]
        else:
            return query.get('v', [None])[0]
    except:
        return None

def fetch_playlist_title(playlist_id: str) -> str:
    """Acessa a API do YouTube par resgatar o Nome/Título original da Playlist."""
    api_key = os.environ.get("YOUTUBE_API_KEY")
    fallback_name = f"Playlist_{playlist_id}"
    if not api_key:
        return fallback_name
        
    url = f"https://www.googleapis.com/youtube/v3/playlists?part=snippet&id={playlist_id}&key={api_key}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            items = response.json().get("items", [])
            if items:
                return items[0].get("snippet", {}).get("title", fallback_name)
    except Exception:
        pass
        
    return fallback_name

def fetch_playlist_videos(playlist_id: str):
    """
    Consome a API oficial do YouTube para recuperar todos os vídeos de uma playlist.
    Funciona como um 'Generator', retornando lotes (batches) de vídeos para processamento lazy UI.
    """
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        raise ValueError("A chave YOUTUBE_API_KEY não foi encontrada nas variáveis de ambiente.")
        
    base_url = "https://www.googleapis.com/youtube/v3/playlistItems"
    params = {
        "part": "snippet",
        "playlistId": playlist_id,
        "maxResults": 50,
        "key": api_key
    }
    
    while True:
        response = requests.get(base_url, params=params)
        
        if response.status_code != 200:
            raise requests.exceptions.RequestException(
                f"Erro na API do Google ({response.status_code}): {response.text}"
            )
            
        data = response.json()
        batch_videos = []
        
        for item in data.get("items", []):
            snippet = item.get("snippet", {})
            video_id = snippet.get("resourceId", {}).get("videoId")
            title = snippet.get("title", "Título indisponível")
            description = snippet.get("description", "")
            
            # Algumas playlists possuem vídeos deledados que não tem ID
            if video_id:
                batch_videos.append({
                    "video_id": video_id,
                    "title": title,
                    "description": description
                })
        
        # Faz o push do lote completo de até 50 vídeos gerados na UI
        if batch_videos:
            yield batch_videos
                
        next_page_token = data.get("nextPageToken")
        if not next_page_token:
            break
            
        params["pageToken"] = next_page_token
