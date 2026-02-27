from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    serpapi_api_key: str
    telegram_bot_token: str
    telegram_chat_id: str
    search_query: str = "python developer vacancy"
    search_interval_minutes: int = 30
    webhook_url: str | None = None

    model_config = {"env_file": ".env"}


settings = Settings()
