import asyncio
import logging

from logging.config import fileConfig
from typing import Optional

# sqlalchemy engine configuration
from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncEngine

# sqlalchemy typing
from sqlalchemy.sql.schema import Column, Table

from alembic import context

# get connection URI
from app.db.database import DATABASE_URL, CustomConnection

# get models Base
from app.db.models import Base

VERSION_TABLE = "library_alembic"

# get alembic migrations logger
log = logging.getLogger("alembic.runtime.migration")

# do not drop tables if unknown to alembic
def include_object(
    obj: Table | Column,
    name: str,
    type_: str,
    reflected: bool,
    compare_to: Optional[Table | Column],
):
    if type_ == "table" and reflected and compare_to is None:
        log.info(
            "Exclude: %s [%s, %s] %s | %s.",
            obj,
            name,
            type_,
            reflected,
            compare_to,
        )
        return False
    else:
        log.info(
            "Include: %s [%s, %s] %s | %s.",
            obj,
            name,
            type_,
            reflected,
            compare_to,
        )
        return True


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# change database URI
config.set_main_option("sqlalchemy.url", str(DATABASE_URL))

# models MetaData
target_metadata = Base.metadata

# configure context
context.configure(
    dialect_name="postgresql",
    version_table=VERSION_TABLE,
    include_object=include_object,
)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = AsyncEngine(
        engine_from_config(
            config.get_section(config.config_ini_section),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
            future=True,
            connect_args={
                "statement_cache_size": 0,
                "prepared_statement_cache_size": 0,
                "connection_class": CustomConnection,
            },
        ),
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
