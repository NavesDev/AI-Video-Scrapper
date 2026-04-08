import os
import warnings
from pathlib import Path

# Silencia avisos de depreciação do SDK para manter a CLI limpa
warnings.filterwarnings("ignore", category=FutureWarning, module="google.generativeai")

import google.generativeai as genai

def _load_system_instruction() -> str:
    """Busca o System Prompt na pasta raiz, servindo como persona de IA restrita."""
    base_dir = Path(__file__).parent.parent.parent
    sys_file = base_dir / "system_instruction.md"
    if sys_file.exists():
        return sys_file.read_text(encoding="utf-8")
    return "Inspecione cuidadosamente esse vídeo e me traga um resumo com conhecimentos chave."

def generate_video_summary(video_url: str, video_title: str, video_description: str) -> str:
    """
    Consome o `gemini-3-pro` aplicando as regras sistêmicas do diretório.
    Fornece máxima autonomia pra Engine gerar seu próprio texto Markdown sem Pydatinc Structs forçados,
    permitindo adaptação natural do modelo dependendo dos contextos técnicos detectados no vídeo.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("A chave GEMINI_API_KEY não foi encontrada ou está vazia.")
        
    genai.configure(api_key=api_key.strip())
    
    instruction = _load_system_instruction()
    
    model = genai.GenerativeModel(
        model_name="gemini-3-flash-preview", 
        system_instruction=instruction,
        generation_config={"temperature": 0.3} # Temperatura controlada pra zero alucinações e respostas cruas e diretas
    )
    
    prompt = f"Siga restritamente suas instruções de sistema. Acesse o conteúdo do link deste vídeo abaixo e analise seu conteúdo principal. \n\nURL do YouTube: {video_url}\nTítulo de Busca: {video_title}\nDescrição Resumida:\n{video_description}"
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"## Ocorreu um Erro Crítico de Extração de IA\n\nA engine do Gemini não conseguiu ler a requisição.\nMotivo Técnico: `{str(e)}`"
