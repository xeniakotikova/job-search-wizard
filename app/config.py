from pydantic import ConfigDict
from pydantic_settings import BaseSettings

_ENV_FILE = ".env"


class SupabaseSettings(BaseSettings):
    url: str
    anon_key: str
    service_role_key: str
    jwt_secret: str | None = None

    model_config = ConfigDict(env_file=_ENV_FILE, env_prefix="SUPABASE_")


class PostgresSettings(BaseSettings):
    url: str
    url_non_pooling: str
    prisma_url: str | None = None
    user: str | None = None
    password: str | None = None
    host: str | None = None
    database: str | None = None

    model_config = ConfigDict(env_file=_ENV_FILE, env_prefix="POSTGRES_")


class Settings(BaseSettings):
    serpapi_api_key: str
    telegram_bot_token: str
    telegram_chat_id: str
    search_query: str = "python developer vacancy"
    webhook_url: str | None = None

    model_config = ConfigDict(env_file=_ENV_FILE)


settings = Settings()
supabase_settings = SupabaseSettings()
postgres_settings = PostgresSettings()
