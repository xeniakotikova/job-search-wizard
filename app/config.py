from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    google_api_key: str
    google_cse_id: str
    telegram_bot_token: str
    telegram_chat_id: str
    search_query: str = "python developer vacancy"
    search_interval_minutes: int = 30
    app_url: str = ""

    model_config = {"env_file": ".env"}


settings = Settings()
