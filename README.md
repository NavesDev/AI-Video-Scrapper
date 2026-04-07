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

## Como Usar

Com o ambiente ativado e as dependências instaladas, basta executar o script principal:

```bash
python src/main.py
```

Você será guiado pelo menu interativo da nossa CLI para selecionar qual o formato de entrada deseja usar.

---
*Em desenvolvimento ativo.*
