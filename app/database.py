import logging
from pathlib import Path

from alembic import command
from alembic.config import Config
from supabase import Client, create_client

from app.config import supabase_settings

logger = logging.getLogger(__name__)

_ALEMBIC_INI = Path(__file__).parent.parent / "alembic.ini"


def _run_migrations() -> None:
    logger.info("Running migrations from: %s", _ALEMBIC_INI)
    cfg = Config(_ALEMBIC_INI)
    command.upgrade(cfg, "head")
    logger.info("Migrations complete")


# Runs at import time — triggered on cold start in Vercel and on startup in Docker
_run_migrations()

supabase: Client = create_client(supabase_settings.url, supabase_settings.service_role_key)
logger.info("Supabase client ready")


def get_supabase() -> Client:
    return supabase
