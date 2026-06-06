# PDF Translator AI Bot

A production-grade Telegram bot that receives PDFs, automatically detects the source language, lets the user select a target language, and returns a fully translated PDF — preserving text, tables, images (via OCR), and document structure.

Powered by **Gemini 2.5 Pro** (LangChain LCEL), **Docling** (PDF parsing), **RapidOCR** (image text extraction), and **Lingua** (language detection).

---

## Architecture

```
User → PDF → Telegram Bot
                ↓
          [Download]
                ↓
          Docling Parser
            ├── Text
            ├── Tables (→ Markdown)
            └── Images
                ↓
          RapidOCR (text from images)
                ↓
          Lingua (language detection)
                ↓
          Bot: "Translate to which language?"
                ↓
          User selects target language
                ↓
          LangChain + Gemini 2.5 Pro
            ├── Chunking (RecursiveCharacterTextSplitter)
            ├── Parallel translation (asyncio.gather)
            └── Preserves markdown, tables, structure
                ↓
          Pandoc + WeasyPrint → PDF
                ↓
          Bot sends translated PDF
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Web Framework | FastAPI |
| Telegram Bot | Aiogram v3 |
| AI Pipeline | LangChain (LCEL) |
| LLM | Gemini 2.5 Pro |
| PDF Parsing | Docling |
| OCR | RapidOCR (ONNX Runtime) |
| Language Detection | Lingua |
| PDF Export | Pandoc + WeasyPrint |
| Config | Pydantic Settings + python-dotenv |
| Async | asyncio (full async/await) |

## Project Structure

```
pdf_translator/                          # Project root
├── .env                                 # Single shared environment
├── .env.example                         # Configuration template
├── .gitignore
├── README.md                            # This file
├── storage/
│   ├── downloads/                       # Temporary PDF storage
│   └── outputs/                         # Translated PDF output
│
└── app/
    ├── extractor/                       # Document extractor utility
    │   └── get_document.py
    │
    └── bot_translator/                  # Telegram bot (main project)
        ├── app/
        │   ├── main.py              # FastAPI + bot polling entry point
        │   ├── config.py            # Pydantic settings (loads ../../.env)
        │   ├── bot/
        │   │   ├── router.py        # Aiogram handlers (FSM flow)
        │   │   ├── keyboards.py     # Inline keyboards
        │   │   └── states.py        # FSM states
        │   ├── api/
        │   │   └── routes.py        # Health / status endpoints
        │   ├── services/
        │   │   ├── pdf_service.py       # Docling extraction
        │   │   ├── ocr_service.py       # RapidOCR
        │   │   ├── language_service.py  # Lingua detection
        │   │   ├── translation_service.py  # LangChain + OpenAI
        │   │   ├── render_service.py    # Markdown → PDF
        │   │   └── telegram_service.py  # Aiogram wrapper
        │   ├── langchain/
        │   │   ├── chain.py         # LCEL chain construction
        │   │   ├── prompts.py       # Translation prompts
        │   │   └── splitter.py      # Text splitter
        │   ├── core/
        │   │   ├── logging.py       # Logging configuration
        │   │   └── exceptions.py    # Error hierarchy
        │   ├── models/
        │   │   └── document.py      # Pydantic document models
        │   └── utils/
        │       └── file_helpers.py  # File validation, paths
        ├── tests/
        │   ├── test_language_service.py
        │   ├── test_translation_service.py
        │   ├── test_file_helpers.py
        │   └── test_prompts.py
        └── requirements.txt
```
```

## Installation

### Prerequisites

- Python 3.11+
- Pandoc and WeasyPrint (for PDF rendering)

```bash
# Install pandoc (Ubuntu/Debian)
sudo apt-get install pandoc

# Install pandoc (macOS)
brew install pandoc

# Install WeasyPrint dependencies (Ubuntu/Debian)
sudo apt-get install libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev libcairo2

# Install WeasyPrint (macOS)
brew install weasyprint
```

### Setup

```bash
# Clone the repository
cd pdf_translator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS

# Install dependencies
cd app/bot_translator
pip install -r requirements.txt

# Configure environment (single .env at project root)
cp .env.example .env
# Edit .env with your tokens:
#   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
#   OPENAI_API_KEY=your_openai_api_key
```

## Usage

### Run with Uvicorn

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Run directly (Python)

```python
python -m app.main
```

### Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message and instructions |
| `/cancel` | Cancel current operation |

### Workflow

1. Open Telegram and find your bot
2. Send `/start`
3. Send a PDF file (max 50 MB)
4. The bot detects the source language automatically
5. Select the target language from the inline keyboard
6. Wait for translation — the bot returns the translated PDF

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | App info |
| `GET /api/v1/health` | Health check |
| `GET /api/v1/status` | Translation stats |

## Environment Variables

All variables are set in a single `.env` file at the **project root** (`pdf_translator/.env`).
Both `app/extractor/` and `app/bot_translator/` read from this file via relative paths.

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | Yes | — | Telegram Bot API token |
| `OPENAI_API_KEY` | Yes | — | OpenAI / OpenRouter API key |
| `BASE_URL` | No | `https://openrouter.ai/api/v1` | API base URL |
| `LLM_MODEL` | No | `openai/gpt-oss-120b:free` | Model name |
| `MAX_FILE_SIZE_MB` | No | `50` | Maximum PDF file size |
| `LOG_LEVEL` | No | `INFO` | Logging level |

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Code Quality

```bash
ruff check app/
mypy app/ --ignore-missing-imports
```

## Error Handling

The system handles:
- Invalid file types (non-PDF)
- File size exceeding limit
- Corrupted or unreadable PDFs
- OCR failures (non-fatal, continues with available text)
- Translation chunk failures (falls back to original text for failed chunks)
- Timeouts and network errors

## License

MIT
