from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Downpour Trade AI API"
    allowed_origins: str = (
        "http://localhost:3000,"
        "http://127.0.0.1:3000,"
        "https://downpour-trade-ai-virid.vercel.app"
    )
    database_url: str = "sqlite:///./data/downpour.db"
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    scan_interval_min: int = 15
    top_pairs_count: int = 50
    scan_pair_limit: int = 20
    scan_light_mode: bool = False
    scan_workers: int = 5
    verdict_cache_ttl_sec: int = 60
    orderbook_cache_ttl_sec: int = 10
    rate_limit_per_minute: int = 60
    cryptopanic_api_key: str = ""
    discord_webhook_url: str = ""
    slack_webhook_url: str = ""
    openai_api_key: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
