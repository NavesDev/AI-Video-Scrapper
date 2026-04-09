import os
import time
import warnings
from pathlib import Path

# Silencia avisos de depreciação do SDK para manter a CLI limpa
warnings.filterwarnings("ignore", category=FutureWarning, module="google.generativeai")

import google.generativeai as genai
from core.config import AppConfig
from core.retry import exponential_backoff_seconds, is_rate_limit_error


def _load_system_instruction() -> str:
    """Busca o System Prompt na pasta raiz, servindo como persona de IA restrita."""
    base_dir = Path(__file__).parent.parent.parent
    sys_file = base_dir / "system_instruction.md"
    if sys_file.exists():
        return sys_file.read_text(encoding="utf-8")
    return "Inspecione cuidadosamente esse vídeo e me traga um resumo com conhecimentos chave."


def _build_model(config: AppConfig):
    instruction = _load_system_instruction()
    return genai.GenerativeModel(
        model_name=config.gemini_model,
        system_instruction=instruction,
        generation_config={"temperature": config.temperature},
    )


def _generate_with_retry(model, prompt: str, config: AppConfig, context_label: str) -> str:
    max_attempts = config.max_retries_429 + 1
    for attempt_index in range(max_attempts):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as error:
            if is_rate_limit_error(error):
                if attempt_index < config.max_retries_429:
                    delay_seconds = exponential_backoff_seconds(
                        attempt_number=attempt_index + 1,
                        base_seconds=config.retry_base_seconds,
                    )
                    time.sleep(delay_seconds)
                    continue

                raise RuntimeError(
                    f"Falha ao gerar {context_label} com Gemini após {config.max_retries_429} retries por limite de taxa."
                ) from error

            raise RuntimeError(f"Falha ao gerar {context_label} com Gemini: erro não recuperável.") from error

    raise RuntimeError(f"Falha ao gerar {context_label} com Gemini: fluxo de retry inválido.")


def generate_video_summary(
    video_url: str,
    video_title: str,
    video_description: str,
    app_config: AppConfig | None = None,
) -> str:
    """
    Consome o `gemini-3-pro` aplicando as regras sistêmicas do diretório.
    Fornece máxima autonomia pra Engine gerar seu próprio texto Markdown sem Pydatinc Structs forçados,
    permitindo adaptação natural do modelo dependendo dos contextos técnicos detectados no vídeo.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("A chave GEMINI_API_KEY não foi encontrada ou está vazia.")

    config = app_config or AppConfig()
    genai.configure(api_key=api_key.strip())
    model = _build_model(config)

    prompt = (
        "Siga restritamente suas instruções de sistema. Acesse o conteúdo do link deste vídeo abaixo e analise "
        "seu conteúdo principal. "
        f"\n\nURL do YouTube: {video_url}\nTítulo de Busca: {video_title}\nDescrição Resumida:\n{video_description}"
    )

    return _generate_with_retry(model, prompt, config, "resumo")


def generate_global_summary_from_abstracts(
    abstract_markdowns: list[str],
    app_config: AppConfig | None = None,
) -> str:
    if not abstract_markdowns:
        raise ValueError("Lista de resumos vazia; informe ao menos um resumo para gerar o consolidado.")

    meaningful_abstracts = [abstract.strip() for abstract in abstract_markdowns if abstract and abstract.strip()]
    if not meaningful_abstracts:
        raise ValueError(
            "Nenhum resumo válido encontrado; informe ao menos um resumo com conteúdo para gerar o consolidado."
        )

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("A chave GEMINI_API_KEY não foi encontrada ou está vazia.")

    config = app_config or AppConfig()
    genai.configure(api_key=api_key.strip())
    model = _build_model(config)

    abstracts_payload = "\n\n---\n\n".join(meaningful_abstracts)
    prompt = (
        "Siga restritamente suas instruções de sistema e sintetize os resumos a seguir em um único resumo global, "
        "objetivo e fácil de entender. "
        "Priorize os temas principais, insights práticos e conclusão final.\n\n"
        f"Resumos coletados:\n{abstracts_payload}"
    )

    return _generate_with_retry(model, prompt, config, "resumo global")
