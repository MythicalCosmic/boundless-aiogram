from typing import Dict


def get_template_files(project_name: str, template: str, options: dict) -> Dict[str, str]:
    from .base import get_base_files
    base_files = get_base_files(project_name, options)

    template_map = {
        "default": "boundless_aiogram.templates.default",
        "hr": "boundless_aiogram.templates.hr",
        "fastfood": "boundless_aiogram.templates.fastfood",
        "shop": "boundless_aiogram.templates.shop",
        "booking": "boundless_aiogram.templates.booking",
        "education": "boundless_aiogram.templates.education",
        "realestate": "boundless_aiogram.templates.realestate",
        "support": "boundless_aiogram.templates.support",
        "delivery": "boundless_aiogram.templates.delivery",
        "news": "boundless_aiogram.templates.news",
        "restaurant": "boundless_aiogram.templates.restaurant",
        "fitness": "boundless_aiogram.templates.fitness",
    }

    if template in template_map:
        import importlib
        mod = importlib.import_module(template_map[template])
        specific = mod.get_files(project_name, options)
        base_files.update(specific)

    return base_files


def get_alembic_env_template() -> str:
    return '''import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine

from core.config import settings
from database.models.base import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline():
    context.configure(
        url=settings.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    connectable = create_async_engine(settings.DATABASE_URL, poolclass=pool.NullPool)
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
'''
