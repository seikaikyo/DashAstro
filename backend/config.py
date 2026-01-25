from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """應用程式設定"""

    # 應用資訊
    app_name: str = "DashAstro API"
    app_version: str = "1.0.0"
    debug: bool = False

    # 資料庫
    database_url: str = ""

    # Claude API
    anthropic_api_key: str = ""

    # CORS
    cors_origins: list[str] = [
        "http://localhost:5173",
        "https://astro.dashai.dev"
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
