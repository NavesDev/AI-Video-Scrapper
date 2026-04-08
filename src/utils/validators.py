import re
from enum import Enum, auto
from urllib.parse import urlparse, parse_qs

class YouTubeLinkType(Enum):
    VIDEO = auto()
    PLAYLIST = auto()
    UNKNOWN = auto()

def is_valid_youtube_url(url: str) -> bool:
    """
    Valida se uma string é uma URL válida do YouTube (Vídeo, Playlist ou Shorts).
    """
    if not url or not isinstance(url, str):
        return False
        
    url = url.strip()
    
    # Validação rápida de domínio via regex
    # Suporta http, https, www, m.youtube, youtu.be, youtube.com
    youtube_regex = (
        r'(https?://)?(www\.|m\.)?'
        r'(youtube\.com/|youtu\.be/)'
    )
    
    if not re.match(youtube_regex, url):
        return False
        
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        path = parsed.path.lower()
        query = parse_qs(parsed.query)
        
        # se for youtu.be (short link), o ID fica no path: youtu.be/VIDEO_ID
        if 'youtu.be' in domain:
            return len(path) > 1 # ex: /abcdefg
            
        if 'youtube.com' in domain:
            # Vídeo principal: youtube.com/watch?v=...
            if path == '/watch':
                return 'v' in query and len(query['v']) > 0
                
            # Playlist: youtube.com/playlist?list=...
            if path == '/playlist':
                return 'list' in query and len(query['list']) > 0
                
            # Shorts: youtube.com/shorts/...
            if path.startswith('/shorts/'):
                return len(path) > 8 # length of /shorts/ is 8
    except Exception:
        return False
        
    return False

def get_youtube_url_type(url: str) -> YouTubeLinkType:
    """Classifica a URL rigidamente apontando a Enum 'VIDEO', 'PLAYLIST' ou 'UNKNOWN'."""
    try:
        parsed = urlparse(url.strip())
        domain = parsed.netloc.lower()
        path = parsed.path.lower()
        query = parse_qs(parsed.query)
        
        if 'youtu.be' in domain and len(path) > 1:
            return YouTubeLinkType.VIDEO
            
        if 'youtube.com' in domain:
            if path == '/watch' and 'v' in query:
                return YouTubeLinkType.VIDEO
            if path == '/playlist' and 'list' in query:
                return YouTubeLinkType.PLAYLIST
            if path.startswith('/shorts/') and len(path) > 8:
                return YouTubeLinkType.VIDEO
    except Exception:
        pass
        
    return YouTubeLinkType.UNKNOWN
