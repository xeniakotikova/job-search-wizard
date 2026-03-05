import asyncio
import logging
from pathlib import Path

from alembic import command
from alembic.config import Config
from supabase import Client, create_client

from app.config import supabase_settings

logger = logging.getLogger(__name__)

supabase: Client | None = None

_ALEMBIC_INI = Path(__file__).parent.parent / "alembic.ini"


def _run_migrations() -> None:
    try:
        logger.info("Running migrations from: %s", _ALEMBIC_INI)
        cfg = Config(_ALEMBIC_INI)
        command.upgrade(cfg, "head")
        logger.info("Migrations complete")
    except Exception:
        logger.exception("Migration failed")
        raise


async def init_db() -> None:
    global supabase
    try:
        logger.info("Initializing Supabase client (url=%s)", supabase_settings.url)
        supabase = create_client(supabase_settings.url, supabase_settings.service_role_key)
        logger.info("Supabase client ready, starting migrations")
        # Run in a thread so Alembic's asyncio.run() doesn't conflict with FastAPI's event loop
        await asyncio.to_thread(_run_migrations)
        logger.info("Database initialized")
    except Exception:
        logger.exception("init_db failed")
        raise


def get_supabase() -> Client:
    if supabase is None:
        raise RuntimeError("Database not initialized — call init_db() first")
    return supabase
