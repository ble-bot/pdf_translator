from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = ROOT_DIR / ".env"


class ExtractorSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    OPENAI_API_KEY: str = ""
    OPENROUTER_API_KEY: str = ""
    BASE_URL: str = "https://openrouter.ai/api/v1"
    LLM_MODEL: str = "openai/gpt-oss-120b:free"
    HF_TOKEN: str = ""
    HF_HUB_DISABLE_SYMLINKS_WARNING: bool = True


settings = ExtractorSettings()
