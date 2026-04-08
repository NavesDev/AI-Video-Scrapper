import sys
from pathlib import Path

# Garante que as importações achem o src corretamente nos testes
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

import pytest
from utils.validators import is_valid_youtube_url

def test_valid_youtube_videos():
    assert is_valid_youtube_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ") is True
    assert is_valid_youtube_url("http://youtube.com/watch?v=dQw4w9WgXcQ&t=4s") is True
    assert is_valid_youtube_url("https://m.youtube.com/watch?v=dQw4w9WgXcQ") is True
    assert is_valid_youtube_url("https://youtu.be/dQw4w9WgXcQ") is True

def test_valid_youtube_playlists():
    assert is_valid_youtube_url("https://www.youtube.com/playlist?list=PLw-VjHDlEOgv_S3hE5w3_T5wF5PqT") is True
    assert is_valid_youtube_url("http://youtube.com/playlist?list=PL_foo_bar") is True

def test_valid_youtube_shorts():
    assert is_valid_youtube_url("https://www.youtube.com/shorts/3Zz-E7R7Z") is True
    assert is_valid_youtube_url("https://youtube.com/shorts/abcdefghijk") is True

def test_invalid_urls():
    # Não tem ID nem path correspondente
    assert is_valid_youtube_url("https://www.youtube.com/") is False
    assert is_valid_youtube_url("https://youtu.be/") is False
    assert is_valid_youtube_url("youtube.com") is False
    
    # Domínios errados
    assert is_valid_youtube_url("https://www.vimeo.com/123456") is False
    assert is_valid_youtube_url("https://google.com") is False
    assert is_valid_youtube_url("isso_nao_e_um_link") is False

def test_invalid_data_types():
    assert is_valid_youtube_url(None) is False
    assert is_valid_youtube_url(123) is False
    assert is_valid_youtube_url("") is False
