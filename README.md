# AI-Video-Scrapper 🎥

O **AI-Video-Scrapper** é uma ferramenta de automação focada em coletar e processar vídeos (inicialmente voltado ao YouTube) utilizando Inteligência Artificial em seu pipeline. Ele possui uma interface de linha de comando (CLI) interativa, colorida e muito intuitiva para ingestão de links.

## Funcionalidades Atuais

- **Interface CLI Moderna:** Construída utilizando `rich` e `questionary`.
- **Entrada Flexível de Links:**
  - **Link Único:** Insira o link de apenas um vídeo ou playlist.
  - **Múltiplos Links Manuais:** Insira quantos links quiser colando-os sequencialmente pelo prompt interativo.
  - **Via Arquivo:** Importe lotes de links através de arquivos `.txt`, `.csv` ou `.json`.

## Requisitos
- Python 3.9+ (recomendado)

## Instalação e Configuração

Para instalar as bibliotecas mantendo o seu sistema organizado, encorajamos que seja feito dentro de um ambiente virtual (venv):

1. **Crie um ambiente virtual**
   ```bash
   python3 -m venv venv
   ```

2. **Ative o ambiente virtual**
   - **Linux/macOS:**
     ```bash
     source venv/bin/activate
     ```
   - **Windows:**
     ```bash
     venv\Scripts\activate
     ```

3. **Instale as dependências**
   ```bash
   pip install -r src/requirements.txt
   ```

4. **Configuração opcional do runtime (`config.json`)**
   - Na primeira execução, `config.json` é criado automaticamente a partir de `config.example.json` (se ainda não existir).
   - Você pode ajustar:
     - `gemini_model`
     - `temperature`
     - `max_retries_429`
     - `retry_base_seconds`
     - `bilingual_mode`
   - Esse arquivo controla tanto a geração dos resumos por vídeo quanto o resumo global (summary-of-summaries).

## Como Usar

Com o ambiente ativado e as dependências instaladas, basta executar o script principal:

```bash
python src/main.py
```

Você será guiado pelo menu interativo da nossa CLI para selecionar qual o formato de entrada deseja usar.

## Validação de API keys e retentativas

- A inicialização valida `GEMINI_API_KEY`; se o `.env` estiver inválido/ausente mas o processo já tiver uma chave válida exportada, ela é reaproveitada automaticamente sem prompt.
- `YOUTUBE_API_KEY` ausente também é solicitada de forma interativa.
- Chamadas Gemini com erro 429 (rate limit) usam retry exponencial configurável por `max_retries_429` e `retry_base_seconds` no `config.json`.

## Summary-of-summaries

No menu principal, além da ingestão de links, existem duas opções de consolidação:

- **Current run**: agrega os `.md` de `abstracts` da sessão atual e gera um `global-summary*.md` na pasta da sessão.
- **Selected folder/session**: solicita um caminho de pasta via CLI, agrega os `.md` encontrados recursivamente naquele escopo e salva o `global-summary*.md` nesse diretório.

---
*Em desenvolvimento ativo.*
