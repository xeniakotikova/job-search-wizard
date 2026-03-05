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
    cfg = Config(_ALEMBIC_INI)
    command.upgrade(cfg, "head")


async def init_db() -> None:
    global supabase
    supabase = create_client(supabase_settings.url, supabase_settings.service_role_key)
    # Run in a thread so Alembic's asyncio.run() doesn't conflict with FastAPI's event loop
    await asyncio.to_thread(_run_migrations)
    logger.info("Database initialized")


def get_supabase() -> Client:
    if supabase is None:
        raise RuntimeError("Database not initialized — call init_db() first")
    return supabase
