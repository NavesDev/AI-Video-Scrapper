import re
import unicodedata

def normalize_name(text: str) -> str:
    """
    Normaliza o texto para atuar como nome de arquivo e diretório seguros:
    - Minúsculo,
    - Remove acentuação e caracteres estranhos.
    - Troca espaços por '-'
    - Limita em 20 letras (tirando hifens soltos na beirada final)
    """
    if not text:
        return "gerado-sem-nome"
        
    # Remove acentuações e unicode invisível usando normalização de NFKD para base ASCII Pura
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
    text = text.lower()
    
    # regex retem apenas letras do alfabeto ocidental puro e algarismos numéricos e injeta os traços conectivos no vácuo
    text = re.sub(r'[^a-z0-9]+', '-', text)
    
    # Subcorte de 20 limites literais com tratamento higiênico dos resíduos
    text = text[:20].strip('-')
    
    if not text:
        return "gerado-sem-nome"
    return text
