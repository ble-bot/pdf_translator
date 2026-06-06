from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parent.parent.parent # app/bot_translator
PROJECT_ROOT = ROOT_DIR.parent # pdf_translator
ENV_PATH = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    TELEGRAM_BOT_TOKEN: str
    OPENAI_API_KEY: str
    BASE_URL: str = "https://openrouter.ai/api/v1"
    LLM_MODEL: str = "openai/gpt-oss-120b:free"

    MAX_FILE_SIZE_MB: int = 50
    LOG_LEVEL: str = "INFO"

    STORAGE_DIR: Path = PROJECT_ROOT / "storage"
    DOWNLOADS_DIR: Path = PROJECT_ROOT / "storage" / "downloads"
    OUTPUTS_DIR: Path = PROJECT_ROOT / "storage" / "outputs"


settings = Settings()
