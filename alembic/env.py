import asyncio
import sys
import os
from pathlib import Path
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Add the project root to the Python path
# project_root = Path(__file__).parent.parent
# sys.path.insert(0, str(project_root / "src"))

# Import our database configuration and models
from fastapi_book import Base

# Import models so they are registered with Base.metadata
# from projects.chatroom.impl.repo.models import User
# from projects.hospital.domain.models import (
#     Hospitalinfo,
#     Doctorinfo,
#     DoctorScheduling,
#     DoctorSubscribeinfo,
# )

# from projects.wechat.domain.models import User, OAuthToken, PaymentOrder, PaymentNotify
from projects.oauth2.backend.impl.repo.user import UserPO, AuthenticationPO

PREFIX = "sqlalchemy."
SQLALCHEMY_URL = PREFIX + "url"
ASYNC_DATABASE_URL = "postgresql+asyncpg://admin:admin123@localhost:25432/fastapi_book"

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the database URL from our configuration
config.set_main_option(SQLALCHEMY_URL, ASYNC_DATABASE_URL)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option(SQLALCHEMY_URL)
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations with the given connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_schemas=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in async mode."""
    configuration = config.get_section(config.config_ini_section, {})
    configuration[SQLALCHEMY_URL] = ASYNC_DATABASE_URL

    connectable = async_engine_from_config(
        configuration, prefix=PREFIX, poolclass=pool.NullPool
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode using async engine."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
